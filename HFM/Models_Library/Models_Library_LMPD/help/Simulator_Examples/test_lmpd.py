"""
EN: Acceptance test for LMPD-Simulator. Every number checked here was produced
    by an independent implementation before this library existed, so the test is
    a regression against a known-good state and not against itself.

    Case A -- the worked module of the technical note, isobaric and with
              pressure drop, against the reference boundary-value solution.
    Case B -- the classical limit: family 'none' with the linear closure must
              reproduce the pressure-drop level of the ladder exactly.
    Case C -- the closed forms against adaptive quadrature, and the removable
              singularity at zero curvature.

PT-BR: Teste de aceitacao. Todo numero conferido aqui veio de implementacao
       independente, anterior a esta biblioteca.

Uso: python3 test_lmpd.py
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path[:0] = [os.path.join(ROOT, "src"),
                os.path.abspath(os.path.join(ROOT, "..", "..", "..",
                                             "Classes", "Common_Library", "src"))]

from Simulator_LMPD import SimulatorRunLMPD, SimulatorGeometryLMPD
from Simulator_LMPD.Correction_Factor_LMPD import (phi_family_Q, correction_factor,
                                                   has_finite_layer)
from Common.Streams.Streams import Stream
from Common.MembraneProperties.Membrane_Permeance import Membrane_Permeance

COMP = ["CO2", "CH4", "N2"]
Q_PI = np.array([32.82e-9, 1.641e-9, 3.282e-9])
MW = np.array([44.01e-3, 16.04e-3, 28.02e-3])
MU = np.array([1.5154e-5, 1.1354e-5, 1.8035e-5])
ZF = np.array([0.10, 0.89, 0.01])

_n_ok = _n_bad = 0


def check(nome, obtido, alvo, tol, unidade=""):
    global _n_ok, _n_bad
    d = abs(obtido - alvo)
    rel = d / abs(alvo) if alvo else d
    ok = rel <= tol
    _n_ok += ok; _n_bad += (not ok)
    print(f"  {'PASSOU' if ok else 'FALHOU'}  {nome:<44} "
          f"{obtido:.6g}{unidade}  alvo {alvo:.6g}{unidade}  desvio {100*rel:.3f} %")


def montar(pressure_drop, family, closure, muR=1.2e-5, muP=1.273e-5):
    sim = SimulatorRunLMPD()
    sim.set_feed(Stream(flow=13.889, composition=ZF, pressure=40e5,
                        temperature=303.15, components=COMP,
                        viscosity=MU, molecularweight=MW))
    sim.set_membrane_permeance(Membrane_Permeance(components=COMP, permeance=Q_PI))
    sim.geometry = SimulatorGeometryLMPD(LSingleMembrane=1.3, DiamShell=0.14,
                                         DiamFiber_o=220e-6, DiamFiber_i=80e-6,
                                         NFibers=None, Void_Frac=0.45)
    sim.PPerm = 1e5
    sim.pressure_drop = pressure_drop
    sim.curvature_family = family
    sim.flow_closure = closure
    sim.viscosity_retentate, sim.viscosity_permeate = muR, muP
    return sim


def main():
    print("=" * 92)
    print("GEOMETRIA")
    g = SimulatorGeometryLMPD(LSingleMembrane=1.3, DiamShell=0.14,
                              DiamFiber_o=220e-6, DiamFiber_i=80e-6,
                              NFibers=None, Void_Frac=0.45)
    check("numero de fibras", g.NFibers, 222727, 0.0)
    check("area total", g.AREA_TOTAL, 200.12, 1e-4, " m2")

    print("\nCASO A -- modulo trabalhado, ISOBARICO (familia E, fecho da Eq. 9)")
    r = montar(False, "E", "modes").run()
    check("stage cut", r.stage_cut, 0.17066, 2e-4)
    check("x_R do CO2", r.retentate_fraction("CO2"), 0.02215, 1e-3)
    check("Phi do CO2", r.correction("CO2"), 1.0225, 1e-3)
    check("residuo", max(r.residual, 1e-16), 1e-12, 1e12)

    print("\nCASO A -- modulo trabalhado, COM QUEDA DE PRESSAO")
    r = montar(True, "E", "modes").run()
    check("stage cut", r.stage_cut, 0.137340, 2e-4)
    check("x_R do CO2", r.retentate_fraction("CO2"), 0.04990, 1e-3)
    check("Phi do CO2", r.correction("CO2"), 0.73677, 1e-3)
    check("P_P na ponta fechada", r.PPermSealed / 1e5, 5.66024, 1e-3, " bar")
    check("P_R na saida", r.PRetOut / 1e5, 39.729, 1e-4, " bar")
    check("I_f", r.If, 0.43673, 1e-3)
    print(f"    incognitas {r.n_unknowns}, convergiu {r.converged}, "
          f"|r| {r.residual:.1e}")

    print("\nCASO B -- limite classico: familia 'none' + fecho linear")
    r = montar(True, "none", "linear").run()
    check("I_f e exatamente 1/2", r.If, 0.5, 1e-14)
    check("todo Phi e unitario", float(np.max(np.abs(r.Phi - 1.0))) + 1.0, 1.0, 1e-14)
    check("incognitas caem para n_c+1", r.n_unknowns, 4, 0.0)

    print("\nCASO C -- as formas fechadas contra quadratura adaptativa")
    from scipy.integrate import quad
    import math
    # EN: NOTE what this grid does NOT cover: every c here is positive, so
    #     a_Q + c > 0 throughout and the cancellation branch of CASO F is never
    #     entered. That is why this check passed while the closed form was
    #     returning 0.0 for (a_Q, c) = (100, -300). Kept as written, with the
    #     gap named, because the gap is the lesson.
    # PT-BR: ATENCAO ao que esta grade NAO cobre: todo c aqui e positivo, entao
    #        a_Q + c > 0 sempre e o ramo de cancelamento do CASO F nunca e
    #        visitado. Por isso esta checagem passava com a forma fechada
    #        devolvendo 0.0 em (a_Q, c) = (100, -300).
    pior = 0.0
    for a in (-3.0, -1.0, -0.05, 0.05, 0.3, 2.0, 10.0):
        for c in (0.2, 1.0, 5.0, 8.0):
            num = quad(lambda z: math.exp(-c * z + a * z * (1 - z)), 0, 1,
                       limit=200)[0] / ((1 - math.exp(-c)) / c)
            pior = max(pior, abs(phi_family_Q(a, c) - num) / abs(num))
    check("erro maximo contra quadratura", pior + 1.0, 1.0, 1e-12)
    check("singularidade removivel em a_Q -> 0", phi_family_Q(1e-8, 3.0), 1.0, 1e-7)

    print("\nCASO F -- os pares patologicos da familia Q")
    # EN: Regression for the two failure modes of the thick-layer branch. The
    #     reference values are LITERALS from an arbitrary-precision evaluation
    #     of the defining integral (mpmath, 40 digits) -- NOT from quadrature in
    #     double, which suffers the same cancellation as the closed form and
    #     therefore agrees with the wrong answer. See
    #     HFM/LMPD/closed_form/Numerical_evaluation_of_the_closed_form.md
    #
    #     For c < -a_Q the two terms of the bracket are equal to leading order,
    #     because u^2 - v^2 = -c identically, and the difference loses every
    #     digit. Before the fix the first pair returned 0.0 and the second
    #     returned -1.22e18: finite, plausible, and wrong.
    # PT-BR: Regressao dos dois modos de falha do ramo de camada espessa. Os
    #        valores de referencia sao LITERAIS de precisao arbitraria, e nao de
    #        quadratura em double -- esta sofre o mesmo cancelamento e concorda
    #        com a resposta errada. Antes do conserto o primeiro par devolvia
    #        0.0 e o segundo -1.22e18: finito, plausivel e errado.
    patologicos = (
        # (a_Q,      c,        Phi verdadeiro)            u        v
        (100.0,   -300.0,   1.492609781736705),      # 20.00   -10.00
        (1.34,     -20.76,  1.06156097562716),       #  9.55    -8.39
        (50.0,    -120.0,   1.681250201436603),      # 12.02    -4.95
        (4.0,      -60.0,   1.068715990752139),      # 16.00   -14.00
        (900.0,  -1000.0,   8.752598003968992),      # 31.67    -1.67
        (0.5,       -9.0,   1.044751843150009),      #  6.72    -6.01
        (25.0,     -40.0,   2.279981239158037),      #  6.50    -1.50
    )
    pior = 0.0
    for a, c, alvo in patologicos:
        pior = max(pior, abs(phi_family_Q(a, c) - alvo) / alvo)
    check("cancelamento c < -a_Q contra precisao arbitraria", pior + 1.0, 1.0, 1e-11)
    check("o caso que devolvia 0.0", phi_family_Q(100.0, -300.0),
          1.492609781736705, 1e-12)
    check("o caso que devolvia -1.2e18", phi_family_Q(1.34, -20.76),
          1.06156097562716, 1e-12)

    # EN: Overflow branch. Phi really is ~exp(6e8) at the argument pair that
    #     appeared at the starting point of the three-bar module, so inf is the
    #     correct double. What must NOT happen is nan, which poisons the Newton
    #     residual; and correction_factor must deliver the physical bound.
    # PT-BR: Ramo de overflow. Phi e mesmo ~exp(6e8), entao inf e o double
    #        correto; o que nao pode acontecer e nan.
    v_ovf = phi_family_Q(2.41e9, 4.3873)
    check("overflow devolve +inf e nao nan",
          float(v_ovf == float("inf")), 1.0, 0.0)
    s0o, s1o, co = np.array([4.82e9]), np.array([-4.82e9]), np.array([4.3873])
    check("correction_factor entrega o limite fisico",
          correction_factor(co, s0o, s1o, "Q")[0], 3.0, 1e-14)

    # EN: nan in, nan out -- explicitly, and with no RuntimeWarning emitted,
    #     because a warning here reads to the user as a failure of the model.
    # PT-BR: nan entra, nan sai, e sem RuntimeWarning.
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        nn = correction_factor(np.array([np.nan]), np.array([np.nan]),
                               np.array([np.nan]), "E")
    check("nan entra, nan sai, sem aviso", float(np.isnan(nn[0])), 1.0, 0.0)

    # EN: math.expm1 raises OverflowError below -709; the library form must
    #     saturate instead, or the residual evaluation aborts rather than
    #     merely returning a large number.
    # PT-BR: math.expm1 levanta OverflowError abaixo de -709; a forma da
    #        biblioteca tem de saturar.
    from Simulator_LMPD.Correction_Factor_LMPD.Curvature_Family_LMPD import (
        expm1_ratio, log_expm1_ratio)
    check("expm1_ratio satura e nao levanta",
          float(np.isinf(expm1_ratio(-800.0))), 1.0, 0.0)
    check("log_expm1_ratio permanece finito onde a razao estoura",
          log_expm1_ratio(-800.0), 800.0 - math.log(800.0), 1e-12)

    print("\nCASO G -- a raiz nao fisica de um modulo superdimensionado")
    # EN: This design (permeation factor 17.7, area 239 m2 for 1.9 mol/s of
    #     feed) admits a root of the residual system at stage cut 1.27 -- more
    #     permeated than fed. Nothing downstream catches it: the retentate flow
    #     is negative, so the mole fractions come back positive and summing to
    #     one. It is reachable to a residual of 6e-15, while the cold start that
    #     stays physical stops at 1.0, so selecting on residual alone prefers
    #     the impossible root to the possible one and reports it as converged.
    #
    #     The design is pinned here rather than left to the random sweep in
    #     test_lmpd_properties.py, because that sweep only finds it for one
    #     particular seed. What is asserted is NOT a value -- no physical
    #     solution was established for this module, and the discretised
    #     reference does not converge on it either -- but the REFUSAL: the model
    #     must not report a stage cut at or above one as a converged answer.
    # PT-BR: Este projeto admite raiz do sistema de residuos em corte 1,27 --
    #        mais permeado do que alimentado -- alcancavel com residuo 6e-15,
    #        enquanto a partida que permanece fisica para em 1,0. Escolher pelo
    #        residuo elegia a raiz impossivel. Fixado aqui, e nao deixado a
    #        varredura aleatoria, que so o encontra com uma semente. O que se
    #        afirma nao e um VALOR -- nao se estabeleceu solucao fisica para
    #        este modulo, e a referencia discretizada tambem nao fecha -- e sim
    #        a RECUSA.
    sim_np = SimulatorRunLMPD()
    sim_np.set_feed(Stream(flow=1.8965525695463499,
                           composition=np.array([0.33898671242104617,
                                                 0.6510132875789538, 0.01]),
                           pressure=4296212.77293854, temperature=303.15,
                           components=COMP, viscosity=MU, molecularweight=MW))
    sim_np.set_membrane_permeance(Membrane_Permeance(components=COMP,
                                                   permeance=Q_PI))
    sim_np.geometry = SimulatorGeometryLMPD(
        LSingleMembrane=1.865525527200918, DiamShell=0.16454423621781478,
        DiamFiber_o=2.4474216494043793e-4, DiamFiber_i=1.1352929841120761e-4,
        NFibers=None, Void_Frac=0.631784772221105)
    sim_np.PPerm = 310255.5416077089
    sim_np.pressure_drop = True
    r_np = sim_np.run()
    check("nao e reportado como convergido", float(not r_np.converged), 1.0, 0.0)
    check("o corte reportado fica dentro de (0, 1)",
          float(0.0 < r_np.stage_cut < 1.0), 1.0, 0.0)
    check("a vazao de retentado permanece positiva",
          float(r_np.FRet > 0.0), 1.0, 0.0)
    # EN: and the clip must not be load-bearing at anything called a solution.
    # PT-BR: e o clipe nao pode sustentar nada chamado de solucao.
    check("Phi nao repousa sobre o clipe",
          float(bool(np.all(r_np.Phi > 0.2 + 1e-9))), 1.0, 0.0)

    print("\nCASO E -- o fecho de vazao padrao e o da Eq. (9)")
    check("o padrao da biblioteca e 'modes'",
          float(SimulatorRunLMPD().flow_closure == "modes"), 1.0, 0.0)
    rd = montar(True, "E", "modes").run()
    rp = montar(True, "E", "modes_phi1").run()
    # EN: The two weightings are indistinguishable in accuracy -- the published
    #     selection rests on coherence, not on error -- but they are NOT the
    #     same number, and the difference grows with the pressure drop. Pinned
    #     here so a silent swap of the default cannot pass unnoticed. The Phi=1
    #     weighting is what the prototype's worked-example script used before
    #     this was reconciled, and the difference below is exactly the size of
    #     that correction.
    # PT-BR: Os dois pesos sao indistinguiveis em precisao mas nao sao o mesmo
    #        numero. Fixado para que troca silenciosa do padrao nao passe.
    check("I_f pelo peso a Phi=1", rp.If, 0.42709, 1e-3)
    check("diferenca entre os dois fechos", abs(rd.If - rp.If), 0.00964, 5e-2)
    check("reflexo no corte", abs(rd.stage_cut - rp.stage_cut) / rp.stage_cut,
          0.00193, 1e-1)

    print("\nCASO D -- a triagem de camada degenerada")
    # EN: Slopes that admit no finite layer must fall through to Family Q and
    #     NOT be pushed into the series branch, which would rescale the
    #     amplitude a second time and return Phi = 1 -- a silent failure that
    #     reports the uncorrected model as if it were corrected. This regression
    #     exists because that bug was live and was caught by a smoke test, not
    #     by the checks above: the worked module takes the genuine E branch.
    # PT-BR: Regressao do Phi = 1 silencioso no ramo degenerado.
    # s0/s1 = -0.5, acima de -1: nao ha camada finita / no finite layer
    s0d, s1d, cd = np.array([0.10]), np.array([-0.20]), np.array([1.5])
    check("o par de teste e mesmo degenerado",
          float(not has_finite_layer(s0d[0], s1d[0])), 1.0, 0.0)
    phi_E = correction_factor(cd, s0d, s1d, "E")[0]
    phi_Q = correction_factor(cd, s0d, s1d, "Q")[0]
    check("familia E cai exatamente na familia Q", phi_E, phi_Q, 1e-14)
    check("e o resultado NAO e o modelo sem correcao",
          1.0 + min(abs(phi_E - 1.0), 1.0), 1.0 + min(abs(phi_Q - 1.0), 1.0), 1e-14)
    _ok = abs(phi_E - 1.0) > 5e-3
    print(f"  {'PASSOU' if _ok else 'FALHOU'}  "
          f"{'Phi difere de 1 por margem util':<44} Phi = {phi_E:.6f}")
    globals()['_n_ok'] += _ok; globals()['_n_bad'] += (not _ok)

    print("\n" + "=" * 92)
    print(f"RESULTADO: {_n_ok} passaram, {_n_bad} falharam")
    return 1 if _n_bad else 0


if __name__ == "__main__":
    sys.exit(main())
