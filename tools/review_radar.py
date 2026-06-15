"""review_radar.py — Radar de dormência por TEMA.

Ranqueia os temas estudados por "frieza": quanto tempo desde a última revisão
cruzado com o decaimento FSRS dos cards do tema. Responde à pergunta do
estudante: *"de quais temas eu não vejo há tempo e por isso erro coisas
simples?"* — e alimenta o refresh inline diário + o boot proativo.

Read-only. Não reimplementa o FSRS: deriva a temperatura do estado que o
pipeline (insert_questao + fsrs_queue) já mantém em fsrs_cards/taxonomia.

Sinais por tema (join taxonomia_cronograma -> flashcards ativos -> fsrs_cards):
  - dias_sem_revisar : hoje - max(last_review do tema); fallback ultima_revisao.
  - n_cards / novos / em_revisao ; vencidos (due < agora).
  - stability media (reviewed) ; retrievability media aprox. (0.9 ^ elapsed/stab).
  - perf% (taxonomia).
  - score de dormencia: prioriza muito-tempo-sem-ver + baixa retrievability.

Uso:
    python tools/review_radar.py [--limit N] [--area X] [--json] [--all]

Default: top frios (limit 12), formato markdown.
"""
import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, date

try:                                   # UTF-8 no console cp1252 do Windows
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ipub.db")

# Limiar acima do qual um tema entra no "horizonte dormente" (dias).
DORMENTE_DIAS = 21


def _parse_dt(s):
    """Parse robusto de DATE ('YYYY-MM-DD') ou DATETIME ('... HH:MM:SS.ffffff')."""
    if not s:
        return None
    s = str(s).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def _retrievability(elapsed_days, stability):
    """Aprox. da curva de esquecimento: R = 0.9 ^ (elapsed / stability)."""
    if not stability or stability <= 0:
        return None
    try:
        return 0.9 ** (max(elapsed_days, 0) / stability)
    except (OverflowError, ZeroDivisionError):
        return 0.0


def coletar(area=None):
    now = datetime.now()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    sql = """
        SELECT t.id, t.area, t.tema, t.percentual_acertos AS perf,
               t.questoes_realizadas AS qfeitas, t.ultima_revisao AS ult_tax,
               (SELECT MAX(rl.reviewed_at) FROM review_log rl WHERE rl.tema_id = t.id) AS rl_last,
               COUNT(f.id) AS n_cards,
               SUM(CASE WHEN f.id IS NOT NULL AND COALESCE(fc.state,0)=0 THEN 1 ELSE 0 END) AS n_novos,
               SUM(CASE WHEN fc.state>0 THEN 1 ELSE 0 END) AS n_review,
               MAX(fc.last_review) AS last_review,
               AVG(CASE WHEN fc.state>0 THEN fc.stability END) AS stab_media,
               SUM(CASE WHEN fc.state>0 AND fc.due IS NOT NULL AND fc.due < ?
                        THEN 1 ELSE 0 END) AS n_vencidos
        FROM taxonomia_cronograma t
        LEFT JOIN flashcards f
               ON f.tema_id = t.id AND COALESCE(f.needs_qualitative,0) < 2
        LEFT JOIN fsrs_cards fc ON fc.card_id = f.id
        {where}
        GROUP BY t.id
    """.format(where="WHERE " + " AND ".join(
        ["t.tema NOT LIKE '[bulk]%'"] + (["t.area = ?"] if area else [])))
    params = [now.isoformat(" ")]
    if area:
        params.append(area)
    rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
    conn.close()

    for r in rows:
        refs = [d for d in (_parse_dt(r.get("rl_last")), _parse_dt(r["last_review"]),
                            _parse_dt(r["ult_tax"])) if d]
        ref = max(refs) if refs else None
        r["dias_sem_revisar"] = (now - ref).days if ref else None
        # retrievability media aprox: usa dias desde a ultima revisao como elapsed
        if r["stab_media"] and r["dias_sem_revisar"] is not None:
            r["retr"] = _retrievability(r["dias_sem_revisar"], r["stab_media"])
        else:
            r["retr"] = None
        # score de dormencia: alto = mais frio / mais urgente
        dias = r["dias_sem_revisar"]
        if dias is None:        # tema sem nenhuma referencia temporal
            r["score"] = 999.0
        else:
            base = dias
            # penaliza baixa retrievability (memoria ja caiu) e cards vencidos
            if r["retr"] is not None:
                base += (1 - r["retr"]) * 30
            base += (r["n_vencidos"] or 0) * 2
            r["score"] = round(base, 1)
    return rows


def render_md(rows, limit):
    frios = sorted(rows, key=lambda r: r["score"], reverse=True)
    com_cards = [r for r in rows if r["n_cards"]]
    nunca = [r for r in rows if r["dias_sem_revisar"] is None]
    dormentes = [r for r in com_cards
                 if (r["dias_sem_revisar"] or 0) >= DORMENTE_DIAS]
    out = []
    out.append("# 🌡️ Radar de Dormência — temas por tempo sem revisar\n")
    out.append(f"*{date.today().isoformat()} — {len(rows)} temas | "
               f"{len(dormentes)} dormentes (≥{DORMENTE_DIAS}d) | "
               f"{len(nunca)} sem timestamp de revisão*\n")
    out.append("| # | Tema | Área | Dias s/ rev | Cards (nov/rev) | Vencidos | Estab.méd | Retr.~ | Perf |")
    out.append("|---|---|---|--:|--:|--:|--:|--:|--:|")
    for i, r in enumerate(frios[:limit], 1):
        dias = r["dias_sem_revisar"]
        dias_s = f"{dias}d" if dias is not None else "—"
        stab = f"{r['stab_media']:.1f}" if r["stab_media"] else "—"
        retr = f"{r['retr']*100:.0f}%" if r["retr"] is not None else "—"
        perf = f"{r['perf']:.0f}%" if r["perf"] else "—"
        cards = f"{r['n_cards']} ({r['n_novos'] or 0}/{r['n_review'] or 0})"
        out.append(f"| {i} | {r['tema'][:38]} | {r['area'][:12]} | {dias_s} | "
                   f"{cards} | {r['n_vencidos'] or 0} | {stab} | {retr} | {perf} |")
    out.append("\n**Legenda:** Dias s/ rev = desde a última revisão FSRS (fallback: última atividade no tema). "
               "Retr.~ = retrievability média aproximada (0.9^(dias/estab.)) — quanto menor, mais a memória caiu.")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Radar de dormência por tema.")
    ap.add_argument("--limit", type=int, default=12, help="Temas no ranking (default 12)")
    ap.add_argument("--area", help="Filtra por área (match exato)")
    ap.add_argument("--json", action="store_true", help="Saída JSON")
    ap.add_argument("--all", action="store_true", help="Ignora --limit (todos os temas)")
    args = ap.parse_args()

    rows = coletar(area=args.area)
    limit = len(rows) if args.all else args.limit
    if args.json:
        frios = sorted(rows, key=lambda r: r["score"], reverse=True)[:limit]
        print(json.dumps(frios, ensure_ascii=False, default=str, indent=2))
    else:
        print(render_md(rows, limit))


if __name__ == "__main__":
    main()
