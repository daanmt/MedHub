# Audit Report: Onda B · Part 3 — Backfill + Aposentar a Heurística

**Verdict: PASS**

> Auditado em 2026-06-03 contra `.vibeflow/specs/onda-b-flashcards-part-3.md`.

### DoD Checklist

- [x] **1 — `cards_regen_queue.py` (read-only, JSON).** Emite erros com `needs_qualitative=1` + substrato metacognitivo (`tipo_erro`, `habilidades_sequenciais`, `o_que_faltou`, `alternativa_correta/marcada`, `armadilha_prova`, `enunciado`) + `cards_atuais` (com `card_id`). Filtros `--area`/`--limit`/`--questao-id`. Verificado em #211 → retornou o erro + `[(382,elo_quebrado,1),(383,armadilha,1)]`.
- [x] **2 — Fluxo de backfill documentado.** Seção "Backfill — regenerar cards legados" em `estilo-flashcard.md`: puxar fila → ancorar no resumo (RAG) → cunhar pelos 5 princípios → persistir via `update_flashcard_fields` (existentes) e/ou `--cards-file` (novos) → priorizar áreas fracas, em lotes.
- [x] **3 — Piloto end-to-end.** #211 regenerado: card 382 → "Quais agentes causam úlcera genital?" e card 383 → "Quais agentes causam corrimento/cervicite?", ambos `tipo=conteudo`, `quality_source=qualitative`, `needs_qualitative=0`, `card_version=2`, **FSRS preservado** (`fsrs_cards` idêntico). Conteúdo conforme a régua da part-1 (atômico, distinção/sobreposição Chlamydia L1-L3 vs D-K, armadilha Trichomonas).
- [x] **4 — Geradores removidos.** `tools/regenerate_cards.py` + `regenerate_cards_llm.py` deletados (`git rm`). Grep `--include=*.py` em `tools/app/.claude/.agents` → limpo.
- [x] **5 — Heurística neutralizada.** `_invert_elo_to_question` + `_extract_key_term` removidas de `insert_questao.py`; fallback do ramo legado simplificado para default não-heurístico. `py_compile` OK.
- [x] **6 — (Quality) Sem órfãos + convenções.** Referências corrigidas: `AGENTE.md §7.4` (→ `cards_regen_queue.py`), `tools/audit_integrity.py:89` (nota atualizada), `README.md:82` (exemplo trocado). Bytecode stale (`__pycache__`, incl. `generate_flashcards.pyc` órfão) limpo. `cards_regen_queue.py` segue convenções de CLI (argparse, UTF-8, consome `app.utils.db` sem `import sqlite3` novo). Única menção remanescente: tombstone intencional em `estilo-flashcard.md` documentando a aposentadoria (não é dependência).

### Pattern Compliance

- [x] **db-access-layer.md** — `cards_regen_queue.py` consome `db.get_connection()`; sem `import sqlite3` novo; queries parametrizadas.
- [x] **error-insertion-pipeline.md** — backfill persiste via `update_flashcard_fields`/`--cards-file` (part-2), respeitando o pipeline canônico.
- [x] **agent-workflow-protocol.md** — fluxo de backfill documentado na skill canônica (§7.2).

### Convention Compliance

- `import sqlite3` não introduzido fora dos autorizados; CLI com argparse + saída UTF-8; pt-BR. Nenhum Don't violado.

### Tests

Sem test runner configurado. DoD #1 e #3 verificados por execução real (fila + piloto com captura de FSRS). `py_compile` OK em todos os arquivos tocados.

### Observação

`ROADMAP.md` (Linha 8) e o pattern `error-insertion-pipeline.md` ainda descrevem os geradores como plano/estado anterior — são docs de planejamento/auto-gerados (fora do escopo de grep do DoD #6); atualizar via `vibeflow:teach` numa passada futura.

### Próximo passo

Ready to ship. Onda B (parts 1-3) completa e auditada.
