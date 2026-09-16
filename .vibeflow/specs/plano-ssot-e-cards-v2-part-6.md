---
type: spec
projeto: MedHub
feature: plano-ssot-e-cards-v2
part: 6
slug: plano-ssot-e-cards-v2-part-6
status: ready
relates_to:
  - .vibeflow/prds/plano-ssot-e-cards-v2.md
  - tools/registrar_sessao_bulk.py
  - tools/listas.py
  - app/utils/db.py
---

# Spec -- Parte 6: ledger de listas de exercícios (`sessoes_bulk.tarefa_id` + `tools/listas.py`)

> PRD `plano-ssot-e-cards-v2`, P2. Depende da Parte 2 (tabela `plano_tarefas`). Fecha o critério de sucesso 3 do PRD.

## Objective
Toda sessão registrada aponta para a tarefa do plano (e portanto para o link da lista e o nº previsto), e um comando read-only responde "listas feitas x previstas, com acertos" por bloco UERJ, por semana e por tarefa -- sem ler o Drive.

## Context
`sessoes_bulk` tem 126 sessões (104 com `observacoes` em prosa, 0 com link). `links_exercicios.json` guarda URL e N por tarefa só para S15-S30 da Reta Final; a Parte 1 traz `url_lista`/`n_questoes` do extensivo quando o PDF expõe. O Dashboard do Drive era a única visão "por lista" e vai ser congelado (Parte 8).

## Definition of Done
1. `app/utils/db.py`: `_ensure_sessoes_bulk_tarefa_id(conn)` adiciona a coluna `tarefa_id INTEGER` (idempotente, `ALTER TABLE ... ADD COLUMN` só se ausente -- mesmo padrão de `_ensure_revlog_columns`) e o writer `vincular_sessao_tarefa(sessao_id, tarefa_id)` valida que `plano_tarefas.area == sessoes_bulk.area` (recusa com mensagem se divergir).
2. `tools/registrar_sessao_bulk.py --tarefa ID` grava o vínculo na inserção; `--vincular SESSAO_ID --tarefa ID` vincula uma sessão existente. Flags documentadas na skill dona do CLI (a que o `cli_signature_check` reconhece hoje), espelho regenerado.
3. `tools/listas.py --backfill --dry-run` casa `observacoes` com `plano_tarefas.tema` por normalização (casefold + sem acento + substring exata do tema) e imprime `N casadas / M ambíguas (2+ candidatas) / K sem match`; `--backfill --apply --expect N` grava só as N inequívocas via `vincular_sessao_tarefa`; ambíguas e sem-match ficam `NULL` (**nunca chute**) e saem numa lista para o usuário.
4. `tools/listas.py --progresso [--bloco X] [--semana N]` e `--pendentes` imprimem, por tarefa: `url_lista | q_previstas | feitas | acertos | %` (feitas/acertos = soma das sessões vinculadas), com totais por bloco UERJ e o delta contra o orçamento da Fase 1 (`history/session_183.md §3`); `--json` disponível. Read-only.
5. `tools/test_listas.py` (db sintético): coluna idempotente, recusa por área divergente, backfill com os 3 desfechos (casa / ambígua / sem match), `--expect` errado não grava, progresso soma só sessões vinculadas; registro em `pytest.ini`; `auto_check --changed` PASSED.
6. Craftsmanship: `tools/listas.py` sem `import sqlite3` e sem escrita própria (o backfill grava pelo writer de `db.py`; allowlist de `tools/listas.py` = vazia, e `app/utils/db.py` ganha `sessoes_bulk`); zero Unicode proibido.

## Scope
`app/utils/db.py`, `tools/registrar_sessao_bulk.py`, `tools/listas.py`, `tools/test_listas.py`, `pytest.ini`, skill dona de `registrar_sessao_bulk.py` + `/engenharia-cli` (entrada de `listas.py`) -- se isso passar de 6 arquivos com os espelhos, os espelhos são gerados e não contam no orçamento (build artifacts).

## Anti-scope
Sem alterar `registrar()` (idempotência e validação de área continuam iguais; `--tarefa` é opcional e só adiciona o vínculo). Sem inferir conclusão de tarefa a partir do vínculo (concluir é `plano.py --concluir`, decisão do usuário/agente). Sem painel (Parte 7). Sem tocar `taxonomia_cronograma.questoes_realizadas` (que não é SSOT de volume, e segue não sendo).

## Technical Decisions
- **Vínculo N:1 sessão -> tarefa em `sessoes_bulk`, não tabela ponte**: uma sessão registra uma lista; quando um bloco cobre 2 listas, são 2 sessões (já é a prática: "Bloco Diarreia", "Lista Urologia T I").
- **Backfill por substring do tema, não fuzzy**: a s183 mediu que 54/735 nomes divergem entre fontes; fuzzy compraria falso vínculo em tema homônimo (Pneumonias na Infância x Pneumonias Bacterianas). Ambíguo = humano decide.
- **`feitas/acertos` sempre derivados de `sessoes_bulk`** (SSOT volumétrico, AGENTE §6); `plano_tarefas` não carrega contagem própria.

## Applicable Patterns
- `db-access-layer.md`, `error-insertion-pipeline.md` (mesmo rito de COUNT-ASSERT).

## Risks
- Sessões de simulado (`area='Simulado'`) não têm tarefa: ficam `NULL` por regra, e `--progresso` as lista à parte como "termômetros".
- Coluna nova em tabela SSOT: `test_init_db_schema` precisa continuar verde (db do zero nasce com a coluna).

## Dependencies
- .vibeflow/specs/plano-ssot-e-cards-v2-part-2.md
