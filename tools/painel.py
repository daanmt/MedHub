#!/usr/bin/env python3
"""Painel de progresso do MedHub -- pagina gerada do banco (part-7, s186).

READ-ONLY ABSOLUTO. Nao abre `sqlite3` por conta propria (AGENTE.md secao 6: CLI
nao faz SQL direto) e nao aparece na allowlist de writers (F49). Toda leitura
passa por funcao ja existente:

    plano/listas  -> `tools/listas.py` (progresso, pendentes)  [plano]
    volume/custo  -> `tools/performance.py`                    [performance]
    FSRS          -> `tools/day_plan.py` + `app/utils/db.py`   [db]

Por que existe: quando o Drive congelar (part-8) o operador perde as 20 tabelas
do Dashboard. O dado todo ja vive no banco -- o que faltava era uma superficie.

--json e o CONTRATO (o que os testes provam); --html e o render. O CLI **nao**
publica: quem publica e o agente no fechamento de sessao, com `url` fixa, para a
pagina manter o mesmo endereco (`.agents/workflows/registrar-sessao.md`).

--------------------------------------------------------------------------
Fronteiras DECLARADAS (numero que nao existe nao vira numero bonito)
--------------------------------------------------------------------------
1. **ENAMED 2027 nao tem projecao** porque nao tem ancora: nao esta em
   `core/provas.json` (que vai ate UERJ/MFC 01/11/2026) nem em
   `performance.MARCOS`. O painel DIZ isso no bloco, em vez de estimar a partir
   de uma data inventada. Vira numero no dia em que o operador cadastrar a data.
2. **Volume sem vinculo e reportado, nao escondido.** Hoje 126 sessoes / 7.326
   questoes nao estao ligadas a nenhuma tarefa do plano (o backfill do part-6
   nao rodou). Um painel que mostrasse so o volume vinculado exibiria ~0% de
   progresso com o operador tendo estudado o ano inteiro -- por isso o bloco
   carrega o nao-vinculado ao lado, com o nome do que falta rodar.
3. **Retencao passa pela regua** (`db.get_retencao_revlog`): nota 2 dada sob a
   regua v1 e LAPSO, sob a v2 e acerto. Contar por limiar fixo de `rating`
   inflaria a retencao exatamente como o F112 inflava o agendamento.
"""
import argparse
import html
import json
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

from app.utils import db                                          # noqa: E402

TITULO = "Painel MedHub"
SAIDA_HTML = ROOT / "artifacts" / "painel.html"

#: Ordem dos blocos na pagina. O `id` e o `data-bloco` do HTML e a chave do JSON
#: -- um nome so para as duas superficies (o teste casa por ele).
BLOCOS = ("plano", "semana", "fsrs", "projecao", "proximas")

FONTES = {
    "plano": "[plano] tools/listas.py --progresso · [db] plano_tarefas",
    "semana": "[plano] tools/listas.py --pendentes --semana N",
    "fsrs": "[db] day_plan._fsrs_counts · db.get_retencao_revlog · app/utils/regua",
    "projecao": "[performance] volume_vs_marco · METAS_MENSAIS · [db] sessoes_bulk",
    "proximas": "[plano] db.plano_listar(status='pendente')",
}


# ------------------------------------------------------------------ coleta

def _semana_corrente():
    """Semana do plano com alguma tarefa pendente -- a menor. `None` se o plano
    acabou ou nao foi semeado."""
    pendentes = [t for t in db.plano_listar(status="pendente")
                 if t.get("semana_plano") is not None]
    if not pendentes:
        return None
    return min(int(t["semana_plano"]) for t in pendentes)


#: Sumidouro mudo: os leitores de `listas.py` imprimem o relatorio de terminal
#: por default. O painel quer o PAYLOAD, nao o texto -- injeta um sink que
#: descarta, mesmo padrao de `plano.listar(out=...)`.
def _mudo(*_a, **_k):
    return None


def _volume_por_bloco(sessoes):
    """Questoes FEITAS por bloco UERJ, de `sessoes_bulk`, em tres cestas.

    🔴 Por que NAO pelo elo `sessoes_bulk.tarefa_id` (part-6): medido em
    18/09/2026, o backfill casa **1 de 126 sessoes** de forma inequivoca (37
    ambiguas, 78 sem match). Um painel alimentado so pelo elo mostraria ~0
    questoes feitas em todo bloco com o operador tendo feito 7.326 -- verde falso
    ao contrario. As duas camadas convivem, rotuladas: VOLUME (cobre tudo,
    granularidade area) e ELO (granularidade tarefa, cobertura hoje parcial).

    Zero vocabulario novo aqui -- as tres cestas saem de portadores que ja
    existem, e essa e a licao do F89 aplicada a este arquivo:
      `areas.AREAS_AGREGADAS`  -> `Simulado` e termometro, nao bloco. Vale 931
                                  das 7.326 questoes (12,7%): dobrado em CM pelo
                                  fallback do `bloco_de`, inflaria um oitavo.
      `areas.area_valida`      -> area FANTASMA (F89, ex.: `GO` solto) nao vira
                                  CM por fallback silencioso; fica nomeada.
      `db.bloco_de`            -> o mapa area -> bloco, ja canonico. Uma copia
                                  minha aqui seria um segundo vocabulario, que e
                                  exatamente o defeito que o F89 registrou.
    """
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


def _bloco_plano():
    import listas
    _code, prog = listas.progresso(como_json=True, out=_mudo)
    todas = db.plano_listar()
    sessoes = db.sessoes_bulk_listar()
    vol, fora, sem_mapa = _volume_por_bloco(sessoes)

    por_bloco = {}
    for t in todas:
        b = por_bloco.setdefault(t.get("bloco") or "CM", {
            "tarefas": 0, "feitas": 0, "pendentes": 0, "cortadas": 0,
            "q_previstas": 0.0})
        b["tarefas"] += 1
        status = (t.get("status") or "pendente").lower()
        if status == "feita":
            b["feitas"] += 1
        elif status in ("cortada", "cortado"):
            b["cortadas"] += 1
        else:
            b["pendentes"] += 1
        b["q_previstas"] += float(t.get("q_previstas") or 0)
    for nome, b in por_bloco.items():
        v = vol.get(nome) or {}
        b["q_feitas"] = int(v.get("feitas") or 0)
        b["q_acertos"] = int(v.get("acertos") or 0)
        b["pct_acerto"] = (round(b["q_acertos"] / b["q_feitas"] * 100, 1)
                           if b["q_feitas"] else None)
        b["pct_tarefas"] = (round(b["feitas"] / b["tarefas"] * 100, 1)
                            if b["tarefas"] else None)
        b["pct_questoes"] = (round(b["q_feitas"] / b["q_previstas"] * 100, 1)
                             if b["q_previstas"] else None)
        # camada fina: o que o ELO por tarefa enxerga hoje (part-6)
        b["q_feitas_por_elo"] = int((prog.get("blocos", {}).get(nome) or {})
                                    .get("feitas") or 0)

    sv = prog.get("sem_vinculo") or {}
    return {
        "blocos": dict(sorted(por_bloco.items())),
        "fora_de_bloco": fora,
        "areas_sem_mapa": sem_mapa,
        "orcamento_fase1": prog.get("orcamento_fase1"),
        "elo_por_tarefa": {
            "sessoes_sem_vinculo": sv.get("sessoes"),
            "questoes_sem_vinculo": sv.get("questoes"),
            "nota": ("o volume acima vem de `sessoes_bulk` por AREA (cobre tudo). "
                     "O elo por TAREFA (`tarefa_id`, part-6) cobre %s sessao(oes): "
                     "o backfill casa 1 de 126 de forma inequivoca, entao a coluna "
                     "`q_feitas_por_elo` e granularidade fina com cobertura parcial "
                     "-- declarada, nao escondida."
                     % max(0, 126 - int(sv.get("sessoes") or 0))),
        },
    }


def _bloco_semana(semana):
    import listas
    if semana is None:
        return {"semana": None, "tarefas": [], "nota": "plano sem tarefa pendente"}
    _code, pend = listas.pendentes(semana=semana, como_json=True, out=_mudo)
    tarefas = [{
        "id": t["id"], "bloco": t["bloco"], "tema": t["tema"],
        "tipo": t["tipo_norm"], "q_previstas": t["q_previstas"],
        "feitas": t["feitas"], "url_lista": t["url_lista"],
    } for t in pend.get("tarefas", [])]
    return {
        "semana": semana,
        "tarefas": tarefas,
        "total": len(tarefas),
        "q_previstas": round(sum(t["q_previstas"] for t in tarefas), 1),
    }


def _bloco_fsrs():
    import day_plan
    con = db.get_connection()
    try:
        contagens = day_plan._fsrs_counts(con)
    finally:
        con.close()
    vencidos = day_plan.vencidos_de(contagens)
    teto = day_plan._teto_efetivo(vencidos)
    ret = db.get_retencao_revlog(dias=7)
    return {
        "atrasados": contagens["atrasados"],
        "hoje": contagens["hoje"],
        "vencidos": vencidos,
        "pool_novos": contagens["backlog_novos"],
        "teto_do_dia": teto,
        "regime_divida": teto > day_plan.TETO_BASE,
        "retencao_7d": ret,
    }


def _bloco_projecao(hoje=None):
    import performance
    hoje = hoje or date.today()
    con = db.get_connection()
    try:
        vol = performance.volume_vs_marco(con, hoje)
        total_q, _ = performance.get_totais(con)
        mes = hoje.strftime("%Y-%m")
        q_mes = performance.get_questoes_do_mes(con, mes)
    finally:
        con.close()
    metas = performance.METAS_MENSAIS.get(mes)
    custo_acum = None
    if metas and total_q:
        custo_acum = round(metas["investimento"] / total_q, 3)
    marcos = []
    for nome, alvo, data_marco in performance.MARCOS:
        if not data_marco:
            continue
        dias = (data_marco - hoje).days
        faltam = max(0, alvo - (total_q or 0))
        marcos.append({
            "nome": nome, "meta": alvo, "data": data_marco.isoformat(),
            "dias": dias, "faltam": faltam,
            "ritmo_alvo": (round(faltam / dias, 1) if dias > 0 else None),
        })
    return {
        "acumulado": vol["total"],
        "acertos": vol["acertos"],
        "pct": (round(vol["acertos"] / vol["total"] * 100, 1) if vol["total"] else None),
        "marco_corrente": vol,
        "marcos": marcos,
        "custo": {
            "mes": mes,
            "questoes_no_mes": q_mes,
            "acumulado_por_questao": custo_acum,
            "meta_por_questao": performance.META_CUSTO_Q,
        },
        # Fronteira 1 -- declarada, nunca estimada.
        "enamed_2027": {
            "projecao": None,
            "motivo": ("sem ancora: ENAMED 2027 nao esta em `core/provas.json` "
                       "nem em `performance.MARCOS`. Cadastre a data para o "
                       "painel projetar em vez de adivinhar."),
        },
    }


def _bloco_proximas(n=7):
    # A ORDEM ja vem de `plano_listar` (`ORDER BY semana_plano, ordem, fonte, ...`).
    # Re-ordenar aqui seria uma segunda regra de ordenacao do plano -- a mesma
    # classe de defeito do mapa de bloco duplicado. Pega-se o topo e pronto.
    pend = db.plano_listar(status="pendente")
    return {"n": n, "tarefas": [{
        "id": t["id"], "semana": t.get("semana_plano"), "bloco": t.get("bloco"),
        "area": t.get("area"), "tema": t.get("tema"), "tipo": t.get("tipo_norm"),
        "q_previstas": float(t.get("q_previstas") or 0),
        "url_lista": t.get("url_lista"),
    } for t in pend[:n]]}


def coletar(hoje=None):
    """O contrato do painel. Dict com os 5 blocos + metadados. Read-only."""
    hoje = hoje or date.today()
    semana = _semana_corrente()
    return {
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "hoje": hoje.isoformat(),
        "titulo": TITULO,
        "semana_corrente": semana,
        "plano": _bloco_plano(),
        "semana": _bloco_semana(semana),
        "fsrs": _bloco_fsrs(),
        "projecao": _bloco_projecao(hoje),
        "proximas": _bloco_proximas(),
        "fontes": FONTES,
    }


# ------------------------------------------------------------------ render

def _e(v):
    return html.escape("" if v is None else str(v), quote=True)


def _num(v, casas=0, vazio="--"):
    if v is None:
        return vazio
    return ("%%.%df" % casas) % v


def _barra(pct):
    p = max(0.0, min(100.0, float(pct or 0)))
    return '<div class="barra"><i style="width:%.1f%%"></i></div>' % p


def _link(url, vazio="sem lista"):
    """`<a>` so para URL ABSOLUTA. O plano guarda tambem caminho LOCAL (ex.:
    `simulados/uerj/uerj_ad_2026_prova.pdf`), que resolve na maquina e morre numa
    pagina publicada -- link quebrado e pior que texto, porque promete."""
    if not url:
        return '<span class="tenue">%s</span>' % _e(vazio)
    if str(url).startswith(("http://", "https://")):
        return '<a href="%s" rel="noopener noreferrer">lista</a>' % _e(url)
    return '<span class="tenue" title="caminho local, nao navegavel aqui">%s</span>' % _e(url)


def _reguas_legivel(por_regua):
    """`{"1": 304}` -> `v1: 304`. Repr de dict na tela e vazamento de estrutura."""
    if not por_regua:
        return "nenhuma"
    return " · ".join("v%s: %d" % (k, v) for k, v in sorted(por_regua.items()))


def _rodape(chave):
    return '<p class="fonte">%s</p>' % _e(FONTES[chave])


def _sec(chave, titulo, corpo):
    return ('<section class="bloco" data-bloco="%s">\n  <h2>%s</h2>\n%s\n%s\n'
            '</section>' % (_e(chave), _e(titulo), corpo, _rodape(chave)))


def _html_plano(d):
    linhas = []
    for nome, b in d["blocos"].items():
        linhas.append(
            '<tr><th scope="row">%s</th><td>%d/%d</td><td>%d</td><td>%d</td>'
            '<td>%s / %s</td><td>%s</td><td>%s</td></tr>' % (
                _e(nome), b["feitas"], b["tarefas"], b["pendentes"], b["cortadas"],
                _num(b["q_feitas"]), _num(b["q_previstas"]),
                (_num(b["pct_questoes"], 1) + "%") if b["pct_questoes"] is not None else "--",
                (_num(b["pct_acerto"], 1) + "%") if b["pct_acerto"] is not None else "--"))
    for nome, v in sorted((d.get("fora_de_bloco") or {}).items()):
        pct = ((_num(v["acertos"] / v["feitas"] * 100, 1) + "%") if v["feitas"] else "--")
        linhas.append('<tr><th scope="row">%s <span class="tenue">fora dos blocos'
                      '</span></th><td>--</td><td>--</td><td>--</td><td>%s / --</td>'
                      '<td>--</td><td>%s</td></tr>'
                      % (_e(nome), _num(v["feitas"]), pct))
    orc = d.get("orcamento_fase1") or {}
    corpo = ['<table><thead><tr><th>bloco</th><th>tarefas feitas</th><th>pendentes</th>'
             '<th>cortadas</th><th>questoes feitas / previstas</th>'
             '<th>do previsto</th><th>acerto</th>'
             '</tr></thead><tbody>%s</tbody></table>'
             % ("".join(linhas) or '<tr><td colspan="7">plano sem tarefas</td></tr>')]
    if orc:
        corpo.append('<p class="metro">Orcamento Fase 1 (semanas 1-7): <b>%d</b> de %d '
                     'questoes <b>vinculadas a tarefa</b> (%s%%)</p>%s'
                     % (orc.get("feitas", 0), orc.get("orcamento", 0),
                        _num(orc.get("pct"), 1), _barra(orc.get("pct"))))
    elo = d.get("elo_por_tarefa") or {}
    if elo.get("nota"):
        corpo.append('<p class="aviso"><b>Duas camadas, e elas medem coisas '
                     'diferentes.</b> %s</p>' % _e(elo["nota"]))
    sm = d.get("areas_sem_mapa") or {}
    if sm:
        corpo.append('<p class="metro tenue">Areas sem bloco no plano (ficam fora da '
                     'tabela, nunca somadas a palpite): %s.</p>'
                     % _e(", ".join("%s (%dq)" % (k, v["feitas"])
                                    for k, v in sorted(sm.items()))))
    return "\n".join(corpo)


def _html_semana(d):
    if not d.get("tarefas"):
        return '<p class="metro">%s</p>' % _e(d.get("nota") or "nada pendente")
    itens = []
    for t in d["tarefas"]:
        alvo = _link(t.get("url_lista"))
        itens.append('<li><b>#%d</b> %s <span class="tenue">%s &middot; %s</span> '
                     '-- %s q previstas &middot; %s</li>'
                     % (t["id"], _e(t["tema"]), _e(t["bloco"]), _e(t["tipo"]),
                        _num(t["q_previstas"]), alvo))
    return ('<p class="metro">Semana <b>%s</b> &middot; %d tarefas &middot; '
            '%s questoes previstas</p><ul>%s</ul>'
            % (_e(d["semana"]), d["total"], _num(d["q_previstas"]), "".join(itens)))


def _html_fsrs(d):
    ret = d["retencao_7d"]
    if ret["retencao"] is None:
        txt_ret = "--"
        det_ret = "retencao 7d -- sem revisao nos ultimos %d dias" % ret["dias"]
    else:
        txt_ret = "%s%%" % _num(ret["retencao"] * 100, 1)
        det_ret = "retencao 7d (%d revisoes, %d lapsos)" % (
            ret["revisoes"], ret["lapsos"])
    regime = (' <span class="tag">REGIME DE DIVIDA</span>' if d["regime_divida"] else "")
    return (
        '<div class="metros">'
        '<div class="m"><b>%d</b><span>vencidos (%d atrasados + %d hoje)</span></div>'
        '<div class="m"><b>%d</b><span>teto do dia%s</span></div>'
        '<div class="m"><b>%d</b><span>pool nunca introduzidos</span></div>'
        '<div class="m"><b>%s</b><span>%s</span></div>'
        '</div>'
        '<p class="metro">Retencao medida pela regua de cada linha '
        '(<code>regua_versao</code>): nota 2 dada sob a regua v1 e LAPSO, sob a v2 '
        'e acerto. Revisoes por regua: %s.</p>'
        % (d["vencidos"], d["atrasados"], d["hoje"], d["teto_do_dia"], regime,
           d["pool_novos"], txt_ret, _e(det_ret),
           _e(_reguas_legivel(ret["por_regua"]))))


def _html_projecao(d):
    linhas = []
    for m in d["marcos"]:
        linhas.append('<tr><th scope="row">%s</th><td>%s</td><td>%d d</td>'
                      '<td>%s</td><td>%s q/dia</td></tr>'
                      % (_e(m["nome"]), _e(m["data"]), m["dias"],
                         _num(m["faltam"]), _num(m["ritmo_alvo"], 1)))
    c = d["custo"]
    custo = ("R$ %s/q <span class=\"tenue\">(meta R$ %s)</span>"
             % (_num(c["acumulado_por_questao"], 2), _num(c["meta_por_questao"], 2))
             if c["acumulado_por_questao"] is not None
             else '<span class="tenue">sem serie de investimento para %s</span>' % _e(c["mes"]))
    return (
        '<div class="metros">'
        '<div class="m"><b>%s</b><span>questoes acumuladas</span></div>'
        '<div class="m"><b>%s%%</b><span>acerto acumulado</span></div>'
        '<div class="m"><b>%s</b><span>custo por questao</span></div>'
        '</div>'
        '<table><thead><tr><th>marco</th><th>data</th><th>faltam</th>'
        '<th>questoes</th><th>ritmo-alvo</th></tr></thead><tbody>%s</tbody></table>'
        '<p class="aviso"><b>ENAMED 2027 sem projecao.</b> %s</p>'
        % (_num(d["acumulado"]), _num(d["pct"], 1), custo,
           "".join(linhas) or '<tr><td colspan="5">sem marco datado</td></tr>',
           _e(d["enamed_2027"]["motivo"])))


def _html_proximas(d):
    if not d["tarefas"]:
        return '<p class="metro tenue">nenhuma tarefa pendente</p>'
    itens = []
    for t in d["tarefas"]:
        alvo = _link(t.get("url_lista"), vazio="--")
        itens.append('<tr><td>#%d</td><td>S%s</td><td>%s</td><td>%s</td>'
                     '<td>%s</td><td>%s</td></tr>'
                     % (t["id"], _e(t["semana"]), _e(t["bloco"]), _e(t["tema"]),
                        _num(t["q_previstas"]), alvo))
    return ('<table><thead><tr><th>id</th><th>sem</th><th>bloco</th><th>tema</th>'
            '<th>q prev</th><th>lista</th></tr></thead><tbody>%s</tbody></table>'
            % "".join(itens))


def render_html(d):
    """Pagina autocontida. Contrato de renderizacao do projeto: UM `.wrap`, tokens
    em `:root`, dark por `prefers-color-scheme` GUARDADO + `[data-theme]`, `body`
    com background explicito, 400px sem scroll horizontal (memoria s151)."""
    corpo = "\n".join([
        _sec("plano", "Progresso por bloco", _html_plano(d["plano"])),
        _sec("semana", "Listas da semana", _html_semana(d["semana"])),
        _sec("fsrs", "Cards (FSRS)", _html_fsrs(d["fsrs"])),
        _sec("projecao", "Volume, custo e projecao", _html_projecao(d["projecao"])),
        _sec("proximas", "Proximas 7 tarefas", _html_proximas(d["proximas"])),
    ])
    return """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(titulo)s</title>
<style>
:root{
  --papel:#f6f4f0; --card:#ffffff; --afundado:#edeae4;
  --tinta:#191817; --tinta2:#54504a; --tinta3:#8b857b;
  --linha:#e0dbd2; --acento:#0e6b5c; --acento-fraco:#d9ece7;
  --alerta:#a2412a; --alerta-fraco:#f6e4de;
  --wrap:64rem; --raio:14px;
  --sombra:0 1px 2px rgba(0,0,0,.05), 0 10px 30px rgba(0,0,0,.06);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --papel:#131519; --card:#1b1e24; --afundado:#23272f;
    --tinta:#edeff3; --tinta2:#b4bac4; --tinta3:#7e8794;
    --linha:#2d323b; --acento:#4fd0b3; --acento-fraco:#123630;
    --alerta:#f0917a; --alerta-fraco:#3a221c;
    --sombra:0 1px 2px rgba(0,0,0,.45), 0 10px 30px rgba(0,0,0,.35);
  }
}
:root[data-theme="dark"]{
  --papel:#131519; --card:#1b1e24; --afundado:#23272f;
  --tinta:#edeff3; --tinta2:#b4bac4; --tinta3:#7e8794;
  --linha:#2d323b; --acento:#4fd0b3; --acento-fraco:#123630;
  --alerta:#f0917a; --alerta-fraco:#3a221c;
  --sombra:0 1px 2px rgba(0,0,0,.45), 0 10px 30px rgba(0,0,0,.35);
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%%}
body{
  margin:0; background:var(--papel); color:var(--tinta);
  font-family:ui-sans-serif,system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  font-size:clamp(15px,.95rem + .2vw,17px); line-height:1.55; overflow-wrap:break-word;
}
.wrap{max-width:var(--wrap);margin:0 auto;padding:24px 16px 72px}
h1{font-size:clamp(1.2rem,1rem + .8vw,1.6rem);margin:0;letter-spacing:-.01em}
h2{font-size:1.02rem;margin:0 0 14px;letter-spacing:-.005em}
p{margin:0}
a{color:var(--acento)}
code{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.86em}
.topo{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:baseline;justify-content:space-between;margin-bottom:22px}
.sub{color:var(--tinta3);font-size:.84em}
.bloco{background:var(--card);border:1px solid var(--linha);border-radius:var(--raio);
       box-shadow:var(--sombra);padding:20px 18px;margin-bottom:18px}
.fonte{color:var(--tinta3);font-size:.74em;margin-top:14px;border-top:1px solid var(--linha);padding-top:10px}
.metro{color:var(--tinta2);font-size:.86em;margin-top:12px}
.tenue{color:var(--tinta3)}
.tag{display:inline-block;font-size:.68em;letter-spacing:.06em;text-transform:uppercase;
     color:var(--alerta);background:var(--alerta-fraco);border-radius:99px;padding:2px 8px;margin-left:6px}
.metros{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}
.m{background:var(--afundado);border-radius:10px;padding:12px 14px}
.m b{display:block;font-size:1.35em;font-variant-numeric:tabular-nums;line-height:1.2}
.m span{font-size:.76em;color:var(--tinta3)}
table{width:100%%;border-collapse:collapse;font-size:.88em;font-variant-numeric:tabular-nums}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--linha)}
thead th{font-size:.74em;letter-spacing:.06em;text-transform:uppercase;color:var(--tinta3);font-weight:600}
tbody th{font-weight:650}
ul{margin:10px 0 0;padding-left:20px}
li{margin-bottom:6px}
.barra{height:6px;background:var(--afundado);border-radius:99px;margin-top:8px;overflow:hidden}
.barra i{display:block;height:100%%;background:var(--acento)}
.aviso{border-left:3px solid var(--alerta);background:var(--alerta-fraco);
       padding:10px 12px;border-radius:8px;margin-top:14px;font-size:.84em}
footer{color:var(--tinta3);font-size:.76em;margin-top:26px;border-top:1px solid var(--linha);padding-top:14px}
@media (max-width:460px){
  .bloco{padding:16px 13px}
  th,td{padding:7px 6px}
  table{font-size:.8em}
}
</style>
</head>
<body>
<div class="wrap">
  <header class="topo">
    <div>
      <h1>%(titulo)s</h1>
      <p class="sub">gerado em %(gerado)s &middot; semana %(semana)s do plano</p>
    </div>
    <p class="sub">pagina gerada por <code>tools/painel.py --html</code> &middot; read-only</p>
  </header>
%(corpo)s
  <footer>
    Todo numero vem do banco pela funcao citada no rodape de cada bloco. Esta pagina
    nao guarda estado e nao escreve nada: e leitura. Regenerar a cada fechamento de
    sessao e republicar na mesma URL.
  </footer>
</div>
</body>
</html>
""" % {"titulo": _e(TITULO), "gerado": _e(d["gerado_em"]),
       "semana": _e(d["semana_corrente"] if d["semana_corrente"] is not None else "--"),
       "corpo": corpo}


# -------------------------------------------------------------------- CLI

def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Painel de progresso do MedHub (read-only). Gera o JSON "
                    "(contrato) ou a pagina HTML (render).")
    ap.add_argument("--json", action="store_true",
                    help="imprime o dado estruturado dos 5 blocos (contrato testavel)")
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
                          "semana": dados["semana_corrente"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
