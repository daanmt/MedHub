"""day_plan.py — Plano do Dia (read-only) para o boot proativo.

Compõe, SEM escrever nada: tema dormente do dia, volume vs ritmo-alvo (ENAMED),
fila FSRS (vencidos + backlog), dica do cronograma e uma sugestão de passo
imediato. O boot (AGENTE §2 passo 4) roda isto e lidera com o plano.

Reusa: dormant_refresh.pick (dormência), performance.get_totais/_questoes_do_mes/MARCOS
(volume/ritmo), app.utils.db (fila FSRS). Não duplica constantes de meta.

Uso: python tools/day_plan.py [--json]
"""
import argparse
import importlib
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


META_PROVA = 10000   # meta-prova ENAMED (decisão s093/ESTADO); 12k = teto/stretch

# Política de teto dinâmico (F4 -- decisão do operador 2026-07-05).
# Norma: core/contracts/fsrs-management-contract.md §Teto dinâmico.
TETO_BASE = 30            # cards/dia fora do regime de dívida
CAP_MULTIPLICADOR = 2     # teto_efetivo nunca excede CAP_MULTIPLICADOR * TETO_BASE


def _teto_efetivo(atrasados):
    """Teto do dia: regime de dívida quando atrasados > TETO_BASE; o teto sobe
    até o cap para drenar (na prática, dobra até a dívida zerar)."""
    if atrasados > TETO_BASE:
        return min(TETO_BASE + atrasados, CAP_MULTIPLICADOR * TETO_BASE)
    return TETO_BASE


def _cronograma_hint():
    """Fallback legado: 1ª linha numerada de '## Próximos passos' do ESTADO (frágil)."""
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


def _semana_conteudo():
    """Ponteiro de semana de CONTEÚDO (HANDOFF > ESTADO). Marca canônica: 'Próxima = SNN'.
    O usuário segue por conteúdo, atrás do calendário nominal — este é o ponteiro textual
    permitido pelo contrato (ultraplan §d.2). None se ausente."""
    for fn in ("HANDOFF.md", "ESTADO.md"):
        try:
            txt = open(os.path.join(ROOT, fn), encoding="utf-8").read()
        except Exception:
            continue
        m = re.search(r"Pr[óo]xima\s*=\s*(?:Semana\s*)?S?\s*(\d+)", txt)
        if m:
            return int(m.group(1))
    return None


def _cronograma_hoje(total_q, hoje):
    """Substitui _cronograma_hint: lê a grade (cronograma.py) e cruza com a posição real.
    Read-only. Retorna None se a grade não existir (degradação graciosa → fallback hint)."""
    try:
        import cronograma as cr
        grade = cr.load_grade()
    except Exception:
        return None
    nominal = cr.semana_corrente(grade, hoje)
    conteudo = _semana_conteudo() or nominal
    wk = cr.get_semana(grade, conteudo)
    if not wk:
        return None
    enamed = datetime.strptime(cr.ENAMED, "%Y-%m-%d").date()
    dias = (enamed - hoje).days  # dias de estudo: hoje inclusive, dia da prova exclusivo
    restante = sum(s["total_questoes"] for s in grade["semanas"] if s["semana"] >= conteudo)
    return {
        "conteudo": conteudo,
        "nominal": nominal,
        "lag": (nominal - conteudo) if (nominal and conteudo and nominal > conteudo) else None,
        "previstas": wk["total_questoes"],
        "n_tasks": wk["n_tasks"],
        "temas": [t["tema"] for t in wk["tasks"] if t.get("tema")][:3],
        "temas_material": [f"{t['tema']} ({t.get('material_indicado', 'resumo')})" for t in wk["tasks"] if t.get("tema")][:3],
        "dias_enamed": dias,
        "ritmo_cronograma": round(restante / dias, 1) if dias > 0 else None,
        "ritmo_meta": round(max(0, META_PROVA - total_q) / dias, 1) if dias > 0 else None,
    }


# ---------------------------------------------------------------------------
# Revisão Calibrada — inferência da nota de dificuldade (read-only).
# infer_nota() é determinística e só lê sinais FRIOS independentes da própria
# saída (anti-circularidade, PRD §7.6). day_plan NÃO escreve estado: a
# persistência da nota é feita na abertura de task (skill /revisar), não aqui.
# Norma: core/contracts/revisao-calibrada-contract.md.
# ---------------------------------------------------------------------------

DEGRAU_PARAGRAFOS = {"D10": (7, 9), "D8": (5, 6), "D5": (3, 4), "D2": (1, 2)}


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def _degrau_de(nota):
    """Mapa nota→degrau de registro (PRD §4.6)."""
    if nota >= 9:
        return "D10"
    if nota >= 7:
        return "D8"
    if nota >= 4:
        return "D5"
    return "D2"


def _divergencia(nota_usuario, nota_inferida):
    """Divergência auto-nota × inferência (PRD §4.4). None se |Δ|<3 ou sem nota do usuário."""
    if nota_usuario is None or abs(nota_usuario - nota_inferida) < 3:
        return None
    return {"usuario": nota_usuario, "inferida": nota_inferida,
            "delta": nota_usuario - nota_inferida}


def infer_nota(sinais):
    """Nota de dificuldade inferida (1-10). Determinística — PRD §7.3.

    `sinais`: dict com acerto_hist (None se 0q), acerto_bloco (None se inexistente),
    score_dorm (float), leu_tema (bool), prevalencia ('alta'|'media'|'baixa').
    Só sinais FRIOS independentes da saída (§7.6): nunca a profundidade da
    preparação nem o acerto "morno" pós-PREPARAR.
    """
    acerto_hist = sinais.get("acerto_hist")
    acerto_bloco = sinais.get("acerto_bloco")
    score_dorm = sinais.get("score_dorm")
    leu_tema = bool(sinais.get("leu_tema"))
    prevalencia = sinais.get("prevalencia") or "media"

    # eixo 1 — performance histórica define a BASE
    if acerto_hist is None and not leu_tema:
        base = 9                      # estreia pura → onboarding
    elif acerto_hist is None:
        base = 6                      # leu, sem volume registrado
    elif acerto_hist < 50:
        base = 8
    elif acerto_hist < 65:
        base = 7
    elif acerto_hist < 80:
        base = 5
    else:
        base = 3                      # >= 80%

    # eixo 2 — frieza (dormência) empurra p/ cima; quente puxa p/ baixo.
    # score_dorm None = sinal AUSENTE (≠ quente) → eixo neutro.
    if score_dorm is not None:
        if score_dorm >= 40:
            base += 2
        elif score_dorm >= 25:
            base += 1
        elif score_dorm < 7:
            base -= 1

    # eixo 3 — último bloco fraco confirma dificuldade VIVA
    if acerto_bloco is not None and acerto_bloco < 60:
        base += 1

    # eixo 4 — prevalência ENAMED = piso de banca, não teto (neutro hoje §7.7)
    if prevalencia == "baixa":
        base -= 1
    nota = _clamp(base, 1, 10)
    if prevalencia == "alta":
        nota = max(nota, 4)
    return nota


def montar_sinais(area, tema):
    """Coleta os sinais frios de um tema do db/radar (read-only). PRD §7.3/§7.6."""
    stats = db.get_tema_stats(area, tema)
    acerto_hist = stats["percentual"] if (stats and stats.get("questoes")) else None
    acerto_bloco = db.get_ultimo_bloco_tema(area, tema)

    score_dorm = None       # None = sem sinal de dormência (≠ quente)
    try:
        import review_radar
        for r in review_radar.coletar(area=area):
            if r.get("tema") == tema:
                score_dorm = r.get("score")
                break
    except Exception:
        pass

    last = db.get_theme_last_review(area=area, tema=tema)
    leu = bool(last and last.get("last_review"))
    if not leu:
        try:
            gtc = importlib.import_module("app.engine.get_topic_context")
            leu = gtc._find_resumo(tema) is not None
        except Exception:
            pass

    return {
        "acerto_hist": acerto_hist,
        "acerto_bloco": acerto_bloco,
        "score_dorm": score_dorm,
        "leu_tema": leu,
        "prevalencia": "media",       # §7.7: grade.json ainda não tem prevalencia_enamed
    }


def _proposito(area, tema):
    """exercicios (amplo) vs flashcards (direcionado). Cluster vencido → flashcards. PRD §5.2/§7.4."""
    try:
        q = db.get_cards_by_bucket(area=area, tema=tema)
        vencidos = len(q.get("atrasados", [])) + len(q.get("hoje", []))
    except Exception:
        vencidos = 0
    return ("flashcards" if vencidos >= 3 else "exercicios"), vencidos


def _norm_tema(s):
    """Normaliza um tema p/ igualdade: casefold + trim + colapso de espaços."""
    return " ".join((s or "").casefold().split())


def _material_do_tema(tema):
    """material_indicado da grade por igualdade normalizada (C1). 'resumo' se ausente.

    Igualdade normalizada (não substring): substring com string vazia era a raiz do C1
    (tema vazio casava qualquer tema; o `break` interno deixava semanas seguintes
    sobrescreverem). Ignora temas vazios e faz early-return no 1º match — determinístico.
    """
    try:
        import cronograma as cr
        grade = cr.load_grade()
    except Exception:
        return "resumo"
    alvo = _norm_tema(tema)
    if not alvo:
        return "resumo"
    for s in grade["semanas"]:
        for t in s["tasks"]:
            tt = t.get("tema", "")
            if tt and _norm_tema(tt) == alvo:
                return t.get("material_indicado", "resumo")
    return "resumo"


def difficulty_report(area, tema):
    """Proposta read-only de nota/degrau/proposito p/ a abertura de task (PRD R3/R4).

    Regra D10 (extensivo): material extensivo ou inferência sem nota explícita → degrau D10 + dever de Deep-Researchness; a nota explícita do usuário (fonte=usuario) sempre vence (precedência input > pergunta > inferência).
    """
    sinais = montar_sinais(area, tema)
    nota_inferida = infer_nota(sinais)
    d = db.get_dificuldade(area, tema)
    nota_usuario = d["nota"] if (d and d.get("nota") is not None) else None
    fonte = d["fonte"] if d else None
    nota_efetiva = nota_usuario if nota_usuario is not None else nota_inferida

    mat = _material_do_tema(tema)

    # G5: nota explícita do usuário NUNCA é sobrescrita. Só quando NÃO há nota explícita
    # o extensivo aplica floor 9 (degrau D10, não D8) + dispara o dever de Deep-Researchness.
    deep_research = False
    if mat == "extensivo" and nota_usuario is None:
        nota_efetiva = max(nota_inferida, 9)
        deep_research = True

    degrau = _degrau_de(nota_efetiva)
    proposito, vencidos = _proposito(area, tema)
    largura = ("amplo (escopo do cronograma)" if proposito == "exercicios"
               else "direcionado (cluster vencido)")
    passo = (f"Revisar {tema} como dif-{nota_efetiva} ({degrau}) [Material: {mat}], PREPARAR "
             f"{'descomprimido' if nota_efetiva >= 7 else 'comprimido'}+mecanismo, "
             f"{largura}; depois DRENAR.")
    return {
        "area": area, "tema": tema,
        "nota_usuario": nota_usuario, "nota_fonte": fonte,
        "nota_inferida": nota_inferida, "nota_efetiva": nota_efetiva,
        "degrau": degrau, "paragrafos": list(DEGRAU_PARAGRAFOS[degrau]),
        "divergencia": _divergencia(nota_usuario, nota_inferida),
        "proposito": proposito, "cards_vencidos": vencidos,
        "material_indicado": mat,
        "deep_research": deep_research,
        "sinais": sinais,
        "sugestao_passo": passo,
    }


def build():
    con = db.get_connection()
    total_q, total_a = get_totais(con)
    hoje = date.today()
    q_mes = get_questoes_do_mes(con, hoje.strftime("%Y-%m"))
    q_hoje = con.cursor().execute(
        "SELECT COALESCE(SUM(questoes_feitas),0) FROM sessoes_bulk "
        "WHERE area <> 'Simulado' AND data_sessao = ?",  # s099: simulado não conta como feita
        (hoje.isoformat(),)).fetchone()[0]
    _nome, alvo, data_marco = MARCOS[0]            # ENAMED 12000 @ 13/09/2026
    faltam = max(0, alvo - (total_q or 0))
    dias = (data_marco - hoje).days  # hoje inclusive, dia da prova exclusivo
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
        "divida": {
            "atrasados": fsrs["atrasados"],
            "regime_divida": fsrs["atrasados"] > TETO_BASE,
            "teto_base": TETO_BASE,
            "teto_efetivo": _teto_efetivo(fsrs["atrasados"]),
        },
        "cronograma": _cronograma_hoje(total_q or 0, hoje),
        "cronograma_hint": _cronograma_hint(),   # fallback se a grade não existir
        "sugestao_passo": passo,
    }


def review_plan(new_limit=10):
    """Clusters do dia derivados da fila real (F3) -- read-only.

    Mesma fonte da fila (get_cards_by_bucket, mesmo new_limit default do
    fsrs_queue): a contagem não pode divergir do que --list entrega. Mata a
    classe de erro de contagem manual observada na s108 (3x).
    """
    buckets = db.get_cards_by_bucket(new_limit=new_limit)
    clusters = {}
    for nome in ("atrasados", "hoje", "novos"):
        for card in buckets.get(nome, []):
            chave = (card.get("area") or "(sem area)", card.get("tema") or "(sem tema)")
            c = clusters.setdefault(chave, {"area": chave[0], "tema": chave[1],
                                            "atrasados": 0, "hoje": 0, "novos": 0,
                                            "total": 0})
            c[nome] += 1
            c["total"] += 1
    return sorted(clusters.values(),
                  key=lambda c: (-(c["atrasados"] + c["hoje"]), -c["total"],
                                 c["area"], c["tema"]))


def render_review_plan(clusters):
    if not clusters:
        return "# 📋 Plano de Revisão — fila vazia"
    total = sum(c["total"] for c in clusters)
    out = [f"# 📋 Plano de Revisão — {total} cards em {len(clusters)} cluster(s)", ""]
    for c in clusters:
        partes = [f"{c[b]} {b}" for b in ("atrasados", "hoje", "novos") if c[b]]
        out.append(f"- **{c['area']} · {c['tema']}** — {c['total']} card(s): {', '.join(partes)}")
    return "\n".join(out)


def render_handoff_block(p):
    """Bloco numerico 'Estado por frente' derivado do db (F6 -- AUDITORIA_MEDHUB).

    ASCII puro, pronto para colar no HANDOFF.md. So numeros derivados: o texto
    qualitativo (proximo tema, gaps, pendencias) continua manual no fechamento.
    """
    v, f = p["volume"], p["fsrs"]
    perf = round(v["acertos"] / v["total"] * 100, 1) if v["total"] else 0.0
    return "\n".join([
        f"- **Volume & Metas:** {v['total']} / {v['alvo_enamed']} (perf. ~{perf}%). "
        f"Hoje: {v['hoje']}. Ritmo-alvo ~{v['ritmo_alvo']}q/dia "
        f"({v['dias_ate_marco']}d p/ ENAMED).",
        f"- **FSRS:** {f['atrasados']} atrasados + {f['hoje']} hoje. "
        f"Backlog: {f['backlog_novos']} novos.",
    ])


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
    dv = p["divida"]
    regime = " · **REGIME DE DÍVIDA** (teto sobe até drenar)" if dv["regime_divida"] else ""
    out.append(f"- 🎯 **Teto do dia:** {dv['teto_efetivo']} cards (base {dv['teto_base']}{regime})")
    c = p.get("cronograma")
    if c:
        lag = f" · calendário em S{c['nominal']} (~{c['lag']} sem atrás)" if c.get("lag") else ""
        out.append(f"- 🧭 **Cronograma:** conteúdo **S{c['conteudo']}** · {c['previstas']}q previstas "
                   f"· {c['n_tasks']} tasks{lag}")
        if c["temas"]:
            out.append(f"    • próximos temas: {', '.join(c.get('temas_material', c['temas']))}")
        out.append(f"    • ritmos-alvo: terminar a grade ~{c['ritmo_cronograma']}/dia · "
                   f"meta-prova {META_PROVA // 1000}k ~{c['ritmo_meta']}/dia ({c['dias_enamed']}d p/ ENAMED)")
    elif p.get("cronograma_hint"):
        out.append(f"- 🧭 **Cronograma:** {p['cronograma_hint'][:120]}")
    out.append(f"- ▶️ **Passo sugerido:** {p['sugestao_passo']}")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Plano do Dia (read-only).")
    ap.add_argument("--json", action="store_true", help="Saída JSON crua")
    ap.add_argument("--handoff-block", action="store_true", dest="handoff_block",
                    help="Emite o bloco numérico 'Estado por frente' derivado do db, "
                         "pronto para colar no HANDOFF.md (F6: número digitado vira derivado)")
    ap.add_argument("--review-plan", action="store_true", dest="review_plan",
                    help="Emite os clusters do dia (area/tema + contagem por bucket) "
                         "derivados da fila real (F3); com --json, sai o agregado cru")
    ap.add_argument("--difficulty", nargs=2, metavar=("AREA", "TEMA"),
                    help="Reporta nota inferida + degrau + proposito de um tema (read-only)")
    args = ap.parse_args()
    if args.handoff_block:
        print(render_handoff_block(build()))
        return
    if args.review_plan:
        clusters = review_plan()
        print(json.dumps(clusters, ensure_ascii=False, indent=2) if args.json
              else render_review_plan(clusters))
        return
    if args.difficulty:
        area, tema = args.difficulty
        print(json.dumps(difficulty_report(area, tema), ensure_ascii=False,
                         default=str, indent=2))
        return
    p = build()
    print(json.dumps(p, ensure_ascii=False, default=str, indent=2) if args.json else render(p))


if __name__ == "__main__":
    main()
