## Hotfix Consolidation -- 2026-09-09 (s174, ciclo A do destilado; audit pelo loop vibeflow, D71)

Metodo: para cada doc em `.vibeflow/hotfixes/`, re-executado o teste da secao `Regression`
(`pytest` sobre os 10 arquivos: **77 passed**) e os checks do `DoD` verificaveis por comando no
HEAD `b8929b3`: `fsrs_load --blackout` = `0 movidos / 17 overflow` (idempotente) · `cronograma --gap`
= `meta 10400 / acumulado 7036` == boot `day_plan` · boot imprime `Overflow de blackout (F71): 17` ·
`sync_skills --check` OK · suite inteira `452 passed` · `auto_check --changed` PASSED (0 BLOCK).
**Critical Gate** sobre `git diff ab0d057...HEAD` (26 arquivos, +2019/-129): nenhum padrao do catalogo
(sem DROP/TRUNCATE/DELETE sem WHERE, sem exec/eval, sem segredo, sem protecao removida) -- limpo.

- `2026-09-06-cronograma-pdf-path.md` — still-holds — `test_cronograma_pdf_path` verde; `--check` real segue `fresh`.
- `2026-09-06-fsrs-balance-stdout.md` — still-holds — `test_fsrs_balance_stdout` verde; o colateral que ele deferiu (blackout de prova) virou o F71 e fechou hoje.
- `2026-09-08-clausula-revogada-em-vigor.md` — still-holds — `test_contrato_revogado` verde; check `CONTRATO_REVOGADO` PASSED no auto_check.
- `2026-09-08-reforja-sem-rastro.md` — still-holds — `test_reforja_event_log` verde; evento `reforja` segue emitido pos-commit nos 2 writers.
- `2026-09-08-suite-mencionada-nao-inscrita.md` — still-holds — `test_suites_orfas` verde; check F43 PASSED com as 5 suites novas de hoje inscritas.
- `2026-09-09-fsrs-balance-blackout-prova.md` — **promote** — 15/15 verde; 34 cards movidos no db real, 0 na re-rodada. Sinal: `Preservation` (f) *calendario de provas* e comportamento permanente novo do balanceador (ja escrito em `AGENTE.md §6`), e o overflow e estado consultavel -- pede contrato (`fsrs-management-contract`).
- `2026-09-09-gap-volume-fonte-unica.md` — still-holds — 5/5 verde; os dois comandos imprimem o mesmo par no db real; leitor unico de `provas.json` em `app/utils/provas.py`.
- `2026-09-09-fuso-unico-writers.md` — **promote** — 6/6 verde; 4 writers no relogio unico. Sinal: zona canonica LOCAL e regra permanente (docstring do `db.py`) sem portador em `core/contracts/`; `Deviations`/`Root cause` nomeiam a divida do backfill UTC->local como item separado com COUNT-ASSERT proprio.
- `2026-09-09-justificativa-orfa-card-gate.md` — still-holds — 4/4 verde; `update_flashcard_fields` fail-loud nos DOIS gates (F84 + F85). Divida nomeada (dependencia `app -> tools/card_checks`) entra abaixo, mas e smell de camada, nao comportamento novo.
- `2026-09-09-reason-divergente-gravado.md` — **promote** — 9/9 verde; `reason_servido` e campo permanente do revlog (nasce no 1o `--record` real, ALTER lazy -- no db real ainda nao existe, esperado). Sinal: o contador de gate-miss com classe (B1, spec F81) vai ler dali -- o campo e contrato, nao detalhe.

### Priority debt
- `2026-09-06-cronograma-pdf-path.md` — `status: partial` / `reproduction: synthetic` — por politica do projeto (suites nao tocam o `ipub.db`); o fix esta de pe. Fechar: promover `status` para `verified` com nota, ou aceitar `partial` como convencao local (decisao do dono do `.vibeflow/`).
- `2026-09-06-fsrs-balance-stdout.md` — `status: partial` / `reproduction: synthetic` — idem; o colateral deferido ja fechou (F71).

### Deviations / deferred
- `2026-09-06-cronograma-pdf-path.md` — por que o PDF saiu da raiz nao foi investigado; `cronograma-contract.md` segue dizendo "raiz" (fallback nao muda a norma).
- `2026-09-08-clausula-revogada-em-vigor.md` — `infer_nota` calibrado contra sinal revogado (`:113`), lapidado; spec propria.
- `2026-09-08-reforja-sem-rastro.md` — `recurate_cards.py:160-166` trata `checar_front`/`checar_verso` como AVISO, nao ERRO; vai para o spec da guarda de nao-crescimento.
- `2026-09-08-suite-mencionada-nao-inscrita.md` — 3 registros de suite mantidos a mao; nao verifica que o teste PASSA, so que e coletado.
- `2026-09-09-fsrs-balance-blackout-prova.md` — 17 cards em overflow em 14/09 (`#321 #558 #788 #1187 #245 #706 #381 #823 #1479 #1159 #707 #553 #709 #419 #486 #632 #463`): alvo original irrecuperavel, folga +-1d nao alcanca antes da prova -- decisao de move-los a mao e do operador. 8 cards do blackout da UERJ (01-02/11) tambem foram movidos (correto, registrado).
- `2026-09-09-gap-volume-fonte-unica.md` — `fsrs_load --blackout` lista overflow pelo caminho do `rebalancear` (os que nao conseguiram mover); o boot usa `overflow_blackout` (todos os presos). Coincidem apos `--apply`. Aceito.
- `2026-09-09-fuso-unico-writers.md` — (1) historico UTC em `review_time`/`data_registro`/`reviewed_at` ate `37e0859`: backfill = shift constante -3h, dry-run + COUNT-ASSERT contando linhas que mudam de DIA, gatilho do operador; (2) **F80b** `get_cards_by_bucket`/`get_fresh_error_cards` comparam `fc.due` (local) com `datetime('now', ...)` UTC na janela de 48h -- 3h de erro, aberto; (3) `init_db.py` mantem `DEFAULT CURRENT_TIMESTAMP` (gate real e o teste estrutural).
- `2026-09-09-justificativa-orfa-card-gate.md` — `app/utils/db.py` importa `tools/card_checks.py` por `__file__` (camada invertida); mover = spec (7 writers). Varredura nova da assinatura "premissa morta governando except" nao feita alem das 4 triadas na s170.
- `2026-09-09-reason-divergente-gravado.md` — `futuro` e bucket que so existe no `reason_servido`; F80b afeta a janela de frescor do recomputado em casos de borda.

### Promote stubs
- `2026-09-09-fsrs-balance-blackout-prova.md` → gen-spec entry stub: **"Calendario de provas no agendamento FSRS"** -- o balanceador nunca pousa em nem cruza o blackout (prova + 1 dia, lido de `core/provas.json`); alvo em blackout vai para antes; overflow e estado do banco exposto no boot e em `fsrs_load --blackout`; re-rodada sob §10.7. Portador: `core/contracts/fsrs-management-contract.md` (hoje so `AGENTE.md §6`).
- `2026-09-09-fuso-unico-writers.md` → gen-spec entry stub: **"Zona canonica de tempo do ipub.db = LOCAL"** -- todo carimbo sai de `db.agora()`; gate estrutural contra writer no DEFAULT; fronteira historica em `37e0859`; backfill UTC->local como operacao §10.7 separada (COUNT por linhas que mudam de dia). Portador: contrato (`fsrs-management` ou `reconcile`), nao so docstring.
- `2026-09-09-reason-divergente-gravado.md` → gen-spec entry stub: **"Proveniencia recomputada no revlog"** -- `reason_servido` e a verdade do bucket no ato; `selection_reason` e o que o agente declarou; a divergencia e a fixture do contador de gate-miss com classe (B1/F81). Entra no spec F81 como campo lido, nao como spec proprio.

### Achado colateral desta consolidacao (nao e regressao)
- A6 (dry-run F65/F67, `docs/DRYRUN-F65-F67-2026-09-09.md`): `normalize_taxonomia.py` simula 286 -> 286 -- as operacoes declaradas (RODADA 2) ja foram aplicadas e nao ha regra para os duplicados do F67 nem para os baldes do F65. O instrumento *le o nada* (Reachability-Debt v1). E as areas fantasma `GO`/`Clinica Medica`, dissolvidas na RODADA 1, **voltaram** (7 linhas novas) porque nenhum writer de taxonomia valida `area` -> **F89** (ledger, so-dado).
