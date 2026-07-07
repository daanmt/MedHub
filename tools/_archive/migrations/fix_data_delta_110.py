#!/usr/bin/env python3
"""
MedHub -- Correcao one-shot do delta planilha-db achado na sessao 110.

Usuario reportou performance desatualizada (4660 real vs 4584 relatado).
Reconciliacao completa contra a planilha `Dashboard EMED 2026` (Quadro Geral
= 4660q vs sessoes_bulk = 4584q, delta de 76q) via download_file_content +
openpyxl nas 20 abas por disciplina. Achados:

1. MISLABEL -- 'GO' (id=38, sessao=86, 2026-06-20, 30q/27a) e na verdade
   Planejamento Familiar (confirmado por history/session_086.md: "Planej.
   familiar 27/30") -> Ginecologia. Recorrencia do padrao ja corrigido em
   normalize_areas_bulk.py (s075); "GO" voltou a aparecer depois daquele fix.

2. MISLABEL -- 'Clinica Medica' (3 linhas, sessoes 103/104/105, 2026-07-02;
   gap Antigravity sem protocolo de fechamento, ver history/INDEX.md "Gap
   103-105") casam EXATAMENTE (feitas E acertos, digito a digito) com 3
   tarefas da planilha que nao tinham nenhum registro em sessoes_bulk:
     id=64 sessao=103 25q/21a -> Infecto   (Sepse - Teoria I)
     id=65 sessao=104 25q/17a -> Hemato    (Anemias Hemoliticas - Teoria I)
     id=66 sessao=105 20q/10a -> Oftalmo   (Sindrome do Olho Vermelho - Teoria I)
   'Clinica Medica' nao existe como aba na planilha -- confirma mislabel
   (nao dado espurio nem volume fantasma).

Efeito: relabeling nao muda o total (permanece 4584), mas fecha o gap EXATO
de Ginecologia/Infecto/Hemato/Oftalmo contra a planilha (db bate 1:1 nessas
4 areas apos o fix). O residual de 76q fica 100% em Cirurgia (-47q/-40a) e
Ortopedia (-29q/-24a) -- volume real nunca registrado sob nenhum rotulo;
tratado a parte via `registrar_sessao_bulk.py --acumular` (fora deste script).

Modos:
    python tools/fix_data_delta_110.py --dry-run   -> mostra UPDATEs sem gravar
    python tools/fix_data_delta_110.py --apply     -> backup + aplica
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

# (id, sessao_num, old_area, new_area, expected_feitas, expected_acertos)
FIXES = [
    (38,  86, "GO",             "Ginecologia", 30, 27),
    (64, 103, "Clínica Médica", "Infecto",     25, 21),
    (65, 104, "Clínica Médica", "Hemato",      25, 17),
    (66, 105, "Clínica Médica", "Oftalmo",     20, 10),
]


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

    for id_, sessao, old, new, exp_f, exp_a in FIXES:
        row = cur.execute(
            "SELECT id, sessao_num, area, questoes_feitas, questoes_acertadas "
            "FROM sessoes_bulk WHERE id = ?", (id_,)
        ).fetchone()
        if row is None:
            print(f"  [ABORT] id={id_} nao encontrado.")
            conn.close()
            sys.exit(1)
        _, r_sessao, r_area, r_f, r_a = row
        if (r_sessao, r_area, r_f, r_a) != (sessao, old, exp_f, exp_a):
            print(f"  [ABORT] id={id_} nao bate com o esperado "
                  f"(achei sessao={r_sessao} area={r_area!r} {r_f}q/{r_a}a).")
            conn.close()
            sys.exit(1)
        clash = cur.execute(
            "SELECT COUNT(*) FROM sessoes_bulk WHERE sessao_num = ? AND area = ? AND id != ?",
            (sessao, new, id_)).fetchone()[0]
        if clash:
            print(f"  [ABORT] (sessao={sessao}, area={new!r}) ja existe -- resolver manualmente.")
            conn.close()
            sys.exit(1)
        print(f"  {'[dry-run] ' if args.dry_run else ''}id={id_} sessao={sessao} "
              f"({exp_f}q/{exp_a}a): {old!r} -> {new!r}")
        if not args.dry_run:
            cur.execute("UPDATE sessoes_bulk SET area = ? WHERE id = ?", (new, id_))
        total += 1

    if args.dry_run:
        print(f"\n[dry-run] {total} linha(s) seriam atualizadas. Nada gravado.")
    else:
        conn.commit()
        print(f"\n[OK] {total} linha(s) atualizadas.")
    conn.close()


if __name__ == "__main__":
    main()
