"""day_plan.py — Plano do Dia para o boot proativo.

Compõe: tema dormente do dia, volume vs ritmo-alvo (ENAMED), fila FSRS
(vencidos + backlog), dica do cronograma e uma sugestão de passo imediato.
O boot (AGENTE §2 passo 4) roda isto e lidera com o plano.

Escritas (únicas, ambas de metadado de processo): a condição declarada do dia
(condicao_dia via db.registrar_condicao_dia) e o PLANO recomendado do dia
(plano_dia via persistir_plano — spec telemetria-estudo-part-1; o realizado já
vive em fsrs_revlog/review_log/sessoes_bulk, o planejado agora sobrevive para a
aderência planejado×real). Todo o resto permanece read-only; --no-persist simula.

Reusa: dormant_refresh.pick (dormência), performance.get_totais/_questoes_do_mes/MARCOS
(volume/ritmo), app.utils.db (fila FSRS). Não duplica constantes de meta.

Uso: python tools/day_plan.py [--json]
"""
import argparse
import glob
import importlib
import json
import math
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

# Recomendador do dia (PRD orquestracao part-2).
# Norma e significado de cada parâmetro: core/contracts/orquestracao-contract.md
# (a tabela de parâmetros do contrato espelha ESTES nomes/valores — paridade testada).
JANELA_RITMO_DIAS = 14            # janela móvel do ritmo real (q/dia)
TEMPO_DEFAULT_H = 4.0             # horas assumidas sem --tempo
ENERGIA_DEFAULT = "media"         # energia assumida sem --energia
QUESTOES_POR_HORA = 15            # conversão tempo -> capacidade de questões
LIMIAR_FOLGA_DESCANSO_DIAS = 3    # folga projetada mínima p/ descanso com energia baixa
PERIODO_SIMULADO_SEMANAS = 4      # slot de simulado a cada N semanas de conteúdo
FRESCOS_JANELA_HORAS = 48         # janela do mini-drill anti-reincidência
FSRS_LEVE_CAP = 15                # cap de cards no dia leve/descanso
FATOR_ENERGIA = {"alta": 1.0, "media": 0.85, "baixa": 0.6}  # modula a capacidade


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


def _resolver_semana_conteudo():
    """Posição SSOT db-first (PRD orquestracao part-1): preparacao_estado > texto
    (deprecado, WARN em stderr) > None. Retorna (semana|None, fonte) com fonte em
    {'db', 'texto', None}. O WARN vai a stderr para não poluir stdout/--json."""
    try:
        s = db.get_semana_conteudo()
    except Exception:
        s = None
    if s is not None:
        return s, "db"
    s = _semana_conteudo()
    if s is not None:
        print("[WARN] POSICAO_VIA_TEXTO (deprecado): semana de conteudo lida por regex "
              "de HANDOFF/ESTADO. Registre a posicao SSOT com: "
              "python tools/preparacao.py --set-semana %d" % s, file=sys.stderr)
        return s, "texto"
    return None, None


def _conclusao_drive():
    """Snapshot de conclusão real + ordem do xlsx do Drive (preparacao_estado.cronograma_conclusao_drive,
    gravado por `python tools/cronograma.py --sync-drive`). Read-only, sem MCP aqui — day_plan
    só consome o que o agente já sincronizou no boot. Retorna dict:
    by_task = {(semana, tarefa): concluido} ou None se ausente/corrompido;
    ordem_by_task = {(semana, tarefa): ordem_xlsx} (vazio se snapshot antigo sem 'ordem' -> fallback PDF);
    fresco = True só se atualizado_em é do dia-calendário corrente (W8/reconcile-contract);
    atualizado_em = 'YYYY-MM-DD' da última sync ou None."""
    vazio = {"by_task": None, "ordem_by_task": {}, "fresco": False, "atualizado_em": None}
    try:
        item = db.get_preparacao("cronograma_conclusao_drive")
    except Exception:
        return vazio
    if not item:
        return vazio
    try:
        snap = json.loads(item["valor"])
        tasks = snap.get("tasks", [])
        by_task = {(t["semana"], t["tarefa"]): t["concluido"] for t in tasks}
        ordem_by_task = {(t["semana"], t["tarefa"]): t["ordem"] for t in tasks
                         if t.get("ordem") is not None}
    except Exception:
        return vazio
    data_sync = (item.get("atualizado_em") or "")[:10] or None
    fresco = data_sync == date.today().isoformat()
    return {"by_task": by_task, "ordem_by_task": ordem_by_task,
            "fresco": fresco, "atualizado_em": data_sync}


def _ordenar_por_drive(tasks, ordem_by_task, semana):
    """Ordena as tasks da semana pela ordem real do xlsx do Drive (ordem_by_task).
    Estável: tasks sem ordem conhecida vão para o fim, preservando a ordem do
    grade.json (PDF). Sem ordem_by_task -> identidade (fallback PDF puro, DoD 3)."""
    if not ordem_by_task:
        return tasks
    return sorted(tasks, key=lambda t: ordem_by_task.get((semana, t["tarefa"]), 10 ** 6))


def _cronograma_hoje(total_q, hoje):
    """Substitui _cronograma_hint: lê a grade (cronograma.py) e cruza com a posição real.
    Read-only. Retorna None se a grade não existir (degradação graciosa → fallback hint)."""
    try:
        import cronograma as cr
        grade = cr.load_grade()
    except Exception:
        return None
    nominal = cr.semana_corrente(grade, hoje)
    conteudo, fonte_pos = _resolver_semana_conteudo()
    if conteudo is None:
        conteudo, fonte_pos = nominal, "nominal"
    wk = cr.get_semana(grade, conteudo)
    if not wk:
        return None
    enamed = datetime.strptime(cr.ENAMED, "%Y-%m-%d").date()
    dias = (enamed - hoje).days  # dias de estudo: hoje inclusive, dia da prova exclusivo
    restante = sum(s["total_questoes"] for s in grade["semanas"] if s["semana"] >= conteudo)

    # W8: fronteira REAL de conclusão (xlsx riscado) em vez de só posição calendário.
    # Sem snapshot fresco -> degradação graciosa pro comportamento antigo (lista a semana
    # inteira) + sinaliza conclusao_desatualizada pro render() avisar (nunca falha silente).
    drive = _conclusao_drive()
    conclusao_by_task = drive["by_task"]
    tasks_semana = wk["tasks"]
    conclusao_desatualizada = True
    if conclusao_by_task is not None and drive["fresco"]:
        conclusao_desatualizada = False
        tasks_semana = [t for t in wk["tasks"]
                        if not conclusao_by_task.get((wk["semana"], t["tarefa"]), False)]
        # ordena pela ordem real do xlsx (o usuário reordena à mão); fallback = ordem do PDF
        tasks_semana = _ordenar_por_drive(tasks_semana, drive["ordem_by_task"], wk["semana"])
    drive_data = drive["atualizado_em"]
    drive_dias = (hoje - date.fromisoformat(drive_data)).days if drive_data else None

    return {
        "conteudo": conteudo,
        "nominal": nominal,
        "posicao_fonte": fonte_pos,
        "lag": (nominal - conteudo) if (nominal and conteudo and nominal > conteudo) else None,
        "previstas": wk["total_questoes"],
        "n_tasks": wk["n_tasks"],
        "temas": [t["tema"] for t in tasks_semana if t.get("tema")][:3],
        "temas_material": [f"{t['tema']} ({_material_efetivo(t['tema'], t.get('material_indicado', 'resumo'))})" for t in tasks_semana if t.get("tema")][:3],
        "conclusao_desatualizada": conclusao_desatualizada,
        "drive_sync_data": drive_data,
        "drive_sync_dias": drive_dias,
        "dias_enamed": dias,
        "restante_q": restante,
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


def _material_efetivo(tema, material):
    """F30: se o cronograma diz 'resumo' mas o .md nao existe, rebaixa para
    'extensivo' -- nao prometer "so ler o resumo" quando ele nao existe (tema-zero
    mascarado). Read-only; reusa o resolver `_find_resumo` (indexa stem desde s096).
    Qualquer falha na resolucao -> mantem o rotulo original (nunca quebra o boot)."""
    if material != "resumo":
        return material
    try:
        gtc = importlib.import_module("app.engine.get_topic_context")
        if gtc._find_resumo(tema) is None:
            return "extensivo"
    except Exception:
        pass
    return material


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

    mat = _material_efetivo(tema, _material_do_tema(tema))   # F30: rebaixa se o .md nao existe

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


def recomendar_dia(sinais, tempo_h=None, energia=None):
    """Recomendador do dia (PRD orquestracao part-2) — função de decisão
    DETERMINÍSTICA e PURA: dict de sinais derivados -> estrutura de blocos.
    Nenhum acesso a db/arquivo aqui (testável por fixtures). Regras R1-R5 e
    parâmetros nomeados: core/contracts/orquestracao-contract.md.
    """
    defaults_assumidos = tempo_h is None and energia is None
    tempo_h = TEMPO_DEFAULT_H if tempo_h is None else float(tempo_h)
    energia = (energia or ENERGIA_DEFAULT).lower()
    fator = FATOR_ENERGIA.get(energia, FATOR_ENERGIA[ENERGIA_DEFAULT])
    capacidade_q = int(tempo_h * QUESTOES_POR_HORA * fator)

    dias = sinais.get("dias_enamed") or 0
    restante = sinais.get("restante_grade_q") or 0
    ritmo_real = sinais.get("ritmo_real") or 0.0
    ritmo_nec = round(restante / dias, 1) if dias > 0 else None
    if restante <= 0:
        dias_p_fechar, folga_dias = 0, dias
    elif ritmo_real > 0:
        dias_p_fechar = math.ceil(restante / ritmo_real)
        folga_dias = dias - dias_p_fechar
    else:
        dias_p_fechar, folga_dias = None, None  # sem ritmo medido na janela
    projecao = {"ritmo_real": ritmo_real, "ritmo_necessario": ritmo_nec,
                "dias_para_fechar": dias_p_fechar, "folga_dias": folga_dias,
                "janela_dias": JANELA_RITMO_DIAS}

    blocos, just = [], []
    contexto = {"tempo_h": tempo_h, "energia": energia, "capacidade_q": capacidade_q}
    frescos = sinais.get("frescos_tema_alvo") or []
    tema_alvo = sinais.get("tema_alvo")
    vencidos = sinais.get("vencidos") or 0
    teto = sinais.get("teto_efetivo") or TETO_BASE

    # R1 — anti-reincidência primeiro: cards de erro frescos do tema-alvo
    if frescos:
        blocos.append({"tipo": "mini-drill", "qtd": len(frescos), "alvo": tema_alvo,
                       "motivo": "card(s) de erro frescos (<%dh) no tema-alvo"
                                 % FRESCOS_JANELA_HORAS})
        just.append("reincidência: %d card(s) frescos de %s" % (len(frescos), tema_alvo))

    # R2 — descanso: energia baixa + folga projetada acima do limiar
    if energia == "baixa" and folga_dias is not None and folga_dias >= LIMIAR_FOLGA_DESCANSO_DIAS:
        blocos.append({"tipo": "descanso", "qtd": 0, "alvo": None,
                       "motivo": "energia baixa + folga projetada de %dd (limiar %dd)"
                                 % (folga_dias, LIMIAR_FOLGA_DESCANSO_DIAS)})
        if vencidos > 0:
            blocos.append({"tipo": "fsrs", "qtd": min(teto, FSRS_LEVE_CAP, vencidos),
                           "alvo": "vencidos", "motivo": "revisão leve (dia de descanso)"})
        just.append("descanso permitido: folga %dd >= %dd e energia baixa — sem tema novo hoje"
                    % (folga_dias, LIMIAR_FOLGA_DESCANSO_DIAS))
        just.append("ritmo real %.1fq/dia vs necessário %sq/dia (janela %dd)"
                    % (ritmo_real, ritmo_nec, JANELA_RITMO_DIAS))
        return {"blocos": blocos, "justificativa": just, "projecao": projecao,
                "defaults_assumidos": defaults_assumidos, "contexto": contexto}

    # R3 — simulado periódico (usa a área 'Simulado' já existente no registro)
    semana = sinais.get("semana_conteudo")
    if semana and semana % PERIODO_SIMULADO_SEMANAS == 0:
        blocos.append({"tipo": "simulado", "qtd": 1, "alvo": "Simulado",
                       "motivo": "slot periódico (semana S%d, a cada %d semanas)"
                                 % (semana, PERIODO_SIMULADO_SEMANAS)})
        just.append("semana S%d é múltipla de %d: slot de simulado"
                    % (semana, PERIODO_SIMULADO_SEMANAS))

    # R4 — questões da grade: alvo = min(capacidade do dia, ritmo necessário);
    # atrasado (folga negativa) => capacidade máxima do dia
    alvo_q = capacidade_q if ritmo_nec is None else min(capacidade_q,
                                                        max(int(math.ceil(ritmo_nec)), 1))
    if folga_dias is not None and folga_dias < 0:
        alvo_q = capacidade_q
        just.append("grade atrasada (%dd de déficit projetado): capacidade máxima em questões"
                    % -folga_dias)
    if alvo_q > 0 and restante > 0:
        blocos.append({"tipo": "questoes", "qtd": alvo_q,
                       "alvo": tema_alvo or "próximo tema da semana",
                       "motivo": "necessário %sq/dia; capacidade ~%dq (%.1fh x %d q/h x %.2f)"
                                 % (ritmo_nec, capacidade_q, tempo_h, QUESTOES_POR_HORA, fator)})
    just.append("ritmo real %.1fq/dia vs necessário %sq/dia (janela %dd)"
                % (ritmo_real, ritmo_nec, JANELA_RITMO_DIAS))

    # R5 — FSRS até o teto efetivo (F4 governa a dívida)
    fsrs_qtd = min(teto, vencidos + 15)
    if fsrs_qtd > 0:
        blocos.append({"tipo": "fsrs", "qtd": fsrs_qtd, "alvo": "fila do dia",
                       "motivo": "teto efetivo %d (dívida: %d vencidos)" % (teto, vencidos)})
    just.append("dívida FSRS: %d vencidos; teto %d; backlog %d novos"
                % (vencidos, teto, sinais.get("backlog_novos") or 0))
    if sinais.get("lag"):
        just.append("posição: conteúdo S%s (%s sem atrás do calendário)"
                    % (semana, sinais["lag"]))

    return {"blocos": blocos, "justificativa": just, "projecao": projecao,
            "defaults_assumidos": defaults_assumidos, "contexto": contexto}


def build(tempo_h=None, energia=None):
    con = db.get_connection()
    total_q, total_a = get_totais(con)
    hoje = date.today()
    q_mes = get_questoes_do_mes(con, hoje.strftime("%Y-%m"))
    q_hoje = con.cursor().execute(
        "SELECT COALESCE(SUM(questoes_feitas),0) FROM sessoes_bulk "
        "WHERE area <> 'Simulado' AND data_sessao = ?",  # s099: simulado não conta como feita
        (hoje.isoformat(),)).fetchone()[0]
    _nome, alvo, data_marco = MARCOS[0]            # ENAMED meta-prova 10000 @ 13/09/2026
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

    cron = _cronograma_hoje(total_q or 0, hoje)

    # Sinais do recomendador (part-2) — todos derivados; falha de um sinal não
    # derruba o plano (degradação graciosa, mesmo espírito do cronograma).
    temas_semana = (cron or {}).get("temas") or []
    tema_alvo = temas_semana[0] if temas_semana else None
    try:
        ritmo_real = db.get_ritmo_real(JANELA_RITMO_DIAS)
    except Exception:
        ritmo_real = 0.0
    try:
        frescos = (db.get_fresh_error_cards(tema=tema_alvo, janela_horas=FRESCOS_JANELA_HORAS)
                   if tema_alvo else [])
    except Exception:
        frescos = []
    sinais = {
        "dias_enamed": (cron or {}).get("dias_enamed") or dias,
        "restante_grade_q": (cron or {}).get("restante_q") or 0,
        "ritmo_real": ritmo_real,
        "vencidos": vencidos,
        "teto_efetivo": _teto_efetivo(fsrs["atrasados"]),
        "backlog_novos": fsrs["backlog_novos"],
        "semana_conteudo": (cron or {}).get("conteudo"),
        "lag": (cron or {}).get("lag"),
        "tema_alvo": tema_alvo,
        "frescos_tema_alvo": frescos,
    }

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
        "cronograma": cron,
        "cronograma_hint": _cronograma_hint(),   # fallback se a grade não existir
        "sugestao_passo": passo,
        "recomendacao": recomendar_dia(sinais, tempo_h=tempo_h, energia=energia),
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

    # Sinal de frieza por cluster (F5) -- score de dormência do review_radar.
    # Fallback silencioso: radar indisponível -> frieza=None (day_plan segue
    # read-only e resiliente; o julgamento frio/quente é do contrato, não daqui).
    frieza = {}
    try:
        import review_radar
        for r in review_radar.coletar():
            frieza[(r.get("area"), r.get("tema"))] = r.get("score")
    except Exception:
        pass
    for c in clusters.values():
        c["frieza"] = frieza.get((c["area"], c["tema"]))

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
        frio = ""
        if c.get("frieza") is not None:
            frio = f" · frieza {c['frieza']}" + (" ❄️" if c["frieza"] >= 25 else "")
        out.append(f"- **{c['area']} · {c['tema']}** — {c['total']} card(s): "
                   f"{', '.join(partes)}{frio}")
    return "\n".join(out)


def _contar_resumos():
    """Higiene (F6): contagem derivada de resumos/**/*.md -- MESMO glob do
    audit_resumos (o numero bate com o linter). Digitar o contador a mao foi a
    raiz do drift 63x61 no ESTADO. None em falha (nunca quebra o bloco)."""
    try:
        return len(glob.glob(os.path.join(ROOT, "resumos", "**", "*.md"), recursive=True))
    except Exception:
        return None


def render_handoff_block(p):
    """Bloco numerico 'Estado por frente' derivado do db (F6 -- AUDITORIA_MEDHUB).

    ASCII puro, pronto para colar no HANDOFF.md. So numeros derivados: o texto
    qualitativo (proximo tema, gaps, pendencias) continua manual no fechamento.
    """
    v, f = p["volume"], p["fsrs"]
    perf = round(v["acertos"] / v["total"] * 100, 1) if v["total"] else 0.0
    linhas = [
        f"- **Volume & Metas:** {v['total']} / {v['alvo_enamed']} (perf. ~{perf}%). "
        f"Hoje: {v['hoje']}. Ritmo-alvo ~{v['ritmo_alvo']}q/dia "
        f"({v['dias_ate_marco']}d p/ ENAMED).",
        f"- **FSRS:** {f['atrasados']} atrasados + {f['hoje']} hoje. "
        f"Backlog: {f['backlog_novos']} novos.",
    ]
    n_resumos = _contar_resumos()
    if n_resumos is not None:
        linhas.append(f"- **Conteudo:** {n_resumos} resumos em resumos/. [derivado: glob]")
    c = p.get("cronograma")
    if c:
        lag_txt = f", atraso {c['lag']} sem" if c.get("lag") else ""
        fonte = c.get("posicao_fonte")
        origem = "preparacao_estado" if fonte == "db" else (fonte or "?")
        linhas.append(
            f"- **Posicao:** conteudo S{c['conteudo']} (nominal S{c['nominal']}{lag_txt}) "
            f"[derivado: {origem}]")
    return "\n".join(linhas)


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
        fonte_pos = c.get("posicao_fonte")
        if fonte_pos == "nominal":
            aviso_pos = (" · ⚠️ posição ASSUMIDA pelo calendário — registre: "
                         "preparacao.py --set-semana N")
        elif fonte_pos == "texto":
            aviso_pos = " · ⚠️ posição via texto (deprecado)"
        else:
            aviso_pos = ""
        out.append(f"- 🧭 **Cronograma:** conteúdo **S{c['conteudo']}** · {c['previstas']}q previstas "
                   f"· {c['n_tasks']} tasks{lag}{aviso_pos}")
        # Banner de frescor do Drive (Part 1 -- disparo forçado): o snapshot carrega conclusão
        # real E ordem das tarefas; velho => os "próximos temas" podem vir fora de ordem ou já
        # feitos. Nunca silencioso -- o sync vira ação obrigatória do boot (AGENTE §2 passo 4).
        if c.get("conclusao_desatualizada"):
            nd = c.get("drive_sync_dias")
            quando = f"{nd}d atrás" if nd is not None else "nunca sincronizado"
            out.append(f"    • ⚠️ **Drive desatualizado ({quando})** -- rodar `python tools/"
                       f"cronograma.py --sync-drive <xlsx>` antes de confiar na lista abaixo "
                       f"(pode conter temas já feitos ou fora da ordem real)")
        else:
            out.append(f"    • Drive sincronizado: {c.get('drive_sync_data') or '—'}")
        if c["temas"]:
            out.append(f"    • próximos temas: {', '.join(c.get('temas_material', c['temas']))}")
        out.append(f"    • ritmos-alvo: terminar a grade ~{c['ritmo_cronograma']}/dia · "
                   f"meta-prova {META_PROVA // 1000}k ~{c['ritmo_meta']}/dia ({c['dias_enamed']}d p/ ENAMED)")
    elif p.get("cronograma_hint"):
        out.append(f"- 🧭 **Cronograma:** {p['cronograma_hint'][:120]}")
    r = p.get("recomendacao")
    if r:
        ctx = r["contexto"]
        rotulo = "defaults" if r["defaults_assumidos"] else "dia"
        out.append(f"- 🧠 **Recomendação do dia** [{rotulo}: {ctx['tempo_h']:g}h/{ctx['energia']}]:")
        for i, b in enumerate(r["blocos"], 1):
            alvo = f" — {b['alvo']}" if b.get("alvo") else ""
            qtd = f" {b['qtd']}" if b.get("qtd") else ""
            out.append(f"    {i}. {b['tipo']}{qtd}{alvo} · {b['motivo']}")
        pj = r["projecao"]
        if pj["dias_para_fechar"] is not None:
            out.append(f"    • projeção: ritmo real {pj['ritmo_real']}q/dia → grade fecha em "
                       f"~{pj['dias_para_fechar']}d (folga {pj['folga_dias']}d) · "
                       f"necessário {pj['ritmo_necessario']}q/dia (janela {pj['janela_dias']}d)")
        else:
            out.append(f"    • projeção: sem ritmo medido na janela de {pj['janela_dias']}d — "
                       f"necessário {pj['ritmo_necessario']}q/dia")
        out.append(f"    • sinais: {'; '.join(r['justificativa'][:3])}")
    out.append(f"- ▶️ **Passo sugerido:** {p['sugestao_passo']}")
    return "\n".join(out)


PLANO_DIA_DDL = '''
CREATE TABLE IF NOT EXISTS plano_dia (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    data               TEXT NOT NULL,
    ordem              INTEGER NOT NULL,
    task_tipo          TEXT NOT NULL,
    alvo_tema          TEXT,
    volume_planejado   INTEGER NOT NULL DEFAULT 0,
    tempo_h            REAL,
    energia            TEXT,
    defaults_assumidos INTEGER NOT NULL DEFAULT 0,
    criado_em          TEXT NOT NULL
)
'''


def persistir_plano(p):
    """Persiste os blocos recomendados do dia (spec telemetria-estudo-part-1).

    delete+insert TRANSACIONAL por data: o plano é atômico por dia — re-rodar
    substitui (precedente F22: nunca acumula); UPSERT por (data, ordem) deixaria
    blocos órfãos quando o re-run recomenda menos blocos. Lazy DDL no padrão
    preparacao_estado (registrar_sessao_bulk). Só metadado de processo:
    tipo/qtd/label/flags — nenhum conteúdo clínico. Falha vira WARN; o plano
    do stdout nunca se perde por causa da persistência.
    """
    r = p.get("recomendacao") or {}
    blocos = r.get("blocos") or []
    ctx = r.get("contexto") or {}
    con = None
    try:
        con = db.get_connection()
        con.execute(PLANO_DIA_DDL)
        con.execute("CREATE INDEX IF NOT EXISTS idx_plano_dia_data ON plano_dia(data)")
        con.execute("DELETE FROM plano_dia WHERE data = ?", (p["data"],))
        agora = datetime.now().isoformat(timespec="seconds")
        for i, b in enumerate(blocos, 1):
            con.execute(
                "INSERT INTO plano_dia (data, ordem, task_tipo, alvo_tema, "
                "volume_planejado, tempo_h, energia, defaults_assumidos, criado_em) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (p["data"], i, b.get("tipo") or "?", b.get("alvo"),
                 int(b.get("qtd") or 0), ctx.get("tempo_h"), ctx.get("energia"),
                 1 if r.get("defaults_assumidos") else 0, agora))
        con.commit()
    except Exception as e:
        if con is not None:
            try:
                con.rollback()
            except Exception:
                pass
        print(f"[WARN] PLANO_DIA: persistência falhou ({e}) — o plano segue no stdout.")
    finally:
        if con is not None:
            con.close()


def ler_plano(data_iso):
    """Blocos planejados de uma data (consumo da part-2 e do --plano-de)."""
    con = None
    try:
        con = db.get_connection()
        rows = con.execute(
            "SELECT ordem, task_tipo, alvo_tema, volume_planejado, tempo_h, "
            "energia, defaults_assumidos, criado_em FROM plano_dia "
            "WHERE data = ? ORDER BY ordem", (data_iso,)).fetchall()
    except Exception:
        rows = []
    finally:
        if con is not None:
            con.close()
    cols = ("ordem", "task_tipo", "alvo_tema", "volume_planejado", "tempo_h",
            "energia", "defaults_assumidos", "criado_em")
    return [dict(zip(cols, r)) for r in rows]


# --- Aderência planejado × real (spec telemetria-estudo-part-2) ---------------
# Família de medição por tipo de bloco: qual fonte MEDIDA responde pelo tipo.
# Trava anti-sycophancy: a classificação deriva SÓ de fsrs_revlog/sessoes_bulk
# (realizado medido); tempo_h/energia são dimensão do plano, nunca evidência.
FAMILIA_MEDICAO = {"mini-drill": "cards", "fsrs": "cards",
                   "questoes": "questoes", "simulado": "simulado",
                   "descanso": None}


def realizado_do_dia(con, data_iso):
    """Realizado MEDIDO do dia, direto das fontes SSOT (read-only)."""
    q = con.execute(
        "SELECT COALESCE(SUM(questoes_feitas),0) FROM sessoes_bulk "
        "WHERE area <> 'Simulado' AND data_sessao = ?", (data_iso,)).fetchone()[0]
    sim = con.execute(
        "SELECT COUNT(*) FROM sessoes_bulk "
        "WHERE area = 'Simulado' AND data_sessao = ?", (data_iso,)).fetchone()[0]
    cards = con.execute(
        "SELECT COUNT(*) FROM fsrs_revlog WHERE date(review_time) = ?",
        (data_iso,)).fetchone()[0]
    return {"questoes": q or 0, "simulado": sim or 0, "cards": cards or 0}


def classificar_dia(plano_rows, realizado):
    """Classificação PURA planejado×real de um dia (testável por fixtures).

    Regras determinísticas: cumprido (real >= planejado), parcial (0 < real <
    planejado), pulado (real == 0 e planejado > 0); volume 0 (ex.: descanso) =
    cumprido trivial. Famílias que dividem a mesma medida (mini-drill e fsrs
    dividem 'cards') alocam o realizado NA ORDEM do plano — mini-drill primeiro
    por construção (R1 vem antes). Realizado sem bloco correspondente (ou acima
    do planejado da família) vira 'extra' — estudo não planejado é sinal de 1ª
    classe, nunca descartado.
    """
    saldo = dict(realizado)
    consumo_planejado = {}
    blocos = []
    for b in sorted(plano_rows, key=lambda r: r.get("ordem", 0)):
        medida = FAMILIA_MEDICAO.get(b.get("task_tipo"))
        planejado = int(b.get("volume_planejado") or 0)
        if medida is None:
            blocos.append(dict(b, realizado=None,
                               status="cumprido" if planejado == 0 else "pulado"))
            continue
        consumo_planejado[medida] = consumo_planejado.get(medida, 0) + planejado
        real = min(saldo.get(medida, 0), planejado)
        saldo[medida] = saldo.get(medida, 0) - real
        if planejado == 0 or real >= planejado:
            status = "cumprido"
        elif real > 0:
            status = "parcial"
        else:
            status = "pulado"
        blocos.append(dict(b, realizado=real, status=status))
    extra = [{"tipo": medida, "qtd": resto}
             for medida, resto in sorted(saldo.items()) if resto > 0]
    return {"blocos": blocos, "extra": extra}


def aderencia(fim=None, semanas=1):
    """Série de aderência por dia na janela (deriva TUDO do db; zero input manual)."""
    fim = fim or date.today()
    dias = []
    con = None
    try:
        con = db.get_connection()
        for delta in range(semanas * 7 - 1, -1, -1):
            d = fim.fromordinal(fim.toordinal() - delta)
            data_iso = d.isoformat()
            plano = ler_plano(data_iso)
            try:
                real = realizado_do_dia(con, data_iso)
            except Exception:
                real = {"questoes": 0, "simulado": 0, "cards": 0}
            if plano:
                dia = classificar_dia(plano, real)
                dia["sem_plano"] = False
            else:
                # honestidade > completude: sem plano gravado, nada é "pulado";
                # o realizado aparece inteiro como extra (sinal, não erro).
                dia = {"blocos": [],
                       "extra": [{"tipo": k, "qtd": v}
                                 for k, v in sorted(real.items()) if v > 0],
                       "sem_plano": True}
            dia["data"] = data_iso
            dias.append(dia)
    finally:
        if con is not None:
            con.close()
    return dias


def render_aderencia(dias):
    out = ["# 📈 Aderência planejado × real", ""]
    for dia in dias:
        if dia["sem_plano"]:
            extras = ", ".join(f"{e['qtd']} {e['tipo']}" for e in dia["extra"])
            out.append(f"- **{dia['data']}** — sem plano gravado"
                       + (f" · extra: {extras}" if extras else ""))
            continue
        marcas = {"cumprido": "OK", "parcial": "parcial", "pulado": "PULADO"}
        partes = []
        for b in dia["blocos"]:
            real_txt = "-" if b["realizado"] is None else b["realizado"]
            partes.append(f"{b['task_tipo']} {real_txt}/{b['volume_planejado']} "
                          f"[{marcas[b['status']]}]")
        extras = ", ".join(f"{e['qtd']} {e['tipo']}" for e in dia["extra"])
        out.append(f"- **{dia['data']}** — " + " · ".join(partes)
                   + (f" · extra: {extras}" if extras else ""))
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
    ap.add_argument("--tempo", type=float, default=None, metavar="H",
                    help="Horas disponíveis hoje (recomendador; default declarado no output)")
    ap.add_argument("--energia", choices=["alta", "media", "baixa"], default=None,
                    help="Energia do dia (recomendador; modula a capacidade)")
    ap.add_argument("--no-persist", action="store_true", dest="no_persist",
                    help="Simulação: monta o plano sem gravar em plano_dia")
    ap.add_argument("--plano-de", metavar="YYYY-MM-DD", dest="plano_de",
                    help="Imprime o plano PERSISTIDO de uma data (JSON)")
    ap.add_argument("--aderencia", action="store_true",
                    help="Relatório aderência planejado×real por dia (derivado do db)")
    ap.add_argument("--semanas", type=int, default=1, metavar="N",
                    help="Janela do --aderencia em semanas (default 1)")
    args = ap.parse_args()
    if args.plano_de:
        print(json.dumps(ler_plano(args.plano_de), ensure_ascii=False, indent=2))
        return
    if args.aderencia:
        dias = aderencia(semanas=max(1, args.semanas))
        print(json.dumps(dias, ensure_ascii=False, indent=2) if args.json
              else render_aderencia(dias))
        return
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
    if args.tempo is not None or args.energia is not None:
        try:   # condição declarada do dia vira série (pergunta em aberto 2 do PRD)
            db.registrar_condicao_dia(args.tempo, args.energia)
        except Exception:
            pass
    p = build(tempo_h=args.tempo, energia=args.energia)
    # Persistência SÓ no caminho que renderiza o plano do dia (default/--json):
    # os modos de relatório (--handoff-block/--review-plan/--difficulty) retornam
    # antes e NÃO regravam — o handoff-block no fechamento rodaria com defaults e
    # sobrescreveria a intenção declarada de manhã (--tempo/--energia), corrompendo
    # a série de aderência da part-2.
    if not args.no_persist:
        persistir_plano(p)
    print(json.dumps(p, ensure_ascii=False, default=str, indent=2) if args.json else render(p))


if __name__ == "__main__":
    main()
