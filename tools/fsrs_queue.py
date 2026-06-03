"""fsrs_queue.py — fila de revisão FSRS em JSON para revisão conversacional.

Camada fina sobre ``app.utils.db``: lê a fila de cards vencidos via
``get_cards_by_bucket()`` e grava avaliações via ``record_review()``. Não abre
``sqlite3`` nem reimplementa o FSRS — delega tudo à camada de acesso canônica,
preservando o caminho de escrita único e o audit trail em ``fsrs_revlog``.

Existe para que o agente (Claude Code) conduza a revisão dentro da conversa
— inclusive via remote-control no celular, onde o player Streamlit local não
é alcançável.

Uso:
    python tools/fsrs_queue.py --next [--area X] [--tema Y]
    python tools/fsrs_queue.py --list [--area X] [--tema Y] [--limit N] [--new-limit M]
    python tools/fsrs_queue.py --record <card_id> --rating <1-4>

Ordem da fila: atrasados -> hoje -> novos. Cards aposentados
(needs_qualitative >= 2) são excluídos pela própria query do db.

Assinatura canônica documentada em .claude/commands/revisar.md (contrato §7.2).
"""
import argparse
import io
import json
import os
import sys

# Saída sempre em UTF-8 — evita UnicodeEncodeError no console cp1252 do Windows
# quando o card contém marcadores clínicos (🔴, ⚠️, ⭐) ou acentuação.
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Permite importar app.utils.db ao rodar como script standalone
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils import db  # noqa: E402


def _ordered_queue(area=None, tema=None, limit=None, new_limit=10):
    """Achata os três buckets na ordem de prioridade, anotando o bucket de origem."""
    buckets = db.get_cards_by_bucket(area=area, tema=tema, new_limit=new_limit)
    ordered = []
    for nome in ("atrasados", "hoje", "novos"):
        for card in buckets.get(nome, []):
            card = dict(card)
            card["bucket"] = nome
            ordered.append(card)
    if limit is not None:
        ordered = ordered[:limit]
    return ordered


def _emit(obj):
    print(json.dumps(obj, ensure_ascii=False, default=str))


def main():
    parser = argparse.ArgumentParser(
        description="Fila de revisão FSRS em JSON para revisão conversacional."
    )
    acao = parser.add_mutually_exclusive_group(required=True)
    acao.add_argument("--next", action="store_true",
                      help="Imprime o próximo card vencido (objeto JSON)")
    acao.add_argument("--list", action="store_true",
                      help="Imprime o lote da fila (array JSON)")
    acao.add_argument("--record", type=int, metavar="CARD_ID",
                      help="Grava a avaliação de um card (exige --rating)")
    parser.add_argument("--rating", type=int, choices=[1, 2, 3, 4],
                        help="Avaliação 1=Novamente 2=Difícil 3=Bom 4=Fácil (com --record)")
    parser.add_argument("--area", help="Filtro de área (match exato)")
    parser.add_argument("--tema", help="Filtro de tema (LIKE)")
    parser.add_argument("--limit", type=int, help="Máximo de cards na fila (--list)")
    parser.add_argument("--new-limit", type=int, default=10, dest="new_limit",
                        help="Máximo de cards novos (state 0). Default: 10")
    args = parser.parse_args()

    if args.record is not None:
        if args.rating is None:
            parser.error("--record exige --rating <1-4>")
        metrics = db.record_review(args.record, args.rating)
        _emit({
            "recorded": True,
            "card_id": args.record,
            "rating": args.rating,
            "next_due": metrics.get("due"),
            "state": metrics.get("state"),
        })
        return

    ordered = _ordered_queue(area=args.area, tema=args.tema,
                             limit=args.limit, new_limit=args.new_limit)

    if args.next:
        _emit(ordered[0] if ordered else {"empty": True})
    else:  # --list
        _emit(ordered)


if __name__ == "__main__":
    main()
