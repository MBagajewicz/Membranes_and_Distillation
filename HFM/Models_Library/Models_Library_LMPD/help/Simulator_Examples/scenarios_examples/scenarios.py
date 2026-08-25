"""
CENARIOS PARA A COMPARACAO DOS CINCO MODELOS.

Mesmo padrao do scenarios.py do HFM_Library: um dicionario SCENARIOS cujas
chaves sao o nome do cenario e cujos valores sao dicionarios de parametros.
As chaves de parametro seguem as do HFM_Library sempre que existe equivalente,
para que um cenario possa ser passado aos dois simuladores sem traducao.

TRES FAMILIAS DE CENARIO
========================
1. ESTUDO      -- a grade do artigo. CO2/CH4/N2, poliimida ou acetato, 40 bar.
2. LITERATURA  -- modulos publicados por terceiros, com os valores reportados
                  guardados em 'Published'. Servem de validacao externa: o
                  modulo nao foi escolhido por nos.
3. DIAGNOSTICO -- casos construidos para exercitar um regime especifico.

SOBRE 'Published'
=================
Quando presente, e uma tupla nomeada de valores REPORTADOS NO ARTIGO ORIGINAL,
nao calculados aqui. Servem para conferir que a nossa referencia discretizada
reproduz o modulo antes de qualquer conclusao sobre os modelos algebricos.
Onde o artigo nao reporta a grandeza, o campo vem como None -- nunca inventado.

ATENCAO A UMA ASSIMETRIA REAL
=============================
Os cenarios de literatura sao BINARIOS (CO2/CH4 ou CO2/C3H8). Os do estudo sao
TERNARIOS. A correcao e definida por especie e nao depende do numero de
componentes, mas as tabelas de erro nao sao comparaveis entre um caso binario e
um ternario: no ternario o erro relativo se concentra no componente minoritario
do retentado, e isso e propriedade da metrica, nao do modelo.
"""
import numpy as np

# --------------------------------------------------------------------------
# Propriedades puras usadas pelos cenarios. Viscosidades proximas de 30 C [Pa s],
# massas molares [kg/mol].
# --------------------------------------------------------------------------
_MU = {"CO2": 1.5154e-5, "CH4": 1.1354e-5, "N2": 1.8035e-5,
       "C2H6": 9.30e-6, "C3H8": 8.10e-6, "He": 1.99e-5, "O2": 2.06e-5}
_MW = {"CO2": 44.01e-3, "CH4": 16.04e-3, "N2": 28.02e-3,
       "C2H6": 30.07e-3, "C3H8": 44.10e-3, "He": 4.003e-3, "O2": 32.00e-3}


def _props(comps):
    return (np.array([_MU[c] for c in comps]), np.array([_MW[c] for c in comps]))


def _cenario(**kw):
    """Preenche MU e M a partir de Components, e defaults comuns."""
    mu, mw = _props(kw["Components"])
    kw.setdefault("MU", mu)
    kw.setdefault("M", mw)
    kw.setdefault("PressureDrop", True)
    kw.setdefault("EnergyBalance", False)
    kw.setdefault("UseFugacity", False)
    kw.setdefault("Void_Frac", None)
    kw.setdefault("N", None)
    kw.setdefault("Published", None)
    kw.setdefault("Family", "estudo")
    return kw


SCENARIOS = {

    # ======================================================================
    # 1. ESTUDO -- a grade do artigo
    # ======================================================================

    "S0_PI": _cenario(
        Description="Caso base do artigo. Poliimida, CO2/CH4/N2 a 40 bar. "
                    "E o modulo trabalhado ao longo de todo o texto.",
        Family="estudo",
        Components=["CO2", "CH4", "N2"],
        ZFeed=np.array([0.10, 0.89, 0.01]),
        Q=np.array([3.282e-8, 1.641e-9, 3.282e-9]),
        T=303.15, PFeed=40e5, PPerm=1e5, FFeed=13.889,
        DiamShell=0.14, DiamFiber_o=220e-6, DiamFiber_i=80e-6,
        FiberLengthInElement=1.3, Void_Frac=0.45,
    ),

    "S0_CA": _cenario(
        Description="Mesmo modulo, membrana de acetato de celulose: seletividade "
                    "menor e permeancia menor. Curvatura mais suave.",
        Family="estudo",
        Components=["CO2", "CH4", "N2"],
        ZFeed=np.array([0.10, 0.89, 0.01]),
        Q=np.array([1.6905e-8, 1.127e-9, 1.127e-9]),
        T=303.15, PFeed=40e5, PPerm=1e5, FFeed=13.889,
        DiamShell=0.14, DiamFiber_o=220e-6, DiamFiber_i=80e-6,
        FiberLengthInElement=1.3, Void_Frac=0.45,
    ),

    "rico_PI": _cenario(
        Description="Alimentacao rica em CO2 (30 %). Corte alto, curvatura "
                    "composicional grande -- o regime em que a correcao mais "
                    "muda o resultado no caso isobarico.",
        Family="estudo",
        Components=["CO2", "CH4", "N2"],
        ZFeed=np.array([0.30, 0.69, 0.01]),
        Q=np.array([3.282e-8, 1.641e-9, 3.282e-9]),
        T=303.15, PFeed=40e5, PPerm=1e5, FFeed=13.889,
        DiamShell=0.14, DiamFiber_o=220e-6, DiamFiber_i=80e-6,
        FiberLengthInElement=1.3, Void_Frac=0.45,
    ),

    "Pp5_PI": _cenario(
        Description="Permeado a 5 bar em vez de 1. Razao de pressoes menor, "
                    "pressurizacao do bore menos severa.",
        Family="estudo",
        Components=["CO2", "CH4", "N2"],
        ZFeed=np.array([0.10, 0.89, 0.01]),
        Q=np.array([3.282e-8, 1.641e-9, 3.282e-9]),
        T=303.15, PFeed=40e5, PPerm=5e5, FFeed=13.889,
        DiamShell=0.14, DiamFiber_o=220e-6, DiamFiber_i=80e-6,
        FiberLengthInElement=1.3, Void_Frac=0.45,
    ),

    # ======================================================================
    # 2. LITERATURA -- modulos publicados por terceiros
    # ======================================================================

    "CHU_2": _cenario(
        Description="Chu, Lindbrathen, Lei, He e Hillestad (2019), cenario 2. "
                    "Poliimida, CO2/CH4 a 35 bar. Chem. Eng. Res. Des. 148, 45-55.",
        Family="literatura", Reference="Chu et al. (2019) [5]",
        Components=["CO2", "CH4"],
        ZFeed=np.array([0.10, 0.90]),
        Q=np.array([3.207e-9, 1.33e-10]),
        T=308.0, PFeed=35e5, PPerm=1e5, FFeed=0.35,
        DiamShell=0.10, DiamFiber_o=250e-6, DiamFiber_i=200e-6,
        FiberLengthInElement=0.6, N=60000,
        # Reportado pelo ChemBrane dos autores: (F_perm [mol/s], y_CO2 [%],
        # F_ret [mol/s], x_CH4 [%])
        Published=dict(fonte="ChemBrane (Chu et al.)",
                       FPerm=0.03, yCO2_pct=59.88, FRet=0.32, xCH4_pct=94.94),
    ),

    "CHU_3": _cenario(
        Description="Chu et al. (2019), cenario 3. Poliimida, 15 bar, fibra fina "
                    "e modulo longo -- queda no bore mais pronunciada.",
        Family="literatura", Reference="Chu et al. (2019) [5]",
        Components=["CO2", "CH4"],
        ZFeed=np.array([0.10, 0.90]),
        Q=np.array([3.207e-9, 1.33e-10]),
        T=308.0, PFeed=15e5, PPerm=1e5, FFeed=0.35,
        DiamShell=0.05, DiamFiber_o=170e-6, DiamFiber_i=120e-6,
        FiberLengthInElement=1.5, N=60000,
        Published=dict(fonte="ChemBrane (Chu et al.)",
                       FPerm=0.0205, yCO2_pct=56.72, FRet=0.3294, xCH4_pct=92.92),
    ),

    "CHU_4": _cenario(
        Description="Chu et al. (2019), cenario 4. Membrana de carbono, 5 bar, "
                    "escala piloto. Os valores publicados sao EXPERIMENTAIS.",
        Family="literatura", Reference="Chu et al. (2019) [5]",
        Components=["CO2", "CH4"],
        ZFeed=np.array([0.10, 0.90]),
        Q=np.array([1.749e-9, 1.227e-10]),
        T=298.0, PFeed=5e5, PPerm=1e5, FFeed=3.718e-4,
        DiamShell=0.024, DiamFiber_o=180e-6, DiamFiber_i=126e-6,
        FiberLengthInElement=0.8, N=2805,
        Published=dict(fonte="experimental (Chu et al.)",
                       FPerm=4.313e-5, yCO2_pct=25.96, FRet=3.287e-4,
                       xCH4_pct=92.09),
    ),

    "SCHOLZ_1": _cenario(
        Description="Scholz, Harlacher, Melin e Wessling (2013), ponto 1 da Fig. 6. "
                    "CO2/C3H8 a 3 bar em modulo comercial de poliimida. "
                    "Ind. Eng. Chem. Res. 52, 1079-1088. Corte baixo.",
        Family="literatura", Reference="Scholz et al. (2013) [29]",
        Components=["CO2", "C3H8"],
        ZFeed=np.array([0.50, 0.50]),
        Q=np.array([6.8e-8, 7.71e-11]),
        T=323.0, PFeed=3e5, PPerm=1e5, FFeed=0.00333333,
        DiamShell=0.0394, DiamFiber_o=4.15e-4, DiamFiber_i=3.41e-4,
        FiberLengthInElement=0.2, N=3380,
    ),

    "SCHOLZ_2": _cenario(
        Description="Scholz et al. (2013), ponto 2 da Fig. 6. Mesmo modulo, "
                    "vazao maior.",
        Family="literatura", Reference="Scholz et al. (2013) [29]",
        Components=["CO2", "C3H8"],
        ZFeed=np.array([0.50, 0.50]),
        Q=np.array([6.8e-8, 7.71e-11]),
        T=323.0, PFeed=3e5, PPerm=1e5, FFeed=0.0077777,
        DiamShell=0.0394, DiamFiber_o=4.15e-4, DiamFiber_i=3.41e-4,
        FiberLengthInElement=0.2, N=3380,
    ),

    "SCHOLZ_3": _cenario(
        Description="Scholz et al. (2013), ponto 3 da Fig. 6.",
        Family="literatura", Reference="Scholz et al. (2013) [29]",
        Components=["CO2", "C3H8"],
        ZFeed=np.array([0.50, 0.50]),
        Q=np.array([6.8e-8, 7.71e-11]),
        T=323.0, PFeed=3e5, PPerm=1e5, FFeed=0.014444444,
        DiamShell=0.0394, DiamFiber_o=4.15e-4, DiamFiber_i=3.41e-4,
        FiberLengthInElement=0.2, N=3380,
    ),

    "SCHOLZ_4": _cenario(
        Description="Scholz et al. (2013), ponto 4 da Fig. 6. Vazao mais alta, "
                    "corte mais baixo da serie.",
        Family="literatura", Reference="Scholz et al. (2013) [29]",
        Components=["CO2", "C3H8"],
        ZFeed=np.array([0.50, 0.50]),
        Q=np.array([6.8e-8, 7.71e-11]),
        T=323.0, PFeed=3e5, PPerm=1e5, FFeed=0.02166666,
        DiamShell=0.0394, DiamFiber_o=4.15e-4, DiamFiber_i=3.41e-4,
        FiberLengthInElement=0.2, N=3380,
    ),

    # ----------------------------------------------------------------------
    # GIGLIA et al. (1991) -- o modulo contra o qual um LMPD PUBLICADO foi
    # validado. Ind. Eng. Chem. Res. 30, 1239-1248.
    #
    # POR QUE ESTE MODULO IMPORTA MAIS QUE OS OUTROS DA LITERATURA
    # ============================================================
    # Pettersen & Lien (1994) -- o artigo que propoe o proprio modelo LMPD que
    # este trabalho corrige -- validam o modelo deles contra ESTE modulo, nas
    # Figs. 11-14, e reportam desvio de ate 5 % na pureza do permeado e ate
    # 10 % no corte. Rodar o mesmo modulo aqui poe as tres coisas lado a lado:
    # o experimento de Giglia, o LMPD classico (que E o modelo de Pettersen &
    # Lien) e o LMPD corrigido. E a unica comparacao disponivel em que o alvo
    # nao e um discretizado nosso, e sim um LMPD de terceiros ja publicado.
    #
    # DE ONDE VEM CADA NUMERO
    # =======================
    # Diretos do texto de Giglia:
    #   D_i = 145 um, D_o = 373 um, N = 80 fibras, P_alim = 691 kPa,
    #   T = 298 K, alfa(He/N2) = 45, alfa(O2/N2) = 5,7,
    #   permeancia de N2 = 3,75e-6 cm3(STP)/(cm2 cmHg s),
    #   alimentacoes de 30,02 % He e 20,78 % O2,
    #   carcaca de aco com diametro INTERNO de 4,8 mm.
    # Da Tabela 2 de Pettersen & Lien, que tabula o mesmo modulo:
    #   area ativa = 1406,2 cm2.
    #
    # DUAS CONFERENCIAS DE CONSISTENCIA, porque nenhum dos dois artigos lista
    # o comprimento e a fracao de vazio explicitamente:
    #   (i)  pi * D_o * L * N = 1406,2 cm2  =>  L = 1,500 m, exatamente.
    #   (ii) 80 fibras de 373 um num tubo de 4,8 mm ocupam 48,3 % da secao,
    #        e Giglia escreve que as fibras ocupam "cerca de 50 % do volume".
    # Os dois fecham. O comprimento e o diametro do casco sao portanto
    # DEDUZIDOS e conferidos, nao arbitrados.
    #
    # TRES RESSALVAS, e nenhuma delas e pequena
    # =========================================
    # 1. A VAZAO DE ALIMENTACAO NAO E PUBLICADA como valor unico: Giglia varre
    #    o corte de 5 % a 80 %. A vazao abaixo foi escolhida para cair num
    #    fator de permeacao R = Q_1 A P_f / n_f dentro da faixa dos graficos de
    #    Pettersen & Lien (R ate 6 no He/N2, ate 2 no O2/N2). E escolha nossa,
    #    ancorada no eixo publicado -- por isso 'Published' fica None.
    # 2. O modulo REAL e uma serie de submodulos com trechos embutidos em
    #    resina, que nao permeiam mas contribuem para a queda no bore (Giglia,
    #    Fig. 4, os patamares horizontais). O nosso modelo tem fibra unica e
    #    continua, entao SUBESTIMA a queda no bore.
    # 3. Giglia calcula a viscosidade do permeado pela regra de Wilke e obtem
    #    229 uP no He/N2 -- ACIMA das duas viscosidades puras, que e o que
    #    misturas He-N2 fazem. A nossa biblioteca carrega uma viscosidade
    #    unica por lado, media pelas fracoes molares, e chega a ~184 uP. A
    #    queda no bore do caso He/N2 sai por isso ~20 % baixa. No O2/N2 o
    #    efeito e desprezivel (193 uP contra ~197 uP).
    # ----------------------------------------------------------------------

    "GIGLIA_HE": _cenario(
        Description="Giglia, Bikson, Perrin e Donatelli (1991), modulo de "
                    "laboratorio He/N2 a 6,91 bar. Ind. Eng. Chem. Res. 30, "
                    "1239-1248. E o modulo usado por Pettersen & Lien (1994) "
                    "para validar o LMPD deles (Figs. 11-12). Seletividade 45, "
                    "razao de pressoes 1/6,8 e fibra estreita: a queda no bore "
                    "domina, que e o regime em que a correcao decide.",
        Family="literatura", Reference="Giglia et al. (1991); Pettersen & Lien (1994)",
        Components=["He", "N2"],
        ZFeed=np.array([0.3002, 0.6998]),
        # Q_N2 = 3,75e-6 cm3(STP)/(cm2 cmHg s) = 1,25491e-9 mol/(m2 s Pa);
        # Q_He = 45 * Q_N2.
        Q=np.array([5.64710e-8, 1.25491e-9]),
        T=298.0, PFeed=6.91e5, PPerm=1.013e5,
        # n_f = Q_He * A * P_f / R com R = 3 e A = 0,140617 m2
        FFeed=1.82898e-3,
        DiamShell=4.8e-3, DiamFiber_o=373e-6, DiamFiber_i=145e-6,
        FiberLengthInElement=1.500, N=80,
    ),

    "GIGLIA_O2": _cenario(
        Description="Giglia et al. (1991), mesmo modulo, ar sintetico O2/N2 a "
                    "6,91 bar. Validado por Pettersen & Lien (1994), Figs. "
                    "13-14. Seletividade 5,7 -- oito vezes menor que a do caso "
                    "He no MESMO hardware, que e o par que isola o efeito da "
                    "seletividade sobre a curvatura.",
        Family="literatura", Reference="Giglia et al. (1991); Pettersen & Lien (1994)",
        Components=["O2", "N2"],
        ZFeed=np.array([0.2078, 0.7922]),
        Q=np.array([7.15299e-9, 1.25491e-9]),
        T=298.0, PFeed=6.91e5, PPerm=1.013e5,
        # n_f = Q_O2 * A * P_f / R com R = 1
        FFeed=6.95034e-4,
        DiamShell=4.8e-3, DiamFiber_o=373e-6, DiamFiber_i=145e-6,
        FiberLengthInElement=1.500, N=80,
    ),

    # ======================================================================
    # 3. DIAGNOSTICO -- construidos para exercitar um regime
    # ======================================================================

    "curto": _cenario(
        Description="Modulo curto: corte muito baixo, curvatura quase nula. "
                    "Aqui o classico ja deve ser exato e a correcao deve ser "
                    "inofensiva -- e o teste de que ela nao estraga o caso facil.",
        Family="diagnostico",
        Components=["CO2", "CH4", "N2"],
        ZFeed=np.array([0.10, 0.89, 0.01]),
        Q=np.array([3.282e-8, 1.641e-9, 3.282e-9]),
        T=303.15, PFeed=40e5, PPerm=1e5, FFeed=13.889,
        DiamShell=0.14, DiamFiber_o=220e-6, DiamFiber_i=80e-6,
        FiberLengthInElement=0.3, Void_Frac=0.45,
    ),

    "severo": _cenario(
        Description="Fibra estreita e modulo longo: queda no bore severa. "
                    "CUIDADO -- este cenario pode cair FORA do dominio de "
                    "Hagen-Poiseuille (Ma > 0,1 no bore), e ali nem a referencia "
                    "vale. O comparador avisa quando isso acontece.",
        Family="diagnostico",
        Components=["CO2", "CH4", "N2"],
        ZFeed=np.array([0.10, 0.89, 0.01]),
        Q=np.array([3.282e-8, 1.641e-9, 3.282e-9]),
        T=303.15, PFeed=40e5, PPerm=1e5, FFeed=13.889,
        DiamShell=0.14, DiamFiber_o=220e-6, DiamFiber_i=60e-6,
        FiberLengthInElement=1.9, Void_Frac=0.45,
    ),
}


def listar():
    """Imprime os cenarios disponiveis, agrupados por familia."""
    for fam in ("estudo", "literatura", "diagnostico"):
        nomes = [k for k, v in SCENARIOS.items() if v.get("Family") == fam]
        print(f"\n{fam.upper()}")
        for n in nomes:
            s = SCENARIOS[n]
            pub = "  [tem valores publicados]" if s.get("Published") else ""
            print(f"  {n:<10} {s['Description'].splitlines()[0][:66]}{pub}")


if __name__ == "__main__":
    listar()
