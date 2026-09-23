---
type: spec
projeto: MedHub
feature: medhub-hub-v0
part: 2
slug: medhub-hub-v0-part-2
status: ready
relates_to:
  - .vibeflow/prds/medhub-hub-2026-09-22.md
  - tools/fsrs_queue.py
  - app/utils/db.py
  - app/utils/fsrs.py
  - tools/test_fsrs_queue_player.py
---

# Spec -- MedHub HUB v0, parte 2: `--record-lote` grava no relogio da revisao, idempotente e com quarentena

> Sessao s192 (22/09/2026). Alteracao B do PRD, revista no mesmo dia pelo `/ai-eng` (GO com condicao):
> o revlog passa a guardar o MOMENTO DA REVISAO (ts da nota), nao o da gravacao, e o writer vira a
> fronteira real (quarentena de doc estranho). Independente da parte 1; tem de estar no ar ANTES da 1a
> gravacao de notas do hub (DoD 2 do PRD).

> **Estado ao fim da s192 (22/09/2026): PENDENTE.** A 1a tentativa (1 subagente Opus) foi interrompida
> depois de ~1h com ~30% feito e o `record_review` QUEBRADO no meio (`quando` indefinido dentro de
> `_aplicar_review` -- o unico caminho de escrita do FSRS). O principal parou o filho, salvou o parcial
> (o leitor `db.estado_gravacao_player` + o `ts` em `ler_notas`) em `tmp/medhub-hub-v0-part-2-wip.patch`
> e devolveu `db.py`/`fsrs_queue.py` ao HEAD (24 testes verdes). Ate esta parte entrar vale o GATE do
> rito (`revisar.md`): notas do hub nao sao gravadas, o lote nao e trocado e nada e podado.

## Objective
Ler e gravar a mesma sessao de notas duas vezes grava ZERO na segunda; cada revisao entra no FSRS no
momento em que aconteceu no celular; e doc estranho no `db` da pagina e recusado sem derrubar os validos.

## Context
O player guarda a 1a nota de cada card no `db` da pagina (`sessoes/<sessao>/notas`, 1 doc por card,
`{card_id, rating_primeira, ts, defeito?, motivo?}`, `ts` ISO UTC) e restaura no reload. Com UM artifact
permanente a mesma sessao e relida. Hoje: (a) a unica guarda contra regravar e o agente lembrar
(`conventions.md` §FSRS, "dedup lives in the agent"); medido em 22/09, o card #92 precisou de marca manual
`gravado_em` no `db`; (b) `record_review` usa a hora da GRAVACAO (`FSRS.evaluate` pega `datetime.now`,
o revlog grava `carimbo()`): a nota das 07:17 gravada as 19:37 deslocou o `due` do #92 em 12h, e com esse
relogio "review_time >= ts" engoliria em silencio uma 2a nota do mesmo card gravada na mesma janela
(objecao do `/ai-eng`); (c) doc invalido RECUSA o lote inteiro (exit 2). Na conta compartilhada todo mundo
e owner (as regras do `db` nao o limitam): a fronteira que protege o dado e o writer.

**Friccao (F110):** remove friccao VICIOSA (lembrar o que ja foi gravado, marcar doc a mao, um doc torto
travar o lote); nao toca a virtuosa -- a nota continua sendo a 1a do operador, gravada uma vez, e agora no
momento em que ele a deu.

## Definition of Done
1. **Relogio:** `FSRS.evaluate(card, rating, quando=None)` e `db.record_review(..., quando=None)` calculam
   e gravam no instante `quando` (LOCAL naive; `review_time = quando` no formato do carimbo); `quando` no
   futuro -> `ValueError`, nada gravado; sem `quando`, comportamento identico (`test_record_review`,
   `test_fsrs_balance*`, `test_fsrs_blackout*`, `test_fuso_unico*` verdes sem edicao). `--record-lote` passa
   `quando` = ts da nota em hora local TRUNCADO AO SEGUNDO e aplica em ordem crescente de ts.
2. **Idempotencia exata:** nota com linha em `fsrs_revlog` de `review_time == trunc(ts_local)` = JA GRAVADA
   (pulada, contada, fora do N do `--expect`); revlog do card com revisao MAIS NOVA e sem a linha igual =
   FORA DE ORDEM (nao grava, reportada com motivo -- nunca silenciosa); defeito com marca `origem='player'`
   de `criado_em >= trunc(ts_local)` = JA MARCADO (sem segunda marca).
3. **Quarentena no writer:** doc estranho (card_id fora do lote, rating fora de 1..4, `ts` ausente/ilegivel/
   no futuro, defeito sem motivo, sem rating e sem defeito) e REJEITADO e REPORTADO por doc, nada dele e
   gravado, os validos seguem; rejeitado nao faz o CLI sair 2. Duplicata no mesmo arquivo: conta a de menor
   `ts`, com aviso.
4. **Testes** em `tools/test_fsrs_queue_player.py` (fixtures antigas ganham `ts`, asserts intocados):
   releitura grava 0 com `--expect 0`; PROPRIEDADE (`/ai-eng`): 2 notas do mesmo card em 2 sessoes, ts1 <
   ts2, gravadas em ordem -> 2 linhas com `review_time` = ts1, ts2; em ordem inversa -> a de ts1 sai FORA DE
   ORDEM, reportada; conversao UTC -> local com fuso INJETADO (`-03:00`); defeito relido nao remarca;
   quarentena com 1 doc de cada tipo + 2 validos grava 2 e reporta cada um; `record_review` com `quando`
   grava `review_time = quando` e recusa futuro.
5. Leituras novas so por `app/utils/db.py` (so `SELECT`, sem `'now'` do SQLite); nenhum writer novo
   (`tools/test_writer_allowlist.py` verde sem edicao); `fsrs_queue.py` sem `import sqlite3`.
6. Craftsmanship: `python -X utf8 tools/auto_check.py --changed` PASSED; `.claude/commands/revisar.md` (linha
   do `--record-lote`) e `conventions.md` §FSRS descrevem relogio, idempotencia e quarentena; espelho
   regenerado.

## Scope
`app/utils/fsrs.py` (`quando`), `app/utils/db.py` (`record_review`/`_aplicar_review` com `quando`, 1 leitor),
`tools/fsrs_queue.py` (`ler_notas`, `aplicar_notas`, `main`), `tools/test_fsrs_queue_player.py`,
`tools/test_record_review.py` (testes novos). Docs: `revisar.md` (+ espelho), `conventions.md`.

## Anti-scope
Mudar a pagina (formato, `ts`, relearning). Coluna ou tabela nova. Reescrever revisoes ja gravadas (o #92 de
22/09 fica com o relogio velho e sai FORA DE ORDEM numa releitura -- seguro, reportado). Mudar o
balanceador, o blackout ou o COUNT-ASSERT. Deduplicar gravacao feita pelo `/revisar` do chat.

## Technical Decisions
- **Relogio da revisao, nao da gravacao:** e o que o FSRS modela (intervalo a partir do momento do recall) e
  e o que torna a idempotencia exata (igualdade no segundo, em vez de `>=`). Trade-off: uma revisao pode
  entrar "no passado" do relogio de parede; o balanceador segue decidindo com o `hoje` real, e o FORA DE
  ORDEM garante que o estado do card so anda para a frente.
- **Quarentena em vez de recusa total:** um doc torto deixa de bloquear as notas boas do operador. A
  janela de override continua no dry-run (Invariante C): o agente le as rejeicoes antes do `--apply`.
- **Sem flag nova:** idempotencia, relogio e quarentena sao o comportamento padrao; o D5 nao muda.

## Applicable Patterns
- `db-access-layer.md`: leitura e escrita so por `db.py`, `conn.close()` explicito.
- `error-insertion-pipeline.md`: dry-run + `--expect` + COUNT-ASSERT pos, intocados.

## Risks
- **`py-fsrs` recusar `review_datetime` anterior ao ultimo review:** o FORA DE ORDEM barra antes; teste
  cobre.
- **Truncagem ao segundo divergente entre gravar e comparar:** um unico helper converte e trunca, usado nos
  dois lados.

## References
- `tools/test_fsrs_queue_player.py` -- a suite do comportamento atual (19 testes).
- `app/utils/fsrs.py::FSRS.evaluate`, `app/utils/db.py::record_review`, `::_aplicar_review`, `::carimbo`.

## Dependencies
Nenhuma.
