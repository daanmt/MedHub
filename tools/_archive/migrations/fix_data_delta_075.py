#!/usr/bin/env python3
"""
MedHub — Correção one-shot de `data_sessao` do delta de Cirurgia (sessão 075).

O delta de +40q (Cirurgia Infantil I — Revisão, 2ª passada) foi importado em
2026-06-03 via `importar_sessoes.py`, mas pela planilha `Dashboard EMED 2026`
as questões foram feitas em **maio** (acumulado de maio = 3.170 já as inclui).
Com `data_sessao = 2026-06-03`, o bloco "custo do mês" do /performance infla
junho com volume que pertence a maio.

Correção: (sessao_num=75, area='Cirurgia') → data_sessao = '2026-05-31'.

Modos:
    python tools/fix_data_delta_075.py --dry-run   → mostra UPDATE sem gravar
    python tools/fix_data_delta_075.py --apply     → backup + aplica
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

SESSAO, AREA = 75, "Cirurgia"
DATA_NOVA = "2026-05-31"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Simula sem gravar")
    mode.add_argument("--apply", action="store_true", help="Backup + aplica UPDATE")
    args = parser.parse_args()

    if args.apply:
        from tools.backup_db import backup
        if backup() is None:
            sys.exit(1)

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT id, questoes_feitas, questoes_acertadas, data_sessao "
        "FROM sessoes_bulk WHERE sessao_num = ? AND area = ?", (SESSAO, AREA)
    ).fetchall()

    if len(rows) != 1:
        print(f"[ABORT] Esperava 1 linha (sessao={SESSAO}, area={AREA!r}), achei {len(rows)}.")
        conn.close()
        sys.exit(1)

    r = rows[0]
    print(f"  {'[dry-run] ' if args.dry_run else ''}id={r[0]} ({r[1]}q/{r[2]}a): "
          f"data_sessao {r[3]!r} -> {DATA_NOVA!r}")

    if not args.dry_run:
        cur.execute(
            "UPDATE sessoes_bulk SET data_sessao = ? WHERE sessao_num = ? AND area = ?",
            (DATA_NOVA, SESSAO, AREA))
        conn.commit()
        print("\n[OK] 1 linha atualizada.")
    else:
        print("\n[dry-run] Nada gravado.")
    conn.close()


if __name__ == "__main__":
    main()
