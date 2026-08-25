# LMPD-Simulator — documentação técnica

Simulador algébrico de módulo de fibra oca em contracorrente, alimentação pelo
casco e permeado no bore, com fator de correção em forma fechada para a média
logarítmica da força motriz.

Companheiro do `HFM-Simulator` e **deliberadamente compatível na interface**: os
mesmos objetos `Stream` e `Membrane_Permeance`, a mesma parametrização geométrica.
Um projeto pode ser entregue a qualquer um dos dois sem alteração.

> Para o *porquê* físico — o que a média logarítmica assume e o que isso custa —
> veja `README.md`. Este documento é sobre **como usar e como o código está
> organizado**.

---

## 1. Início rápido

```python
import sys
B = "<raiz do repositorio>/"
sys.path[:0] = [B + "HFM/Models_Library/LMPD_Library/src",
                B + "Classes/Common_Library/src"]

from Simulator_LMPD import SimulatorRunLMPD, SimulatorGeometryLMPD
from Common.Streams.Streams import Stream
from Common.MembraneProperties.Membrane_Permeance import Membrane_Permeance
import numpy as np

COMP = ["CO2", "CH4", "N2"]
MU   = np.array([1.5154e-5, 1.1354e-5, 1.8035e-5])  # viscosidade [Pa s]
MW   = np.array([44.01e-3, 16.04e-3, 28.02e-3])     # massa molar [kg/mol]
Q    = np.array([3.282e-8, 1.641e-9, 3.282e-9])     # permeância [mol/(s m² Pa)]

sim = SimulatorRunLMPD()
sim.set_feed(Stream(flow=13.889, composition=[0.10, 0.89, 0.01],
                    pressure=40e5, temperature=303.15, components=COMP,
                    viscosity=MU, molecularweight=MW))
sim.set_membrane_permeance(Membrane_Permeance(components=COMP, permeance=Q))
sim.geometry = SimulatorGeometryLMPD(LSingleMembrane=1.3, DiamShell=0.14,
                                     DiamFiber_o=220e-6, DiamFiber_i=80e-6,
                                     NFibers=None, Void_Frac=0.45)
sim.PPerm = 1e5
sim.pressure_drop   = True     # queda nos dois lados
sim.curvature_family = "E"     # correção ligada
sim.flow_closure     = "modes" # Eq. (9)

r = sim.run()
print(r.summary())
print(r.stage_cut, r.retentate_fraction("CO2"), r.correction("CO2"))
```

`NFibers=None` faz o número de fibras sair da fração de vazio. Com a geometria
acima: 222 727 fibras e 200,12 m².

---

## 2. As cinco configurações

O artigo compara cinco modelos. Quatro são esta biblioteca com dois interruptores;
o quinto é o `HFM-Simulator`.

| modelo | `curvature_family` | `flow_closure` | `pressure_drop` |
|---|---|---|---|
| LMPD clássico, isobárico | `"none"` | `"linear"` | `False` |
| LMPD clássico, com queda | `"none"` | `"linear"` | `True` |
| LMPD corrigido, isobárico | `"E"` | `"modes"` | `False` |
| LMPD corrigido, com queda | `"E"` | `"modes"` | `True` |
| discretizado (referência) | — usa `HFM-Simulator` — | | |

**`family="none"` com `closure="linear"` é o modelo clássico exato**: Φ = 1,
I_f = 1/2, todos os sistemas possuem n_c + 1 incógnitas.

---

## 3. Referência da API

### `SimulatorRunLMPD`

**Entradas obrigatórias**

| membro | tipo | significado |
|---|---|---|
| `set_feed(stream)` | `Stream` | vazão, composição, pressão, temperatura, viscosidades, massas molares |
| `set_membrane_permeance(mp)` | `Membrane_Permeance` | permeância por espécie [mol/(s m² Pa)] |
| `geometry` | `SimulatorGeometryLMPD` | geometria do módulo |
| `PPerm` | `float` | pressão do permeado na extremidade **aberta** [Pa] |

**Interruptores**

| membro | valores | efeito |
|---|---|---|
| `pressure_drop` | `True` / `False` | `False` anula `K_B` e `K_S`; `P_P,L` sai das incógnitas |
| `curvature_family` | `"E"`, `"Q"`, `"none"` | `E` série elementar; `Q` limite de camada espessa (erf); `none` clássico |
| `flow_closure` | ver `CLOSURES` | `modes` é a Eq. (9), padrão; `linear` é I_f = 1/2 |
| `simultaneous` | `True` / `False` | `False` prevê Φ dentro do resíduo. Mesma solução, mais avaliações |

**Saída:** `run()` devolve `SimulatorResultsLMPD`. Levanta `LMPDNotConverged`
apenas em falha estrutural; falha numérica vem sinalizada nos campos do resultado.

#### Seleção de raiz: uma raiz não é automaticamente uma solução

`run()` parte de quatro pontos iniciais e **não** escolhe simplesmente o de menor
resíduo. Antes de comparar resíduos, cada raiz passa por um teste de fisicalidade,
e uma raiz física vence uma não-física **qualquer que seja o resíduo**.

O motivo é concreto. O sistema de resíduos não sabe que a alimentação é finita:
as incógnitas entram como `|v_i| n_F x_F`, sem limite superior, então uma raiz com
`Σu > n_F` — mais permeado do que alimentado — satisfaz todas as equações
exatamente. E nada a jusante pega: a vazão de retentado fica **negativa**, e as
frações molares, sendo razão de dois números negativos, voltam **positivas e
somando um**. Toda checagem de composição passa sobre um estado impossível.

Pior, essa raiz é alcançável com precisão de máquina. Num módulo muito
superdimensionado (fator de permeação 17,7) uma partida converge a resíduo
6 × 10⁻¹⁵ com corte 1,27, enquanto a partida que permanece física para em 1,0.
Escolher pelo resíduo elegia a resposta impossível **sobre** a possível, e a
reportava com a maior confiança que o código sabe expressar.

Dois sinais são testados:

- **corte fora de (0, 1)** — a violação em si;
- **Φ repousando sobre o clipe** `[0.2, 3.0]`. O clipe é documentado como limite
  que estado convergido não alcança, e o resíduo achatado que ele cria é parte do
  que permite ao Newton estacionar ali. Φ no clipe é sintoma, não resultado.

Quando nenhuma raiz física é encontrada, `feasible` e `converged` ficam `False` e
`message` **nomeia a violação em vez do resíduo** — que nesse caso é minúsculo e
enganaria quem o lesse.

> Nota honesta sobre o caso que revelou isto: não foi estabelecido que aquele
> módulo tenha solução física. O modelo discretizado de referência também não
> fecha nele. O que a biblioteca passou a garantir é a **recusa**, não uma
> resposta melhor.

### `SimulatorGeometryLMPD`

Passiva — só calcula. `LSingleMembrane`, `DiamShell`, `DiamFiber_o`,
`DiamFiber_i`, `NFibers` (ou `None`), `Void_Frac`. Deriva área total, número de
fibras e os coeficientes `K_B` (bore) e `K_S` (casco).

### `SimulatorResultsLMPD`

| campo | significado |
|---|---|
| `converged`, `feasible`, `message` | **cheque sempre os dois primeiros antes de ler números** |
| `stage_cut` | corte |
| `ZRet`, `ZPerm` | frações molares de retentado e de permeado (mistura) |
| `ZPermSealed` | composição do permeado na ponta selada (Weller–Steiner) |
| `PRetIn/Out`, `PPermOut`, `PPermSealed` | pressões [Pa] |
| `Phi` | fator de correção por espécie |
| `c_chord`, `slope_feed`, `slope_sealed` | os quatro números terminais que alimentam a forma fechada |
| `If` | integral do perfil de vazão do permeado |
| `family`, `closure` | o que foi de fato usado |
| `residual`, `n_unknowns`, `n_evaluations` | convergência e custo |

Auxiliares: `retentate_fraction(comp)`, `permeate_fraction(comp)`,
`correction(comp)`, `retentate_stream(T)`, `permeate_stream(T)`, `summary()`.

---

## 4. Arquitetura

```
src/Simulator_LMPD/
  Simulator_Run_LMPD.py          orquestração e o sistema de Newton
  Simulator_Geometry_LMPD.py     geometria passiva, K_B e K_S
  Simulator_State_LMPD.py        montagem do estado, fecho de Weller–Steiner
  Simulator_Results_LMPD.py      container de resultados
  Correction_Factor_LMPD/
    Terminal_Slopes_LMPD.py      inclinações exatas, L'Hôpital na ponta selada
    Curvature_Family_LMPD.py     famílias E e Q, as quatro guardas
    Flow_Closure_LMPD.py         I_f, derivado e não assumido
```

**Um único Newton, n_c + 1 incógnitas** — as n_c quantidades permeadas `u_i` e a
pressão `P_P,L` na ponta selada. Tudo o mais, inclusive Φ, é recalculado do zero
dentro de cada avaliação de resíduo. **Nenhuma integral é avaliada numericamente
em nenhum ponto do caminho de solução**: sem malha, sem quadratura, sem perfil.
É isso que permite embutir o modelo num MINLP e carregar limitantes.

---

## 5. As cinco guardas numéricas

Documentadas em `Curvature_Family_LMPD.py`. **Omitir qualquer uma produz resposta
errada em silêncio, não erro.**

1. **A forma escalada `erfcx` é obrigatória.** A expressão direta carrega
   `exp(u²)` e transborda.
2. **`a_Q = 0` é singularidade removível** cujo limite é Φ = 1 — o caso clássico,
   que certamente será avaliado.
3. **O ramo `a_Q < 0` é metade do domínio**, continuado pelo plano complexo via
   Faddeeva, `erfcx(z) = w(iz)`.
4. **A própria forma escalada tem teto e ponto cego.** Com
   `u = (a_Q − c)/2√a_Q` e `v = (a_Q + c)/2√a_Q`, valem duas falhas distintas,
   de tratamentos opostos:
   - `u² > 708` — nem `erfcx` cabe no double. Φ é mesmo enorme ali; devolver
     `nan` diz "desconhecido" e envenena o resíduo do Newton.
   - `a_Q + c < 0` (isto é, `v < 0`) — os **dois** termos do colchete valem
     `~2exp(u²)`, porque `u² − v² = −c` é identidade, e se cancelam em todos os
     dígitos. Aqui o logaritmo **não** salva: o cancelamento tem de sair no
     papel, por `erfcx(−x) = 2exp(x²) − erfcx(x)`, que anula os dois `2exp(u²)`
     analiticamente e deixa `exp(−c)·erfcx(−v) − erfcx(u)`, com os dois
     argumentos positivos. Sem isso a forma direta devolve `0.0` em
     `(a_Q, c) = (100, −300)`, onde o valor é `1.4926`: **errado, finito e
     silencioso** — o pior dos três modos de falha.

   `_phi_family_Q_log` resolve os dois casos, e `_phi_Q_needs_log` decide quando
   desviar. O critério é conservador de propósito: desvia sempre que
   `a_Q + c < 0`, mesmo onde a forma direta ainda acertaria, para que a fronteira
   não dependa de estimar quantos dígitos sobraram.
5. **Todo `(1 − exp(−d))/d` usa `expm1`**, porque `c` tende a zero sempre que a
   força motriz de uma espécie é quase constante — o regime isobárico inteiro.
   Abaixo de `d = −700` usa-se a forma do numpy, que satura: `math.expm1`
   **levanta** `OverflowError` em vez de devolver `inf`, e uma exceção ali
   abortaria a avaliação do resíduo em vez de apenas torná-la grande.

E uma sexta, no `log_mean`: o **clipe na condição de pinch é continuação, não
cosmética**. Substituí-lo por zero achata o resíduo localmente e mata o Newton.

### Verificação das formas fechadas

`phi_family_Q` foi conferida contra a **integral em precisão arbitrária**
(`mpmath`, 30 dígitos): 594 pares `(a_Q, c)` sorteados nos dois sinais, com
`|a_Q|` e `|c|` de 10⁻⁶ a 10³, dão erro relativo máximo de **6,2 × 10⁻¹³**,
nenhum acima de 10⁻¹⁰. Quadratura adaptativa sozinha não bastava: ela concorda
com a forma direta justamente onde as duas erram juntas.

---

## 6. Validação

```bash
python3 help/Simulator_Examples/test_lmpd.py             # 25 checagens
python3 help/Simulator_Examples/test_lmpd_properties.py  # 49 checagens
```

Os alvos do primeiro foram produzidos por uma implementação independente **antes
desta biblioteca existir**, então é regressão contra um estado conhecido e não
contra si mesma. Cobre geometria, o módulo trabalhado nos dois regimes, o limite
clássico, as formas fechadas contra quadratura adaptativa, a triagem de camada
degenerada e o fecho padrão.

Contra a grade fatorial de 576 projetos e o modelo discretizado do grupo, os
resultados estão em `HFM/LMPD/` (`analise_biblioteca.py`, `validade.py`). Duas
afirmações importam a quem usa a biblioteca:

- **Dentro do domínio de Hagen–Poiseuille** — `Re < 2100`, `Ma ≤ 0,1`,
  `Kn < 1e-3` nos dois lados — o corrigido fica abaixo de 1,11 % de erro no corte
  em **todos** os 238 projetos válidos.
- **338 dos 576 estão FORA desse domínio**, com Mach no bore até 0,93. Estatística
  sobre grade sem filtro é dominada por projetos onde a própria referência não
  vale. **Cheque o domínio antes de citar um número.**

---

## 7. Comparar os cinco modelos num módulo

Os cenários ficam em `help/Simulator_Examples/scenarios_examples/scenarios.py`,
no mesmo padrão do `scenarios.py` do `HFM_Library`. Três famílias:

| família | o que é |
|---|---|
| `estudo` | a grade do artigo — `S0_PI`, `S0_CA`, `rico_PI`, `Pp5_PI` |
| `literatura` | módulos publicados por terceiros — `CHU_2/3/4`, `SCHOLZ_1..4`, com os valores reportados em `Published` |
| `diagnostico` | construídos para exercitar um regime — `curto`, `severo` |

**Sem terminal.** Abra `HFM/LMPD/comparar_modelos.py` no editor, edite o bloco
de configuração no topo e aperte Run (F5):

```python
CENARIOS = "todos"                  # ou "literatura", ou ["S0_PI", "CHU_2"], ou "S0_PI"
ARQUIVO_XLSX = "comparacao.xlsx"    # None para não gerar Excel
NCELLS = 120                        # células da referência discretizada
```

O Excel sai **ao lado do script**, não no diretório de onde o editor disparou o
processo. Os caminhos do repositório são derivados da localização do próprio
arquivo, então funciona em Windows e Linux sem ajuste.

Com terminal, se preferir:

```bash
cd HFM/LMPD
python comparar_modelos.py --listar
python comparar_modelos.py CHU_2 SCHOLZ_1 --xlsx comparacao.xlsx
python comparar_modelos.py --familia literatura
python comparar_modelos.py --todos
```

No PowerShell o executável é `python` (ou `.\.venv\Scripts\python.exe`), e um
script no diretório atual precisa de `.\` na frente — `python comparar_modelos.py`
evita as duas pegadinhas.

Sai em **dois blocos**, cada um com a sua própria referência — isobárico e com
queda. Ver o cabeçalho do script para por que uma tabela única com uma só coluna
de referência compararia contra a referência errada.

O Excel traz uma linha por grandeza e por bloco, com valor da referência, valor
e erro de cada modelo algébrico, e o ganho. Congelado na coluna D e formatado
para colar direto numa tabela do artigo.

**Três coisas que a ferramenta faz e que vale saber:**

- **Checa o domínio de Hagen–Poiseuille** e avisa quando o cenário cai fora. Ali
  nem a referência vale, e os erros impressos não medem o modelo algébrico. Os
  cenários `S0_PI` e `rico_PI` a 1,3 m caem fora — não é defeito, é o aviso
  funcionando.
- **Não convergir é resultado, não exceção.** A coluna sai marcada `NAO CONV.`
  com resíduo e número de avaliações, e o cenário continua. Abortar esconderia
  exatamente os casos que interessam.
- **Confere os valores publicados** contra a nossa referência discretizada,
  quando o cenário os tem, antes de qualquer conclusão sobre os algébricos.

## 8. Modos de falha conhecidos

| sintoma | causa provável | o que fazer |
|---|---|---|
| `converged=False` com resíduo grande | projeto inviável por construção (área insuficiente para a especificação) | cheque `feasible`; a partida de Weller–Steiner já é tentada automaticamente |
| Φ exatamente 1,0 com `family="E"` | inclinações que não admitem camada finita | é o comportamento correto: cai para a família Q. Há regressão para isso |
| resultado plausível mas fora do domínio H-P | Mach no bore acima de 0,1 | o modelo de pressão não vale ali; a referência também não |
| custo alto com `closure="modes"` | o fecho coerente precisa das forças motrizes terminais no laço interno | use `"averaged"` se o custo dominar; a acurácia é indistinguível |

---

## 9. Limitações declaradas

- **Gás ideal.** Peng–Robinson nas condições do estudo dá Z = 0,912 na
  alimentação. Afeta referência e modelo **igualmente**, então a comparação vale;
  o que limita é a acurácia absoluta contra experimento.
- **Isotérmico.** Sem balanço de energia; Joule–Thomson não é modelado.
- **Fibra representativa.** Descreve um feixe de fibras **idênticas**. A
  variabilidade real de diâmetro interno é efeito maior em serviço de alta pureza,
  e não é tratada aqui.
- **Sem polarização de concentração** no suporte poroso.
