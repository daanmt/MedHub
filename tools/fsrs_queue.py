"""fsrs_queue.py — fila de revisão FSRS em JSON para revisão conversacional.

Camada fina sobre ``app.utils.db``: lê a fila de cards vencidos via
``get_cards_by_bucket()`` e grava avaliações via ``record_review()``. Não abre
``sqlite3`` nem reimplementa o FSRS — delega tudo à camada de acesso canônica,
preservando o caminho de escrita único e o audit trail em ``fsrs_revlog``.

Existe para que o agente (Claude Code) conduza a revisão dentro da conversa
— inclusive via remote-control no celular. É a ÚNICA superfície de revisão
desde o pivot agent-first (s074): a UI local foi removida.

Uso:
    python tools/fsrs_queue.py --next [--area X] [--tema Y]
    python tools/fsrs_queue.py --list [--area X] [--tema Y] [--limit N] [--new-limit M] [--cluster]
    python tools/fsrs_queue.py --record <card_id> --rating <1-4>

Ordem da fila: atrasados -> hoje -> novos. Com --cluster (F3), a prioridade de
bucket é preservada e, dentro de cada bucket, os cards são agrupados por
(area, tema) — revisão em cluster sem re-agrupamento manual. Cards aposentados
(needs_qualitative >= 2) são excluídos pela própria query do db.

Assinatura canônica documentada em .claude/commands/revisar.md (contrato §7.2).
"""
import argparse
import io
import json
import os
from pathlib import Path
import sys

# Saída sempre em UTF-8 — evita UnicodeEncodeError no console cp1252 do Windows
# quando o card contém marcadores clínicos (🔴, ⚠️, ⭐) ou acentuação.
if __name__ == "__main__" and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Permite importar app.utils.db ao rodar como script standalone
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils import db  # noqa: E402


def _cluster_key(card):
    """Chave de agrupamento (area, tema); cards sem taxonomia vão ao fim do bucket."""
    return (card.get("area") is None, card.get("area") or "",
            card.get("tema") is None, card.get("tema") or "")


PREVALENCIA_PATH = Path(__file__).resolve().parents[1] / "core" / "cronograma" / "prevalencia_enamed.json"
_RANK = {"alta": 0, "media": 1, "baixa": 2}


def load_prevalencia(path=None):
    """Mapa (area, tema) -> rank (0 alta, 1 media, 2 baixa) lido de
    core/cronograma/prevalencia_enamed.json (insumo manual, F63). Arquivo
    ausente ou invalido -> {} (a fila volta ao FIFO, nunca quebra)."""
    path = Path(path) if path else PREVALENCIA_PATH
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return {(t.get("area"), t.get("tema")): _RANK.get(t.get("prevalencia"), 3)
            for t in data.get("temas", []) if t.get("tema")}


def rank_novos_por_prevalencia(cards, prev_map, new_limit):
    """Reordena o bucket `novos` por prevalencia ENAMED (alta -> media -> baixa
    -> sem sinal), desempate por card_id (FIFO original), e corta em new_limit.
    Puro: nao toca banco nem FSRS -- so a ORDEM de introducao muda (s165:
    'prevalencia = prioridade na fila dos nunca introduzidos')."""
    def key(c):
        return (prev_map.get((c.get("area"), c.get("tema")), 3), int(c.get("card_id", 0)))
    ordered = sorted(cards, key=key)
    return ordered[:new_limit] if new_limit is not None else ordered


def _ordered_queue(area=None, tema=None, limit=None, new_limit=10, cluster=False,
                   prevalencia=False):
    """Achata os buckets na ordem de prioridade, anotando o bucket de origem.

    P3 part-2: ordem `atrasados → erros_frescos → hoje → novos` — card de erro
    recente fura a fila ANTES de novos FIFO (banda prioritária explícita); cada
    card já vem com `selection_reason` do db. Com cluster=True (F3), ordena
    secundariamente por (area, tema) DENTRO de cada bucket — sort estável
    preserva a sub-ordem por due no mesmo tema.
    """
    if prevalencia:
        # puxa o pool inteiro de state=0 e reordena em Python (o LIMIT do SQL
        # cortaria em FIFO antes da prevalencia agir)
        buckets = db.get_cards_by_bucket(area=area, tema=tema, new_limit=10**6)
        buckets["novos"] = rank_novos_por_prevalencia(
            buckets.get("novos", []), load_prevalencia(), new_limit)
    else:
        buckets = db.get_cards_by_bucket(area=area, tema=tema, new_limit=new_limit)
    ordered = []
    for nome in ("atrasados", "erros_frescos", "hoje", "novos"):
        cards = buckets.get(nome, [])
        if cluster:
            cards = sorted(cards, key=_cluster_key)
        for card in cards:
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
    acao.add_argument("--preview", type=int, metavar="CARD_ID",
                      help="P3: consequencia dos 4 ratings p/ um card (JSON), sem gravar nada")
    acao.add_argument("--pre-bloco", dest="pre_bloco", metavar="TEMA",
                      help="Mini-drill anti-reincidência (F23): lista SÓ os cards de erro "
                           "FRESCOS (state 0, janela --janela-horas) do tema-alvo, antes de "
                           "um bloco de questões. Rating segue o --record normal")
    parser.add_argument("--rating", type=int, choices=[1, 2, 3, 4],
                        help="Avaliação 1=Novamente 2=Difícil 3=Bom 4=Fácil (com --record)")
    parser.add_argument("--reason", default=None,
                        choices=["vencido", "fresh_error", "agendado", "novo", "pre_bloco"],
                        help="P3: por que o card foi servido — propague o selection_reason "
                             "que veio no --next/--list; persiste no revlog")
    parser.add_argument("--area", help="Filtro de área (match exato)")
    parser.add_argument("--tema", help="Filtro de tema (LIKE)")
    parser.add_argument("--limit", type=int, help="Máximo de cards na fila (--list)")
    parser.add_argument("--prevalencia", action="store_true",
                        help="Reordena os cards NOVOS por prevalencia ENAMED "
                             "(core/cronograma/prevalencia_enamed.json: alta -> media -> "
                             "baixa -> sem sinal; desempate FIFO). Opt-in; so muda a "
                             "ordem de introducao, nunca o FSRS (s165)")
    parser.add_argument("--new-limit", type=int, default=10, dest="new_limit",
                        help="Máximo de cards novos (state 0). Default: 10")
    parser.add_argument("--cluster", action="store_true",
                        help="Agrupa por (area, tema) dentro de cada bucket, preservando "
                             "a prioridade atrasados -> hoje -> novos (F3). Opt-in: sem a "
                             "flag, a ordem é a atual")
    parser.add_argument("--janela-horas", type=int, default=48, dest="janela_horas",
                        help="Janela de frescor do --pre-bloco em horas (default 48; "
                             "norma: core/contracts/orquestracao-contract.md)")
    args = parser.parse_args()

    if args.pre_bloco:
        frescos = db.get_fresh_error_cards(tema=args.pre_bloco,
                                           janela_horas=args.janela_horas)
        if not frescos:
            _emit({"empty": True, "pre_bloco": args.pre_bloco,
                   "msg": "0 cards frescos p/ '%s' na janela de %dh"
                          % (args.pre_bloco, args.janela_horas)})
            return
        out = []
        for card in frescos:
            card = dict(card)
            card["bucket"] = "pre-bloco"
            out.append(card)
        _emit(out)
        return

    if args.record is not None:
        if args.rating is None:
            parser.error("--record exige --rating <1-4>")
        try:
            metrics = db.record_review(args.record, args.rating,
                                       selection_reason=args.reason)
        except db.ConcurrentReviewError as e:
            # part-2: fail-safe — reporta e NAO regrava (Invariante C).
            _emit({"recorded": False, "card_id": args.record,
                   "error": f"rating nao gravado (estado mudou desde a leitura): {e}"})
            sys.exit(1)
        _emit({
            "recorded": True,
            "card_id": args.record,
            "rating": args.rating,
            "next_due": metrics.get("due"),
            "state": metrics.get("state"),
        })
        return

    if args.preview is not None:
        _emit({"card_id": args.preview, "preview": db.preview_ratings(args.preview)})
        return

    ordered = _ordered_queue(area=args.area, tema=args.tema,
                             limit=args.limit, new_limit=args.new_limit, prevalencia=args.prevalencia,
                             cluster=args.cluster)

    if args.next:
        if not ordered:
            _emit({"empty": True})
            return
        card = ordered[0]
        # P3 part-3: preview embutido no momento do rating (so no --next; no
        # --list seria 4xN evaluates sem uso). Falha de preview nunca derruba
        # a fila — o card sai sem o campo, com o erro anotado.
        try:
            card["preview"] = db.preview_ratings(card["card_id"])
        except Exception as e:
            card["preview_error"] = str(e)
        _emit(card)
    else:  # --list
        _emit(ordered)


if __name__ == "__main__":
    main()
