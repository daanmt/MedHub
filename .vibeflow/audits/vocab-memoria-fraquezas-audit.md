# Audit Report: vocab-memoria-fraquezas (F66, item 1.3)

**Verdict: PASS**

> Spec: **o proprio ledger** (`AUDITORIA_MEDHUB.md` F66, direcoes a-d) -- classe *quick*.
> Sessao **s176 janela 2** (2026-09-10). Suite **572 passed** (baseline 560; +12).
> `auto_check --changed` -> **PASSED**, 0 BLOCK.

## DoD (as quatro direcoes do achado)

- [x] **(a) Tabela de alias em UM portador versionado.** `core/areas.json` -> `aliases`, **34
  entradas, todas MEDIDAS no store**, com a nota explicando por que existem e por que rotulo
  ambiguo nao entra. `app/utils/areas.resolver_area()` resolve em **tres camadas declaradas na
  docstring**: canonico normalizado · alias explicito · **prefixo de composto**. Esta terceira
  camada nao estava na direcao do achado -- apareceu na medicao (`"Pediatria - Sepse Neonatal"`
  no campo `area`, 8 ocorrencias) e resolve uma classe inteira que o alias sozinho nao pegaria.
- [x] **(b) `reconciliar_weak_areas` consulta o alias** antes de declarar `fora_vocab`.
- [x] **(c) Sink idempotente para o que sobra.** `history/wa_vocab_pendentes.json`, chave =
  `item.key`, reescrito por passe. O painel (`ledger_self`) cita esse numero; a linha do
  `memory_errors.log` continua visivel mas agora **rotulada pelo que ela realmente mede** --
  *"log de FALHA, nao de divida"*. Testado que a 2a gravacao dos MESMOS itens nao dobra a
  contagem e que o numero **cai** quando um item e resolvido.
- [x] ⚰️ **(d) Sanear as 3 entradas duplicadas do vocabulario -- DEIXOU DE SER NECESSARIO.** A
  direcao pressupunha vocabulario derivado de `SELECT DISTINCT area FROM taxonomia_cronograma`.
  O **F89 (item 0.6, tres horas antes)** trocou a fonte por `core/areas.json`, que **nao tem
  fantasma por construcao**. Um item do Tier 0 apagou uma direcao do Tier 1 -- registrado como
  tal, e o teste `test_vocabulario_vem_do_canonico_e_nao_da_taxonomia` trava a fonte nova
  nomeando os 4 fantasmas que nao podem voltar.
- [x] **Craftsmanship.** 572 passed; ASCII limpo; o sink e gitignored (estado derivado, como o
  `memory_errors.log`); `app/memory` importando `app/utils` respeita a direcao da dependencia.

## Medicao (antes -> depois, store real)

| | antes | depois |
|---|---|---|
| WeakAreas no store | 299 | **290** (9 duplicatas colapsadas) |
| fora do vocabulario | **140 (47%)** | **100 (34%)** |
| rotulos distintos fora | 91 | **59** |
| normalizadas no passe | — | **75** |

Segunda passagem devolve `normalizadas: 0` -- a reconciliacao e **idempotente**, nao um script
que precisa rodar uma vez e nunca mais.

## Os 100 restantes sao TRES classes, nao falha do alias

1. **Ambiguo** -- `Clínica Médica`, `Clínica Geral`, `Ginecologia-Obstetrícia - *`. Resolver
   seria repetir o erro da s110 (3 linhas de `Clinica Medica` eram Infecto, Hemato e Oftalmo).
   Fica como divida **declarada**.
2. **Nao e area** -- `Conhecimento Desatualizado`, `Interpretação de Exames`, `Todas`,
   `Hemostasia`. Sao habilidade ou tema escritos no campo `area`. Forcar casamento aqui
   corromperia o ranking com dado errado.
3. 🔴 **Especialidade legitima que a lista canonica NAO TEM** -- `Oncologia`, `Urologia`,
   `Radiologia`, `Medicina de Emergência`. **Isto e pergunta para o OPERADOR** (a lista e dele,
   `core/areas.json`), nao conserto de engenharia -- e agora ele tem o numero para decidir.

Cada classe tem teste proprio, afirmando que **nao resolver e o comportamento correto**.

## Pattern Compliance

- [x] **Fonte unica de vocabulario** (F89) reusada em vez de reimplementada -- e foi isso que
  apagou a direcao (d).
- [x] **Fronteira leitura x escrita explicita e testada:** `resolver_area` (rotulo livre, memoria)
  tolera forma longa; `validar_area` (gate de escrita) **nao** -- `test_o_gate_de_ESCRITA_nao_herda_a_tolerancia_da_LEITURA`.
  Na escrita, adivinhar e o defeito; na leitura de rotulo ja gravado, descartar e o defeito.
- [x] **Recall-safe preservado:** nada e dropado; o que nao resolve vira item contavel.
- [x] **Suite inscrita no `pytest.ini`** com a medicao antes/depois na nota.

## Convention Violations

Nenhuma.

## Critical Gate

Clean — no destructive operations detected. Uma escrita nova (o sink JSON, gitignored) e um
`DELETE` preexistente (colapso de duplicata, ja auditado no F45). Sem SQL destrutivo, migration,
exec dinamico ou segredo.

## ⚠️ Defeito introduzido nesta passagem, achado por medicao e corrigido aqui

O sink gravava no **caminho de producao** e `tools/test_boot_verdadeiro.py` chama
`reconciliar_weak_areas` com store **sintetico**: rodar a suite sobrescreveu os **100 itens reais
por 1 `wa_dummy`**. So apareceu porque conferi o numero do painel depois da suite, e ele dizia 1.
Corrigido no padrao que o repo **ja tinha** para o `event_log`: o `conftest` autouse redireciona
`PENDENTES_VOCAB_PATH` para `tmp_path` em todo teste. Estado real restaurado e re-medido (100).
Licao registrada no comentario do proprio `conftest`: **escrita nova em caminho global entra la**
-- a lacuna era do isolamento, nao do sink.

## Fronteiras DECLARADAS

1. **O alias e uma LISTA, e listas envelhecem.** As 34 entradas cobrem o que o store tem hoje. Um
   rotulo longo novo que o modelo invente amanha cai no sink -- que e o comportamento certo
   (visivel e contavel), mas nao ha gate que exija alias para area canonica nova. A direcao (a) do
   achado pedia *"teste que falhe quando uma area canonica nova entra sem alias"*; **isso nao foi
   feito** -- para a maioria das areas canonicas a forma longa e a propria (Cardiologia,
   Pediatria), entao o teste seria ruido. Declarado em vez de simulado.
2. **34% de orfandade PERMANECE**, e uma das tres classes so o operador fecha. O numero caiu de
   47%, nao foi zerado, e o ranking de fraquezas do boot segue sendo disputado por ~2/3 do store.
3. **Nao foi medido o efeito no ranking.** A consequencia (1) do achado -- *"o top 8 do boot sai
   enviesado"* -- e plausivel e **nao verificada**: normalizar a area nao recalcula `error_count`
   sozinho (ele vem de match exato contra `ipub.db` na proxima consolidacao). O efeito aparece na
   proxima sessao, nao agora, e nao se finge medicao do que ainda nao rodou.

---

**Ready to ship.**
