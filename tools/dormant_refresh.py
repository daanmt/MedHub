"""dormant_refresh.py — ritual diário de refresh de tema DORMENTE.

Seleciona 1 tema dormente (via review_radar.coletar), monta o substrato
narrativo (via app.engine.get_topic_context) e carimba a revisão temática
(db.log_review). **NÃO toca o FSRS** — é re-ensino narrativo de tema,
complementar (não substituto) ao /revisar card-a-card.

Ver core/contracts/forgetting-curve-contract.md (pendente) e
.claude/commands/refrescar.md.

Uso:
    python tools/dormant_refresh.py --pick   [--area X] [--window-days N]
    python tools/dormant_refresh.py --context --tema "X" [--area Y]
    python tools/dormant_refresh.py --stamp  --tema-id N [--resumo PATH] [--note "..."]

Ordem de prioridade do --pick: tema com cards ativos, não-[bulk]/Geral, não
refrescado nos últimos N dias (anti-repetição), maior `score` de dormência.
"""
import argparse
import json
import os
import sys
from datetime import datetime

try:                                   # UTF-8 no console cp1252 do Windows
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
# repo root p/ app.*, e tools/ (dir do script) já está em sys.path[0] p/ review_radar
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app.utils.db as db                       # noqa: E402
from review_radar import coletar                # noqa: E402

REPETITION_WINDOW_DAYS = 7   # não repetir o mesmo tema como dormant_refresh nessa janela


def _emit(obj):
    print(json.dumps(obj, ensure_ascii=False, default=str))


def _days_since_dormant_refresh(tema_id):
    """Dias desde o último dormant_refresh do tema (None se nunca)."""
    con = db.get_connection()
    row = con.execute(
        "SELECT MAX(reviewed_at) FROM review_log WHERE tema_id=? AND kind='dormant_refresh'",
        (tema_id,)).fetchone()
    con.close()
    if not row or not row[0]:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(row[0], fmt)
            return (datetime.now() - dt).days
        except ValueError:
            continue
    return None


def pick(area=None, window_days=REPETITION_WINDOW_DAYS):
    """Escolhe o tema dormente do dia. Retorna dict do tema ou {'empty': True}."""
    rows = coletar(area=area)
    cands = []
    for r in rows:
        if (r.get("n_cards") or 0) <= 0:          # só temas realmente estudados (com cards)
            continue
        if r["tema"].startswith("[bulk]") or r["tema"] == "Geral":
            continue
        since = _days_since_dormant_refresh(r["id"])
        if since is not None and since < window_days:   # anti-repetição
            continue
        cands.append(r)
    cands.sort(key=lambda r: r["score"], reverse=True)
    if not cands:
        return {"empty": True}
    r = cands[0]
    return {
        "tema_id": r["id"], "area": r["area"], "tema": r["tema"],
        "dias_sem_revisar": r["dias_sem_revisar"], "retr": r["retr"],
        "n_cards": r["n_cards"], "n_novos": r["n_novos"], "n_review": r["n_review"],
        "n_vencidos": r["n_vencidos"], "perf": r["perf"], "score": r["score"],
    }


def _find_resumo_by_filename(tema):
    """Fallback: localiza resumos/**/<tema>.md por nome de arquivo (o índice do
    engine indexa por especialidade/área/alias, não pelo nome granular do tema)."""
    import difflib
    from pathlib import Path
    base = Path("resumos")
    if not base.exists():
        return None, None
    stems = {p.stem.lower(): p for p in base.rglob("*.md") if p.name != "INDEX.md"}
    t = (tema or "").lower()
    p = stems.get(t)
    if p is None:
        m = difflib.get_close_matches(t, stems.keys(), n=1, cutoff=0.7)
        p = stems[m[0]] if m else None
    if p is None:
        return None, None
    try:
        return str(p), p.read_text(encoding="utf-8")
    except Exception:
        return None, None


def context(tema, area=None):
    """Substrato narrativo do tema (resumo + erros + cards + RAG) p/ o agente narrar.

    Resumo: tenta o engine (índice por especialidade/área/alias); se não achar,
    cai para match por nome de arquivo (temas granulares costumam = nome do .md).
    """
    from app.engine import get_topic_context
    ctx = get_topic_context(tema, area)
    resumo_path = ctx.get("resumo_path")
    resumo_content = ctx.get("resumo_content")
    if not resumo_content:
        rp, rc = _find_resumo_by_filename(tema)
        if rc:
            resumo_path, resumo_content = rp, rc
    return {
        "tema": tema, "area": area,
        "resumo_path": resumo_path,
        "resumo_content": resumo_content,                # completo — o agente narra a partir daqui
        "erros_recentes": (ctx.get("erros_recentes") or [])[:10],
        "cards_ativos": ctx.get("cards_ativos", 0),
        "weak_areas": ctx.get("weak_areas") or [],
        "relevant_chunks": ctx.get("relevant_chunks") or [],
    }


VALID_KINDS = ("dormant_refresh", "directed_review")


def stamp(tema_id, resumo=None, note=None, kind="dormant_refresh"):
    """Carimba o refresh/PREPARAR em review_log. NÃO toca o FSRS (Invariante A).

    kind ∈ {dormant_refresh, directed_review}: discrimina o gatilho do PREPARAR
    (radar de dormência vs cronograma/fila FSRS/pedido direto). Invariante B da
    Revisão Calibrada — TODO PREPARAR carimba review_log para a curva nunca cegar.
    Ver core/contracts/revisao-calibrada-contract.md.
    """
    if kind not in VALID_KINDS:
        raise ValueError(f"kind inválido: {kind!r} (use {VALID_KINDS})")
    rid = db.log_review(tema_id=tema_id, resumo_path=resumo,
                        kind=kind, source="agent", note=note)
    return {"logged": True, "review_log_id": rid, "tema_id": tema_id, "kind": kind}


def main():
    ap = argparse.ArgumentParser(description="Ritual de refresh de tema dormente.")
    acao = ap.add_mutually_exclusive_group(required=True)
    acao.add_argument("--pick", action="store_true", help="Escolhe o tema dormente do dia (JSON)")
    acao.add_argument("--context", action="store_true", help="Substrato narrativo do tema (JSON)")
    acao.add_argument("--stamp", action="store_true", help="Carimba o refresh em review_log")
    ap.add_argument("--area", help="Filtro de área (match exato)")
    ap.add_argument("--tema", help="Tema (com --context)")
    ap.add_argument("--tema-id", type=int, dest="tema_id", help="id do tema (com --stamp)")
    ap.add_argument("--resumo", help="Caminho do resumo refrescado (com --stamp)")
    ap.add_argument("--note", help="Nota curta do que foi refrescado (com --stamp)")
    ap.add_argument("--kind", choices=VALID_KINDS, default="dormant_refresh",
                    help="Gatilho do PREPARAR (com --stamp): dormant_refresh|directed_review")
    ap.add_argument("--window-days", type=int, default=REPETITION_WINDOW_DAYS, dest="window_days",
                    help=f"Janela anti-repetição em dias (default {REPETITION_WINDOW_DAYS})")
    args = ap.parse_args()

    if args.pick:
        _emit(pick(area=args.area, window_days=args.window_days))
    elif args.context:
        if not args.tema:
            ap.error("--context exige --tema")
        _emit(context(args.tema, args.area))
    else:  # --stamp
        if args.tema_id is None:
            ap.error("--stamp exige --tema-id")
        _emit(stamp(args.tema_id, resumo=args.resumo, note=args.note, kind=args.kind))


if __name__ == "__main__":
    main()
