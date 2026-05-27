import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / 'ipub.db'

# Tipos corretos por coluna
COLS = [
    ("frente_contexto",    "TEXT"),
    ("frente_pergunta",    "TEXT"),
    ("verso_resposta",     "TEXT"),
    ("verso_regra_mestre", "TEXT"),
    ("verso_armadilha",    "TEXT"),
    ("quality_source",     "TEXT    DEFAULT 'legacy'"),
    ("card_version",       "INTEGER DEFAULT 1"),
    ("needs_qualitative",  "INTEGER DEFAULT 0"),
]

def migrate():
    with sqlite3.connect(DB) as conn:
        existing = {r[1] for r in conn.execute("PRAGMA table_info(flashcards)")}
        for col, coltype in COLS:
            if col in existing:
                print(f"  ~ {col} (ja existe)")
            else:
                conn.execute(f"ALTER TABLE flashcards ADD COLUMN {col} {coltype}")
                print(f"  + {col} {coltype}")
        conn.commit()
    print("Migration OK.")

if __name__ == '__main__':
    migrate()
