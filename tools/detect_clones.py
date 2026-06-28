"""detect_clones.py — near-duplicates de flashcards POR TEMA. Read-only.

Complementa audit_flashcard_quality.py (que é sintático e cego a clone). Compara
frente_pergunta + verso_resposta entre cards ativos do MESMO tema via SequenceMatcher;
lista pares acima do limiar como candidatos a fusão na curadoria (ver
.agents/workflows/curar-cards.md). NÃO grava nada.

Uso:
    python tools/detect_clones.py                 # limiar 0.72
    python tools/detect_clones.py --limiar 0.80
    python tools/detect_clones.py --area Cirurgia
"""
import sqlite3, argparse, os, sys
from difflib import SequenceMatcher
from collections import defaultdict

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')


def norm(s):
    return " ".join((s or "").lower().split())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--limiar', type=float, default=0.72, help='Similaridade mínima (0-1, default 0.72)')
    ap.add_argument('--area', default=None, help='Filtrar por área')
    args = ap.parse_args()

    cur = sqlite3.connect(DB_PATH).cursor()
    q = ("SELECT f.id, t.area, t.tema, f.frente_pergunta, f.verso_resposta "
         "FROM flashcards f JOIN taxonomia_cronograma t ON f.tema_id=t.id "
         "WHERE f.needs_qualitative!=2")
    params = ()
    if args.area:
        q += " AND t.area=?"
        params = (args.area,)
    rows = cur.execute(q, params).fetchall()

    by_tema = defaultdict(list)
    for cid, area, tema, fp, vr in rows:
        by_tema[(area, tema)].append((cid, norm(fp) + " || " + norm(vr)))

    pares = []
    for (area, tema), cards in by_tema.items():
        for i in range(len(cards)):
            for j in range(i + 1, len(cards)):
                r = SequenceMatcher(None, cards[i][1], cards[j][1]).ratio()
                if r >= args.limiar:
                    pares.append((r, area, tema, cards[i][0], cards[j][0]))

    pares.sort(reverse=True)
    print(f"Near-duplicates (limiar {args.limiar}) — {len(rows)} cards ativos, {len(by_tema)} temas:\n")
    for r, area, tema, a, b in pares:
        print(f"  {r:.2f}  [{area}/{tema}]  #{a} ~ #{b}")
    print(f"\n{len(pares)} par(es) candidato(s) a fusão.")


if __name__ == "__main__":
    main()
