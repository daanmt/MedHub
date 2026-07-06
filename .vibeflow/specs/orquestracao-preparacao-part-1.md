# Spec: Orquestracao da Preparacao -- Part 1: Posicao SSOT no db + registro acumulativo

> Gerado via /vibeflow:gen-spec em 2026-07-05, a partir de `.vibeflow/prds/orquestracao-preparacao.md` (Onda 1).
> Encoding ASCII limpo. Budget: <= 6 arquivos.

## Objetivo

A posicao no cronograma (semana de conteudo) vira estado de primeira classe no `ipub.db` -- lida por todo CLI, alterada por comando explicito, NUNCA mais parseada de texto; e o registro de volume aceita 2o bloco da mesma area/sessao sem falsear `sessao_num`.

## Contexto

`day_plan.py::_semana_conteudo()` le a semana por REGEX sobre HANDOFF/ESTADO (marca "Proxima = SNN") -- quebrada NESTE momento ("Proximo: S12" nao casa) com fallback silencioso para a semana nominal-por-data, que assume preparacao em dia. O operador reensina a posicao repetidas vezes (decisao 2026-07-05: inaceitavel). `registrar_sessao_bulk.py:56-65` bloqueia 2o bloco da mesma (sessao, area) -- a s109 falseou `sessao_num=110` para nao perder 42q (F22).

## Definition of Done

1. [ ] `python tools/preparacao.py --set-semana 12 --fonte operador` grava a posicao em `ipub.db` (tabela nova `preparacao_estado`, key-value com `atualizado_em` e `fonte`); `--show` exibe; um processo NOVO (boot frio) le a mesma posicao. Teste standalone cobre o roundtrip em copia temp do db (padrao test_revisao_calibrada: NUNCA tocar o db real).
2. [ ] `day_plan.py` obtem a semana de conteudo do db (via funcao em `app/utils/db.py`); a regex `_semana_conteudo` vira fallback que, QUANDO usado, emite `[WARN] POSICAO_VIA_TEXTO (deprecado)`; a semana nominal-por-data deixa de ser fallback silencioso e vira sinal comparativo exposto no plano (`atraso/adiantamento: nominal SNN vs conteudo SNN`).
3. [ ] `day_plan.py --handoff-block` EMITE a linha de posicao derivada (ex.: `Posicao: conteudo S12 (nominal S13, atraso 1) [derivado: preparacao_estado]`) -- a posicao passa a ser SAIDA do sistema, nunca input textual.
4. [ ] `auto_check.py` ganha check `POSICAO_DRIFT` (WARN, politica s106/107): dispara quando o HANDOFF cita uma semana ("S<NN>" no bloco de estado) divergente da posicao do db; silencio quando coerente ou quando o db nao tem posicao registrada. Roda em `--all` e quando HANDOFF esta no diff.
5. [ ] `registrar_sessao_bulk.py --acumular` SOMA `questoes_feitas`/`questoes_acertadas` na linha existente de (sessao_num, area) e concatena `--obs`; sem a flag, o aviso anti-duplo atual permanece byte-identico; a taxonomia recebe apenas o delta (sem dupla contagem). Flag opcional `--semana N` atualiza a posicao no ato do registro (mesmo caminho do preparacao.py).
6. [ ] Craftsmanship: `import sqlite3` continua confinado (novas queries em `app/utils/db.py`; `tools/preparacao.py` importa `db.py` como o `day_plan` faz); encoding ASCII nos arquivos tocados; `pytest` na raiz verde (novo teste integrado ao bridge F12), scripts standalone preservados, `auto_check --staged` verde; sem as flags novas, TODOS os CLIs byte-identicos.

## Escopo

- `app/utils/db.py`: `CREATE TABLE IF NOT EXISTS preparacao_estado` (chave TEXT PK, valor TEXT, atualizado_em TIMESTAMP, fonte TEXT) + `get_preparacao(chave)` / `set_preparacao(chave, valor, fonte)` + `get_semana_conteudo()` tipada.
- `tools/preparacao.py` (NOVO CLI): `--set-semana N [--fonte X]`, `--show`. Argparse padrao tools/, prints legiveis, ASCII.
- `tools/day_plan.py`: `_cronograma_hoje` le db-first; regex rebaixada a fallback com WARN; sinal nominal-vs-conteudo; linha de posicao no `--handoff-block`.
- `tools/registrar_sessao_bulk.py`: `--acumular` (UPDATE somando) + `--semana N` opcional.
- `tools/auto_check.py`: check `POSICAO_DRIFT` (WARN).
- `tools/test_preparacao.py` (NOVO): roundtrip posicao (db temp) + acumular (db temp) + POSICAO_DRIFT (fixture HANDOFF divergente) + regressao do fallback.

## Anti-escopo

- NADA de recomendador (part-2), pre-bloco/reincidencia (part-3), batch/status (part-4).
- Nao remover a regex nesta part (so rebaixar com WARN) -- remocao quando a base zerar (WARN->BLOCK).
- Nao tocar schema de tabelas existentes; `preparacao_estado` e a UNICA tabela nova.
- Nao popular a posicao automaticamente por inferencia de volume (a fonte e comando explicito/registro; inferencia e sinal, nao escrita).

## Decisoes tecnicas

- **Tabela key-value dedicada** (`preparacao_estado`) em vez de coluna em `taxonomia_cronograma`: grade (estrutura) e estado (posicao) nao se misturam; a tabela serve tambem para condicoes do dia (part-2) sem novo schema. Trade-off: mais um JOIN-zero (leitura pontual) -- irrelevante.
- **Comando explicito > inferencia**: derivar posicao do volume registrado por area e impreciso (grade e por semana/tema; volume e por area). O operador/coordenador declara a mudanca de semana (1 comando, ou junto do registro de volume); o sistema PERSISTE e nunca esquece. O nominal-por-data vira o comparativo que detecta atraso.
- **`--acumular` opt-in** preserva a guarda anti-duplo por default (a protecao original tem valor; o caso novo e explicito). UPDATE na linha existente evita chave nova e mantem 1 linha por (sessao, area).
- **WARN antes de BLOCK** (politica s106/107) para `POSICAO_DRIFT` e para o fallback da regex.

## Padroes aplicaveis

- `db-access-layer.md` (conexao helper, write com commit/close, tools/ standalone como excecao historica -- o CLI novo usa db.py).
- `agent-workflow-protocol.md` (HANDOFF como saida derivada -- extensao do precedente F6/`--handoff-block`).
- Precedente de codigo: `check_session_pointer` no auto_check (F1, ciclo 1) e o molde do `POSICAO_DRIFT`.

## Riscos (premortem)

- **Regex do POSICAO_DRIFT gerar falso-positivo** (HANDOFF cita "S12" em outro contexto, ex. "questoes da S12"): mitigar ancorando o match ao padrao do bloco de estado ("Proximo: S12" / "conteudo S12") e testando com o HANDOFF real atual como fixture.
- **Dupla contagem na taxonomia via --acumular**: o UPDATE do bulk ja incrementa taxonomia; somar de novo duplicaria. Mitigacao: DoD-5 exige delta-only + teste com asserts nos contadores da taxonomia antes/depois.
- **Sessao do coordenador ignorar o comando novo**: mitigado fora do codigo -- o `--handoff-block` emite a posicao e o AGENTE/contrato de fechamento (part-2 toca o contrato) passa a apontar `preparacao.py` como o caminho.

## Dependencies

Nenhuma (primeira part). As parts 2-4 dependem desta.
