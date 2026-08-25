#region Title: CurvatureFamilyLMPD
# Nature: Closed forms for the LMPD correction factor
# Methodology: Two-parameter curvature family anchored on the terminal slopes of
#              eta; Family E integrates to an elementary series and Family Q, its
#              thick-layer limit, to an error function. No numerical quadrature.
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#  0.0       11-Aug-2026    J.V.A. Tupinamba               First version, ported into library layout
##################################################################################################################
#endregion

import math
from typing import Tuple

import numpy as np
from scipy.optimize import brentq
from scipy.special import erfc, erfcx, wofz

# EN: Below this layer parameter the series parameterisation is ill-conditioned
#     and Family Q is the correct evaluation. This is a LIMIT, not a fallback.
# PT-BR: Abaixo deste parametro de camada a serie fica mal condicionada e a
#        familia Q e a avaliacao correta. E um LIMITE, nao um plano B.
K_SWITCH: float = 1.0

# EN: Physical clip on the correction factor. Values outside cannot occur for a
#     converged state and indicate a diverging Newton step.
# PT-BR: Limite fisico do fator de correcao.
PHI_MIN, PHI_MAX = 0.2, 3.0


def expm1_ratio(d: float) -> float:
    """
    EN: (1 - exp(-d))/d evaluated with expm1. Load-bearing: c tends to zero
        whenever a species' driving force is nearly constant, and the naive form
        returns 0/0 = nan for the whole isobaric regime.
    PT-BR: (1 - exp(-d))/d com expm1. Sem isto o regime isobarico devolve nan.
    """
    if abs(d) > 1e-8:
        # EN: math.expm1 RAISES OverflowError past d = -709 rather than
        #     returning inf. An exception escaping from here would abort the
        #     residual evaluation instead of merely making it large, so the
        #     numpy form is used, which saturates.
        # PT-BR: math.expm1 LEVANTA OverflowError abaixo de d = -709 em vez de
        #        devolver inf; a forma numpy satura e nao interrompe o residuo.
        if d > -700.0:
            return -math.expm1(-d) / d
        with np.errstate(over="ignore"):
            return float(-np.expm1(-d) / d)
    return 1.0 - d / 2.0 + d * d / 6.0


def log_expm1_ratio(d: float) -> float:
    """
    EN: ln of expm1_ratio, without forming it. The ratio is positive for every
        real d, but it grows as exp(|d|)/|d| for d < 0 and overflows near
        d = -709, which is precisely where the log-domain evaluation of Family Q
        needs it. Written so that the exponential never appears.
    PT-BR: ln de expm1_ratio sem formar a razao, que estoura para d < -709.
    """
    if abs(d) < 1e-8:
        return math.log1p(-d / 2.0 + d * d / 6.0)
    a = abs(d)
    return (a if d < 0.0 else 0.0) + math.log(-math.expm1(-a)) - math.log(a)


def log_erfcx(z: float) -> float:
    """
    EN: ln erfcx(z) for real z, valid where erfcx itself overflows. For
        z < -25 the asymptote erfc(-z) -> 2 makes ln erfcx(z) = z^2 + ln 2 to
        better than machine precision, and the correction term is retained
        rather than assumed.
    PT-BR: ln erfcx(z) real, valido onde o proprio erfcx estoura.
    """
    if z > -25.0:
        v = float(erfcx(z))
        return math.log(v) if v > 0.0 else -math.inf
    return z * z + math.log(2.0 - float(erfc(-z)))


def _phi_family_Q_log(a_Q: float, c: float) -> float:
    """
    EN: Family Q on the real branch (a_Q > 0), evaluated so that neither term of
        the bracket can overflow and neither can cancel against the other.
        Mathematically identical to phi_family_Q, and used only where the direct
        form cannot be trusted, so that no working value moves.

        Write the bracket with

            u = (a - c) / 2 sqrt(a),      v = (a + c) / 2 sqrt(a),
            bracket = erfcx(-u) - exp(-c) erfcx(v),

        and note the identity  u^2 - v^2 = -c,  which holds exactly.

        TWO SEPARATE FAILURES LIVE HERE, and they need opposite treatments.

        (i) v >= 0. Then erfcx(-u) ~ 2 exp(u^2) is the whole answer and the
            second term is exponentially smaller. Nothing cancels; the only
            problem is that exp(u^2) leaves double range past u ~ 26. Taking
            logarithms is enough, and Phi really is enormous there.

        (ii) v < 0, that is c < -a. Now BOTH terms are ~ 2 exp(u^2), because
            -c + v^2 = u^2 identically, and they cancel to every digit a double
            carries. Logarithms alone do NOT rescue this: the difference of two
            equal logarithms is zero and the answer is lost either way. The
            cancellation must be removed in closed form, using

                erfcx(-x) = 2 exp(x^2) - erfcx(x),

            applied to both terms. The two 2 exp(u^2) then cancel ANALYTICALLY,
            by the identity above, leaving

                bracket = exp(-c) erfcx(-v) - erfcx(u),   u > 0,  -v > 0,

            in which both erfcx arguments are positive, so both factors are of
            order 1/x and nothing overflows or cancels. This is not a numerical
            trick; it is the same expression with the divergent part removed on
            paper. Without it the direct form returns 0.0 for (a, c) = (100,
            -300), where the true value is 1.4926, and -1.2e18 for (1.34,
            -20.76), where it is 1.0616 -- wrong, finite, and silent.

    PT-BR: Familia Q no ramo real, escrita de modo que nenhum termo do colchete
           estoure nem se cancele contra o outro. Ha DUAS falhas distintas, com
           tratamentos opostos: para v >= 0 basta o logaritmo, pois Phi e mesmo
           enorme; para v < 0 os dois termos sao iguais na ordem dominante e o
           logaritmo NAO salva -- e preciso remover o cancelamento no papel, por
           erfcx(-x) = 2exp(x^2) - erfcx(x), o que faz os dois 2exp(u^2) se
           anularem pela identidade u^2 - v^2 = -c. Sem isso a forma direta
           devolve 0.0 onde o valor e 1.4926: errado, finito e silencioso.
    """
    sa = math.sqrt(a_Q)
    u = (a_Q - c) / (2.0 * sa)
    v = (a_Q + c) / (2.0 * sa)
    if v >= 0.0:
        L1, L2 = log_erfcx(-u), -c + log_erfcx(v)
    else:
        L1, L2 = -c + log_erfcx(-v), log_erfcx(u)
    d = L1 - L2
    if d == 0.0:
        return 0.0
    if d > 0.0:
        sign, ln_br = 1.0, L1 + math.log(-math.expm1(-d))
    else:
        sign, ln_br = -1.0, L2 + math.log(-math.expm1(d))
    ln_phi = (math.log(0.5) + 0.5 * math.log(math.pi / a_Q)
              + ln_br - log_expm1_ratio(c))
    if ln_phi > 700.0:
        return sign * math.inf
    return sign * math.exp(ln_phi)


def phi_family_Q(a_Q: float, c: float) -> float:
    """
    EN: Family Q -- eta = a_Q * zeta * (1 - zeta). The integral is an error
        function. Four numerical guards are load-bearing:

          * the SCALED form with erfcx, because the direct expression carries
            exp(u^2) and overflows whenever (a_Q - c)^2 / 4 a_Q is large;
          * the limit a_Q -> 0, a removable singularity whose value is Phi = 1 --
            the classical case, which will certainly be evaluated;
          * the branch a_Q < 0, roughly half the domain, taken by continuing the
            square root into the complex plane and retaining the real part;
          * the CEILING of the scaled form itself: erfcx grows as 2 exp(u^2), so
            past u^2 ~ 708 the intermediates leave double range even though Phi
            usually does not. There the value is recovered in the log domain
            rather than reported as nan (see below).

    PT-BR: Familia Q, eta quadratico. A integral e uma funcao erro. Quatro
           guardas sao estruturais: a forma escalada por erfcx, o limite
           removivel em a_Q = 0, o ramo a_Q < 0 por continuacao analitica e o
           teto da propria forma escalada, tratado em dominio logaritmico.
    """
    if abs(a_Q) < 1e-10:
        return 1.0
    if not (math.isfinite(a_Q) and math.isfinite(c)):
        return float("nan")
    sa = np.sqrt(complex(a_Q))
    u = (a_Q - c) / (2.0 * sa)

    def _erfcx_c(z):
        """
        EN: erfcx on the complex plane. The real fast path uses scipy's erfcx;
            off the real axis the identity erfcx(z) = w(i z) with the Faddeeva
            function is used. Writing exp(z^2)(1 - erf(z)) instead would be
            wrong twice over: scipy's erf is real-only and returns nan for a
            complex argument, and exp(z^2) overflows exactly where the scaled
            form exists to avoid it.
        PT-BR: erfcx no plano complexo, pela identidade com a funcao de Faddeeva.
        """
        z = complex(z)
        if abs(z.imag) < 1e-14 and z.real > -25.0:
            return complex(erfcx(z.real))
        return complex(wofz(1j * z))

    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        # EN: np.exp and not math.exp: math.exp RAISES OverflowError for
        #     c < -709 instead of returning inf, and an exception here would
        #     escape into the caller's fallback and re-enter this function.
        # PT-BR: np.exp e nao math.exp -- math.exp levanta OverflowError.
        bracket = _erfcx_c(-u) - float(np.exp(-c)) * _erfcx_c(sa - u)
        val = (0.5 * np.sqrt(np.pi / complex(a_Q)) * bracket) / expm1_ratio(c)
    out = float(val.real)
    if not _phi_Q_needs_log(a_Q, c, out):
        return out

    # EN: FOURTH GUARD -- the scaled form has a ceiling and a blind spot of its
    #     own. erfcx(-u) grows as 2 exp(u^2), so beyond u^2 ~ 708 not even the
    #     scaled form is representable; and for a_Q + c < 0 the two terms of the
    #     bracket are equal to leading order and every digit of the difference
    #     is lost. Neither case means the answer is unknown -- it means the
    #     INTERMEDIATES cannot be written down, while Phi itself usually can.
    #     The first case returned nan, which poisoned the Newton on a three-bar
    #     module: one nan residual and every later iterate was nan. The second
    #     is worse, because it returns a plausible finite number.
    #
    #     On the real branch _phi_family_Q_log answers both. The complex branch
    #     is bounded except through exp(-c), which is left DECLARED rather than
    #     guessed: its sign has not been established here, and c < -709 requires
    #     a driving-force ratio of e^709 between the two ends, which no state of
    #     this model can reach.
    # PT-BR: QUARTA GUARDA. A forma escalada tem teto (erfcx(-u) ~ 2exp(u^2)
    #        estoura para u^2 > 708) e ponto cego (para a_Q + c < 0 os dois
    #        termos do colchete sao iguais na ordem dominante e a diferenca
    #        perde todos os digitos). Nenhum dos dois significa resposta
    #        desconhecida: sao os INTERMEDIARIOS que nao cabem no double. O
    #        primeiro devolvia nan e envenenou o Newton; o segundo e pior, pois
    #        devolve numero plausivel. No ramo real a forma logaritmica resolve
    #        os dois; o ramo complexo fica DECLARADO, nao adivinhado.
    if a_Q > 0.0:
        return _phi_family_Q_log(a_Q, c)
    return out


def _phi_Q_needs_log(a_Q: float, c: float, direct: float) -> bool:
    """
    EN: Whether the direct evaluation of Family Q may be trusted. Two conditions
        disqualify it, and only these two, so that every value the direct form
        gets right keeps the bits it has today:

          * a non-finite result -- the intermediates left double range;
          * a_Q + c < 0 on the real branch -- the two terms of the bracket are
            equal to leading order and the difference has no significant digits
            left, whether or not the result happens to look finite. This is the
            silent case: it returns a plausible number.
    PT-BR: Diz se a forma direta pode ser usada. So duas condicoes a
           desqualificam -- resultado nao finito, e a_Q + c < 0 no ramo real,
           onde o colchete perde todos os digitos e devolve numero plausivel.
    """
    return (not math.isfinite(direct)) or (a_Q > 0.0 and a_Q + c < 0.0)


def phi_family_E(a: float, c: float, k: float, E: float,
                 n_max: int = 400, tol: float = 1e-16) -> float:
    """
    EN: Family E -- eta = a [g_k(zeta) - zeta] with g_k the exponential boundary
        layer of thickness 1/k. Expanding the inner exponential and integrating
        term by term gives an elementary, sign-agnostic series, with the
        prefactor folded into t_0 so that no cancellation occurs when a < 0:

            exp(B) * int_0^1 exp(-b z - B exp(-k z)) dz
                = sum_n t_n [1 - exp(-(b + n k))] / (b + n k)

        with b = c + a, B = a/(1 - E), t_0 = exp(B), t_n = t_{n-1} (-B)/n.
        Below K_SWITCH the parameterisation degrades because B ~ a/k diverges,
        and Family Q with a_Q = a k / 2 is used instead.

    PT-BR: Familia E. Serie elementar, valida para curvatura de qualquer sinal.
           Abaixo de K_SWITCH usa-se a familia Q, que e o limite dela.
    """
    if abs(c) < 1e-12:
        c = 1e-12
    if k < K_SWITCH:
        return phi_family_Q(a * k / 2.0, c)
    B = a / (1.0 - E)
    b = c + a
    t = math.exp(B)
    s = 0.0
    for n in range(n_max):
        if n:
            t *= -B / n
        s += t * expm1_ratio(b + n * k)
        if n > 5 and abs(t) < tol * abs(s):
            break
    v = s / expm1_ratio(c)
    return v if np.isfinite(v) else float("nan")


def has_finite_layer(s0: float, s1: float) -> bool:
    """
    EN: Whether the two terminal slopes admit a finite layer thickness at all.
        They do not when s1 is near zero or when the ratio sits on the wrong
        side of -1, and in that case the thick-layer member of the family -- the
        error function, evaluated at a_Q = (s0 - s1)/2 -- IS the answer.

        This screen must be applied BY THE CALLER, before fit_layer. Feeding the
        degenerate pair (a_Q, k -> 0) into the series branch is silently wrong:
        that branch would rescale the amplitude a second time, as a_Q k / 2,
        collapsing the curvature to zero and returning Phi = 1. The failure is
        invisible -- the model reports a converged solution that is simply the
        uncorrected one.
    PT-BR: Diz se as duas inclinacoes admitem espessura de camada finita. A
           triagem e do CHAMADOR: passar o par degenerado para o ramo da serie
           reescala a amplitude de novo e devolve Phi = 1 em silencio.
    """
    return not (abs(s1) < 1e-12 or s0 / s1 > -1.0001)


def fit_layer(s0: float, s1: float) -> Tuple[float, float]:
    """
    EN: Anchor the family on BOTH terminal slopes. Eliminating the amplitude from
        eta'(0) and eta'(1) leaves one monotone scalar equation for k; a then
        follows in closed form. Call only when has_finite_layer is true.
    PT-BR: Ancora a familia nas DUAS inclinacoes terminais. Chamar so quando
           has_finite_layer for verdadeiro.
    """
    if abs(s1) < 1e-12 or s0 / s1 > -1.0001:
        return 0.5 * (s0 - s1), 1e-9
    try:
        k = brentq(lambda kk: (kk - 1.0 + math.exp(-kk))
                   / (kk * math.exp(-kk) - 1.0 + math.exp(-kk)) - s0 / s1,
                   1e-6, 80.0)
        return s0 / (k / (1.0 - math.exp(-k)) - 1.0), k
    except Exception:
        return 0.5 * (s0 - s1), 1e-9


def correction_factor(c: np.ndarray, s0: np.ndarray, s1: np.ndarray,
                      family: str = "E") -> np.ndarray:
    """
    EN: Phi_i for every species from the four terminal numbers per species.
        family = 'none' returns unity, which is the classical LMPD model.
    PT-BR: Phi_i de cada especie a partir dos quatro numeros terminais.
    """
    nc = len(c)
    if family == "none":
        return np.ones(nc)
    # EN: nan in, nan out -- said explicitly, rather than reached by taking the
    #     square root of a nan and emitting a RuntimeWarning that reads to the
    #     user like a failure of the model. A non-finite iterate is the solver's
    #     business; this function has nothing to say about it and should say so
    #     in one line instead of three warnings from three different lines.
    # PT-BR: nan entra, nan sai -- dito de forma explicita, e nao alcancado por
    #        sqrt de nan com RuntimeWarning que parece falha do modelo.
    if not (np.all(np.isfinite(c)) and np.all(np.isfinite(s0))
            and np.all(np.isfinite(s1))):
        return np.full(nc, np.nan)
    Phi = np.ones(nc)
    for i in range(nc):
        a_Q = 0.5 * (s0[i] - s1[i])
        # EN: The thick-layer member is used both when it is asked for and when
        #     the slopes admit no finite layer. See has_finite_layer.
        # PT-BR: O membro de camada espessa vale tambem quando nao ha camada.
        if family == "Q" or not has_finite_layer(s0[i], s1[i]):
            Phi[i] = phi_family_Q(a_Q, c[i]) if abs(a_Q) > 1e-9 else 1.0
            continue
        try:
            a, k = fit_layer(s0[i], s1[i])
            v = phi_family_E(a, c[i], k, math.exp(-k))
            Phi[i] = v if np.isfinite(v) else phi_family_Q(a_Q, c[i])
        except Exception:
            Phi[i] = phi_family_Q(a_Q, c[i]) if abs(a_Q) > 1e-9 else 1.0
    return np.clip(Phi, PHI_MIN, PHI_MAX)
