---
tags: [fsrs, spaced-repetition, flashcards, streamlit, sqlite, scheduling]
modules: [app/pages/, app/utils/]
applies_to: [pages, handlers, scripts]
confidence: inferred
---
# Pattern: FSRS Review Flow

<!-- vibeflow:auto:start -->
## What
Full spaced-repetition flow: load due cards from SQLite, render front/back with structured fields, record 4-button rating, compute next interval via FSRS v4 simplified, and persist state. Used in both Streamlit (`2_estudo.py`) and CLI (`tools/review_cli.py`).

## Where
- `app/pages/2_estudo.py` — tab2 (FSRS Player)
- `app/utils/db.py` — `record_review()`, `get_due_cards_count()`, `get_next_due_card()`
- `app/utils/fsrs.py` — FSRS class with `init_card()` and `evaluate()`
- `tools/review_cli.py` — CLI interface for reviews

## The Pattern

**Loading due cards (Streamlit, with caching):**
```python
@st.cache_data(ttl=60)
def load_flashcards():
    if not os.path.exists(DB_PATH): return []
    c = sqlite3.connect(DB_PATH).cursor()
    c.execute('''
        SELECT f.id, f.frente, f.verso, t.area, t.tema, c.state,
               f.frente_contexto, f.frente_pergunta, f.verso_resposta,
               f.verso_regra_mestre, f.verso_armadilha
        FROM flashcards f
        LEFT JOIN taxonomia_cronograma t ON f.tema_id = t.id
        JOIN fsrs_cards c ON f.id = c.card_id
        WHERE (c.due <= datetime('now') OR c.state = 0)
          AND f.needs_qualitative < 2
    ''')
    rows = c.fetchall()
    return [{"id": r[0], ..., "frente_contexto": r[6], ...} for r in rows]
```

**Structured vs legacy render decision:**
```python
use_structured = bool(
    card.get('frente_pergunta') and card['frente_pergunta'].strip() and
    card.get('verso_resposta') and card['verso_resposta'].strip()
)

if not st.session_state.fc_verso:
    if use_structured:
        if card.get('frente_contexto') and card['frente_contexto'].strip():
            st.caption(card['frente_contexto'])
        st.markdown(f'<div style="background:#11161D; border:1px solid #202A36; '
                    f'padding:20px; border-radius:12px; font-size:1.1rem;">'
                    f'{card["frente_pergunta"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div ...>{card["frente"]}</div>', unsafe_allow_html=True)
```

**Rating buttons (4 columns):**
```python
b1, b2, b3, b4 = st.columns(4)
if b1.button("Novamente", width='stretch'): _avancar(1)  # Again
if b2.button("Difícil (1d)", width='stretch'): _avancar(2)  # Hard
if b3.button("Bom (3d)", width='stretch'): _avancar(3)   # Good
if b4.button("Fácil (7d)", width='stretch'): _avancar(4)  # Easy
```

**Advance + record (deduped by session_state):**
```python
def _avancar(rating):
    if rating > 0:
        if 'reviewed_ids' not in st.session_state:
            st.session_state.reviewed_ids = set()
        if card['id'] not in st.session_state.reviewed_ids:
            record_review(card['id'], rating)
            st.session_state.reviewed_ids.add(card['id'])
    st.session_state.fc_idx += 1
    st.session_state.fc_verso = False
    if st.session_state.fc_idx >= total:
        st.cache_data.clear()
        st.session_state.pop('fc_order', None)
        st.session_state.pop('reviewed_ids', None)
    st.rerun()
```

**`record_review()` in db.py:**
```python
def record_review(flashcard_id, rating):
    conn = get_connection()
    cursor = conn.cursor()
    df = pd.read_sql("SELECT * FROM fsrs_cards WHERE card_id = ?", conn, params=(flashcard_id,))
    if df.empty:
        fsrs = FSRS()
        card_data = fsrs.init_card()
        card_data['card_id'] = flashcard_id
    else:
        card_data = df.iloc[0].to_dict()
    fsrs = FSRS()
    new_metrics = fsrs.evaluate(card_data, rating)
    cursor.execute('''
        UPDATE fsrs_cards
        SET state=?, due=?, stability=?, difficulty=?,
            elapsed_days=?, scheduled_days=?, reps=?, lapses=?, last_review=?
        WHERE card_id=?
    ''', (new_metrics['state'], new_metrics['due'], ..., flashcard_id))
    cursor.execute('''
        INSERT INTO fsrs_revlog (card_id, rating, state, due, stability, ...)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (...))
    conn.commit()
    conn.close()
    return new_metrics
```

**FSRS v4 algorithm (simplified):**
```python
class FSRS:
    DEFAULT_W = [0.4, 0.6, 2.4, 5.8, 4.93, 0.94, 0.86, 0.01, 1.49, ...]

    def evaluate(self, card, rating):
        # rating: 1=Again, 2=Hard, 3=Good, 4=Easy
        if state == 0:  # New card
            stability = self.w[rating - 1]
            difficulty = self.w[4] - (rating - 3) * self.w[5]
            state = 1  # → Learning
        else:
            if rating == 1:  # Again
                lapses += 1
                stability = self.w[4] / 2
                state = 1
            else:
                difficulty = max(1, min(10, difficulty - (rating - 3) * 0.5))
                stability = stability * (1 + exp(self.w[6]) * (11 - difficulty) * pow(stability, -0.1))
                state = 2  # → Review
        scheduled_days = max(1, round(stability * 9 / 10))  # 90% retention target
        due = datetime.now() + timedelta(days=scheduled_days)
        return {"state": state, "stability": stability, ..., "due": due}
```

## Rules
- `needs_qualitative < 2` filter: excludes retired cards (value 2) from review queue
- `state = 0` cards always appear in queue (new cards, regardless of `due`)
- Rating 1 = "Novamente" (Again), 2 = "Difícil", 3 = "Bom", 4 = "Fácil" — always 4 buttons
- Deduplication: `reviewed_ids` set in session_state prevents double-recording within a session
- After rating, `cache_data.clear()` reloads the queue so completed cards don't reappear
- FSRS state: 0=New, 1=Learning, 2=Review
- `fsrs_revlog` entry written on every review (audit trail)
- Retention target: 90% (`stability * 9 / 10` interval)

## Examples from this codebase

File: `app/pages/2_estudo.py` (lines 74-184) — complete FSRS player implementation

File: `app/utils/db.py` (lines 105-147) — `record_review()` with FSRS evaluation and dual-table update
<!-- vibeflow:auto:end -->

## Anti-patterns
- Calling `record_review()` twice for the same card in one session — causes duplicate revlog entries; guard with `reviewed_ids` set
- Loading flashcards without `needs_qualitative < 2` filter — shows retired cards
- Skipping `fsrs_revlog` insert — breaks audit trail and FSRS operational audit tool
