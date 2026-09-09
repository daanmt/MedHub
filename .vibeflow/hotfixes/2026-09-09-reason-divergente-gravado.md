# Hotfix: reason-divergente-gravado

origin: third-party
status: verified

## Symptom

Ledger **F76** (s167): `tools/fsrs_queue.py --record <id> --rating N --reason R` aceita
qualquer `R` sem conferir com o bucket em que o card de fato estava. Caso real: o bloco 7 da
s167 misturava 1 card `vencido` (#559) com 8 `agendado`; o agente gravou os 9 com `--reason
agendado`. O CLI aceitou e o revlog de #559 carrega proveniencia falsa. O contrato
(`revisar.md` §4: "gravar SEMPRE com `--reason` igual ao `selection_reason` servido") e prosa
sem gate -- o `selection_reason` e derivado (bucket) e nada o recomputa no `--record`.

Medido em 2026-09-09 (HEAD `f658e9f`): `db.record_review(id, 3, selection_reason="agendado")`
sobre um card com `due` ontem grava `selection_reason='agendado'` e nenhum outro campo diz
que o card era `vencido`. Nao ha coluna para consultar a divergencia.

## Checkpoint

hypothesis: o bucket e uma funcao pura de `(state, due, questao_id, agora)` -- e exatamente o
que `get_cards_by_bucket` calcula ao servir. Recomputa-lo no ato do `--record` (ANTES de
aplicar a revisao, que muda `state`/`due`) da a proveniencia REAL; grava-la na propria linha
do rating (`fsrs_revlog.reason_servido`) e o que torna a divergencia consultavel; o WARN em
stderr e so a apresentacao. Veredito do `/ai-eng` (A4): **WARN, nao BLOCK**; **gravado, nao so
impresso** -- o contador de gate-miss com classe (B1) vai ler dali.

falsification_test: se o `--record` ja recomputasse, o revlog do caso acima teria algum campo
com `vencido`. Nao tem coluna nenhuma para isso (PRAGMA: `selection_reason` e a unica).

blind_spots: (a) `pre_bloco` nao e bucket, e MODO de servico (mini-drill de erros frescos de um
tema): o card por baixo e `fresh_error` ou `novo` -- `pre_bloco` recebido sobre esses dois
NAO e divergencia. (b) card servido fora de qualquer bucket (state>0 com `due` no futuro,
ex.: `--preview` seguido de `--record` por engano) recebe `futuro` como servido -- e
divergencia de qualquer reason recebido, de proposito. (c) `--reason` ausente nao e
divergencia (nada a comparar): fica `selection_reason NULL` + `reason_servido` preenchido; o
contador B1 pode contar os NULL a parte. (d) a janela de erro fresco usa o relogio LOCAL
(`db.agora()`), coerente com F80; `get_fresh_error_cards` ainda usa `datetime('now')` UTC
na propria query -- e o F80b, nao tocado aqui.

## Preservation

- `record_review` continua o caminho unico de escrita do FSRS; lock otimista, revlog na mesma
  transacao, balanceador (F71) intactos. `test_record_review` / `test_fila_prioritaria` /
  `test_preview_ratings` verdes.
- stdout do `--record` continua JSON puro (WARN em stderr).
- Historico do revlog: `reason_servido` nasce NULL nas linhas antigas (mesmo padrao de
  `card_version`/`selection_reason`, `_ensure_revlog_columns`), sem backfill.
- `--reason R` valido e coerente grava exatamente como antes.

## Eliminated / Evidence

## Root cause

`selection_reason` era um argumento de CLI que o `record_review` persistia como veio: o
contrato de propagacao vivia so em prosa (`revisar.md` §4). A regra que define o bucket
existia (em `get_cards_by_bucket`), mas so no caminho de SERVIR; o caminho de GRAVAR nao a
reusava, e o revlog aceitava proveniencia que o proprio banco podia desmentir.

## Fix

files_changed: `app/utils/db.py` · `tools/fsrs_queue.py` (os 2 de codigo) ·
`.claude/commands/revisar.md` + espelho gerado (`sync_skills`, §10.3) ·
`tools/test_reason_divergente.py` + `pytest.ini`

- **`db.bucket_de(state, due, questao_id, instante)`** (puro): a regra de `get_cards_by_bucket`
  sem banco -- `vencido | agendado | fresh_error | novo | futuro`; relogio unico (F80).
- **`db.reason_diverge(recebido, servido)`** com a tabela `REASONS_EQUIVALENTES`
  (`pre_bloco` cobre `fresh_error`/`novo`; sem `recebido` nao ha divergencia).
- **`record_review`** recomputa ANTES de aplicar (le `questao_id` do card), resolve
  `--reason auto`, passa `reason_servido` a `_aplicar_review`, que o grava na linha do revlog
  (coluna nova via `_ensure_revlog_columns`, historico NULL). O retorno carrega
  `selection_reason`, `reason_servido`, `reason_divergente`.
- **`fsrs_queue --record`**: divergencia -> `[WARN] reason divergente: servido=X, recebido=Y`
  em **stderr** (stdout segue JSON puro, agora com os 3 campos); `--reason` ganha `auto`.
- **`revisar.md`** (assinatura canonica do CLI, §7.2): linha do `--record` e o passo 4 do
  contrato citam a recomputacao; o WARN e nomeado como gate-miss do agente.

Consulta do contador B1 (fixada em teste):
`SELECT COUNT(*) FROM fsrs_revlog WHERE selection_reason IS NOT NULL AND reason_servido IS NOT NULL
AND selection_reason != reason_servido AND NOT (selection_reason='pre_bloco' AND reason_servido IN ('fresh_error','novo'))`.

## DoD

- [x] **Nasceu vermelho:** 9/9 falhando (sem `bucket_de`, sem coluna, sem campos no retorno);
      9/9 verdes depois.
- [x] **Caso real:** card `vencido` gravado como `agendado` -> linha `('agendado', 'vencido')`,
      `reason_divergente=True`, WARN em stderr, stdout JSON valido.
- [x] **WARN, nao BLOCK:** a revisao e gravada mesmo divergente (`recorded: true`).
- [x] **Gravado e consultavel:** a query do B1 devolve 1 na fixture com 1 divergente, 1
      coerente e 1 sem reason. Suite **452 passed**; `auto_check --changed` PASSED;
      `sync_skills --check` exit 0.

## Regression

WHEN um card `vencido` (state 2, due ontem) e gravado com `--reason agendado`, THEN a linha do
revlog carrega `selection_reason='agendado'` E `reason_servido='vencido'`, o retorno marca
`reason_divergente=True` e o CLI escreve `[WARN] reason divergente` em stderr com stdout JSON
intacto; WHEN o reason coincide, THEN `reason_servido == selection_reason` e nenhum WARN; WHEN
`--reason auto`, THEN grava o recomputado; WHEN `pre_bloco` sobre erro fresco, THEN nao e
divergencia; AND a divergencia e consultavel por SQL na propria tabela.
test: `tools/test_reason_divergente.py` (9 testes; inscrito em `pytest.ini`)
oracle_type: specified
reproduction: real
verification: red-green

## Deviations

- **`futuro` e um bucket novo, so no `reason_servido`:** nenhum servidor de fila o emite; existe
  para nomear o card gravado fora de qualquer bucket (ex.: `--record` apos `--preview`). E
  divergencia de qualquer reason recebido, por construcao.
- **Skill tocada num hotfix:** `revisar.md` carrega a assinatura canonica do `--record`; sem
  a linha, o CLI e a skill divergiriam (drift D4). `sync_skills` regenerou o espelho no mesmo
  commit (§10.3); `--check` exit 0.
- **F80b segue aberto:** `get_fresh_error_cards` compara `fc.due` (local) com
  `datetime('now', '-48 hours')` (UTC). `bucket_de` usa o relogio local, entao a janela de
  frescor do `reason_servido` pode diferir em 3h da janela do servidor de fila nos casos de
  borda -- registrado, nao tocado.
