---
tags: [sqlite, db, data-access, ipub, queries, pandas]
modules: [app/utils/db.py, tools/]
applies_to: [services, handlers, scripts]
confidence: inferred
---
# Pattern: DB Access Layer

<!-- vibeflow:auto:start -->
## What
All SQLite access is funneled through `app/utils/db.py`. Pages and components never import `sqlite3` directly — they call typed functions that return DataFrames or dicts. The only exception is `tools/insert_questao.py`, which is a standalone CLI.

## Where
- `app/utils/db.py` — the sole authorized DB module in the app layer
- `tools/insert_questao.py` — standalone CLI with its own connection (authorized exception)
- `tools/review_cli.py`, `tools/audit_*.py` — standalone CLIs (authorized exception)

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

**Read-write function (FSRS update):**
```python
def record_review(flashcard_id, rating):
    conn = get_connection()
    cursor = conn.cursor()
    df = pd.read_sql("SELECT * FROM fsrs_cards WHERE card_id = ?", conn, params=(flashcard_id,))
    if df.empty:
        card_data = FSRS().init_card()
        card_data['card_id'] = flashcard_id
    else:
        card_data = df.iloc[0].to_dict()
    new_metrics = FSRS().evaluate(card_data, rating)
    cursor.execute('UPDATE fsrs_cards SET state=?, due=?, ... WHERE card_id=?', (..., flashcard_id))
    cursor.execute('INSERT INTO fsrs_revlog (...) VALUES (...)', (...))
    conn.commit()
    conn.close()
    return new_metrics
```

**UPSERT pattern (fsrs_cache_cards):**
```python
cursor.execute('''
    INSERT INTO fsrs_cache_cards (erro_origem, state, stability, ...)
    VALUES (?, ?, ?, ...)
    ON CONFLICT(erro_origem) DO UPDATE SET
        state=excluded.state, stability=excluded.stability, ...
''', (erro_origem, ...))
```

**Graceful count with try/except:**
```python
def get_cache_due_count() -> int:
    try:
        init_fsrs_cache_tables()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM fsrs_cache_cards WHERE due <= ? AND state > 0",
                       (datetime.now(),))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0  # Safe default — never crash the UI
```

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

File: `app/utils/db.py` (lines 9-10) — connection helper
File: `app/utils/db.py` (lines 12-33) — `get_db_metrics()` read pattern
File: `app/utils/db.py` (lines 62-68) — `update_cronograma_status()` write pattern
File: `app/utils/db.py` (lines 105-147) — `record_review()` read-write with dual INSERT+UPDATE
File: `app/utils/db.py` (lines 217-260) — `record_cache_review()` with UPSERT pattern
File: `app/utils/db.py` (lines 263-277) — `get_cache_due_count()` graceful try/except
<!-- vibeflow:auto:end -->

## Anti-patterns
- `import sqlite3` in a Streamlit page (found in `2_estudo.py` tab1 as legacy fallback — do not replicate)
- String interpolation in SQL: `f"SELECT * WHERE id = {user_id}"` — SQL injection risk
- Forgetting `conn.close()` — SQLite WAL mode won't release the file lock
- Returning raw cursor rows from db.py functions — callers would depend on positional column order
