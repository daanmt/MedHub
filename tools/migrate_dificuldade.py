"""migrate_dificuldade.py — adiciona as 3 colunas de dificuldade-do-tema.

Parte 1 da Revisão Calibrada (PRD s094 §4.5). Acrescenta a
`taxonomia_cronograma`:
  - dificuldade        INTEGER    (1-10, nullable; NULL = ainda não calibrado)
  - dificuldade_fonte  TEXT       ('usuario' | 'agente_inferida')
  - dificuldade_at     TIMESTAMP  (recência, para reinferir nota envelhecida)

Idempotente: checa PRAGMA antes de cada ADD COLUMN (rodar 2× é seguro).
Local-only — `ipub.db` não vai pro git.

Uso: python tools/migrate_dificuldade.py
"""
import os
import sqlite3
import sys

try:                                   # UTF-8 no console cp1252 do Windows
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ipub.db")

COLUNAS = [
    ("dificuldade", "INTEGER"),
    ("dificuldade_fonte", "TEXT"),
    ("dificuldade_at", "TIMESTAMP"),
]


def main():
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        existing = {r[1] for r in cur.execute("PRAGMA table_info(taxonomia_cronograma)")}
        added = []
        for nome, tipo in COLUNAS:
            if nome in existing:
                print(f"  - {nome}: já existe (skip)")
                continue
            cur.execute(f"ALTER TABLE taxonomia_cronograma ADD COLUMN {nome} {tipo}")
            added.append(nome)
            print(f"  + {nome} {tipo} adicionada")
        conn.commit()
        print(f"Migracao OK - {len(added)} coluna(s) nova(s): {added or '(nenhuma)'}")
        return True
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
