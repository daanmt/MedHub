"""
MedHub FSRS Audit — Auditoria Operacional
Verifica o estado real do motor FSRS no ipub.db.
Uso: python Tools/audit_fsrs.py
"""

import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.utils.db import get_connection

STATE_LABELS = {0: "New", 1: "Learning", 2: "Review", 3: "Relearning"}


def main():
    conn = get_connection()

    revlog_count = conn.execute(
        "SELECT COUNT(*) FROM fsrs_revlog"
    ).fetchone()[0]

    nonzero_stability = conn.execute(
        "SELECT COUNT(*) FROM fsrs_cards WHERE stability > 0"
    ).fetchone()[0]

    state_dist = conn.execute(
        "SELECT state, COUNT(*) FROM fsrs_cards GROUP BY state ORDER BY state"
    ).fetchall()
    state_counts = dict(state_dist)

    due_hoje = conn.execute("""
        SELECT COUNT(*) FROM fsrs_cards
        WHERE state > 0
          AND due >= datetime('now','start of day')
          AND due <  datetime('now','start of day','+1 day')
    """).fetchone()[0]

    atrasados = conn.execute("""
        SELECT COUNT(*) FROM fsrs_cards
        WHERE state > 0 AND due < datetime('now','start of day')
    """).fetchone()[0]

    novos = conn.execute(
        "SELECT COUNT(*) FROM fsrs_cards WHERE state = 0"
    ).fetchone()[0]

    top_dues = conn.execute("""
        SELECT fc.card_id, fc.due, fc.stability, COALESCE(t.area,'')
        FROM fsrs_cards fc
        LEFT JOIN flashcards f ON fc.card_id = f.id
        LEFT JOIN taxonomia_cronograma t ON f.tema_id = t.id
        WHERE fc.state > 0
        ORDER BY fc.due ASC
        LIMIT 5
    """).fetchall()

    conn.close()

    print()
    print("=== FSRS — Auditoria Operacional ===")
    print(f"Reviews gravadas (fsrs_revlog):   {revlog_count}")
    print(f"Cards com stability > 0:          {nonzero_stability}")
    print("Distribuição por state:")
    for s in range(4):
        count = state_counts.get(s, 0)
        label = STATE_LABELS.get(s, str(s))
        print(f"  state={s} ({label:<10}):  {count}")
    print(f"Due hoje:                {due_hoje}")
    print(f"Atrasados (due < now):   {atrasados}")
    print(f"Novos remanescentes:     {novos}")

    if top_dues:
        print("Próximas dues (top 5):")
        for r in top_dues:
            due_str = r[1][:10] if r[1] else "?"
            print(f"  card={r[0]:<4}  due={due_str}  stability={r[2]:.2f}  area={r[3]}")
    print()


if __name__ == '__main__':
    main()
