---
tags: [sqlite, db, data-access, ipub, queries, pandas]
modules: [app/utils/db.py, tools/]
applies_to: [services, handlers, scripts]
confidence: inferred
status: active
canonical_source: app/utils/db.py module docstring
last_verified: 2026-08-25
---
# Pattern: DB Access Layer

<!-- vibeflow:auto:start -->
## What
All SQLite access is funneled through `app/utils/db.py`. Pages and components never import `sqlite3` directly — they call typed functions that return DataFrames or dicts. Standalone CLI tools (`tools/`) have their own connections as authorized exceptions. `app/engine/` wraps `db.py` for agent consumers, adding RAG and graceful error handling.

## Where
- `app/utils/db.py` — the sole authorized DB module in the app layer (see its module docstring for the full contract)
- `app/engine/` — domain API layer that wraps db.py calls for external agents; agents import `app.engine`, not `app.utils.db` directly
- `tools/insert_questao.py` — standalone CLI with its own connection (authorized exception)
- `tools/audit_*.py`, `tools/fsrs_queue.py` — standalone CLIs (authorized exception)

## The Pattern

**Connection helper:**
```python
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'ipub.db')

def get_connection():
    return sqlite3.connect(DB_PATH)
```

**Read function (returns DataFrame):**
```python
def get_db_metrics():
    conn = get_connection()
    df = pd.read_sql('''
        SELECT area AS "Área",
               SUM(questoes_realizadas) AS "Total",
               SUM(questoes_acertadas)  AS "Acertos"
        FROM taxonomia_cronograma
        GROUP BY area
        HAVING SUM(questoes_realizadas) > 0
    ''', conn)
    conn.close()
    # Post-process in Python, not SQL
    if df.empty:
        return {'total_questoes': 0, 'total_acertos': 0, 'media_desempenho': 0.0, 'df_areas': df}
    df['Desempenho'] = (df['Acertos'] / df['Total'] * 100).round(1)
    return {'total_questoes': int(df['Total'].sum()), ..., 'df_areas': df}
```

**Write function (cursor + commit):**
```python
def update_cronograma_status(row_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE cronograma_progresso SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        (new_status, row_id)
    )
    conn.commit()
    conn.close()
```

**Read-write function (FSRS update):** `record_review(flashcard_id, rating, selection_reason=None)`
now delegates to an optimistic-lock helper (`_aplicar_review`) that raises `ConcurrentReviewError`
on a race rather than silently overwriting — see `record_review()` in `app/utils/db.py` for the
current implementation; do not copy an inline example here, it will rot (db.py is 1000+ lines
and this function has changed shape twice since this pattern was written).

**UPSERT pattern (fsrs_cache_cards):**
```python
conn.execute('''
    INSERT INTO preparacao_estado (chave, valor, atualizado_em, fonte)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(chave) DO UPDATE SET
        valor = excluded.valor, atualizado_em = excluded.atualizado_em, fonte = excluded.fonte
''', (chave, str(valor), datetime.now().isoformat(timespec="seconds"), fonte))
```
(`set_preparacao()` in `db.py` — idempotent key-value upsert. `fsrs_cache_cards`/
`get_cache_due_count()` from an earlier version of this pattern no longer exist — removed
with the pre-P3 cache layer.)

## Rules
- `import sqlite3` only in `app/utils/db.py` and standalone CLI tools — never in pages
- Every function: `conn = get_connection()` → work → `conn.close()` (explicit, always)
- `conn.commit()` before `conn.close()` on any write
- Use `pd.read_sql(..., conn, params=(...))` for parameterized reads — never string interpolation in SQL
- Use `cursor.execute('... WHERE x = ?', (value,))` for writes — never f-strings in SQL
- Post-process results in Python (filtering, sorting, ratio calculation) — keep SQL simple
- Return typed values: `pd.DataFrame`, `dict`, `int`, `bool` — not raw cursor rows to callers
- `try/except` in count functions that might fail on empty tables — return safe default (0 or [])

## Examples from this codebase

Line-number citations rot as `db.py` grows (now 1000+ lines, was ~150 when this pattern was
written) — find functions by name instead: `get_connection()`, `get_db_metrics()`,
`update_cronograma_status()`, `record_review()`, `set_preparacao()`. See the module docstring
at the top of `app/utils/db.py` for the current contract.
<!-- vibeflow:auto:end -->

## Anti-patterns
- `import sqlite3` outside `app/utils/db.py` or an authorized standalone CLI — there is no UI layer anymore (Streamlit was removed, see `AGENTE.md`); every `app/` caller goes through `db.py`
- String interpolation in SQL: `f"SELECT * WHERE id = {user_id}"` — SQL injection risk
- Forgetting `conn.close()` — SQLite WAL mode won't release the file lock
- Returning raw cursor rows from db.py functions — callers would depend on positional column order
