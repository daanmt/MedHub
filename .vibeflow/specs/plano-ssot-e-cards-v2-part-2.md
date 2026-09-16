---
type: spec
projeto: MedHub
feature: plano-ssot-e-cards-v2
part: 2
slug: plano-ssot-e-cards-v2-part-2
status: ready
relates_to:
  - .vibeflow/prds/plano-ssot-e-cards-v2.md
  - app/utils/db.py
  - tools/plano.py
  - .claude/commands/engenharia-cli.md
---

# Spec -- Parte 2: tabela `plano_tarefas` + semeadura + listagem

> PRD `plano-ssot-e-cards-v2`, P1 (segunda metade). Depende da Parte 1.

## Objective
O plano de estudo passa a existir como dado no `ipub.db` (`plano_tarefas`), semeado das três fontes (extensivo, Reta Final pendente, tarefas custom) com o status inicial do Dashboard marcado como aproximado, e consultável por CLI.

## Context
Hoje o "plano" é a soma de `grade.json` (calendário do PDF), `preparacao_estado.cronograma_conclusao_drive` (snapshot de 26/07) e a cabeça do usuário. A s183 mediu: Dashboard = 707 tarefas do extensivo, 178 feitas, flag aproximada por confissão do usuário. A Parte 1 entrega `grade_extensivo.json`; a Reta Final S17-S28 pendente já foi computada (139 tarefas / 4.036q, `history/session_183.md §3`); as tarefas custom são 7 resumos MFC-UERJ + 8 temas sem resumo + termômetros INEP.

## Definition of Done
1. `app/utils/db.py` ganha `_ensure_plano_table(conn)` (padrão `preparacao_estado`) criando `plano_tarefas(id PK, fonte CHECK IN ('extensivo','rf','custom'), ref_semana_fonte INT, tarefa_fonte INT, semana_plano INT, ordem INT, area TEXT, tema TEXT, tipo TEXT, tipo_norm TEXT, url_lista TEXT, q_previstas REAL, status CHECK IN ('pendente','feita','cortada') DEFAULT 'pendente', data_conclusao TEXT, sessao_bulk_id INT, origem_conclusao TEXT, nota TEXT, criado_em TEXT, atualizado_em TEXT, UNIQUE(fonte, ref_semana_fonte, tarefa_fonte))` e os writers `plano_upsert_tarefas(rows)` e `plano_listar(filtros)`; `area` validada por `app/utils/areas.validar_area` (F89) -- área fantasma é recusada.
2. `python tools/plano.py --semear --dry-run` imprime o COUNT-ASSERT por fonte (extensivo S21-S48 = 425; rf = 139 pendentes S17-S28; custom = N do arquivo `core/cronograma/plano_custom.json`) e `--semear --apply --expect N` grava exatamente N linhas (recusa se N difere, exit 2); idempotente (2ª execução = 0 inseridas, atualizações só em campos declarados).
3. Status inicial: tarefa do extensivo cuja (disciplina, assunto, tipo) casa uma linha `Realizada? = Sim` do snapshot do Dashboard (`core/cronograma/dashboard_snapshot.json`, exportado da leitura via MCP da s183) nasce `status='feita'`, `origem_conclusao='dashboard_2026-09-10'`; todas as outras `pendente`; **nenhuma linha nasce `feita` por inferência** (sem match = pendente). Teste com fixture cobre os 3 casos (match exato, variante de nome sem match, tipo diferente).
4. `python tools/plano.py --listar [--semana N] [--bloco MFC|PED|CIR|GO|CM] [--status pendente|feita|cortada] [--fonte ...]` imprime tabela e `--json` -- read-only.
5. `tools/test_plano.py` (db sintético em tmp; asserts nativos) + registro em `pytest.ini`; `tools/test_writer_allowlist.py` lista `tools/plano.py` -> `{plano_tarefas}` e `app/utils/db.py` ganha `plano_tarefas`; `auto_check --changed` PASSED.
6. Craftsmanship: `tools/plano.py` não importa `sqlite3` (toda escrita via `db.py`); flags documentadas em `/engenharia-cli` (D5); zero LaTeX/setas Unicode.

## Scope
- `app/utils/db.py` (tabela + 2 funções).
- `tools/plano.py` (`--semear`, `--dry-run`, `--apply`, `--expect`, `--listar`, `--semana`, `--bloco`, `--status`, `--fonte`, `--json`).
- `core/cronograma/plano_custom.json` (tarefas custom, editável à mão: MFC-UERJ, temas sem resumo, termômetros INEP) e `core/cronograma/dashboard_snapshot.json` (as 707 linhas com `Realizada?`, exportadas na s183 -- dado, não código).
- `tools/test_plano.py`, `pytest.ini`, `tools/test_writer_allowlist.py`, `.claude/commands/engenharia-cli.md` (+ espelho).

## Anti-scope
Sem `--concluir/--cortar/--mover/--revisar-area` (Parte 3). Sem ligação com `day_plan.py` (Parte 4). Sem tocar `taxonomia_cronograma`, `sessoes_bulk` (Parte 6), FSRS ou `review_log`. Sem leitura do Drive em runtime: o snapshot é arquivo versionado da s183.

## Technical Decisions
- **`semana_plano` semeada pelo agente, não pelo PDF**: Fase 1 (semanas 1-7 até 01/11) recebe a RF pendente ordenada por bloco UERJ (MFC/PED/CIR/GO primeiro, CM dirigida, cauda `cortada`), Fase 2 (semanas 8+) recebe o extensivo S21-S48 com Preventiva/APS puxada para a frente -- a regra vive em `core/cronograma/plano_regras.json`? **Não**: v0 grava a ordem como dado semeado por uma função `ordenar_fase1()/ordenar_fase2()` testada; regra em JSON viria depois se a ordem precisar mudar sem código.
- **UNIQUE(fonte, ref_semana_fonte, tarefa_fonte)** torna a semeadura idempotente e permite re-rodar após um `--rebuild-extensivo`.
- **`q_previstas` = `n_questoes` da lista quando declarado, senão média por tipo medida no PDF (43 q/lista)**, com `nota='q_estimada'` -- o número derivado nunca se passa por medido.
- **Status inicial via snapshot versionado, não via MCP**: a Cláusula 5b do `cronograma-contract` proíbe passo de boot que dependa do Drive; a semeadura roda uma vez, com dado congelado e auditável.

## Applicable Patterns
- `db-access-layer.md`: writers em `db.py`; o CLI é camada fina.
- `error-insertion-pipeline.md`: COUNT-ASSERT + dry-run + `--expect` (mesmo rito do `cards_prune.py`).
- `warn-first-check.md`: nenhuma regra nova de harness nesta parte.

## Risks
- Nome de assunto divergente entre PDF e Dashboard (54/735 na s183) -> status nasce `pendente` e a revisão por área (Parte 3) corrige; o número de não-casados é impresso no `--semear`.
- Duplicata entre RF pendente e extensivo (mesmo tema em ambas as fontes) é esperada e legítima (fontes diferentes); a Parte 4 escolhe qual servir por `semana_plano`.

## Dependencies
- .vibeflow/specs/plano-ssot-e-cards-v2-part-1.md
