# Hotfix: gap-volume-fonte-unica

origin: third-party
status: verified

## Symptom

Achado da s173 (destilado A5, sem F-id -> numerado **F88** nesta sessao; regra G2): dois
comandos do repo reportam **pares diferentes** para "acumulado / meta" lidos do MESMO banco:

| comando | acumulado | meta | fonte da meta |
|---|---|---|---|
| `python tools/day_plan.py` (boot, hook SessionStart) | **7.036** | **10.400** | `performance.MARCOS[0]` + `get_totais(con)` (inclui Simulado, s126) |
| `python tools/cronograma.py --gap` | **6.305** | **10.000** | `argparse --meta default=10000` (literal) + `get_totais(con, escopo="cronograma")` (exclui Simulado) |

Medido em 2026-09-09 (HEAD `015dac0`): `--gap` imprime `"meta": 10000, "acumulado": 6305`;
o `day_plan` do mesmo instante imprime `7036 acum. · faltam 3364 p/ UERJ/MFC` (10.400). O db
diz 7.036 (`SUM(questoes_feitas)` em `sessoes_bulk`). **`--gap` e o defasado**: a meta 10.000
e o marco ENAMED revogado na s126 e substituido por UERJ 10.400 na s159; ninguem atualizou o
literal do argparse porque ele nao lia o `MARCOS`. Viola G4 ("fonte unica") -- dois leitores
dos mesmos arquivos, cada um com sua conta.

## Checkpoint

hypothesis: `--gap` tem DUAS fontes proprias para os dois numeros: (1) a meta e um literal de
CLI (`default=10000`) que envelheceu quando `MARCOS[0]` mudou (s126 -> s159); (2) o acumulado
usa `escopo="cronograma"` (exclui o bloco Simulado), decisao local ao `--gap` que contradiz a
regra da s126 de que simulado CONTA no volume oficial. O `day_plan` le `MARCOS[0]` e o total.
Remedio (ALTERA do `/ai-eng`): UMA funcao de calculo em `performance.py` (onde `MARCOS` e
`get_totais` ja vivem) chamada pelos dois; nenhum dos dois callers pode hospeda-la
(`cronograma` <- `day_plan` ja importa `cronograma`; o inverso seria circular).

falsification_test: se `--gap` ja lesse `MARCOS[0]`, `--meta` sem argumento imprimiria 10400.
Imprime 10000 (medido). Se lesse o total oficial, imprimiria 7036. Imprime 6305 (medido).

blind_spots: (a) `--gap` tem um 3o numero proprio, `cronograma_restante` (soma da grade a partir
da semana corrente) -- nao esta em disputa e continua do `cronograma`; (b) `--meta` como
override explicito ("what-if") e legitimo -- o defeito e o DEFAULT literal, nao a existencia
do flag; (c) `ritmo_alvo` do day_plan divide por dias ate o marco: entra na funcao unica para
nao virar a proxima duplicata.

## Preservation

- `day_plan` continua imprimindo o MESMO par (7.036 / 10.400 hoje) e o mesmo `ritmo_alvo`
  (~63.5q/dia) -- o boot nao muda de numero, so de fonte.
- `--gap` continua reportando `cronograma_restante` e `projecao_se_100pct`; `--meta N`
  explicito continua vencendo (what-if).
- `cronograma.py` segue **read-only** no `ipub.db` (Clausula 5 do contrato).
- Suite verde; `auto_check --changed` 0 BLOCK.

## Eliminated / Evidence

## Root cause

Dois callers, duas contas. O `--gap` nasceu no ultraplan (pre-s126) com `meta=10000` literal
no argparse e `escopo="cronograma"` no acumulado; quando o marco mudou (s126 -> s159:
UERJ 10.400) so o `day_plan` foi atualizado, porque so ele lia `MARCOS`. O literal de CLI e
um numero em canonico que ninguem re-mede (D67): envelheceu em silencio por ~50 sessoes.
Mesma classe do rider b do F71: `db.blackout_provas` e `day_plan.carregar_provas` eram dois
parsers do mesmo `core/provas.json`.

## Fix

files_changed: `tools/performance.py` · `tools/day_plan.py` · `tools/cronograma.py` ·
`app/utils/provas.py` (NOVO, leitor unico) · `app/utils/db.py` (delega + `overflow_blackout`) ·
`tools/test_volume_fonte_unica.py` + `pytest.ini` (regressao) · `tools/test_fsrs_blackout_provas.py`
(monkeypatch aponta para o leitor unico)

- **`performance.volume_vs_marco(conn, hoje)`** -- a UNICA conta: `{marco, meta, data_marco,
  total, acertos, faltam, dias, ritmo_alvo}` (total = `get_totais(escopo="total")`, inclui
  Simulado; meta = `MARCOS[0]`). Mora onde `MARCOS`/`get_totais` ja moravam; nenhum dos dois
  callers pode hospeda-la (`day_plan` importa `cronograma`).
- **`day_plan.build`** chama `volume_vs_marco`; zero `MARCOS[0]`/`get_totais` soltos.
- **`cronograma.gap_payload(conn, grade, hoje, meta, desde)`** chama `volume_vs_marco`;
  `--meta` vira what-if com `default=None`; `gap_volume` perde o default literal. `--gap`
  passa a imprimir tambem `marco`.
- **Rider b (leitor unico de `provas.json`):** `app/utils/provas.py` recebe `PROVAS_PATH` +
  `carregar_provas` (movidos verbatim do `day_plan`, WARNs preservados) + `datas_de_prova` +
  `blackout_provas`; `day_plan` re-exporta; `db.blackout_provas` delega (sem `json.load`).
  `tools/test_provas.py` (13) segue verde sem mudar.
- **Rider a (overflow no painel):** `db.overflow_blackout(cursor)` (read-only) e o boot
  `day_plan` imprime `⚠️ Overflow de blackout (F71): N card(s) presos em <dia> -- #ids` --
  derivado do ESTADO do banco a cada boot, nao de um log: e a forma mais forte de "gravado".

**Medido depois, no `ipub.db` real:** `--gap` = `meta 10400 / acumulado 7036 / marco UERJ`;
boot = `7036 acum. · faltam 3364 p/ UERJ/MFC ... ~63.5q/dia` -- o mesmo par, e o boot nao
mudou de numero (Preservation). Overflow no boot: 17 cards em 2026-09-14.

## DoD

- [x] **Nasceu vermelho:** 5/5 falhando antes (`volume_vs_marco`/`gap_payload` inexistentes;
      `--meta default=10000` medido); 5/5 verdes depois.
- [x] **Mesma fixture, dois comandos, mesmo par:** `test_gap_e_boot_devolvem_o_mesmo_par`
      (db sintetico com Simulado) -- (600, MARCOS[0]) nos dois; what-if `--meta` so muda a meta.
- [x] **Estrutural:** `build` sem `MARCOS[0]`; `cronograma.main` sem default literal >= 1000
      (AST); `db.blackout_provas` sem `json.load`/`open(`; `day_plan.carregar_provas is
      provas.carregar_provas`.
- [x] **Preservacao:** `test_provas` 13/13 · `test_fsrs_blackout_provas` 15/15 · suite
      **433 passed** · `auto_check --changed` PASSED (0 BLOCK) · boot imprime o mesmo par de antes.

## Regression

WHEN o mesmo banco (fixture com linhas de area clinica E de Simulado) e lido pelo bloco de
volume do `day_plan` e pelo `--gap` do `cronograma`, THEN os dois devolvem o MESMO par
(acumulado, meta), com acumulado = SUM de `sessoes_bulk` incluindo Simulado e meta =
`MARCOS[0]`; WHEN `--meta` e passado explicitamente, THEN so a meta muda e o acumulado segue
o mesmo.
test: `tools/test_volume_fonte_unica.py` (5 testes; inscrito em `pytest.ini`)
oracle_type: specified
reproduction: real
verification: red-green

## Deviations

- **Orcamento:** 5 arquivos de codigo contra os 2 do `vibeflow:hotfix`. Tres sao o minimo
  estrutural de "uma funcao, dois callers" (nenhum caller pode hospeda-la); os outros dois sao
  o rider b do `/ai-eng` (absorver o leitor duplicado de `provas.json` aqui em vez de deferir).
  GO explicito dele em 09/09 ("fatiar so adicionaria cerimonia"). Declarado, nao escondido.
- **`escopo="cronograma"` do `--gap` foi descartado**, nao preservado: contradizia a decisao
  s126 (simulado CONTA no volume oficial). `projecao_se_100pct` sobe de 8.232 para 8.963 e o
  `gap_volume` cai de 1.768 para 1.437 -- e a mesma pergunta respondida com o numero oficial.
- **`fsrs_load.py --blackout` continua listando overflow pelo caminho do `rebalancear`** (os
  que NAO conseguiram mover), enquanto o boot usa `overflow_blackout` (todos os presos). Apos
  um `--apply` os dois conjuntos coincidem; antes, o do `rebalancear` e subconjunto. Aceito.
