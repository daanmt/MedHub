#!/usr/bin/env python3
"""
MedHub — Bankruptcy dos flashcards heurísticos legados (sessão 075).

Decisão (sessão 075): em vez de regenerar os 70 cards heurísticos legados
(`needs_qualitative = 1`, cunhados pela geração heurística aposentada), eles são
**aposentados** — `needs_qualitative = 2` os remove da fila do `/revisar`
(`fsrs_queue` exclui `needs_qualitative >= 2`). Mantém o histórico no banco; só
tira do ciclo de revisão. Supera o caminho de backfill-regeneração de
`estilo-flashcard.md` para estes cards especificamente.

O foco do FSRS passa a ser os 332 cards qualitativos (cunhados pelo agente).

Modos:
    python tools/retire_heuristic_cards.py --dry-run   → conta e mostra sem gravar
    python tools/retire_heuristic_cards.py --apply      → backup + aposenta

Backup-first via tools/backup_db.py.
"""

import argparse
import os
import sqlite3
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

DB = os.path.join(ROOT, "ipub.db")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Conta sem gravar")
    mode.add_argument("--apply", action="store_true", help="Backup + aposenta")
    args = parser.parse_args()

    if args.apply:
        from tools.backup_db import backup
        if backup() is None:
            sys.exit(1)

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    n = cur.execute(
        "SELECT COUNT(*) FROM flashcards WHERE needs_qualitative = 1"
    ).fetchone()[0]
    print(f"  Cards heuristicos legados (needs_qualitative=1): {n}")

    if args.dry_run:
        print(f"\n[dry-run] {n} cards seriam aposentados (needs_qualitative -> 2). Nada gravado.")
    else:
        cur.execute("UPDATE flashcards SET needs_qualitative = 2 WHERE needs_qualitative = 1")
        conn.commit()
        print(f"\n[OK] {n} cards aposentados (needs_qualitative = 2). Excluidos da fila do /revisar.")
    conn.close()


if __name__ == "__main__":
    main()
