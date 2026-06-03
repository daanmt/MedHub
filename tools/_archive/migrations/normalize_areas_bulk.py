#!/usr/bin/env python3
"""
MedHub — Normalização one-shot de rótulos de área em `sessoes_bulk` (sessão 075).

Divergências encontradas na conciliação com a planilha `Dashboard EMED 2026`
(skill /importar-planilha, primeira sessão com acesso ao Google Drive MCP):

    'GO'          → 'Ginecologia'   (sessão 071, Úlceras Genitais — registrada
                                     antes de AREAS_VALIDAS existir)
    'Obstetricia' → 'Obstetrícia'   (migração histórica gravou sem acento;
                                     AREAS_VALIDAS usa a forma acentuada)

Ambos os rótulos quebram agregações por área (fragmentam o GROUP BY) e não
passam na validação de `registrar_sessao_bulk.AREAS_VALIDAS`.

Modos:
    python tools/normalize_areas_bulk.py --dry-run   → mostra UPDATEs sem gravar
    python tools/normalize_areas_bulk.py --apply     → backup + aplica

Backup-first: usa tools/backup_db.py antes de gravar.
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

RENAMES = {
    "GO": "Ginecologia",
    "Obstetricia": "Obstetrícia",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Simula sem gravar")
    mode.add_argument("--apply", action="store_true", help="Backup + aplica UPDATEs")
    args = parser.parse_args()

    if args.apply:
        from tools.backup_db import backup
        if backup() is None:
            sys.exit(1)

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    total = 0
    for old, new in RENAMES.items():
        rows = cur.execute(
            "SELECT id, sessao_num, questoes_feitas, questoes_acertadas "
            "FROM sessoes_bulk WHERE area = ?", (old,)
        ).fetchall()
        for r in rows:
            print(f"  {'[dry-run] ' if args.dry_run else ''}id={r[0]} sessao={r[1]} "
                  f"({r[2]}q/{r[3]}a): {old!r} -> {new!r}")
        # colisão (old.sessao_num, new) já existente quebraria a chave lógica
        for r in rows:
            clash = cur.execute(
                "SELECT COUNT(*) FROM sessoes_bulk WHERE sessao_num = ? AND area = ?",
                (r[1], new)).fetchone()[0]
            if clash:
                print(f"  [ABORT] (sessao={r[1]}, area={new!r}) já existe — resolver manualmente.")
                conn.close()
                sys.exit(1)
        if not args.dry_run:
            cur.execute("UPDATE sessoes_bulk SET area = ? WHERE area = ?", (new, old))
        total += len(rows)

    if args.dry_run:
        print(f"\n[dry-run] {total} linha(s) seriam atualizadas. Nada gravado.")
    else:
        conn.commit()
        print(f"\n[OK] {total} linha(s) atualizadas.")
    conn.close()


if __name__ == "__main__":
    main()
