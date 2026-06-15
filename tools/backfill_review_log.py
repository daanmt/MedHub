"""backfill_review_log.py — semeia review_log com a ÚLTIMA REVISÃO REAL por tema.

Para cada tema COM cards: insere 1 linha kind='backfill' com reviewed_at = o
sinal real mais forte — MAX(fsrs_cards.last_review) → source 'fsrs_derived';
senão taxonomia.ultima_revisao → 'taxonomia_derived'. **NUNCA usa a data de
hoje** (não falsifica a curva). Tema sem nenhum sinal real é pulado.

Idempotente: pula tema que já tenha qualquer linha em review_log. Rodar APÓS a
dedup (para não semear ids que seriam mesclados). `--dry-run` é o default.

Uso:
    python tools/backfill_review_log.py            # dry-run
    python tools/backfill_review_log.py --apply
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


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--apply', action='store_true', help='Grava (default: dry-run)')
    args = ap.parse_args()
    dry = not args.apply

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    temas = cur.execute("""
        SELECT t.id, t.area, t.tema,
               (SELECT MAX(fc.last_review) FROM fsrs_cards fc
                  JOIN flashcards f ON f.id = fc.card_id WHERE f.tema_id = t.id) AS fsrs_last,
               t.ultima_revisao
        FROM taxonomia_cronograma t
        WHERE t.tema NOT LIKE '[bulk]%' AND t.tema <> 'Geral'
          AND EXISTS (SELECT 1 FROM flashcards f WHERE f.tema_id = t.id)
        ORDER BY t.area, t.tema
    """).fetchall()

    plano, n_skip = [], 0
    for tid, area, tema, fsrs_last, ult in temas:
        if cur.execute("SELECT 1 FROM review_log WHERE tema_id=? LIMIT 1", (tid,)).fetchone():
            n_skip += 1
            continue
        if fsrs_last:
            plano.append((tid, area, tema, fsrs_last, 'fsrs_derived'))
        elif ult:
            plano.append((tid, area, tema, ult, 'taxonomia_derived'))
        else:
            n_skip += 1                     # sem sinal real → não inventa

    print(f"{'(DRY-RUN) ' if dry else ''}{len(plano)} temas a semear, {n_skip} pulados.\n")
    for tid, area, tema, ra, src in plano:
        print(f"  [{src:17}] {area:11} | {tema[:34]:34} | {ra}")

    if not dry:
        for tid, area, tema, ra, src in plano:
            cur.execute("INSERT INTO review_log (tema_id, kind, source, note, reviewed_at) "
                        "VALUES (?, 'backfill', ?, 'backfill s083', ?)", (tid, src, ra))
        con.commit()
        print(f"\nAPLICADO: {len(plano)} temas semeados em review_log.")
    else:
        print(f"\n(dry-run) {len(plano)} seriam semeados. Nada gravado.")
    con.close()


if __name__ == "__main__":
    main()
