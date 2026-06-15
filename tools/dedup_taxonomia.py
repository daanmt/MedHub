"""dedup_taxonomia.py — colapsa linhas duplicadas (area,tema) em taxonomia_cronograma.

[DESTRUTIVO] Rode `tools/backup_db.py` ANTES. `--dry-run` é o default; `--apply` grava.

Contexto: a taxonomia acumulou duplicatas legadas do mesmo (area,tema) — snapshots
de re-imports (não sessões aditivas). `taxonomia.questoes_realizadas` NÃO é o SSOT de
volume (esse é `sessoes_bulk`), então o merge é cosmético → MAX (não infla).

Algoritmo (1 transação atômica via `with con`, rollback on error):
  1. grupos (area,tema) com COUNT>1, excluindo '[bulk]%' e 'Geral'.
  2. sobrevivente = id com mais filhos (questoes_erros+flashcards); empate -> menor id.
  3. remap FK: questoes_erros.tema_id e flashcards.tema_id -> sobrevivente.
  4. merge das métricas (MAX, default) em qr/qa/ultima_revisao; recomputa percentual.
  5. DELETE perdedores (já sem filhos).
  6. CREATE UNIQUE INDEX ux_taxonomia_area_tema (falha => duplicata restante => rollback).
Verificação (read-only, sempre): grupos_dup==0, órfãos==0, linhas antes/depois.

Uso:
    python tools/dedup_taxonomia.py            # dry-run
    python tools/dedup_taxonomia.py --apply     # grava (merge=max)
"""
import argparse
import os
import sqlite3
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')


def _nchild(cur, tid):
    return (cur.execute("SELECT COUNT(*) FROM questoes_erros WHERE tema_id=?", (tid,)).fetchone()[0]
            + cur.execute("SELECT COUNT(*) FROM flashcards WHERE tema_id=?", (tid,)).fetchone()[0])


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--apply', action='store_true', help='Grava (default: dry-run)')
    ap.add_argument('--merge', choices=['max', 'sum'], default='max',
                    help='Estratégia de merge das métricas (default: max)')
    args = ap.parse_args()
    dry = not args.apply
    agg = 'MAX' if args.merge == 'max' else 'SUM'

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    rows_antes = cur.execute("SELECT COUNT(*) FROM taxonomia_cronograma").fetchone()[0]
    groups = cur.execute("""
        SELECT area, tema, COUNT(*) n, GROUP_CONCAT(id) ids
        FROM taxonomia_cronograma
        WHERE tema NOT LIKE '[bulk]%' AND tema <> 'Geral'
        GROUP BY area, tema HAVING COUNT(*) > 1
        ORDER BY n DESC, area, tema
    """).fetchall()

    print(f"{'(DRY-RUN) ' if dry else ''}{len(groups)} grupos duplicados (merge={args.merge}).\n")

    plano = []
    for area, tema, n, ids in groups:
        id_list = [int(x) for x in ids.split(",")]
        surv = sorted(id_list, key=lambda t: (-_nchild(cur, t), t))[0]
        losers = [t for t in id_list if t != surv]
        qr, qa, ult = cur.execute(
            f"SELECT {agg}(questoes_realizadas), {agg}(questoes_acertadas), MAX(ultima_revisao) "
            f"FROM taxonomia_cronograma WHERE id IN ({','.join('?' * len(id_list))})",
            id_list).fetchone()
        pct = round((qa or 0) / qr * 100, 2) if qr else 0.0
        plano.append((id_list, surv, losers, qr, qa, pct, ult))
        print(f"  {area:12} | {tema[:38]:38} | ids={id_list} surv={surv} "
              f"del={losers} | qr={qr} qa={qa}")

    total_del = sum(len(p[2]) for p in plano)

    if not dry:
        try:
            with con:                                  # commit on success / rollback on raise
                for id_list, surv, losers, qr, qa, pct, ult in plano:
                    ph = ','.join('?' * len(losers))
                    for L in losers:
                        con.execute("UPDATE questoes_erros SET tema_id=? WHERE tema_id=?", (surv, L))
                        con.execute("UPDATE flashcards   SET tema_id=? WHERE tema_id=?", (surv, L))
                    con.execute("UPDATE taxonomia_cronograma SET questoes_realizadas=?, "
                                "questoes_acertadas=?, percentual_acertos=?, ultima_revisao=? WHERE id=?",
                                (qr, qa, pct, ult, surv))
                    con.execute(f"DELETE FROM taxonomia_cronograma WHERE id IN ({ph})", losers)
                con.execute("CREATE UNIQUE INDEX IF NOT EXISTS "
                            "ux_taxonomia_area_tema ON taxonomia_cronograma(area, tema)")
            print(f"\nAPLICADO: {total_del} linhas deletadas; índice UNIQUE ux_taxonomia_area_tema criado.")
        except sqlite3.Error as e:
            print(f"\n[ERRO] transação revertida: {e}")
            con.close()
            sys.exit(1)
    else:
        print(f"\n(dry-run) {total_del} linhas seriam deletadas. Nada gravado.")

    # Verificação read-only
    dup = cur.execute("SELECT COUNT(*) FROM (SELECT 1 FROM taxonomia_cronograma "
                      "WHERE tema NOT LIKE '[bulk]%' AND tema<>'Geral' "
                      "GROUP BY area,tema HAVING COUNT(*)>1)").fetchone()[0]
    orf_q = cur.execute("SELECT COUNT(*) FROM questoes_erros q "
                        "LEFT JOIN taxonomia_cronograma t ON q.tema_id=t.id WHERE t.id IS NULL").fetchone()[0]
    orf_f = cur.execute("SELECT COUNT(*) FROM flashcards f "
                        "LEFT JOIN taxonomia_cronograma t ON f.tema_id=t.id WHERE t.id IS NULL").fetchone()[0]
    rows_depois = cur.execute("SELECT COUNT(*) FROM taxonomia_cronograma").fetchone()[0]
    print(f"VERIF -> linhas {rows_antes} -> {rows_depois} | grupos_dup={dup} | "
          f"orfaos(erros={orf_q}, cards={orf_f})")
    con.close()


if __name__ == "__main__":
    main()
