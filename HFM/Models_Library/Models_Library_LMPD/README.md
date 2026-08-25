# LMPD-Simulator

Algebraic log-mean pressure difference simulator for a countercurrent hollow
fiber membrane module, shell-side feed and bore-side permeate. Companion to
`HFM-Simulator`, and deliberately interface-compatible with it: the same
`Stream`, the same `Membrane_Permeance`, the same geometric parameterisation, so
a design can be handed to either simulator unchanged.

## What it solves, and what makes it one Newton

Every LMPD model computes the permeated amount of each species as a permeance
times an area times **one** representative driving force built from the terminal
states. The logarithmic mean is exact when the driving force decays
exponentially between the terminals. It does not, and the correction factor

    Phi_i = <theta_i> / theta_i,LM

is defined as the ratio of the true mean to the log-mean, so it measures exactly
what the classical derivation neglects and nothing else. `Phi_i = 1` recovers
Hogsett–Mazur and Pettersen–Lien alike.

`Phi_i` is available in **closed form** from four numbers per species — the two
terminal driving forces and the two terminal slopes of `eta`, the departure of
`ln theta` from the chord between them. Being closed form, it is carried as an
unknown of the same system instead of being recomputed in an outer loop, which
makes the whole calculation a single Newton solve in `2 n_c + 1` variables.

**No integral is evaluated numerically anywhere in the solution path.** There is
no mesh, no quadrature and no profile. That is the point: four algebraic
equations can be embedded in a mixed-integer nonlinear program and can carry
certifiable bounds, and a discretised boundary-value problem cannot.

## Layout

    src/Simulator_LMPD/
      Simulator_Run_LMPD.py             orchestration, the Newton system
      Simulator_Geometry_LMPD.py        passive geometry, K_bore and K_shell
      Simulator_State_LMPD.py           state assembly, Weller-Steiner closure
      Simulator_Results_LMPD.py         results container
      Correction_Factor_LMPD/
        Terminal_Slopes_LMPD.py         exact slopes, L'Hopital at the sealed end
        Curvature_Family_LMPD.py        Families E and Q, the four guards
        Flow_Closure_LMPD.py            I_f, derived rather than assumed
    help/Simulator_Examples/
      test_lmpd.py                      acceptance test, 25 checks
      test_lmpd_properties.py           invariants and stress, 49 checks

## Usage

```python
from Simulator_LMPD import SimulatorRunLMPD, SimulatorGeometryLMPD
from Common.Streams.Streams import Stream
from Common.MembraneProperties.Membrane_Permeance import Membrane_Permeance

sim = SimulatorRunLMPD()
sim.set_feed(Stream(flow=13.889, composition=[0.10, 0.89, 0.01], pressure=40e5,
                    temperature=303.15, components=["CO2", "CH4", "N2"],
                    viscosity=MU, molecularweight=MW))
sim.set_membrane_permeance(Membrane_Permeance(components=["CO2", "CH4", "N2"],
                                             permeance=Q))
sim.geometry = SimulatorGeometryLMPD(LSingleMembrane=1.3, DiamShell=0.14,
                                     DiamFiber_o=220e-6, DiamFiber_i=80e-6,
                                     NFibers=None, Void_Frac=0.45)
sim.PPerm = 1e5
sim.pressure_drop = True
sim.curvature_family = "E"      # 'E', 'Q', or 'none' for the classical model
sim.flow_closure = "modes"      # Eq. (9); ver CLOSURES

r = sim.run()
print(r.summary())
```

## Switches

| switch | values | meaning |
|---|---|---|
| `pressure_drop` | `True` / `False` | when `False`, both `K` vanish, `P_P,L` leaves the unknowns and the remaining system is unchanged |
| `curvature_family` | `E`, `Q`, `none` | `E` is an elementary series, `Q` its thick-layer limit and an error function, `none` the classical model |
| `flow_closure` | see `CLOSURES` | `modes` is the derived closure of Eq. (9), weighted by `u_i/u_tot`, and is the default; `linear` is `I_f = 1/2` and reproduces the classical pressure-drop level exactly |
| `simultaneous` | `True` / `False` | `False` predicts `Phi_i` inside the residual instead of carrying it as an unknown. Same solution, more evaluations |

### A note on the closure name

The prototype this library was ported from carries two mode weightings under
names that invite confusion, and they are worth separating once and for all.

The derivation weights each mode by `u_i/u_tot`, the amount the model actually
solves for, because `F_P(0) = sum_i u_i` exactly. That is Eq. (9), it is the
coherent choice, and **it is what `modes` means here** and is the default. The
prototype called it `modes_u`.

The prototype's own `modes` was a **different** weighting,
`Q_i theta_i,0 (1 - e^-c)/c` — the permeated amount the LMPD hypothesis alone
would give, that is, the amount at `Phi = 1`. The two coincide only in the
uncorrected model. It is kept here as `modes_phi1`, under a name that says what
it is, because part of the prototype's output was produced with it.

**This has been reconciled.** The prototype's grid analysis always ran on
`u_i/u_tot`, but its worked-example and audit scripts ran on the `Phi = 1`
weighting, so the table that illustrates Eq. (9) had been computed with a
weighting that is not Eq. (9) — and the audit compared against that same
weighting, so it did not flag it. `regen1.py`, `figs.py`, `audit_final.py`,
`regen2.py`, `exact_lh.py` and `trace.py` were switched to `u_i/u_tot` and the
worked-example numbers regenerated and propagated to `HANDOFF.md`,
`technical_note_source.md` and `article_source.md`:

| quantity | was | is |
|---|---|---|
| stage cut, with `dP` | 0.137606 | **0.137340** |
| `x_R,CO2`, with `dP` | 0.04972 | **0.04990** |
| `Phi_k`, with `dP` | 0.73780 | **0.73677** |
| `P_P,L` | 5.6047 bar | **5.6602 bar** |
| `I_f` | 0.42709 | **0.43673** |

The isobaric column does not move, because with `K = 0` the closure never
enters the pressure relations. One consumer is NOT fixed by editing:
`sep2.py` indexes stored runs by the key `('E','modes')`, so its pickles have
to be regenerated before it reports anything.

Measured over the smoke-test cases, the two differ by 0.01 % in `I_f` without
pressure drop and by 5.2 % at a 15 bar bore drop, and the reflection on the
stage cut is at most 1.3 percentage points. Accuracy does not separate them —
which is why the published selection rests on coherence and says so.

Families **E** and **Q** are **one family, not two**: expanding the layer shape
for small `k` gives `a_Q = a k / 2 = (s_0 - s_1)/2` identically, so `Q` is `E` at
infinite layer thickness — and it is the correct evaluation in exactly the region
where the series parameterisation degrades, since `B = a/(1 - E)` behaves as
`a/k`. The switch at `K_SWITCH = 1` is a limit, not a fallback.

## Four numerical guards, each load-bearing

Documented in `Curvature_Family_LMPD.py`, because omitting any of them produces
a silent wrong answer rather than an error.

1. **The scaled `erfcx` form is mandatory.** The direct expression carries
   `exp(u^2)` and overflows whenever `(a_Q - c)^2 / 4 a_Q` is large.
2. **`a_Q = 0` is a removable singularity** whose limit is `Phi = 1` — the
   classical case, which will certainly be evaluated. The scaled form traverses
   it at machine precision.
3. **The branch `a_Q < 0` is roughly half the domain**, the sign of `a_Q` being
   the physical sign of the correction. It is continued through the complex
   plane via the Faddeeva function, `erfcx(z) = w(i z)`.
4. **Every `(1 - exp(-d))/d` uses `expm1`**, because `c` tends to zero whenever a
   species' driving force is nearly constant, which is the whole isobaric regime.

## The one thing that must not be simplified

In the sealed-end L'Hopital system, the right-hand side is

    R_j = (dP_R/dzeta) x_R,j + P_R (dx_R,j/dzeta)

and the first term looks negligible, since the shell-side loss is a fraction of
a bar. It is not. Validated against high-order numerical differentiation of a
reference profile, dropping it costs 0.37 % at 0.9 m, 0.74 % at 1.3 m and 1.19 %
at 1.7 m in the terminal slope, growing with the shell drop. With it retained
the slope is exact to three parts in 10^5.

## Acceptance test

`python3 help/Simulator_Examples/test_lmpd.py` — 25 checks, all passing. Every
target was produced by an independent implementation before this library
existed, so the test is a regression against a known-good state and not against
itself.

- geometry: 222 727 fibers and 200.12 m² from the void fraction;
- worked module, isobaric: stage cut 0.17066, `x_R,CO2` 0.02215, `Phi_k` 1.0225;
- worked module, with pressure drop: stage cut 0.137606, `x_R,CO2` 0.04972,
  `Phi_k` 0.73780, `P_P,L` 5.60468 bar, `I_f` 0.42709;
- classical limit: `family='none'` with the linear closure gives `I_f = 1/2`
  exactly, unit `Phi`, and drops to `n_c + 1` unknowns;
- closed forms against adaptive quadrature over the full parameter range, and
  the removable singularity at zero curvature;
- **the degenerate-layer screen**: slopes that admit no finite layer must fall
  through to Family Q and must NOT be pushed into the series branch, which would
  rescale the amplitude a second time and return `Phi = 1` — a silent failure
  that reports the uncorrected model as if it were corrected. This regression
  exists because that bug was live, and was caught by a smoke test rather than
  by the checks above, since the worked module takes the genuine E branch;
- **the default closure is Eq. (9)**, with the difference against the `Phi = 1`
  weighting pinned, so a silent swap of the default cannot pass unnoticed.

Case A is run with `modes_phi1`, because that is the weighting its published
targets were produced with. Everything else runs on the default.

Agreement with the reference values is within 0.007 % on every quantity, and the
converged residual is 2 × 10⁻¹⁴.

## Validation status

Against the reference `HFM-Simulator` over a 576-design factorial grid, and
against published module data (Chu et al. 2019; the module of Scholz et al.
2012), the results are in `HFM/LMPD/` — `analise_cf.py`, `analise_dominio.py`
and `validacao_literatura.py`. Two statements from there matter to a user of
this library:

- **inside the Hagen–Poiseuille validity domain** — `Re < 2100`, `Ma <= 0.1`,
  `Kn < 1e-3` on both sides — the corrected model stays below 2 % in stage-cut
  error on **every** design of that grid, worst case 1.05 %;
- **338 of those 576 designs are outside that domain**, with bore Mach up to
  0.93. Error statistics quoted over an unfiltered grid are dominated by designs
  where the reference model itself does not hold. Check the domain before
  quoting a number.
