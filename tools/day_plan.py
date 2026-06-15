"""day_plan.py — Plano do Dia (read-only) para o boot proativo.

Compõe, SEM escrever nada: tema dormente do dia, volume vs ritmo-alvo (ENAMED),
fila FSRS (vencidos + backlog), dica do cronograma e uma sugestão de passo
imediato. O boot (AGENTE §2 passo 4) roda isto e lidera com o plano.

Reusa: dormant_refresh.pick (dormência), performance.get_totais/_questoes_do_mes/MARCOS
(volume/ritmo), app.utils.db (fila FSRS). Não duplica constantes de meta.

Uso: python tools/day_plan.py [--json]
"""
import argparse
import json
import os
import re
import sys
from datetime import date, datetime

try:                                   # UTF-8 no console cp1252 do Windows
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import app.utils.db as db                                     # noqa: E402
import dormant_refresh as dr                                  # noqa: E402
from performance import get_totais, get_questoes_do_mes, MARCOS  # noqa: E402


def _fsrs_counts(con):
    now = datetime.now()
    ts = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat(" ")
    te = now.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat(" ")
    base = ("FROM fsrs_cards fc JOIN flashcards f ON f.id=fc.card_id "
            "WHERE COALESCE(f.needs_qualitative,0) < 2")
    cur = con.cursor()

    def c(extra, *p):
        return cur.execute(f"SELECT COUNT(*) {base} {extra}", p).fetchone()[0]

    return {
        "atrasados": c("AND fc.state>0 AND fc.due < ?", ts),
        "hoje": c("AND fc.state>0 AND fc.due >= ? AND fc.due <= ?", ts, te),
        "backlog_novos": c("AND fc.state = 0"),
    }


def _cronograma_hint():
    try:
        with open(os.path.join(ROOT, "ESTADO.md"), encoding="utf-8") as fh:
            txt = fh.read()
    except Exception:
        return None
    m = re.search(r'##\s*Pr[óo]ximos passos(.*?)(?:\n##\s|\Z)', txt, re.S)
    if not m:
        return None
    lm = re.search(r'^\s*\d+\.\s*(.+)$', m.group(1), re.M)
    return lm.group(1).strip() if lm else None


def build():
    con = db.get_connection()
    total_q, total_a = get_totais(con)
    hoje = date.today()
    q_mes = get_questoes_do_mes(con, hoje.strftime("%Y-%m"))
    q_hoje = con.cursor().execute(
        "SELECT COALESCE(SUM(questoes_feitas),0) FROM sessoes_bulk WHERE data_sessao = ?",
        (hoje.isoformat(),)).fetchone()[0]
    _nome, alvo, data_marco = MARCOS[0]            # ENAMED 12000 @ 13/09/2026
    faltam = max(0, alvo - (total_q or 0))
    dias = (data_marco - hoje).days + 1
    ritmo_alvo = round(faltam / dias, 1) if dias > 0 else None
    fsrs = _fsrs_counts(con)
    con.close()

    dormant = dr.pick()
    vencidos = fsrs["atrasados"] + fsrs["hoje"]
    if (q_hoje or 0) == 0:
        passo = "Quebrar o zero do dia: bloco de questões da área prioritária (refresh pré-bloco antes)."
    elif vencidos > 0:
        passo = f"Revisar {vencidos} cards vencidos (/revisar) + seguir com questões."
    else:
        passo = "Seguir o cronograma: próximo tema previsto + questões."

    return {
        "data": hoje.isoformat(),
        "dormant": dormant,
        "volume": {
            "total": total_q or 0, "acertos": total_a or 0,
            "hoje": q_hoje or 0, "mes": q_mes or 0,
            "alvo_enamed": alvo, "faltam": faltam,
            "dias_ate_marco": dias, "ritmo_alvo": ritmo_alvo,
        },
        "fsrs": fsrs,
        "cronograma_hint": _cronograma_hint(),
        "sugestao_passo": passo,
    }


def render(p):
    d, v, f = p["dormant"], p["volume"], p["fsrs"]
    out = [f"# 🗓️ Plano do Dia — {p['data']}", ""]
    if d.get("empty"):
        out.append("- 🌡️ **Refrescar (dormente):** nenhum tema elegível.")
    else:
        out.append(f"- 🌡️ **Refrescar (dormente):** {d['tema']} ({d['area']} · "
                   f"{d['dias_sem_revisar']}d sem rever · {d['n_cards']} cards · {d.get('perf') or '—'}%)")
    out.append(f"- 📊 **Volume:** {v['total']} acum. · hoje {v['hoje']} · faltam {v['faltam']} "
               f"p/ ENAMED em {v['dias_ate_marco']}d → ritmo-alvo ~{v['ritmo_alvo']}q/dia")
    out.append(f"- 🔁 **FSRS:** {f['atrasados']} atrasados + {f['hoje']} hoje + "
               f"{f['backlog_novos']} novos (backlog)")
    if p["cronograma_hint"]:
        out.append(f"- 🧭 **Cronograma:** {p['cronograma_hint'][:120]}")
    out.append(f"- ▶️ **Passo sugerido:** {p['sugestao_passo']}")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Plano do Dia (read-only).")
    ap.add_argument("--json", action="store_true", help="Saída JSON crua")
    args = ap.parse_args()
    p = build()
    print(json.dumps(p, ensure_ascii=False, default=str, indent=2) if args.json else render(p))


if __name__ == "__main__":
    main()
