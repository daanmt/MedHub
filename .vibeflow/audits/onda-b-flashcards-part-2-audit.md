# Audit Report: Onda B · Part 2 — Persistência de N Cards Atômicos + UPDATE in-place

**Verdict: PASS**

> Auditado em 2026-06-03 contra `.vibeflow/specs/onda-b-flashcards-part-2.md`.

### DoD Checklist

- [x] **1 — `--cards-file` insere N cards atômicos.** Teste real: JSON de 2 cards → 2 linhas em `flashcards` (`tipo=conteudo`, `quality_source=qualitative`, `needs_qualitative=0`) + 2 em `fsrs_cards`. Evidência: `insert_questao.py` ramo `if cards is not None` + verificação executada.
- [x] **2 — Sem `--cards-file`, comportamento inalterado.** Teste legado: produziu `('elo_quebrado','heuristic',1)` — idêntico ao original. O bloco antigo foi apenas movido para `else`, sem alteração lógica.
- [x] **3 — `update_flashcard_fields(card_id, fields)` preserva FSRS.** Teste no card real #3: mudou os campos, `card_version` 3→4, `quality_source='qualitative'`/`needs_qualitative=0` setados, `fsrs_cards` **idêntico** (comparação dict completa). Card inexistente → `False`. `db.py`.
- [x] **4 — JSON lido como UTF-8.** `open(args.cards_file, encoding="utf-8")`; conteúdo com acentos (úlcera, é) inserido sem corrupção. Contorna o limite de quoting/unicode inline do PowerShell.
- [x] **5 — (Quality) Pattern + schema.** `update_flashcard_fields` segue `db-access-layer` (`get_connection`→cursor→`commit`→`close`; valores parametrizados; nomes de coluna de allowlist fixo, sem injeção). `insert_questao.py` mantém `import sqlite3` como CLI standalone autorizado. Schema `flashcards` inalterado (`tipo` permanece TEXT). `py_compile` OK em ambos.
- [x] **6 — Teste manual documentado.** Round-trips com captura+restauração executados; zero alteração líquida no `ipub.db` (test-insert e legacy removidos; card #3 restaurado).

### Pattern Compliance

- [x] **error-insertion-pipeline.md** — transação atômica preservada (taxonomia → questao → cards → fsrs_cards → métricas, commit único); o ramo de N cards reusa a mesma engine de inserção/commit.
- [x] **db-access-layer.md** — `update_flashcard_fields` no padrão de escrita; params parametrizados; `conn.close()` explícito.

### Convention Compliance

- `import sqlite3` apenas em `db.py` + CLI standalone (`insert_questao.py`) — respeitado. Sem f-string com input em SQL. Nenhum Don't violado.

### Observações (não-bloqueantes)

- `DeprecationWarning` (datetime adapter, Python 3.12) em `insert_questao.py:157` é **pré-existente** (init de `fsrs_cards` com `datetime.now()`), fora do escopo desta part. Candidato a limpeza futura.

### Tests

Sem test runner configurado. DoD #6 (teste manual) executado com evidência (round-trip + cleanup). Adequado.

### Próximo passo

Ready to ship. Prosseguir para a part-3 (backfill + aposentar heurística).
