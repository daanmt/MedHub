# Spec: Onda B · Part 3 — Backfill dos Cards Legados + Aposentar a Heurística

> Gerado via /vibeflow:gen-spec em 2026-06-03
> PRD: `.vibeflow/prds/onda-b-flashcards-metacognitivos.md`
> Split: part 3 de 3. Ver part-1 (contrato), part-2 (persistência).

## Objective

Regenerar os cards legados de baixa qualidade — pelo agente, seguindo o contrato da part-1 e persistindo via o caminho de UPDATE da part-2 — e aposentar a geração heurística, fechando o ciclo de qualidade dos flashcards.

## Context

Há ~200+ erros em `questoes_erros` cujos cards foram cunhados pela heurística (muitos `needs_qualitative=1`). Com a régua (part-1) e o UPDATE in-place (part-2) prontos, o agente pode reprocessá-los um a um, ancorado em `questoes_erros` + resumo (RAG local), preservando o estado FSRS. Os geradores heurísticos (`regenerate_cards.py`, `regenerate_cards_llm.py`, 421 linhas) deixam de ter função e devem sair.

## Definition of Done

1. Existe `tools/cards_regen_queue.py`: CLI **read-only** que emite, em JSON, os erros com cards a regenerar (default: `needs_qualitative=1`), incluindo o registro de `questoes_erros` (campos metacognitivos) + os cards atuais (`card_id` + campos) — para o agente reprocessar. Suporta filtros `--area`/`--limit` (priorizar áreas fracas).
2. Existe um fluxo documentado (skill ou seção em `estilo-flashcard.md`/`revisar` companion) de como o agente: lê a fila → cunha cards atômicos pela régua (part-1) → persiste via `update_flashcard_fields` (cards existentes) e/ou `--cards-file` (cards novos do mesmo erro).
3. Um lote-piloto real (≥1 erro, ex.: #211) é regenerado de ponta a ponta pelo fluxo, e os cards resultantes passam na régua da part-1 (verificável).
4. `tools/regenerate_cards.py` e `tools/regenerate_cards_llm.py` são removidos; nenhuma referência viva resta (workflows/skills/docs atualizados).
5. A função heurística `_invert_elo_to_question` (e correlatas) em `insert_questao.py` é removida ou neutralizada, já que o agente passa a fornecer os campos sempre.
6. **(Quality gate)** Nenhuma referência órfã aos arquivos removidos (grep limpo em `.agents/`, `.claude/`, `tools/`, `app/`); `MEMORY.md`/`AGENTE.md`/`index.md` que citem os geradores são corrigidos; `cards_regen_queue.py` segue convenções de CLI (argparse, UTF-8, sem `sqlite3` novo — consome `db.py`).

## Scope

- `tools/cards_regen_queue.py` (novo) — fila de regeneração read-only em JSON.
- Documentação do fluxo de backfill (em `estilo-flashcard.md` ou skill dedicada).
- Remover `tools/regenerate_cards.py` + `tools/regenerate_cards_llm.py`.
- Limpar `_invert_elo_to_question` e referências em `insert_questao.py`.
- Corrigir referências órfãs em docs (`AGENTE.md` §7.4, `index.md`, etc.).

## Anti-scope

- Reprocessar TODOS os 200+ erros nesta spec (apenas habilitar o fluxo + piloto; o backfill em massa é trabalho contínuo do agente, priorizado por áreas fracas).
- FSRS fiel (Onda A part-2), Google MCP (Onda C), Streamlit (Onda D).
- Mudança de schema.

## Technical Decisions

- **Backfill é trabalho do agente, não script.** Coerente com a tese agent-first: o código só fornece a fila (`cards_regen_queue.py`) e o caminho de escrita (part-2); a *geração* é do agente pela régua. Por isso a heurística sai inteira — não é "melhorada".
- **Piloto antes de massa.** DoD #3 exige um erro regenerado de ponta a ponta para validar o fluxo; o volume restante é incremental (priorizado por áreas fracas via `--area`), evitando big-bang.
- **Remoção, não arquivamento, dos geradores heurísticos.** Já há histórico em git; manter `regenerate_cards*.py` só geraria confusão sobre qual caminho é canônico.

## Applicable Patterns

- `db-access-layer.md` — `cards_regen_queue.py` consome `db.py`, sem `sqlite3` novo.
- `error-insertion-pipeline.md` — o fluxo de backfill respeita o pipeline canônico (persistência via part-2).
- `agent-workflow-protocol.md` — fluxo documentado como skill/contrato (§7.2).

## Risks

- **Regenerar em massa sem revisão** degradar a base → piloto obrigatório (DoD #3) + a régua falsificável (part-1) como gate; o usuário dá feedback ao longo.
- **Referências órfãs** após remover os geradores → DoD #6 com grep limpo.
- **Perda de cards "armadilha" úteis** ao trocar a estrutura → o UPDATE preserva `card_id`; cards que viram conteúdo atômico mantêm seu FSRS.

## Dependencies

- `.vibeflow/specs/onda-b-flashcards-part-1.md` (régua)
- `.vibeflow/specs/onda-b-flashcards-part-2.md` (persistência: `--cards-file` + `update_flashcard_fields`)
