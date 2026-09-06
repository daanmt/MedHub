# Hotfix: fsrs-balance-stdout

origin: session
status: partial

## Symptom
Sessao s166 (2026-09-05/06), drenagem do bloco 1 (62 cards) via `python -X utf8 tools/fsrs_queue.py --record <id> --rating <n> --reason <r>` com a saida canalizada para `json.load`. Em 3 de 14 records do sub-bloco 1.1 (cards 788, 1187, 244) o parse falhou com `json.decoder.JSONDecodeError: Expecting value: line 1 column 2 (char 1)`; a gravacao tinha persistido (os cards sumiram da fila). Nos sub-blocos 1.2-1.4 o stdout cru mostrou a causa: uma linha `[FSRS_BALANCE] due 2026-09-13 -> 2026-09-14 (+1d; carga 21 -> 8)` impressa ANTES do objeto JSON `{"recorded": true, ...}` sempre que o balanceador de carga desloca o `due` (cards 381, 823, 1101, 485, 122, 1404, 1475, 1476, 1354, 459, 1472, 1480). O contrato do CLI (`skill /revisar`: "--record ... Imprime {recorded, card_id, rating, next_due, state}") e JSON puro em stdout.

## Checkpoint
hypothesis: `app/utils/db.py::_balancear_due` (linha 359) e o fallback de excecao em `_aplicar_review` (linha 476) usam `print()` sem `file=sys.stderr`; qualquer consumidor que parseia o stdout do `fsrs_queue --record` quebra sempre que o balanceador age (deslocamento != 0) ou pula por excecao.
falsification_test: chamar `_balancear_due` num banco sintetico em que o dia-alvo esta carregado e o vizinho vazio (deslocamento garantido) capturando stdout; se stdout sair vazio na versao atual, a hipotese esta errada.
blind_spots: outros prints no caminho de `record_review` (nao encontrados por grep de `print(` em db.py fora dos dois sitios); consumidores que LEEM a linha informativa do stdout (nenhum encontrado: `tools/fsrs_load.py` calcula a carga por query, nao pelo log).

## Preservation
- A gravacao da revisao (UPDATE `fsrs_cards` + INSERT `fsrs_revlog`) continua acontecendo mesmo quando o balanceamento e pulado por excecao.
- O balanceamento continua movendo apenas o `due`/`scheduled_days` (stability/difficulty intocados) -- suite `tools/test_fsrs_balance.py` (BLOCKING no auto_check) segue verde.
- A informacao do deslocamento continua visivel ao operador (em stderr), nao e silenciada.

## Eliminated / Evidence

## Root cause
`app/utils/db.py::_balancear_due` (informe de deslocamento) e o `except` de `_aplicar_review` (WARN de balanceamento pulado) chamavam `print()` sem `file=sys.stderr`. O CLI `tools/fsrs_queue.py` imprime o resultado do `--record` como JSON em stdout e nao filtra o que a camada de banco escreve antes; qualquer deslocamento do balanceador (ou excecao nele) prefixava o JSON com texto livre.

## Fix
files_changed: app/utils/db.py, tools/test_fsrs_balance_stdout.py (novo), pytest.ini (registro F43)
Os dois `print()` ganharam `file=sys.stderr` (+ `import sys` no modulo). A informacao segue visivel ao operador no terminal; o stdout volta a ser JSON puro. Nenhuma mudanca de logica de agendamento.


## DoD
- [x] `tools/test_fsrs_balance_stdout.py` vermelho antes do fix (stdout = '[FSRS_BALANCE] due 2026-10-06 -> 2026-10-05 ...'), verde depois.
- [x] `_balancear_due` sobre o ipub.db real (read-only, alvo 2026-09-13, carga 22 -> 11): stdout vazio, informe em stderr.
- [x] `python -X utf8 tools/auto_check.py --changed` PASSED (exit 0); `tools/test_fsrs_balance.py` e `tools/test_record_review.py` verdes.

## Regression
WHEN `_balancear_due` recebe um card de revisao (state 2, intervalo 30d) cujo dia-alvo tem 5 cards agendados e os vizinhos nenhum (deslocamento garantido) THEN stdout fica vazio e a linha `[FSRS_BALANCE]` sai em stderr; WHEN `_balancear_due` levanta excecao dentro de `record_review` THEN a revisao e gravada (1 linha no revlog), stdout fica vazio e `[WARN] FSRS_BALANCE` sai em stderr.
test: tools/test_fsrs_balance_stdout.py
oracle_type: specified
reproduction: synthetic
verification: red-green

## Deviations
- `reproduction: synthetic` por politica do projeto (suites nunca tocam o `ipub.db` real); a mesma funcao foi exercitada read-only sobre o banco real apos o fix (DoD 2), sem gravar nada. Por isso `status: partial` e nao `verified`, apesar de red-green + suite verde + gate limpo.
- Colateral NAO corrigido aqui (deferido, vai para o ledger): o balanceador moveu cards para 14/09 -- um dia depois da prova ENAMED (13/09) -- porque nao conhece `core/provas.json`; achado separado.
