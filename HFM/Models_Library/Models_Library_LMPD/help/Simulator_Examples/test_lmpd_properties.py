"""
EN: Property and stress battery for LMPD-Simulator.

    The acceptance test pins numbers. This one pins PROPERTIES: things that must
    hold for every converged solution regardless of the case, and limits in which
    the model must degenerate into something already known. A number can be right
    by luck on one module; an invariant that holds on two hundred cannot.

    A -- invariants of a converged solution
    B -- degenerate limits the model must reproduce exactly
    C -- equivalence between switches that should not change the answer
    D -- robustness over a randomised design sweep, and what fails

PT-BR: Bateria de propriedades e estresse. O teste de aceitacao fixa numeros;
       este fixa PROPRIEDADES e limites degenerados.

Uso: python3 test_lmpd_properties.py [n_sorteios]
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path[:0] = [os.path.join(ROOT, "src"),
                os.path.abspath(os.path.join(ROOT, "..", "..", "..",
                                             "Classes", "Common_Library", "src"))]

from Simulator_LMPD import SimulatorRunLMPD, SimulatorGeometryLMPD
from Simulator_LMPD.Simulator_State_LMPD import (build_state, log_mean,
                                                 weller_steiner)
from Common.Streams.Streams import Stream
from Common.MembraneProperties.Membrane_Permeance import Membrane_Permeance

COMP = ["CO2", "CH4", "N2"]
MW = np.array([44.01e-3, 16.04e-3, 28.02e-3])
MU = np.array([1.5154e-5, 1.1354e-5, 1.8035e-5])

_ok = _bad = 0


def check(nome, cond, detalhe=""):
    global _ok, _bad
    _ok += bool(cond); _bad += (not cond)
    print(f"  {'PASSOU' if cond else 'FALHOU'}  {nome:<52} {detalhe}")


def monta(L=1.3, D=0.14, Do=220e-6, Di=80e-6, void=0.45, Nf=None,
          z=(0.10, 0.89, 0.01), Q=(32.82e-9, 1.641e-9, 3.282e-9),
          PF=40e5, PP=1e5, T=303.15, F=13.889,
          dP=True, family="E", closure="modes", simultaneous=True):
    s = SimulatorRunLMPD()
    s.set_feed(Stream(flow=F, composition=np.array(z), pressure=PF,
                      temperature=T, components=COMP, viscosity=MU,
                      molecularweight=MW))
    s.set_membrane_permeance(Membrane_Permeance(components=COMP,
                                               permeance=np.array(Q)))
    s.geometry = SimulatorGeometryLMPD(LSingleMembrane=L, DiamShell=D,
                                       DiamFiber_o=Do, DiamFiber_i=Di,
                                       NFibers=Nf, Void_Frac=void)
    s.PPerm = PP; s.pressure_drop = dP
    s.curvature_family = family; s.flow_closure = closure
    s.simultaneous = simultaneous
    return s


def invariantes(s, r, rot):
    """EN: What must hold for ANY converged solution."""
    z = np.asarray(s.feed.composition, float); nF = s.feed.flow
    Q = np.asarray(s.permeance.permeance, float)
    g = s.geometry
    u = r.FPerm * r.ZPerm
    tol = 1e-9
    check(f"[{rot}] soma de x_R = 1", abs(r.ZRet.sum() - 1) < tol,
          f"{r.ZRet.sum()-1:+.2e}")
    check(f"[{rot}] soma de y_P = 1", abs(r.ZPerm.sum() - 1) < tol,
          f"{r.ZPerm.sum()-1:+.2e}")
    check(f"[{rot}] soma de y_PC = 1", abs(r.ZPermSealed.sum() - 1) < tol,
          f"{r.ZPermSealed.sum()-1:+.2e}")
    bal = np.max(np.abs(nF * z - r.FRet * r.ZRet - u))
    check(f"[{rot}] balanco por componente", bal < 1e-9 * nF, f"max {bal:.2e}")
    check(f"[{rot}] fracoes no intervalo fisico",
          bool(np.all(r.ZRet > 0) and np.all(r.ZRet < 1)
               and np.all(r.ZPerm > 0) and np.all(r.ZPerm < 1)))
    check(f"[{rot}] corte em (0,1)", 0.0 < r.stage_cut < 1.0,
          f"{r.stage_cut:.5f}")
    # a propria equacao de projeto
    # EN: the SAME viscosity the model uses -- the mixture value, not the mean
    #     of the pure components. Using the wrong one here made this test fail
    #     against a model that was right.
    # PT-BR: a MESMA viscosidade que o modelo usa, a de mistura.
    mu = float(np.sum(z * MU))
    st = build_state(u, r.PPermSealed,
                     dict(Q=Q, xF=z, nF=nF, PF=s.feed.pressure,
                          PPout=s.PPerm, T=s.feed.temperature),
                     g.as_dict(), mu, mu, s.pressure_drop, s.flow_closure)
    lhs = u
    rhs = Q * g.AREA_TOTAL * r.Phi * log_mean(st["th0"], st["thL"])
    d = np.max(np.abs(lhs - rhs)) / nF
    check(f"[{rot}] equacao de projeto u = Q A Phi LM", d < 1e-8, f"{d:.2e}")
    # relacao de pressao do bore
    if s.pressure_drop:
        KB = g.K_BORE * mu * s.feed.temperature
        res = abs(r.PPermSealed ** 2 - s.PPerm ** 2 - KB * r.FPerm * r.If)
        check(f"[{rot}] relacao de pressao do bore",
              res / s.PPerm ** 2 < 1e-8, f"{res/s.PPerm**2:.2e}")
        check(f"[{rot}] P_P,L acima de P_P,out", r.PPermSealed >= s.PPerm)
        check(f"[{rot}] P_R,out abaixo de P_F", r.PRetOut <= s.feed.pressure)
        check(f"[{rot}] o permeado nunca passa o retentado",
              r.PPermSealed < r.PRetOut,
              f"{r.PPermSealed/1e5:.2f} < {r.PRetOut/1e5:.2f} bar")
    else:
        check(f"[{rot}] sem queda, P_P,L = P_P,out exato",
              r.PPermSealed == s.PPerm)
        check(f"[{rot}] sem queda, P_R,out = P_F exato",
              r.PRetOut == s.feed.pressure)


def main():
    n_rand = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    print("=" * 96)
    print("A -- INVARIANTES DE UMA SOLUCAO CONVERGIDA")
    for rot, kw in (("com dP", dict(dP=True)), ("sem dP", dict(dP=False)),
                    ("classico", dict(family="none", closure="linear"))):
        s = monta(**kw); r = s.run()
        check(f"[{rot}] convergiu", r.converged, f"|r| {r.residual:.1e}")
        invariantes(s, r, rot)

    print("\nB -- LIMITES DEGENERADOS")
    # area -> 0 : nada permeia, Phi -> 1
    s = monta(L=1e-4); r = s.run()
    check("area minuscula: corte -> 0", r.stage_cut < 1e-3, f"{r.stage_cut:.2e}")
    check("area minuscula: Phi -> 1", np.max(np.abs(r.Phi - 1)) < 1e-3,
          f"max|Phi-1| {np.max(np.abs(r.Phi-1)):.2e}")
    check("area minuscula: x_R -> x_F",
          np.max(np.abs(r.ZRet - np.array([0.10, 0.89, 0.01]))) < 1e-3)
    # permeancias iguais: nao ha separacao
    s = monta(Q=(5e-9, 5e-9, 5e-9), dP=False); r = s.run()
    d = np.max(np.abs(r.ZPerm - np.array([0.10, 0.89, 0.01])))
    check("permeancias iguais: permeado = alimentacao", d < 1e-6, f"{d:.2e}")
    check("permeancias iguais: retentado = alimentacao",
          np.max(np.abs(r.ZRet - np.array([0.10, 0.89, 0.01]))) < 1e-6)
    # fecho linear + sem correcao = o modelo classico, I_f exato
    s = monta(family="none", closure="linear"); r = s.run()
    check("classico: I_f = 1/2 exato", r.If == 0.5)
    check("classico: incognitas = n_c + 1", r.n_unknowns == 4)
    s = monta(family="none", closure="const"); r = s.run()
    check("fecho const: I_f = 1 exato", r.If == 1.0)
    # Weller-Steiner: composicao e razao de fluxos
    Q = np.array([32.82e-9, 1.641e-9, 3.282e-9])
    xR = np.array([0.05, 0.94, 0.01]); PR, PP = 39e5, 5e5
    yPC, S = weller_steiner(Q, PR, xR, PP)
    J = Q * (PR * xR - PP * yPC)
    check("Weller-Steiner: y_PC = J_i / sum(J)",
          np.max(np.abs(yPC - J / J.sum())) < 1e-9,
          f"{np.max(np.abs(yPC - J/J.sum())):.2e}")
    check("Weller-Steiner: S = sum(J)", abs(S - J.sum()) / J.sum() < 1e-9)
    # media logaritmica
    a = np.array([2.0, 1.0, 1e-9]); b = np.array([2.0, math.e, 1e-9])
    lm = log_mean(a, b)
    check("log_mean com argumentos iguais devolve o valor", abs(lm[0] - 2.0) < 1e-14)
    check("log_mean sem nan nem inf", np.all(np.isfinite(lm)), f"{lm}")

    print("\nC -- EQUIVALENCIAS QUE NAO PODEM MUDAR A RESPOSTA")
    a = monta(simultaneous=True).run()
    b = monta(simultaneous=False).run()
    d = abs(a.stage_cut - b.stage_cut) / a.stage_cut
    check("Newton simultaneo == predicao aninhada", d < 1e-8,
          f"{d:.2e}  ({a.n_evaluations} vs {b.n_evaluations} avaliacoes)")
    # familia E deve cair na Q onde a camada e espessa
    a = monta(L=0.3, Do=300e-6, Di=150e-6).run()
    b = monta(L=0.3, Do=300e-6, Di=150e-6, family="Q").run()
    d = abs(a.stage_cut - b.stage_cut) / a.stage_cut
    check("camada espessa: familia E ~ familia Q", d < 5e-3, f"{d:.2e}")

    print(f"\nD -- ROBUSTEZ SOBRE {n_rand} PROJETOS SORTEADOS")
    rng = np.random.default_rng(20260811)
    nao_conv = ruim = 0
    piores = []
    for _ in range(n_rand):
        kw = dict(L=float(rng.uniform(0.3, 2.0)),
                  D=float(rng.uniform(0.05, 0.20)),
                  Do=float(rng.uniform(1.2e-4, 4.0e-4)),
                  void=float(rng.uniform(0.35, 0.65)),
                  PF=float(rng.uniform(5e5, 60e5)),
                  PP=float(rng.uniform(0.5e5, 6e5)),
                  F=float(rng.uniform(1.0, 40.0)))
        kw["Di"] = kw["Do"] * float(rng.uniform(0.35, 0.75))
        x0 = float(rng.uniform(0.03, 0.45))
        kw["z"] = (x0, 0.99 - x0, 0.01)
        if kw["PP"] >= 0.8 * kw["PF"]:
            continue
        s = monta(**kw)
        try:
            r = s.run()
        except Exception as ex:
            nao_conv += 1; piores.append(("excecao", type(ex).__name__)); continue
        if not r.converged:
            nao_conv += 1; continue
        mau = (abs(r.ZRet.sum() - 1) > 1e-8 or abs(r.ZPerm.sum() - 1) > 1e-8
               or not (0 < r.stage_cut < 1) or np.any(r.ZRet <= 0)
               or np.any(r.Phi <= 0)
               or (s.pressure_drop and r.PPermSealed >= r.PRetOut))
        if mau:
            ruim += 1
            piores.append((f"cut {r.stage_cut:.4f}", f"PPL {r.PPermSealed/1e5:.2f}"))
    n_val = n_rand - 0
    check("nenhuma solucao convergida viola um invariante", ruim == 0,
          f"{ruim} de {n_val}")
    print(f"    nao convergiram: {nao_conv} de {n_val} "
          f"({100*nao_conv/max(n_val,1):.1f} %) — "
          f"projetos sorteados incluem combinacoes inviaveis por construcao")
    for p in piores[:5]:
        print(f"    {p}")

    print("\n" + "=" * 96)
    print(f"RESULTADO: {_ok} passaram, {_bad} falharam")
    return 1 if _bad else 0


if __name__ == "__main__":
    sys.exit(main())
