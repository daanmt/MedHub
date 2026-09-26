#!/usr/bin/env python3
"""Painel de progresso do MedHub -- pagina gerada do banco (part-7, s186; refeito na s194).

READ-ONLY ABSOLUTO. Nao abre `sqlite3` por conta propria (AGENTE.md secao 6: CLI nao faz SQL
direto) e nao aparece na allowlist de writers (F49). Todo numero sai de um leitor que JA existe e
que outra superficie tambem usa -- o painel nao tem regra propria de semana, de teto nem de ritmo:

    semana e listas   -> `plano.panorama` (o MESMO do `plano.py --panorama` do boot)
    cota do dia       -> `day_plan.cota_do_dia` (o MESMO do Plano do Dia)
    saldo de cards    -> `day_plan._fsrs_counts` + `_teto_efetivo` + `realizado_do_dia`
    agenda de 7 dias  -> `db.agenda_revisoes` (o MESMO da tela de fim da aba Cards)
    ritmo             -> `db.get_ritmo_real` + `performance.volume_vs_marco` + `day_plan._cronograma_hoje`
    retencao          -> `db.get_retencao_revlog` (pela regua de cada linha, F112)
    volume por bloco  -> `db.sessoes_bulk_listar` + `db.bloco_de` + `areas.AREAS_AGREGADAS`

s194 (auditoria de fidelidade de 23/09/2026, pedido do operador): a semana era a MENOR com
pendencia (o boot usa a de calendario: um dizia S1, o outro S2); o saldo de cards nao aparecia (se
lia "faltam 83" com o saldo zerado); a coluna de percentual sobre o previsto dividia volume
historico por um plano com cortadas e simulados; o numero de sessoes fixo no codigo e a constante
do orcamento da Fase 1 envelheceram; e o simulado contava como
tarefa de CM (`bloco_de('Simulado')` = CM por fallback). Tudo isso saiu ou foi trocado pelo
leitor-fonte, e cada numero tem teste que o amarra a ele (`tools/test_painel.py`).

--json e o CONTRATO (o que os testes provam); --html e o render. O CLI **nao** publica: a pagina
vai no hub (`tools/hub.py --build`), e o tique do /hub-backend a regenera e republica quando o
conteudo muda (o carimbo de hora fica entre `MARCA_GERADO_*`, fora da comparacao).

Fronteira DECLARADA: area fantasma (F89, ex.: `GO` solto) nao vira CM por fallback; o volume dela
aparece nomeado, fora dos blocos.
"""
import argparse
import html
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

from app.utils import db                                          # noqa: E402

TITULO = "Painel MedHub"
SAIDA_HTML = ROOT / "artifacts" / "painel.html"
QUADRO = ROOT / "core" / "hub_quadro.json"

#: Ordem dos blocos na pagina. O `id` e o `data-bloco` do HTML e a chave do JSON.
BLOCOS = ("dia", "semana", "ritmo", "blocos")

#: O carimbo de geracao mora entre estes marcadores: o hub os ignora ao comparar a projecao
#: publicada (a hora muda a cada geracao; o conteudo, nao).
MARCA_GERADO_ABRE = "<!--gerado-->"
MARCA_GERADO_FECHA = "<!--/gerado-->"

#: Tarefas da semana a vista antes do "ver as outras".
VISIVEIS_SEMANA = 6

DIAS_SEMANA = ("seg", "ter", "qua", "qui", "sex", "sáb", "dom")
DIAS_EXTENSO = ("segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo")


# ------------------------------------------------------------------ coleta

def _volume_por_bloco(sessoes):
    """Questoes FEITAS por bloco UERJ, de `sessoes_bulk`, em tres cestas (licao do F89):
    `areas.AREAS_AGREGADAS` (Simulado: termometro, nao bloco), `areas.area_valida` (area fantasma
    fica nomeada) e `db.bloco_de` (o mapa canonico area -> bloco; copia aqui seria um 2o
    vocabulario)."""
    from app.utils import areas
    por_bloco, agregadas, fantasmas = {}, {}, {}
    for s in sessoes:
        area = s.get("area")
        q = int(s.get("questoes_feitas") or 0)
        a = int(s.get("questoes_acertadas") or 0)
        if area in areas.AREAS_AGREGADAS:
            alvo = agregadas.setdefault(area, {"feitas": 0, "acertos": 0})
        elif not areas.area_valida(area):
            alvo = fantasmas.setdefault(area or "(sem area)", {"feitas": 0, "acertos": 0})
        else:
            alvo = por_bloco.setdefault(db.bloco_de(area), {"feitas": 0, "acertos": 0})
        alvo["feitas"] += q
        alvo["acertos"] += a
    return por_bloco, agregadas, fantasmas


def _aulas_por_tarefa():
    """{tarefa_id: slug} do registro do quadro de aulas (`core/hub_quadro.json`). Ilegivel ou
    ausente = {} (a tarefa de aula so perde o atalho; o numero nao muda)."""
    try:
        reg = json.loads(QUADRO.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    saida = {}
    for slug, item in (reg.get("itens") or {}).items():
        tid = (item or {}).get("tarefa_id")
        if tid is not None:
            saida[int(tid)] = slug
    return saida


def _bloco_semana(linhas, hoje):
    """A semana corrente e as abertas pela MESMA funcao do boot (`plano.panorama`)."""
    import plano
    pan = plano.panorama(linhas, plano.calendario_trilha(), hoje)
    if not pan:
        return {"semana": None, "tarefas": [], "total": 0, "q": 0, "atrasadas": 0,
                "inicio": None, "fim": None, "dias": None, "proxima": None}
    from app.utils import areas
    aulas = _aulas_por_tarefa()
    try:  # s201: tarefa com questoes no banco se resolve na aba Listas do hub
        no_hub = db.tarefas_com_questoes()
    except Exception:  # noqa: BLE001
        no_hub = set()
    tarefas = []
    for t in pan["abertas"]:
        agregada = t.get("area") in areas.AREAS_AGREGADAS
        tarefas.append({
            "id": t["id"], "semana": t["semana"], "atrasada": t["atrasada"],
            "tema": t["tema"], "q": t["q"], "classe": t["classe"],
            "url_lista": t["url_lista"],
            # simulado se apresenta como simulado, nunca pelo bloco de fallback (CM)
            "rotulo": t.get("area") if agregada else (t.get("bloco") or t.get("area")),
            "aula": aulas.get(t["id"]),
            "no_hub": t["id"] in no_hub,
        })
    return {
        "semana": pan["semana"], "inicio": pan["inicio"], "fim": pan["fim"],
        "dias": pan["dias"], "tarefas": tarefas, "total": len(tarefas),
        "q": pan["q_abertas"], "atrasadas": pan["atrasadas"],
        "feitas_semana": pan["feitas_semana"], "tarefas_semana": pan["tarefas_semana"],
        "proxima": pan["proxima"],
    }


def _bloco_dia(linhas, hoje):
    """Hoje: cota de questoes, saldo de cards e a agenda de 7 dias -- leitores do `day_plan` e o
    `db.agenda_revisoes` do export do player."""
    import day_plan
    pendentes = [l for l in linhas if l.get("status") == "pendente"]
    cota = day_plan.cota_do_dia(pendentes, day_plan._calendario_trilha(), hoje)
    feitas_hoje = sum(int(s.get("questoes_feitas") or 0) for s in db.sessoes_bulk_listar()
                      if str(s.get("data_sessao") or "")[:10] == hoje.isoformat())
    con = db.get_connection()
    try:
        cont = day_plan._fsrs_counts(con)
        try:
            consumo = int(day_plan.realizado_do_dia(con, hoje.isoformat())["cards"])
        except Exception:  # noqa: BLE001 -- sem contador: sem saldo, declarado na tela
            consumo = None
    finally:
        con.close()
    vencidos = day_plan.vencidos_de(cont)
    teto = int(day_plan._teto_efetivo(vencidos))
    return {
        "questoes": {
            "feitas_hoje": feitas_hoje,
            "cota": (cota or {}).get("cota"),
            "q_restantes": (cota or {}).get("q_restantes"),
            "q_atrasadas": (cota or {}).get("q_atrasadas"),
            "semana": (cota or {}).get("semana"),
            "fim": (cota or {}).get("fim"),
            "dias": (cota or {}).get("dias"),
        },
        "cards": {
            "vencidos": vencidos,
            "novos": cont["backlog_novos"],
            "teto": teto,
            "consumo_hoje": consumo,
            "restantes": None if consumo is None else max(0, teto - consumo),
            "retencao_7d": db.get_retencao_revlog(dias=7),
        },
        "agenda": db.agenda_revisoes(dias=7),
    }


def _bloco_ritmo(hoje):
    """Real (7 e 14 dias) ao lado do alvo ate a UERJ (o marco de volume do boot) e da Fase 1."""
    import day_plan
    import performance
    con = db.get_connection()
    try:
        vm = performance.volume_vs_marco(con, hoje)
    finally:
        con.close()
    cron = day_plan._cronograma_hoje(vm["total"], hoje) or {}
    return {
        "real_7d": db.get_ritmo_real(7),
        "real_14d": db.get_ritmo_real(14),
        "marco": vm["marco"],
        "meta": vm["meta"],
        "faltam": vm["faltam"],
        "dias_marco": vm["dias"],
        "alvo_marco": vm["ritmo_alvo"],
        "alvo_fase1": cron.get("ritmo_cronograma"),
        "fase1_q": cron.get("restante_q"),
        "fim_fase1": cron.get("fim_conteudo_alvo"),
        "acumulado": vm["total"],
        "acerto": (round(vm["acertos"] / vm["total"] * 100, 1) if vm["total"] else None),
    }


def _bloco_blocos(linhas):
    """Tarefas e volume por bloco. Simulado (area agregada) sai para a linha propria; cortada nao
    conta. Sem percentual sobre o previsto: o volume historico nao depende do plano."""
    from app.utils import areas
    vol, agregadas, fantasmas = _volume_por_bloco(db.sessoes_bulk_listar())
    blocos, sim = {}, {"tarefas": 0, "feitas": 0}
    for t in linhas:
        status = (t.get("status") or "pendente").lower()
        if status in ("cortada", "cortado"):
            continue
        if t.get("area") in areas.AREAS_AGREGADAS:
            alvo = sim
        else:
            alvo = blocos.setdefault(t.get("bloco") or db.bloco_de(t.get("area")),
                                     {"tarefas": 0, "feitas": 0})
        alvo["tarefas"] += 1
        alvo["feitas"] += status == "feita"
    for nome in set(blocos) | set(vol):
        b = blocos.setdefault(nome, {"tarefas": 0, "feitas": 0})
        v = vol.get(nome) or {}
        b["q_feitas"] = int(v.get("feitas") or 0)
        b["acerto"] = (round(v["acertos"] / v["feitas"] * 100, 1) if v.get("feitas") else None)
    sv = {"feitas": sum(v["feitas"] for v in agregadas.values()),
          "acertos": sum(v["acertos"] for v in agregadas.values())}
    sim["q_feitas"] = sv["feitas"]
    sim["acerto"] = round(sv["acertos"] / sv["feitas"] * 100, 1) if sv["feitas"] else None
    return {"blocos": dict(sorted(blocos.items())), "simulados": sim, "sem_bloco": fantasmas}


def coletar(hoje=None):
    """O contrato do painel. Dict com os 4 blocos + metadados. Read-only."""
    hoje = hoje or db.hoje()
    linhas = db.plano_listar()
    return {
        "gerado_em": db.agora().isoformat(timespec="seconds"),
        "data": hoje.isoformat(),
        "titulo": TITULO,
        "dia": _bloco_dia(linhas, hoje),
        "semana": _bloco_semana(linhas, hoje),
        "ritmo": _bloco_ritmo(hoje),
        "blocos": _bloco_blocos(linhas),
    }


# ------------------------------------------------------------------ render

def _e(v):
    return html.escape("" if v is None else str(v), quote=True)


def _n(v, casas=0, vazio="--"):
    """Numero em pt-BR: milhar com ponto, decimal com virgula."""
    if v is None:
        return vazio
    txt = ("{:,.%df}" % casas).format(float(v))
    return txt.replace(",", "X").replace(".", ",").replace("X", ".")


def _dm(iso):
    return "%s/%s" % (iso[8:10], iso[5:7]) if iso else "?"


def _dia_curto(iso):
    d = date.fromisoformat(iso)
    return "%s %s" % (DIAS_SEMANA[d.weekday()], d.strftime("%d/%m"))


def _link(url, texto):
    """`<a>` so para URL ABSOLUTA. O plano guarda tambem caminho LOCAL (a prova em PDF), que
    resolve na maquina e morre numa pagina publicada -- link quebrado promete e nao entrega."""
    if url and str(url).startswith(("http://", "https://")):
        return '<a href="%s" rel="noopener noreferrer">%s</a>' % (_e(url), _e(texto))
    return '<span class="tenue">%s</span>' % _e(texto)


def _pct(parte, todo):
    if not todo:
        return 0.0
    return max(0.0, min(100.0, 100.0 * float(parte or 0) / float(todo)))


def _acao(t):
    c = t["classe"]
    if c == "lista":
        if t["url_lista"] and str(t["url_lista"]).startswith(("http://", "https://")):
            return _link(t["url_lista"], "abrir lista")
        if t.get("no_hub"):
            return '<a href="#questoes" data-hub-aba="questoes" data-hub-modo="simulados">resolver no hub</a>'
        return '<span class="tenue">prova em PDF no computador</span>'
    if c == "aula":
        if t.get("aula"):
            return ('<a href="aulas/%s.html" data-hub-aula="%s">abrir aula</a>'
                    % (_e(t["aula"]), _e(t["aula"])))
        return '<span class="tenue">aula a preparar</span>'
    if c == "caderno":
        return '<span class="tenue">montar caderno no banco</span>'
    return '<span class="tenue">sem lista ainda</span>'


def _html_dia(d, data_iso):
    hoje = date.fromisoformat(data_iso)
    q, c, ag = d["questoes"], d["cards"], d["agenda"]

    if q["cota"] is not None:
        partes = ["cota de ~%s por dia até %s" % (_n(q["cota"]), _dia_curto(q["fim"]))]
        if q["q_atrasadas"]:
            partes.append("inclui %s de semana atrasada" % _n(q["q_atrasadas"]))
        nota_q = "; ".join(partes) + "."
        num_q = '<b>%s</b> de ~%s' % (_n(q["feitas_hoje"]), _n(q["cota"]))
        barra_q = _pct(q["feitas_hoje"], q["cota"])
    else:
        nota_q = "sem cota: o calendário do plano acabou."
        num_q = '<b>%s</b> feitas' % _n(q["feitas_hoje"])
        barra_q = 0.0

    if c["consumo_hoje"] is None:
        num_c = '<b>--</b> de %s' % _n(c["teto"])
        nota_c = "não consegui contar as revisões de hoje."
        barra_c = 0.0
    else:
        num_c = '<b>%s</b> de %s' % (_n(c["consumo_hoje"]), _n(c["teto"]))
        barra_c = _pct(c["consumo_hoje"], c["teto"])
        nota_c = ("faltam %d: saldo do dia cumprido." % c["restantes"] if c["restantes"] == 0
                  else "faltam %d hoje." % c["restantes"])
    ret = c["retencao_7d"]
    extra_c = ["%s vencidos agora" % _n(c["vencidos"]), "%s novos esperando" % _n(c["novos"])]
    if ret.get("retencao") is not None:
        extra_c.append("retenção de %s%% em 7 dias" % _n(ret["retencao"] * 100, 1))

    maior = max([x["n"] for x in ag["dias"]] + [1])
    barras = "".join(
        '<li><span class="ag-n">%d</span><span class="ag-trilho"><i style="height:%.0f%%"></i></span>'
        '<span class="ag-d">%s</span></li>'
        % (x["n"], max(4.0, 100.0 * x["n"] / maior), DIAS_SEMANA[date.fromisoformat(x["data"]).weekday()])
        for x in ag["dias"])
    return (
        '<h2>Hoje, %s %s</h2>\n'
        '<div class="doses">\n'
        '  <div class="dose"><h3>Questões</h3><p class="fracao">%s</p>'
        '<div class="barra"><i style="width:%.1f%%"></i></div><p class="nota">%s</p></div>\n'
        '  <div class="dose"><h3>Cards</h3><p class="fracao">%s</p>'
        '<div class="barra"><i style="width:%.1f%%"></i></div><p class="nota">%s</p>'
        '<p class="nota">%s.</p>'
        '<p class="ir"><a href="#cards" data-hub-aba="cards">Ir para os cards</a></p></div>\n'
        '</div>\n'
        '<div class="agenda"><h3>Revisões nos próximos 7 dias</h3>'
        '<ol class="ag-barras" aria-label="Revisões por dia">%s</ol></div>'
        % (DIAS_EXTENSO[hoje.weekday()], hoje.strftime("%d/%m"),
           num_q, barra_q, _e(nota_q),
           num_c, barra_c, _e(nota_c), _e(", ".join(extra_c)),
           barras))


def _html_semana(d):
    if d["semana"] is None:
        return '<h2>Semana</h2><p class="nota">Nenhuma tarefa pendente no plano.</p>'
    if d["inicio"]:
        janela = "%s a %s, %d dia(s) contando hoje." % (_dm(d["inicio"]), _dm(d["fim"]), d["dias"])
    else:
        janela = "Fora do calendário do plano: pela ordem das tarefas."
    resumo = "%d tarefa(s) em aberto, %s questões." % (d["total"], _n(d["q"]))
    if d["atrasadas"]:
        resumo += " %d vêm atrasadas de semana anterior." % d["atrasadas"]
    itens = []
    for t in d["tarefas"]:
        meta = ['<span class="t-rot">%s</span>' % _e(t["rotulo"] or "?")]
        if t["q"]:
            meta.append("<span>%s questões</span>" % _n(t["q"]))
        if t["atrasada"]:
            meta.append('<span class="t-atraso">da semana %s</span>' % _e(t["semana"]))
        itens.append('<li class="tarefa%s"><p class="t-tema">%s</p><p class="t-meta">%s</p>'
                     '<p class="t-acao">%s</p></li>'
                     % (" atrasada" if t["atrasada"] else "", _e(t["tema"] or "(sem tema)"),
                        " ".join(meta), _acao(t)))
    prox = d.get("proxima")
    txt_prox = ""
    if prox:
        quando = " (%s a %s)" % (_dm(prox["inicio"]), _dm(prox["fim"])) if prox.get("inicio") else ""
        txt_prox = ('<p class="nota prox">Depois: semana %s%s, %d tarefa(s), %s questões.</p>'
                    % (_e(prox["semana"]), quando, prox["tarefas"], _n(prox["q"])))
    # A semana inteira passa de 20 tarefas: as primeiras (e todas as atrasadas) ficam a vista, o
    # resto recolhido na MESMA ordem do plano -- nada some, so para de gritar.
    corte = max(VISIVEIS_SEMANA, sum(1 for t in d["tarefas"] if t["atrasada"]))
    lista = '<ol class="tarefas">%s</ol>' % "".join(itens[:corte])
    if len(itens) > corte:
        lista += ('<details class="mais"><summary>Ver as outras %d</summary>'
                  '<ol class="tarefas" start="%d">%s</ol></details>'
                  % (len(itens) - corte, corte + 1, "".join(itens[corte:])))
    return ('<h2>Semana %s do plano</h2>\n<p class="sub">%s %s</p>\n%s\n%s'
            % (_e(d["semana"]), _e(janela), _e(resumo), lista, txt_prox))


def _html_ritmo(r):
    alvo = r["alvo_marco"]
    atras = alvo is not None and (r["real_7d"] or 0) < alvo
    fig = []
    fig.append('<div class="fig%s"><p class="fig-n">%s</p><p class="fig-r">por dia nos '
               'últimos 7 dias</p></div>' % (" abaixo" if atras else "", _n(r["real_7d"], 1)))
    fig.append('<div class="fig"><p class="fig-n">%s</p><p class="fig-r">por dia nos '
               'últimos 14 dias</p></div>' % _n(r["real_14d"], 1))
    fig.append('<div class="fig alvo"><p class="fig-n">%s</p><p class="fig-r">por dia até a '
               'prova de 01/11 (faltam %s para %s)</p></div>'
               % (_n(alvo, 1), _n(r["faltam"]), _n(r["meta"])))
    fig.append('<div class="fig"><p class="fig-n">%s%%</p><p class="fig-r">de acerto em %s '
               'questões</p></div>' % (_n(r["acerto"], 1), _n(r["acumulado"])))
    nota = ""
    if r["alvo_fase1"] is not None:
        nota = ('<p class="nota">Para fechar as listas da Fase 1 até %s: ~%s por dia (%s questões '
                'em aberto).</p>' % (_dm(r["fim_fase1"]), _n(r["alvo_fase1"], 1), _n(r["fase1_q"])))
    return '<h2>Ritmo de questões</h2>\n<div class="figs">%s</div>\n%s' % ("".join(fig), nota)


def _html_blocos(b):
    linhas = []
    for nome, v in b["blocos"].items():
        linhas.append('<tr><th scope="row">%s</th><td>%d de %d</td><td>%s</td><td>%s</td></tr>'
                      % (_e(nome), v["feitas"], v["tarefas"], _n(v["q_feitas"]),
                         (_n(v["acerto"], 1) + "%") if v["acerto"] is not None else "--"))
    s = b["simulados"]
    linhas.append('<tr class="sim"><th scope="row">Simulados</th><td>%d de %d</td><td>%s</td>'
                  '<td>%s</td></tr>'
                  % (s["feitas"], s["tarefas"], _n(s["q_feitas"]),
                     (_n(s["acerto"], 1) + "%") if s["acerto"] is not None else "--"))
    nota = ""
    if b["sem_bloco"]:
        nota = ('<p class="nota">Fora da tabela: %s, sem área reconhecida.</p>'
                % _e(", ".join('%s questões registradas só como "%s"' % (_n(v["feitas"]), k)
                               for k, v in sorted(b["sem_bloco"].items()))))
    return ('<h2>Por bloco</h2>\n<table><thead><tr><th scope="col">Bloco</th>'
            '<th scope="col">Tarefas feitas</th><th scope="col">Questões</th>'
            '<th scope="col">Acerto</th></tr></thead><tbody>%s</tbody></table>\n%s'
            % ("".join(linhas), nota))


def _sec(chave, corpo, extra=""):
    return ('<section class="bloco %s" data-bloco="%s">\n%s\n</section>'
            % (_e(extra or chave), _e(chave), corpo))


CSS = """
:root{
  --papel:#f6f4f0; --card:#ffffff; --afundado:#edeae4;
  --tinta:#191817; --tinta2:#54504a; --tinta3:#8b857b;
  --linha:#e0dbd2; --acento:#0e6b5c; --acento-fraco:#d9ece7;
  --alerta:#a2412a; --alerta-fraco:#f6e4de;
  --wrap:58rem; --raio:14px;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --papel:#131519; --card:#1b1e24; --afundado:#23272f;
    --tinta:#edeff3; --tinta2:#b4bac4; --tinta3:#7e8794;
    --linha:#2d323b; --acento:#4fd0b3; --acento-fraco:#123630;
    --alerta:#f0917a; --alerta-fraco:#3a221c;
  }
}
:root[data-theme="dark"]{
  --papel:#131519; --card:#1b1e24; --afundado:#23272f;
  --tinta:#edeff3; --tinta2:#b4bac4; --tinta3:#7e8794;
  --linha:#2d323b; --acento:#4fd0b3; --acento-fraco:#123630;
  --alerta:#f0917a; --alerta-fraco:#3a221c;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{
  margin:0; background:var(--papel); color:var(--tinta);
  font-family:ui-sans-serif,system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  font-size:clamp(15px,.95rem + .2vw,17px); line-height:1.5; overflow-wrap:break-word;
}
.wrap{max-width:var(--wrap);margin:0 auto;padding:4px 2px 40px}
h2{font-size:1.08rem;margin:0 0 4px;letter-spacing:-.005em;text-wrap:balance}
h3{font-size:.86rem;font-weight:600;color:var(--tinta2);margin:0 0 6px}
p{margin:0}
a{color:var(--acento);text-underline-offset:2px}
a:focus-visible{outline:3px solid var(--acento);outline-offset:2px;border-radius:4px}
.atualizado{color:var(--tinta3);font-size:.76em;margin:0 0 10px;text-align:right}
.bloco{padding:18px 0 22px;border-top:1px solid var(--linha)}
.bloco:first-of-type{border-top:0;padding-top:4px}
.sub{color:var(--tinta2);font-size:.9em;margin:0 0 14px}
.nota{color:var(--tinta3);font-size:.84em;margin-top:6px}
.tenue{color:var(--tinta3)}

/* Hoje: as duas doses do dia, o elemento que o olho acha primeiro */
.dia h2{font-size:1.25rem;margin-bottom:14px}
.doses{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,15rem),1fr));gap:12px}
.dose{min-width:0;background:var(--card);border:1px solid var(--linha);border-radius:var(--raio);
      padding:14px 16px 16px;border-left:4px solid var(--acento)}
.fracao{font-size:1.02rem;color:var(--tinta2);font-variant-numeric:tabular-nums}
.fracao b{font-size:2.3rem;line-height:1.1;color:var(--tinta);font-weight:750;letter-spacing:-.02em;margin-right:4px}
.barra{height:6px;background:var(--afundado);border-radius:99px;margin:10px 0 4px;overflow:hidden}
.barra i{display:block;height:100%;background:var(--acento)}
.ir{margin-top:10px;font-weight:600}
.ir a{display:inline-block;padding:8px 0;min-height:44px}
.agenda{margin-top:18px}
.ag-barras{list-style:none;margin:6px 0 0;padding:0;display:grid;grid-template-columns:repeat(7,minmax(0,1fr));
           gap:6px;height:112px;align-items:end}
.ag-barras li{min-width:0;height:100%;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;gap:3px}
.ag-trilho{flex:1 1 auto;width:100%;display:flex;align-items:flex-end;justify-content:center}
.ag-barras i{display:block;width:min(100%,34px);background:var(--acento-fraco);border-top:3px solid var(--acento);border-radius:4px 4px 0 0}
.ag-n{font-size:.8em;font-variant-numeric:tabular-nums;color:var(--tinta2)}
.ag-d{font-size:.74em;color:var(--tinta3)}

/* Semana */
.tarefas{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.tarefa{min-width:0;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:2px 14px;align-items:baseline;
        padding:10px 12px;background:var(--card);border:1px solid var(--linha);border-radius:10px}
.tarefa.atrasada{border-left:4px solid var(--alerta)}
.t-tema{min-width:0;font-weight:600;line-height:1.35}
.t-meta{grid-column:1;min-width:0;color:var(--tinta3);font-size:.82em;display:flex;flex-wrap:wrap;gap:2px 10px}
.t-rot{color:var(--tinta2);font-weight:600}
.t-atraso{color:var(--alerta)}
.t-acao{grid-column:2;grid-row:1 / span 2;align-self:center;font-size:.88em;text-align:right}
.prox{margin-top:12px}
.mais{margin-top:8px}
.mais summary{cursor:pointer;color:var(--acento);font-weight:600;padding:10px 0;min-height:44px}
.mais .tarefas{margin-top:4px}

/* Ritmo */
.figs{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,9.5rem),1fr));gap:10px;margin-top:10px}
.fig{min-width:0;background:var(--afundado);border-radius:10px;padding:10px 12px}
.fig-n{font-size:1.5rem;font-weight:700;font-variant-numeric:tabular-nums;line-height:1.2}
.fig-r{font-size:.78em;color:var(--tinta3)}
.fig.abaixo .fig-n{color:var(--alerta)}
.fig.alvo{background:var(--acento-fraco)}

/* Blocos */
table{width:100%;border-collapse:collapse;font-size:.9em;font-variant-numeric:tabular-nums;margin-top:8px}
th,td{text-align:left;padding:7px 8px;border-bottom:1px solid var(--linha)}
thead th{font-size:.78em;color:var(--tinta3);font-weight:600}
tbody th{font-weight:650}
tr.sim th,tr.sim td{color:var(--tinta2)}

@media (max-width:520px){
  .tarefa{grid-template-columns:minmax(0,1fr)}
  .t-acao{grid-column:1;grid-row:auto;text-align:left}
  th,td{padding:6px 5px}
  table{font-size:.84em}
}
"""

SCRIPT_ATUALIZADO = """
<script>
(function(){
  var el = document.querySelector("[data-gerado]");
  if(!el){ return; }
  var t = Date.parse(el.getAttribute("data-gerado"));
  if(isNaN(t)){ return; }
  function rotulo(){
    var min = Math.floor((Date.now() - t) / 60000);
    if(min < 1){ return "atualizado agora"; }
    if(min < 60){ return "atualizado há " + min + " min"; }
    var h = Math.floor(min / 60);
    if(h < 24){ return "atualizado há " + h + " h"; }
    return el.getAttribute("data-fallback") || el.textContent;
  }
  el.textContent = rotulo();
  setInterval(function(){ el.textContent = rotulo(); }, 60000);
})();
</script>
"""


def render_html(d):
    """Pagina autocontida. UM `.wrap`, tokens em `:root` (os MESMOS do hub), dark por
    `prefers-color-scheme` GUARDADO + `[data-theme]`, `body` com background explicito, 360px sem
    scroll horizontal. Nada de bastidor na tela: sem CLI, tabela ou fonte citada."""
    gerado = d["gerado_em"]
    fallback = "atualizado em %s, %s" % (_dm(gerado[:10]), gerado[11:16])
    corpo = "\n".join([
        _sec("dia", _html_dia(d["dia"], d["data"])),
        _sec("semana", _html_semana(d["semana"])),
        _sec("ritmo", _html_ritmo(d["ritmo"])),
        _sec("blocos", _html_blocos(d["blocos"])),
    ])
    return ("<!DOCTYPE html>\n<html lang=\"pt-BR\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n"
            "<title>%s</title>\n<style>%s</style>\n</head>\n<body>\n<div class=\"wrap\">\n"
            "<p class=\"atualizado\">%s<span data-gerado=\"%s\" data-fallback=\"%s\">%s</span>%s</p>\n"
            "%s\n</div>\n%s</body>\n</html>\n"
            % (_e(TITULO), CSS, MARCA_GERADO_ABRE, _e(gerado), _e(fallback), _e(fallback),
               MARCA_GERADO_FECHA, corpo, SCRIPT_ATUALIZADO))


# -------------------------------------------------------------------- CLI

def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    ap = argparse.ArgumentParser(
        description="Painel de progresso do MedHub (read-only). Gera o JSON "
                    "(contrato) ou a pagina HTML (render).")
    ap.add_argument("--json", action="store_true",
                    help="imprime o dado estruturado dos 4 blocos (contrato testavel)")
    ap.add_argument("--html", action="store_true",
                    help="gera a pagina autocontida (default: artifacts/painel.html)")
    ap.add_argument("--out", metavar="PATH",
                    help="destino do --html (default: artifacts/painel.html)")
    args = ap.parse_args(argv)

    if not args.json and not args.html:
        ap.error("informe --json ou --html")

    dados = coletar()
    if args.json:
        print(json.dumps(dados, ensure_ascii=False, indent=2, default=str))
    if args.html:
        destino = Path(args.out) if args.out else SAIDA_HTML
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(render_html(dados), encoding="utf-8")
        print(json.dumps({"html": str(destino), "blocos": list(BLOCOS),
                          "semana": dados["semana"]["semana"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
