# Hotfix: fuso-unico-writers

origin: third-party
status: verified

## Symptom

Ledger **F80** (s169): writers do `ipub.db` discordam de FUSO. As 21:30 locais de 07/09 o
`fsrs_revlog` carimbou `review_time = 2026-09-08 00:29` e o `questoes_erros` carimbou
`data_registro = 2026-09-08 00:20`, enquanto as 3 linhas de `sessoes_bulk` da mesma sessao
ficaram em `data_sessao = 2026-09-07`. Confirmado com `select datetime('now')` (UTC
2026-09-08 00:30) x `datetime('now','localtime')` (2026-09-07 21:30). O subagente que leu o
banco concluiu, com razao aparente, que "a sessao cruzou a meia-noite" -- nao cruzou. **O
defeito nao quebra: mente.**

Mapa medido em 2026-09-09 (HEAD `91c40e2`) de quem carimba o que, e em que zona:

| coluna | writer | como | zona |
|---|---|---|---|
| `fsrs_revlog.review_time` | `db._aplicar_review` (INSERT sem a coluna) | `DEFAULT CURRENT_TIMESTAMP` | **UTC** |
| `questoes_erros.data_registro` | `tools/insert_questao.py:217` (INSERT sem a coluna) | `DEFAULT CURRENT_TIMESTAMP` | **UTC** |
| `review_log.reviewed_at` | `db.log_review` (INSERT sem a coluna) | `DEFAULT CURRENT_TIMESTAMP` | **UTC** |
| `sessoes_bulk.data_sessao` | `tools/registrar_sessao_bulk.py` | `date.today()` | local (dia) |
| `fsrs_cards.due` / `last_review` | `app/utils/fsrs.py:121-137` (`due_local`, `last_review_local`) | explicito | **local por construcao** |
| `fsrs_revlog.due` | idem (copia do metrics) | explicito | local |
| `fsrs_cards.due` (card novo) | `insert_questao.py:241`, `insert_card_base/extra` | `datetime.now()` | local |

Leitores de "dia": `day_plan.realizado_do_dia` (`date(review_time) = data_sessao`),
`get_cards_by_bucket` (`fc.due` x `datetime.now()`), F38 `ERROS_ORFAOS`
(`date(data_registro) BETWEEN d AND d+1`), `review_radar`/`dormant_refresh`
(`MAX(reviewed_at)` x `fsrs_cards.last_review`) -- **todos assumem local**.

## Checkpoint

hypothesis: os tres carimbos em UTC nao sao decisao -- sao o `DEFAULT CURRENT_TIMESTAMP` do
SQLite herdado do `init_db`, num banco cujo nucleo (FSRS) e cujos leitores sao locais. A
mistura e produzida no ATO da escrita, por omissao da coluna no INSERT. Remedio: um helper
unico `db.agora()` (naive local, mesma convencao do `fsrs.py`) que TODO writer de carimbo
passa explicitamente; leitores atuais ficam corretos sem mudar.

Zona canonica = **LOCAL** (decisao do `/ai-eng` em 09/09 apos a evidencia do nucleo FSRS;
a ALTERA anterior "UTC no db" caiu: UTC canonico exigiria migrar nucleo + balanceador +
fila + leitores -- spec, nao hotfix -- e deixaria o banco em duas zonas ate la).

falsification_test: se os writers ja passassem o carimbo explicitamente, congelar `db.agora()`
em `2026-09-07 21:30` faria as 3 colunas gravarem exatamente esse valor. Medido no HEAD: o
INSERT nao nomeia a coluna em nenhum dos 3 -- o valor vem do relogio do SQLite (UTC, nao
congelavel). Hipotese sobrevive.

blind_spots: (a) `backfill_review_log.py` grava `reviewed_at` explicito (historico real por
tema) -- one-shot, nao e writer de carimbo corrente; fora do teste estrutural por nome.
(b) `get_cards_by_bucket` compara `fc.due` (local) com `datetime('now', '-48 hours')` (UTC) na
janela de erro fresco -- erro de 3h numa janela de 48h; **fora deste hotfix** (uma chamada,
um bug), registrado em Deviations. (c) Historico UTC nas 3 colunas (ate este commit) fica
como esta: reescrever timestamp e operacao destrutiva sobre SSOT (AGENTE §1.1) e o revlog
calibra o FSRS. **Brasil nao tem horario de verao desde 2019 (Decreto 9.772/2019)**: o
deslocamento historico e um shift CONSTANTE de -3h (`America/Sao_Paulo`), entao o backfill,
se um dia for pedido, e `datetime(col, '-3 hours')` puro -- e o COUNT-ASSERT pode contar
quantas linhas mudam de DIA (as gravadas entre 21:00 e 23:59 locais), nao so de hora.

## Preservation

- Formato do carimbo identico ao de `CURRENT_TIMESTAMP` (`YYYY-MM-DD HH:MM:SS`): todo leitor
  que faz `date(col)`/`MAX(col)` continua funcionando sem edicao.
- `sessoes_bulk.data_sessao` continua sendo o DIA de estudo local (SSOT volumetrica) --
  agora derivado do mesmo relogio (`db.agora().date()`), `--data` explicito segue vencendo.
- Nucleo FSRS (`fsrs.py`) intocado; `fsrs_cards.due`/`last_review` continuam locais.
- `insert_questao`/`registrar_sessao_bulk` continuam CLIs standalone com `sqlite3` direto
  (AGENTE §6): importam so o helper do `db`, nao trocam de caminho de escrita.
- Suite verde; `auto_check --changed` 0 BLOCK; allowlist de writers (F49) inalterada.

## Eliminated / Evidence

## Root cause

Tres writers de carimbo OMITIAM a coluna no INSERT e herdavam o `DEFAULT CURRENT_TIMESTAMP`
do schema (`init_db.py`), que no SQLite e UTC. Nao houve decisao de zona em lugar nenhum: a
zona UTC entrou por omissao, num banco cujo nucleo FSRS grava local por construcao e cujos
leitores comparam com `date.today()`. Reachability-Debt variante 3 invertida: nao e uma
razao morta governando codigo, e uma AUSENCIA de razao (o default) governando o dado.

## Fix

files_changed: `app/utils/db.py` · `tools/insert_questao.py` · `tools/registrar_sessao_bulk.py`
(os 3 de codigo, orcamento GO do `/ai-eng`) · `tools/test_fuso_unico.py` + `pytest.ini`
(regressao) · `tools/test_batch_insert.py` (sandbox do CLI passa a copiar `app/`)

- **Relogio unico** em `db.py`: `agora()` (LOCAL naive), `carimbo()` (`YYYY-MM-DD HH:MM:SS`),
  `hoje()`. Docstring do modulo declara a zona canonica, a fronteira historica e a regra
  do shift constante. Writers chamam pelo ATRIBUTO do modulo (`db.agora()`), o que e o que
  permite congelar o instante no teste.
- **`fsrs_revlog.review_time`** e **`review_log.reviewed_at`** passam explicitos em
  `_aplicar_review`/`log_review`; os demais carimbos locais do proprio `db.py`
  (`dificuldade_at`, `preparacao_estado.atualizado_em`, `habilidades.criado_em`) tambem
  passam por `agora()` -- mesma zona, um relogio.
- **`questoes_erros.data_registro`** explicito em `insert_questao.py` (`db.carimbo()`); os 3
  `datetime.now()` do arquivo (`ultima_revisao`, `fsrs_cards.due` de card novo) viram
  `db.agora()`. O CLI segue standalone no `sqlite3`; so o relogio vem de `app/`.
- **`sessoes_bulk.data_sessao`** = `db.hoje()` (mesmo relogio); `--data` explicito vence.

**Historico (fronteira):** linhas de `review_time`/`data_registro`/`reviewed_at` gravadas
ANTES deste commit estao em UTC e ficam assim. Shift constante de -3h (sem horario de verao
no Brasil desde 2019 -- Decreto 9.772/2019); backfill = item separado, dry-run +
COUNT-ASSERT contando linhas que mudam de DIA, gatilho do operador.

## DoD

- [x] **Nasceu vermelho:** a varredura estrutural acusou exatamente os 3 INSERTs
      (`insert_questao.py: questoes_erros`, `db.py: fsrs_revlog`, `db.py: review_log`);
      os testes de instante congelado erraram por `db.agora` inexistente. 6/6 verdes depois.
- [x] **3 writers + bulk no mesmo instante congelado** (`2026-09-07 21:30`): as 3 colunas
      valem `2026-09-07 21:30:00` e `data_sessao` vale `2026-09-07`.
- [x] **Leitor que junta revlog x sessoes_bulk** (`day_plan.realizado_do_dia`) ve card e
      questoes em 07/09 e ZERO em 08/09 -- a meia-noite fantasma morreu.
- [x] **Gate contra writer novo:** `test_nenhum_insert_depende_do_default_do_sqlite` varre
      `tools/` + `app/` e falha nomeando o arquivo; contra-prova verifica que o scanner ve
      os 4 writers conhecidos. Suite **439 passed**; `auto_check --changed` PASSED.

## Regression

WHEN o relogio unico `db.agora()` e congelado em `2026-09-07 21:30` (local) e os writers
gravam uma revisao de card (`fsrs_revlog`), um erro analisado (`questoes_erros`), um carimbo
de tema (`review_log`) e um bloco de volume (`sessoes_bulk`), THEN as tres colunas de carimbo
valem exatamente `2026-09-07 21:30:00` e `data_sessao` vale `2026-09-07`; AND o leitor
`day_plan.realizado_do_dia(con, "2026-09-07")` conta o card e as questoes no MESMO dia; AND
nenhum INSERT nas 4 tabelas (em `tools/` e `app/`, fora de testes/arquivo) omite a coluna de
carimbo -- um writer novo que dependa do DEFAULT do SQLite falha o teste nomeando o arquivo.
test: `tools/test_fuso_unico.py` (6 testes; inscrito em `pytest.ini`)
oracle_type: specified
reproduction: real
verification: red-green

## Deviations

- **4 writers, nao 3:** o ledger falava em 3 tabelas; a varredura achou `review_log.reviewed_at`
  no mesmo defeito (DEFAULT UTC) e `db.log_review` entrou no fix. Continua dentro dos 3
  arquivos acordados (`review_log` e escrito pelo `db.py`).
- **Sandbox de `test_batch_insert` passou a copiar `app/`:** o CLI `insert_questao.py` agora
  importa o relogio de `app/utils/db.py`; o sandbox que copiava so `tools/insert_questao.py`
  + `card_checks.py` quebrou com `ModuleNotFoundError: app` (2 testes). Copiar `app/` mantem
  o isolamento (o db real segue intocado). Alternativa rejeitada: fallback `datetime.now()`
  se `app` faltar -- seria um segundo caminho de carimbo, exatamente o que o termo 1 do GO
  proibe.
- **Schema (`init_db.py`) mantem `DEFAULT CURRENT_TIMESTAMP`:** remove-lo nao alteraria o
  banco vivo (schema ja criado) e o gate real e o teste estrutural. Registrado, nao tocado.
- **Colateral observado, nao tocado (uma chamada, um bug):** `get_cards_by_bucket` compara
  `fc.due` (local) com `datetime('now', '-48 hours')` (UTC) na janela de erro fresco -- 3h de
  erro numa janela de 48h. Vai para o ledger como sub-achado do F80.
