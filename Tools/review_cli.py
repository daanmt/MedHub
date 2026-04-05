"""
MedHub FSRS Review CLI
Sessão de revisão espaçada com política de 3 buckets (atrasados → hoje → novos).
Uso: python Tools/review_cli.py [--limit N] [--new-limit N] [--area STR] [--tema STR]
"""

import sys
import os
import argparse
from collections import Counter

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stdin.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.utils.db import record_review, get_connection

SELECT_FIELDS = """
    SELECT f.id, f.frente_pergunta, f.verso_resposta, f.frente_contexto,
           f.verso_regra_mestre, f.verso_armadilha,
           fc.state, fc.due, COALESCE(t.area,''), COALESCE(t.tema,'')
    FROM flashcards f
    JOIN fsrs_cards fc ON f.id = fc.card_id
    LEFT JOIN taxonomia_cronograma t ON f.tema_id = t.id
"""

# Índices das colunas no resultado
COL_ID, COL_FRENTE_PERGUNTA, COL_VERSO_RESPOSTA, COL_FRENTE_CONTEXTO = 0, 1, 2, 3
COL_VERSO_REGRA, COL_VERSO_ARMADILHA = 4, 5
COL_STATE, COL_DUE, COL_AREA, COL_TEMA = 6, 7, 8, 9


def build_filters(area, tema):
    clauses, params = [], []
    if area:
        clauses.append("t.area = ?")
        params.append(area)
    if tema:
        clauses.append("t.tema LIKE ?")
        params.append(f"%{tema}%")
    return clauses, params


def get_queue(limit, new_limit, area, tema):
    conn = get_connection()
    filter_clauses, filter_params = build_filters(area, tema)

    def make_where(base_clauses):
        all_clauses = base_clauses + filter_clauses
        return ("WHERE " + " AND ".join(all_clauses)) if all_clauses else ""

    # Bucket 1: atrasados (state > 0, due antes de hoje)
    w1 = make_where(["fc.state > 0", "fc.due < datetime('now','start of day')", "f.needs_qualitative < 2"])
    b1 = conn.execute(
        f"{SELECT_FIELDS} {w1} ORDER BY fc.due ASC LIMIT ?",
        filter_params + [limit]
    ).fetchall()

    remaining = limit - len(b1)
    b2 = []
    if remaining > 0:
        # Bucket 2: due hoje
        w2 = make_where([
            "fc.state > 0",
            "fc.due >= datetime('now','start of day')",
            "fc.due < datetime('now','start of day','+1 day')",
            "f.needs_qualitative < 2",
        ])
        b2 = conn.execute(
            f"{SELECT_FIELDS} {w2} ORDER BY fc.due ASC LIMIT ?",
            filter_params + [remaining]
        ).fetchall()

    remaining = remaining - len(b2)
    b3 = []
    if remaining > 0:
        new_cap = min(remaining, new_limit)
        # Bucket 3: novos (state = 0)
        w3 = make_where(["fc.state = 0", "f.needs_qualitative < 2"])
        b3 = conn.execute(
            f"{SELECT_FIELDS} {w3} ORDER BY f.id ASC LIMIT ?",
            filter_params + [new_cap]
        ).fetchall()

    conn.close()
    return b1, b2, b3


def display_front(card, label):
    area = card[COL_AREA]
    tema = card[COL_TEMA]
    frente_pergunta = card[COL_FRENTE_PERGUNTA]
    frente_contexto = card[COL_FRENTE_CONTEXTO]

    print()
    print("=" * 64)
    print(f"  {label}  |  {area} › {tema}")
    print("=" * 64)

    if frente_contexto and frente_contexto.strip():
        print(f"\n  Contexto: {frente_contexto}")
    print(f"\n  {frente_pergunta or '(sem frente)'}")
    print()


def display_back(card):
    verso_resposta = card[COL_VERSO_RESPOSTA]
    verso_regra = card[COL_VERSO_REGRA]
    verso_armadilha = card[COL_VERSO_ARMADILHA]

    print("-" * 64)
    print(f"\n  RESPOSTA:\n  {verso_resposta or '(sem verso)'}")
    if verso_regra and verso_regra.strip():
        print(f"\n  REGRA MESTRE:\n  {verso_regra}")
    if verso_armadilha and verso_armadilha.strip():
        print(f"\n  ARMADILHA:\n  {verso_armadilha}")
    print()


def ask_rating():
    while True:
        try:
            raw = input("  Avaliação — 1 Novamente | 2 Difícil | 3 Bom | 4 Fácil | s Pular: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return None
        if raw == 's':
            return 0
        if raw in ('1', '2', '3', '4'):
            return int(raw)
        print("  Entrada inválida. Use 1, 2, 3, 4 ou s.")


def session_summary(reviewed, ratings):
    print()
    print("=" * 64)
    print(f"  SESSÃO CONCLUÍDA — {reviewed} cards revisados")
    if ratings:
        dist = Counter(ratings)
        print(f"  Novamente(1):{dist[1]:3}  Difícil(2):{dist[2]:3}  Bom(3):{dist[3]:3}  Fácil(4):{dist[4]:3}")

    conn = get_connection()
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

    if top_dues:
        print("\n  Próximas dues (top 5):")
        for r in top_dues:
            due_str = r[1][:10] if r[1] else "?"
            print(f"    card={r[0]:<4}  due={due_str}  stability={r[2]:.2f}  area={r[3]}")
    print("=" * 64)
    print()


def main():
    parser = argparse.ArgumentParser(description="MedHub FSRS Review CLI")
    parser.add_argument('--limit', type=int, default=20,
                        help='Máx total de cards na sessão (default: 20)')
    parser.add_argument('--new-limit', type=int, default=10, dest='new_limit',
                        help='Máx de cards novos do Bucket 3 (default: 10)')
    parser.add_argument('--area', type=str, default=None,
                        help='Filtrar por área (ex: "Clínica Médica")')
    parser.add_argument('--tema', type=str, default=None,
                        help='Filtrar por tema (busca parcial)')
    args = parser.parse_args()

    b1, b2, b3 = get_queue(args.limit, args.new_limit, args.area, args.tema)
    queue = b1 + b2 + b3

    if not queue:
        print("\nNenhum card disponível para revisão. Volte mais tarde!")
        return

    labels = (
        ['ATRASADO'] * len(b1) +
        ['HOJE']     * len(b2) +
        ['NOVO']     * len(b3)
    )

    print(f"\nMedHub FSRS — {len(queue)} cards  "
          f"({len(b1)} atrasados | {len(b2)} hoje | {len(b3)} novos)")

    reviewed = 0
    ratings = []

    for i, (card, label) in enumerate(zip(queue, labels), 1):
        print(f"\n[{i}/{len(queue)}] {label}")
        display_front(card, label)

        try:
            input("  [ENTER para revelar]")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        display_back(card)
        rating = ask_rating()

        if rating is None:
            break
        if rating > 0:
            record_review(card[COL_ID], rating)
            reviewed += 1
            ratings.append(rating)
        else:
            print("  (pulado)")

    session_summary(reviewed, ratings)


if __name__ == '__main__':
    main()
