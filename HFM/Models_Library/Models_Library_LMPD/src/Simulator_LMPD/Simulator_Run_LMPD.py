#region Title: SimulatorRunLMPD
# Nature: Run LMPD
# Methodology: Orchestration of the algebraic simulator. One simultaneous Newton
#              system in the permeated amounts, the sealed-end permeate pressure
#              and the correction factors. No mesh, no quadrature, no nested
#              iteration over the model.
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#  0.0       11-Aug-2026    J.V.A. Tupinamba               First version, mirrors SimulatorRunHFM
##################################################################################################################
#endregion

import math
from typing import Optional, Any

import numpy as np
from scipy.optimize import root

from .Simulator_Geometry_LMPD import SimulatorGeometryLMPD
from .Simulator_Results_LMPD import SimulatorResultsLMPD
from .Simulator_State_LMPD import build_state, log_mean
from .Correction_Factor_LMPD.Terminal_Slopes_LMPD import terminal_slopes
from .Correction_Factor_LMPD.Curvature_Family_LMPD import (
    correction_factor, PHI_MIN, PHI_MAX)

from Common.Streams.Streams import Stream
from Common.MembraneProperties.Membrane_Permeance import Membrane_Permeance


class LMPDNotConverged(RuntimeError):
    """
    EN: Raised when the Newton system fails to converge from every starting
        point. Lets an enumeration catch the candidate explicitly instead of
        consuming a garbage solution -- the same contract SimulationNotConverged
        offers in the HFM library.
    PT-BR: Levantada quando o Newton falha em todas as partidas.
    """
    pass


class SimulatorRunLMPD:
    """
    EN: Algebraic log-mean pressure difference simulator for a countercurrent
        hollow fiber module, shell-side feed and bore-side permeate.

        WHAT IT SOLVES. Every LMPD model computes the permeated amount of each
        species as a permeance times an area times ONE representative driving
        force built from the terminal states. The logarithmic mean is exact when
        the driving force decays exponentially; it does not, and the correction
        factor Phi_i is defined as the ratio of the true mean to the log-mean,
        so it measures exactly what the classical derivation neglects and
        nothing else.

        WHY IT IS ONE NEWTON. Phi_i is available in CLOSED FORM from the two
        terminal driving forces and the two terminal slopes of eta. Being closed
        form, it can be carried as an unknown of the same system rather than
        recomputed in an outer loop, which is what makes the whole calculation a
        single solve in 2 n_c + 1 variables. The nested alternative converges to
        the identical solution -- it is the same system -- in thirteen to
        twenty-three outer passes.

        Interface intentionally mirrors SimulatorRunHFM, so a design and a feed
        can be handed to either simulator unchanged.

    PT-BR: Simulador algebrico LMPD para modulo contracorrente, alimentacao pelo
           casco. Um unico Newton em 2 n_c + 1 incognitas, porque Phi_i tem forma
           fechada e entra como incognita em vez de laco externo. Interface
           igual a da SimulatorRunHFM de proposito.
    """

    # EN: Starting points, as permeated fractions of the feed of each species.
    # PT-BR: Partidas, como fracao permeada da alimentacao de cada especie.
    COLD_STARTS = (0.05, 0.15, 0.35, 0.60)

    # EN: Two thresholds, and conflating them is a mistake worth naming. The
    #     first is an EARLY EXIT: once a starting point reaches it there is
    #     nothing to gain from trying the others, so the loop stops. The second
    #     is the CONVERGENCE VERDICT: whether the solution may be used at all.
    #     They are three orders apart on purpose. Every residual here is scaled
    #     -- component balances by the feed of that species, the pressure
    #     relation by P_P,out squared -- so 1e-8 already means the balances close
    #     to one part in a hundred million. Using the early-exit value as the
    #     verdict marks perfectly good solutions as failures: the CO2/propane
    #     module at selectivity 882 lands at 6e-10 and is correct to 0.2 %.
    # PT-BR: Dois limiares. O primeiro e SAIDA ANTECIPADA entre as partidas; o
    #        segundo e o VEREDITO de convergencia. Confundir os dois reprova
    #        solucao boa: o modulo CO2/propano para em 6e-10 e esta certo.
    EARLY_EXIT_TOL = 1e-11
    RESIDUAL_TOL = 1e-8

    def __init__(self):
        self.feed: Optional[Stream] = None
        self.permeance: Optional[Membrane_Permeance] = None
        self.geometry: Optional[SimulatorGeometryLMPD] = None

        # EN: Model switches, named as in the HFM simulator where they coincide.
        # PT-BR: Chaves do modelo, nomeadas como no simulador HFM.
        self.pressure_drop: bool = True
        self.curvature_family: str = "E"      # 'E', 'Q' or 'none'
        self.flow_closure: str = "modes"      # Eq. (9); see Flow_Closure_LMPD.CLOSURES
        self.simultaneous: bool = True
        self.PPerm: float = 1e5

        # EN: One constant viscosity per side. The algebraic model carries no
        #     profile, so a composition-dependent viscosity would have nowhere
        #     to vary; using the feed mixture value on both sides is the
        #     consistent choice and is what the reference comparison uses.
        # PT-BR: Uma viscosidade constante por lado.
        self.viscosity_retentate: Optional[float] = None
        self.viscosity_permeate: Optional[float] = None

        self.case_name: tuple = ("lmpd", "case")

    # ------------------------------------------------------------------ setup
    def set_feed(self, feed: Stream) -> None:
        """EN: Feed stream. PT-BR: Corrente de alimentacao."""
        self.feed = feed

    def set_membrane_permeance(self, permeance: Membrane_Permeance) -> None:
        """EN: Membrane permeances. PT-BR: Permeancias da membrana."""
        self.permeance = permeance

    def _mixture_viscosity(self) -> float:
        mu = getattr(self.feed, "viscosity", None)
        if mu is None:
            raise ValueError("feed.viscosity is required / viscosidade obrigatoria")
        mu = np.asarray(mu, float)
        if mu.ndim == 0:
            return float(mu)
        return float(np.sum(np.asarray(self.feed.composition, float) * mu))

    def _pack(self) -> tuple:
        if self.feed is None or self.permeance is None or self.geometry is None:
            raise ValueError("feed, permeance and geometry must be set first")
        Q = np.asarray(self.permeance.permeance, float)
        xF = np.asarray(self.feed.composition, float)
        info = dict(Q=Q, xF=xF, nF=float(self.feed.flow),
                    PF=float(self.feed.pressure), PPout=float(self.PPerm),
                    T=float(self.feed.temperature))
        return info, self.geometry.as_dict(), Q, xF

    # ------------------------------------------------------------------- solve
    def _residual_factory(self, info, geo, muR, muP):
        Q, xF, nF, nc = info["Q"], info["xF"], info["nF"], len(info["Q"])
        use_phi = self.simultaneous and self.curvature_family != "none"

        def residual(v):
            u = np.abs(v[:nc]) * nF * xF
            PPL = abs(v[nc]) * info["PPout"] if self.pressure_drop else info["PPout"]
            Phi = v[nc + 1:] if use_phi else None
            st = build_state(u, PPL, info, geo, muR, muP,
                             self.pressure_drop, self.flow_closure)
            if Phi is None:
                Phi = self._predict(st)
            r = list((u - Q * geo["Atot"] * Phi * log_mean(st["th0"], st["thL"]))
                     / (nF * xF))
            if self.pressure_drop:
                r.append((PPL ** 2 - info["PPout"] ** 2
                          - geo["K_bore"] * muP * info["T"] * st["ut"] * st["If"])
                         / info["PPout"] ** 2)
            else:
                r.append(0.0)
            if use_phi:
                r += list(Phi - self._predict(st))
            return r

        return residual, use_phi

    def _predict(self, st: dict) -> np.ndarray:
        """EN: Phi_i in closed form. PT-BR: Phi_i em forma fechada."""
        if self.curvature_family == "none":
            return np.ones(len(st["Q"]))
        if np.any(st["th0"] <= 0) or np.any(st["thL"] <= 0):
            return np.ones(len(st["Q"]))
        c, s0, s1 = terminal_slopes(st)
        return correction_factor(c, s0, s1, self.curvature_family)

    def run(self) -> SimulatorResultsLMPD:
        """
        EN: Solve and return the results container. Never returns a silently bad
            solution: if no starting point converges below RESIDUAL_TOL the best
            residual found is reported and converged stays False.
        PT-BR: Resolve e devolve os resultados. Nunca devolve solucao ruim em
               silencio.
        """
        info, geo, Q, xF = self._pack()
        nc = len(Q)
        mu = self._mixture_viscosity()
        muR = self.viscosity_retentate if self.viscosity_retentate else mu
        muP = self.viscosity_permeate if self.viscosity_permeate else mu

        residual, use_phi = self._residual_factory(info, geo, muR, muP)

        # EN: Starting ratio for the sealed-end permeate pressure, P_P,L / P_P,out.
        #     It MUST lie inside the physical range [1, P_F/P_P,out): the bore is
        #     fed by permeation, so its dead end can never reach the retentate
        #     pressure. A fixed 3.0 satisfies that only while the module is run at
        #     a high pressure ratio. On a three-bar module with a one-bar permeate
        #     -- Scholz et al., and any low-ratio case -- 3.0 lands exactly ON the
        #     feed pressure, so the starting point has zero driving force at the
        #     sealed end. The terminal slope there diverges, Phi comes back as nan,
        #     and the Newton spends its first twenty evaluations inside a nan
        #     region before finding its way out. It did converge, but by luck.
        #     Half the available span reproduces the previous 3.0 exactly whenever
        #     P_F/P_P,out >= 5, which covers the whole design grid of the article.
        # PT-BR: Razao de partida de P_P,L. Precisa cair DENTRO da faixa fisica: o
        #        bore e alimentado por permeacao e a ponta selada nunca alcanca a
        #        pressao do retentado. O valor fixo 3.0 so respeita isso em razao
        #        de pressoes alta; num modulo de 3 bar com permeado a 1 bar ele
        #        cai exatamente SOBRE a alimentacao e a partida nasce com forca
        #        motriz nula. Metade do vao disponivel reproduz o 3.0 anterior
        #        sempre que P_F/P_P,out >= 5, ou seja, em toda a grade do artigo.
        r_max = info["PF"] / info["PPout"]
        pp0 = min(3.0, 1.0 + 0.5 * (r_max - 1.0)) if self.pressure_drop else 1.0

        # EN: WHY A ROOT IS NOT AUTOMATICALLY A SOLUTION.
        #     The residual system does not know that the module has a finite
        #     feed. The unknowns enter as |v_i| n_F x_F with no upper bound, so a
        #     root with sum(u) > n_F -- more permeated than fed -- satisfies every
        #     equation exactly. It is not caught downstream either: the retentate
        #     flow goes NEGATIVE, and the mole fractions, being ratios of two
        #     negative numbers, come back positive and summing to one. Every
        #     sanity check on composition passes on a state that cannot exist.
        #
        #     Such a root is also reachable to machine precision. On a heavily
        #     oversized module (permeation factor 17.7) one cold start converges
        #     to a residual of 6e-15 at a stage cut of 1.27, while the start that
        #     stays physical does not converge at all. Selecting on residual
        #     alone therefore picks the impossible answer OVER the possible one,
        #     and reports it with the highest confidence the code can express.
        #
        #     A second tell accompanies it: Phi rests exactly on PHI_MIN. The
        #     clip is documented as a bound that a converged state cannot reach,
        #     and the flat residual it creates is part of what lets Newton park
        #     there. Both conditions are therefore tested, and a root that fails
        #     either is never preferred to one that passes.
        # PT-BR: POR QUE UMA RAIZ NAO E AUTOMATICAMENTE UMA SOLUCAO. O sistema de
        #        residuos nao sabe que a alimentacao e finita: uma raiz com
        #        sum(u) > n_F satisfaz todas as equacoes, e a jusante nada pega,
        #        porque a vazao de retentado fica NEGATIVA e as fracoes molares,
        #        razao de dois negativos, voltam positivas e somando um. Pior,
        #        essa raiz e alcancavel com residuo 6e-15 enquanto a partida que
        #        permanece fisica nao converge -- escolher pelo residuo elege a
        #        resposta impossivel. Junto vem Phi exatamente sobre PHI_MIN, um
        #        limite que estado convergido nao deveria alcancar. As duas
        #        condicoes sao testadas.
        def _fisica(v):
            """EN: (ok, reason). PT-BR: (ok, motivo)."""
            u_ = np.abs(v[:nc]) * info["nF"] * xF
            cut_ = float(u_.sum()) / info["nF"]
            if not np.isfinite(cut_) or not (0.0 < cut_ < 1.0):
                return False, f"stage cut {cut_:.4f} outside (0, 1)"
            if use_phi:
                ph = np.asarray(v[nc + 1:], float)
                if np.any(ph <= PHI_MIN * (1.0 + 1e-9)) or \
                   np.any(ph >= PHI_MAX * (1.0 - 1e-9)):
                    return False, ("correction factor resting on the clip "
                                   f"[{PHI_MIN}, {PHI_MAX}]")
            return True, ""

        best, best_res, n_eval = None, np.inf, 0
        best_ok, motivo = False, ""
        for f0 in self.COLD_STARTS:
            v0 = np.append(np.full(nc, f0), pp0)
            if use_phi:
                v0 = np.append(v0, np.ones(nc))
            try:
                sol = root(residual, v0, method="hybr", tol=1e-12)
            except Exception:
                continue
            n_eval += int(getattr(sol, "nfev", 0))
            m = float(np.max(np.abs(residual(sol.x))))
            ok, por = _fisica(sol.x)
            # EN: physical beats non-physical regardless of residual; residual
            #     decides only between roots of the same standing.
            # PT-BR: fisica vence nao-fisica independente do residuo.
            melhor = (ok and not best_ok) or (ok == best_ok and m < best_res)
            if best is None or melhor:
                best, best_res, best_ok, motivo = sol.x, m, ok, por
            if ok and m < self.EARLY_EXIT_TOL:
                break

        res = SimulatorResultsLMPD()
        res.components = list(self.feed.components)
        res.case_name = self.case_name
        res.family = self.curvature_family
        res.closure = self.flow_closure
        res.n_unknowns = (2 * nc + 1) if use_phi else (nc + 1)
        res.n_evaluations = n_eval
        res.residual = best_res

        if best is None or not np.isfinite(best_res):
            res.feasible = False
            res.message = "Newton failed from every starting point"
            return res

        u = np.abs(best[:nc]) * info["nF"] * xF
        PPL = abs(best[nc]) * info["PPout"] if self.pressure_drop else info["PPout"]
        st = build_state(u, PPL, info, geo, muR, muP,
                         self.pressure_drop, self.flow_closure)
        Phi = best[nc + 1:] if use_phi else self._predict(st)
        # EN: Same guard _predict applies. Without it a converged state with a
        #     pinched species -- theta <= 0 at a terminal -- divides by zero here
        #     and reports inf slopes, in a call that exists only for reporting.
        # PT-BR: Mesma guarda do _predict; sem ela um estado com especie em pinch
        #        divide por zero numa chamada que so serve para relatar.
        pinch = np.any(st["th0"] <= 0) or np.any(st["thL"] <= 0)
        c, s0, s1 = ((np.array([]),) * 3
                     if (self.curvature_family == "none" or pinch)
                     else terminal_slopes(st))

        # EN: A non-physical root is reported as NOT converged, and the message
        #     names the violation rather than the residual -- the residual is
        #     tiny in exactly this case and quoting it would mislead. feasible
        #     stays False so that an enumeration discards the candidate instead
        #     of consuming it.
        # PT-BR: Raiz nao fisica e reportada como NAO convergida, e a mensagem
        #        nomeia a violacao em vez do residuo, que aqui e minusculo e
        #        enganaria. feasible fica False para a enumeracao descartar.
        if not best_ok:
            res.feasible = False
            res.converged = False
            res.message = (f"no physical root found: {motivo} "
                           f"(residual {best_res:.2e})")
        else:
            res.converged = best_res < self.RESIDUAL_TOL
            res.message = "" if res.converged else f"residual {best_res:.2e}"
        res.stage_cut = st["ut"] / info["nF"]
        res.FRet, res.FPerm = st["FR"], st["ut"]
        res.ZRet, res.ZPerm, res.ZPermSealed = st["xR"], st["yP"], st["yPC"]
        res.PRetIn, res.PRetOut = info["PF"], st["PRo"]
        res.PPermOut, res.PPermSealed = info["PPout"], PPL
        res.Phi, res.If = np.asarray(Phi, float), st["If"]
        res.c_chord, res.slope_feed, res.slope_sealed = c, s0, s1
        return res
