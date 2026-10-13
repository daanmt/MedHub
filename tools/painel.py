#!/usr/bin/env python3
"""Painel de progresso do MedHub -- pagina gerada do banco (part-7, s186; refeito na s194).

READ-ONLY ABSOLUTO. Nao abre `sqlite3` por conta propria (AGENTE.md secao 6: CLI nao faz SQL
direto) e nao aparece na allowlist de writers (F49). Todo numero sai de um leitor que JA existe e
que outra superficie tambem usa -- o painel nao tem regra propria de semana, de teto nem de ritmo:

    semana e listas   -> `plano.panorama` (o MESMO do `plano.py --panorama` do boot), sobre as linhas
                         com a contagem do banco do hub (`plano.linhas_com_q_hub`, P20 -- s219)
    meta do dia       -> `performance.volume_vs_marco` (a MESMA linha Meta do boot; s203)
    saldo de cards    -> `day_plan._fsrs_counts` + `_teto_efetivo` + `consumo_logico` (P09, s216)
    agenda de 7 dias  -> `db.agenda_revisoes` (o MESMO da tela de fim da aba Cards)
    ritmo             -> `db.get_ritmo_real` + `performance.volume_vs_marco` + `day_plan._cronograma_hoje`
                         (a Fase 1 entra como COBERTURA da meta, nunca como 2o ritmo -- s203)
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
import math
import subprocess
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
ARTIFATOS = ROOT / "artifacts"
#: s216 (hub-integracao part-6): o marcador do `--record-lote` -- QUAL lote ja esta no numero publicado
#: (o "Hoje ao vivo" da pagina so soma as notas de lote que ainda nao foi gravado). Ausente = "".
MARCADOR_GRAVACAO = ROOT / "tmp" / "hub" / "ultima_gravacao_hub.json"
#: s226 (sprint-final-uerj part-3): o estado `quadro/<slug>` que o tique baixa do db do hub (o mesmo
#: `--quadro-estado tmp/hub_db` do `hub.py`) -- a RD sem assinatura entra no "Hoje". s226 (part-4, audit
#: da part-3): AUSENTE = estado desconhecido -- o Painel nao afirma "nao assinada" (nenhuma RD no Hoje).
QUADRO_ESTADO = ROOT / "tmp" / "hub_db" / "quadro"

#: Ordem dos blocos na pagina. O `id` e o `data-bloco` do HTML e a chave do JSON. Os 4 que a
#: pagina SEMPRE desenha.
BLOCOS = ("dia", "ritmo", "semana", "blocos")
#: O 5o bloco, Documentacao (s212): sempre no JSON (lista, vazia sem documento), na pagina so com
#: documento -- por isso fora de `BLOCOS`.
BLOCO_DOCS = "docs"

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
    """{tarefa_id: [{slug, titulo}]} do registro do quadro de aulas (`core/hub_quadro.json`), com a
    semantica de `hub.ligacoes_do_quadro`: `tarefa_id` = a aula CUMPRE a tarefa; `tarefas` = a
    aula a PREPARA (s213: antes so o `tarefa_id`, e a aula que prepara uma lista nao aparecia).
    So aula com arquivo em `artifacts/` (a mesma regra do hub: sem arquivo, o atalho abriria
    nada). Ilegivel ou ausente = {} (a tarefa so perde o atalho; o numero nao muda)."""
    try:
        reg = json.loads(QUADRO.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    saida = {}
    for slug, item in (reg.get("itens") or {}).items():
        item = item or {}
        if not (ARTIFATOS / ("aula-%s.html" % slug)).is_file():
            continue
        ids = {int(x) for x in (item.get("tarefas") or [])}
        if item.get("tarefa_id") is not None:
            ids.add(int(item["tarefa_id"]))
        for tid in sorted(ids):
            saida.setdefault(tid, []).append({"slug": slug, "titulo": item.get("titulo") or slug})
    return saida


def _tarefa(t, aulas, no_hub):
    """Uma tarefa do panorama como o painel a desenha -- o MESMO construtor para a semana
    corrente e para a rota."""
    from app.utils import areas
    agregada = t.get("area") in areas.AREAS_AGREGADAS
    ligadas = aulas.get(t["id"]) or []
    return {
        "id": t["id"], "semana": t["semana"], "atrasada": t["atrasada"],
        "tema": t["tema"], "q": t["q"], "classe": t["classe"],
        "url_lista": t["url_lista"], "area": t.get("area"),
        # simulado se apresenta como simulado, nunca pelo bloco de fallback (CM)
        "rotulo": t.get("area") if agregada else (t.get("bloco") or t.get("area")),
        "aula": ligadas[0]["slug"] if ligadas else None,
        "aulas": ligadas,
        "no_hub": t["id"] in no_hub,
    }


def _bloco_semana(linhas, hoje):
    """A semana corrente e as abertas pela MESMA funcao do boot (`plano.panorama`); a `rota`
    (s213) = as semanas seguintes ate a ultima da Fase 1, da mesma funcao. `linhas` ja vem com a
    contagem do banco do hub (`coletar`: `plano.linhas_com_q_hub`, P20)."""
    import plano
    pan = plano.panorama(linhas, plano.calendario_trilha(), hoje)
    if not pan:
        return {"semana": None, "tarefas": [], "total": 0, "q": 0, "atrasadas": 0,
                "inicio": None, "fim": None, "dias": None, "proxima": None, "rota": []}
    aulas = _aulas_por_tarefa()
    # s201: tarefa com questoes no banco se resolve na aba Listas do hub. P20 (s219): a marca sai da
    # MESMA leitura que a contagem (`q_hub`), a da Teoria e a do boot
    no_hub = {int(l["id"]) for l in linhas if l.get("q_hub") and l.get("id") is not None}
    tarefas = [_tarefa(t, aulas, no_hub) for t in pan["abertas"]]
    rota = [{"semana": r["semana"], "inicio": r["inicio"], "fim": r["fim"], "q": r["q"],
             "feitas": r["feitas"], "total": r["total"],
             "tarefas": [_tarefa(t, aulas, no_hub) for t in r["tarefas"]]}
            for r in pan.get("rota") or []]
    return {
        "semana": pan["semana"], "inicio": pan["inicio"], "fim": pan["fim"],
        "dias": pan["dias"], "tarefas": tarefas, "total": len(tarefas),
        "q": pan["q_abertas"], "atrasadas": pan["atrasadas"],
        "feitas_semana": pan["feitas_semana"], "tarefas_semana": pan["tarefas_semana"],
        "proxima": pan["proxima"], "rota": rota,
    }


def _datas_das_aulas(caminhos):
    """{caminho: AAAA-MM-DD}: a data em que cada aula ENTROU no git (1o commit que a adicionou), numa
    chamada SO de `git log` para todas (s226 part-4, audit da part-3: era um `git log --follow` por
    candidata). Sem `--follow` (o rename conta como entrada: limite aceito, so ordena o backlog); fora
    do git ou fora do repo, a data do arquivo. Injetavel nos testes."""
    rels = {}
    for c in caminhos:
        c = Path(c)
        try:
            rels[c.resolve().relative_to(ROOT.resolve()).as_posix()] = c
        except ValueError:
            rels[c.as_posix()] = c
    datas, atual = {}, None
    if rels:
        try:
            saida = subprocess.run(["git", "-c", "core.quotepath=off", "log", "--diff-filter=A",
                                    "--format=@@%as", "--name-only", "--"] + sorted(rels),
                                   cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", timeout=30)
            for linha in (saida.stdout or "").splitlines() if saida.returncode == 0 else ():
                if linha.startswith("@@"):
                    atual = linha[2:].strip()
                elif linha.strip() and atual:
                    datas[linha.strip()] = atual   # o log vem do mais novo ao mais velho: fica a ultima vista
        except (OSError, ValueError, subprocess.SubprocessError):
            pass
    return {c: datas.get(rel) or date.fromtimestamp(c.stat().st_mtime).isoformat() for rel, c in rels.items()}


def _rd_nao_assinada():
    """A Revisao Direcionada NAO assinada mais antiga: item `revisao` do quadro (`core/hub_quadro.json`)
    com arquivo em `artifacts/` e sem `feito` no estado do quadro (`QUADRO_ESTADO`, lido por
    `hub.ler_estado_quadro`). None = nenhuma. Registro ilegivel = None (o Hoje so perde a linha da RD).
    s226 (part-4, audit da part-3): sem a pasta do estado, o estado e DESCONHECIDO e a funcao devolve
    None -- falha para o lado certo (nunca chamar de "nao assinada" a RD que ele pode ja ter assinado)."""
    import hub
    if not Path(QUADRO_ESTADO).exists():
        return None
    try:
        reg = json.loads(QUADRO.read_text(encoding="utf-8")).get("itens") or {}
        estado = hub.ler_estado_quadro(QUADRO_ESTADO)
    except (OSError, ValueError):
        return None
    arqs = {}
    for slug, item in reg.items():
        item = item or {}
        arq = ARTIFATOS / ("aula-%s.html" % slug)
        if item.get("tipo") != "revisao" or not arq.is_file() or (estado.get(slug) or {}).get("feito"):
            continue
        arqs[slug] = (arq, item.get("titulo") or slug)
    datas = _datas_das_aulas([a for a, _t in arqs.values()]) if arqs else {}
    candidatas = [{"slug": s, "titulo": t, "data": datas.get(a)} for s, (a, t) in arqs.items()]
    return min(candidatas, key=lambda r: (r["data"] or "9999", r["slug"])) if candidatas else None


def _bloco_sprint(linhas, hoje):
    """s226 (sprint-final-uerj part-3): Hoje / Proximos dias / Fora do sprint pela MESMA funcao que a
    aba Listas e o boot leem (`plano.agenda_sprint`); cada tarefa pelo MESMO construtor da semana
    (`_tarefa`). None = banco sem sprint (`dia_plano` todo NULL): a pagina desenha a semana antiga."""
    import plano
    ag = plano.agenda_sprint(linhas, hoje)
    if ag is None:
        return None
    aulas = _aulas_por_tarefa()
    no_hub = {int(l["id"]) for l in linhas if l.get("q_hub") and l.get("id") is not None}
    tarefa = lambda t: _tarefa(t, aulas, no_hub)
    return {
        "hoje": [tarefa(t) for t in ag["hoje"]], "q_hoje": ag["q_hoje"],
        "proximos": [{"data": p["data"], "q": p["q"], "tarefas": [tarefa(t) for t in p["tarefas"]]}
                     for p in ag["proximos"]],
        "fora": [dict(tarefa(t), motivo=t["motivo"]) for t in ag["fora"]],
        "rd": _rd_nao_assinada(),
    }


def _sessao_gravada():
    """A `sessao` do ultimo lote gravado (marcador do tique); ilegivel ou ausente = "" (a pagina
    soma o lote no ar inteiro: no pior caso, a mais por um tique -- limite aceito na spec)."""
    try:
        return str(json.loads(Path(MARCADOR_GRAVACAO).read_text(encoding="utf-8")).get("sessao") or "")
    except (OSError, ValueError, AttributeError):
        return ""


def _bloco_dia(linhas, hoje):
    """Hoje: questoes contra o ritmo da META, saldo de cards e a agenda de 7 dias -- leitores do
    `performance`, do `day_plan` e o `db.agenda_revisoes` do export do player.

    s203 (decisao do operador em 27/09: "pode remover essa meta de 27/09; a unica meta e 01/11"):
    o alvo do dia e o ritmo da meta (`volume_vs_marco`), o mesmo da linha Meta do boot. ⚰️ *Era a
    cota da semana de calendario (`day_plan.cota_do_dia`), que no domingo despejava a semana
    inteira: "0 de ~474, cota de ~474 por dia ate dom 27/09".*"""
    import day_plan
    import performance
    feitas_hoje = sum(int(s.get("questoes_feitas") or 0) for s in db.sessoes_bulk_listar()
                      if str(s.get("data_sessao") or "")[:10] == hoje.isoformat())
    con = db.get_connection()
    try:
        vm = performance.volume_vs_marco(con, hoje)
        cont = day_plan._fsrs_counts(con)
        try:
            # s216 (part-5, regra P09): o lote conta no dia da 1a nota -- o MESMO consumo do teto do
            # export de cards (`consumo_do_dia`); o cabecalho "Hoje, <data>" segue o relogio
            consumo = int(day_plan.consumo_logico(con, hoje))
        except Exception:  # noqa: BLE001 -- sem contador: sem saldo, declarado na tela
            consumo = None
    finally:
        con.close()
    vencidos = day_plan.vencidos_de(cont)
    teto = int(day_plan._teto_efetivo(vencidos))
    return {
        "questoes": {
            "feitas_hoje": feitas_hoje,
            "alvo_dia": vm["ritmo_alvo"],
            "meta": vm["meta"],
            "faltam": vm["faltam"],
            "dias": vm["dias"],
            "data_meta": vm["data_marco"].isoformat() if vm.get("data_marco") else None,
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
        "sessao_gravada": _sessao_gravada(),
    }


def _bloco_ritmo(hoje):
    """Real (7 e 14 dias) ao lado do ritmo da META (o do boot) e a Fase 1 como COBERTURA dela:
    onde o acumulado chega se o plano fechar (s203 -- era um 2o ritmo, "~90,9 por dia")."""
    import day_plan
    import performance
    con = db.get_connection()
    try:
        vm = performance.volume_vs_marco(con, hoje)
    finally:
        con.close()
    cron = day_plan._cronograma_hoje(vm["total"], hoje) or {}
    # s226 (sprint-final-uerj part-5): havendo sprint, a cobertura conta o SPRINT (o mesmo
    # `plano.resumo_sprint` do boot); None = a frase da Fase 1
    sp = cron.get("sprint")
    return {
        "real_7d": db.get_ritmo_real(7),
        "real_14d": db.get_ritmo_real(14),
        "marco": vm["marco"],
        "meta": vm["meta"],
        "faltam": vm["faltam"],
        "dias_marco": vm["dias"],
        "alvo_marco": vm["ritmo_alvo"],
        "fase1_q": cron.get("restante_q"),
        "fase1_simulados_q": cron.get("simulados_q"),
        "fechando_q": cron.get("fechando_q"),
        "fim_fase1": cron.get("fim_conteudo_alvo"),
        "sprint": ({"q": sp["q_sprint"], "simulados_q": sp["simulados_q"], "fechando_q": sp["fechando_q"],
                    "fim": sp["fim"], "fora": sp["fora"], "q_fora": sp["q_fora"]} if sp else None),
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
    """O contrato do painel. Dict com os 4 blocos de `BLOCOS` + o de Documentacao (`BLOCO_DOCS`)
    + metadados. Read-only."""
    import plano
    hoje = hoje or db.hoje()
    # P20 (s219): as questoes de cada tarefa contam o banco do hub quando ela tem questoes la -- o MESMO
    # numero da Teoria, da aba Listas e do boot (`plano.q_da_tarefa`)
    linhas = plano.linhas_com_q_hub(db.plano_listar())
    return {
        "gerado_em": db.agora().isoformat(timespec="seconds"),
        "data": hoje.isoformat(),
        "titulo": TITULO,
        "dia": _bloco_dia(linhas, hoje),
        "semana": _bloco_semana(linhas, hoje),
        # s226 (sprint-final-uerj part-3): a agenda por dia; None = sem sprint (a pagina usa a semana)
        "sprint": _bloco_sprint(linhas, hoje),
        "ritmo": _bloco_ritmo(hoje),
        "blocos": _bloco_blocos(linhas),
        BLOCO_DOCS: _bloco_docs(),
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


def _bloco_docs():
    """Documentos de referencia do hub (s212, pedido do operador em 03/10/2026: "um bloco de
    documentacao no Painel"): os itens `tipo: analise` do registro do quadro cujo arquivo existe em
    `artifacts/aula-<slug>.html`. Registro ilegivel ou ausente = [] (o bloco some; nada quebra)."""
    try:
        reg = json.loads(QUADRO.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    docs = []
    for slug, item in (reg.get("itens") or {}).items():
        item = item or {}
        if item.get("tipo") == "analise" and (ARTIFATOS / ("aula-%s.html" % slug)).is_file():
            docs.append({"slug": slug, "titulo": item.get("titulo") or slug})
    return docs


def _html_docs(docs):
    """Sem `data-tarefa` (nao e tarefa do plano); o link leva o titulo (`data-titulo`) que o hub
    mostra no leitor (s216)."""
    itens = "".join(
        '<li class="tarefa"><p class="t-tema">%s</p><p class="t-acao">'
        '<a href="aulas/%s.html" data-hub-aula="%s" data-titulo="%s">abrir documento</a></p></li>'
        % (_e(d["titulo"]), _e(d["slug"]), _e(d["slug"]), _e(d["titulo"])) for d in docs)
    return '<h2>Documentação</h2>\n<ol class="tarefas">%s</ol>' % itens


def _modo_hub(t):
    """Modo da aba Listas para a tarefa com questoes no banco do hub: Simulados para simulado,
    Questoes para o resto (s213: o modo sai da AREA)."""
    from app.utils import areas
    return "simulados" if t.get("area") in areas.AREAS_AGREGADAS else "questoes"


def _acao(t):
    """O que fazer com a tarefa FORA do alvo da linha: a lista externa (ou a prova em PDF) e cada
    aula ligada.

    s213 (D4-1, decisao do operador em 25/09: "nao sair do medhub"): tarefa com questoes no banco do
    hub (`no_hub`) abre a aba Listas e o link do EMED some; so fora do banco o "abrir lista" externo
    aparece. s226 (part-3, padrao da Teoria): na `no_hub` a LINHA INTEIRA e o alvo (`_html_tarefa`);
    aqui sobra so a aula, pequena e secundaria ("aula", ou o titulo quando ha varias). ⚰️ *Era o
    "resolver no hub" em toda linha.* P20 (s219): a tarefa sem acao diz a classe na META, apagada
    (`plano.meta_da_tarefa`, a regra da Teoria)."""
    partes = []
    no_hub = bool(t.get("no_hub"))
    if no_hub:
        pass
    elif t["url_lista"] and str(t["url_lista"]).startswith(("http://", "https://")):
        partes.append(_link(t["url_lista"], "abrir lista"))
    elif t["url_lista"]:
        partes.append('<span class="tenue">prova em PDF no computador</span>')
    # aula que CUMPRE (tarefa de aula) ou PREPARA (lista) -- o que a aba Aulas ja mostrava
    aulas = t.get("aulas") or ([{"slug": t["aula"], "titulo": None}] if t.get("aula") else [])
    varias = len(aulas) > 1
    for a in aulas:
        # s216 (part-2): o titulo vai no link -- o hub abre o leitor direto, sem achar o link na Teoria
        partes.append('<a href="aulas/%s.html" data-hub-aula="%s" data-titulo="%s">%s</a>'
                      % (_e(a["slug"]), _e(a["slug"]), _e(a.get("titulo") or a["slug"]),
                         _e(a.get("titulo") or a["slug"]) if varias else ("aula" if no_hub else "abrir aula")))
    return "<br>".join(partes)


def _html_dia(d, data_iso):
    hoje = date.fromisoformat(data_iso)
    q, c, ag = d["questoes"], d["cards"], d["agenda"]

    # s216 (part-6, P08 v0): o numero publicado leva a ancora do "Hoje ao vivo" -- a pagina soma "+K"
    # AO LADO (o que ela gravou depois do publish), nunca o substitui
    b_q = '<b data-vivo="questoes" data-base="%s">%s</b>' % (_e(q["feitas_hoje"]), _n(q["feitas_hoje"]))
    if q["alvo_dia"] is not None:
        alvo = math.ceil(q["alvo_dia"])
        nota_q = ("para %s em %s: faltam %s em %s dias."
                  % (_n(q["meta"]), _dm(q["data_meta"]), _n(q["faltam"]), _n(q["dias"])))
        num_q = '%s de ~%s' % (b_q, _n(alvo))
        barra_q = _pct(q["feitas_hoje"], alvo)
    elif q["faltam"] == 0:
        nota_q = "meta de %s atingida." % _n(q["meta"])
        num_q = '%s feitas' % b_q
        barra_q = 100.0
    else:
        nota_q = "a data da meta passou."
        num_q = '%s feitas' % b_q
        barra_q = 0.0

    if c["consumo_hoje"] is None:
        num_c = '<b>--</b> de %s' % _n(c["teto"])
        nota_c = "não consegui contar as revisões de hoje."
        barra_c = 0.0
    else:
        num_c = '<b data-vivo="cards" data-base="%s">%s</b> de %s' % (
            _e(c["consumo_hoje"]), _n(c["consumo_hoje"]), _n(c["teto"]))
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
        '<div class="doses" data-sessao-gravada="%s">\n'
        '  <div class="dose"><h3>Questões</h3><p class="fracao">%s</p>'
        '<div class="barra"><i style="width:%.1f%%"></i></div><p class="nota">%s</p></div>\n'
        '  <div class="dose"><h3>Cards</h3><p class="fracao">%s</p>'
        '<div class="barra"><i style="width:%.1f%%"></i></div><p class="nota">%s</p>'
        '<p class="nota">%s.</p>'
        '<p class="ir"><a href="#cards" data-hub-aba="cards">Ir para os cards</a></p></div>\n'
        '</div>\n'
        '<div class="agenda"><h3>Revisões nos próximos 7 dias</h3>'
        '<ol class="ag-barras" aria-label="Revisões por dia">%s</ol></div>'
        % (DIAS_EXTENSO[hoje.weekday()], hoje.strftime("%d/%m"), _e(d.get("sessao_gravada") or ""),
           num_q, barra_q, _e(nota_q),
           num_c, barra_c, _e(nota_c), _e(", ".join(extra_c)),
           barras))


def _html_tarefa(t, proxima=False):
    """Um `<li class="tarefa">`: tema, rotulo, questoes e acao -- o MESMO na semana corrente e na
    rota. s216 (hub-integracao part-2): carrega `data-tarefa` (o id do plano) -- e por ele que o hub
    pinta, sem publish, a lista resolvida na aba Listas. P20 (s219): a meta segue a regra da Teoria
    (`plano.meta_da_tarefa`) e o titulo, a correcao de exibicao (`plano.tema_exibido`).
    s226 (part-3, P21): com questoes no banco do hub, tema + meta viram UM alvo (`a.t-alvo` com
    `data-hub-aba`, o atalho que o hub ja trata); a aula fica fora dele (link dentro de link e
    invalido). O atraso sai da linha: o subtitulo "Atrasadas · N" diz uma vez (`_html_semana`).
    `proxima` = a 1a tarefa da semana: so o rotulo "Proxima", o mesmo controle das outras."""
    import plano
    meta = ['<span class="t-rot">%s</span>' % _e(t["rotulo"] or "?")]
    meta += ["<span>%s</span>" % _e(x) for x in plano.meta_da_tarefa(t["q"], t["classe"], plano.tem_acao(t))]
    classes = "tarefa" + (" atrasada" if t["atrasada"] else "") + (" proxima" if proxima else "")
    corpo = ('<p class="t-tema">%s</p><p class="t-meta">%s</p>'
             % (_e(plano.tema_exibido(t["tema"]) or "(sem tema)"), " ".join(meta)))
    acao = _acao(t)
    if t.get("no_hub"):
        corpo = ('<a class="t-alvo" href="#questoes" data-hub-aba="questoes" data-hub-modo="%s">%s</a>'
                 % (_modo_hub(t), corpo))
        if acao:
            corpo += '<p class="t-acao t-sec">%s</p>' % acao
    else:
        corpo += '<p class="t-acao">%s</p>' % acao
    return '<li class="%s" data-tarefa="%s">%s</li>' % (classes, _e(t["id"]), corpo)


def _html_rota(rota):
    """s213 (pedido do operador: "a rota inteira no Painel"): cada semana seguinte ate a prova,
    RECOLHIDA (`<details>` fechado; a corrente segue aberta acima), com as tarefas no mesmo
    `<li>` e os mesmos links. Datas com " a " (o travessao e proibido na pagina)."""
    semanas = []
    for r in rota:
        tit = "Semana %s" % _e(r["semana"])
        if r.get("inicio"):
            tit += " · %s a %s" % (_dm(r["inicio"]), _dm(r["fim"]))
        n = len(r["tarefas"])
        # espaco duro entre numero e palavra: o resumo quebra entre os pares, nunca "789 / questoes"
        conta = "%d&nbsp;tarefa%s" % (n, "" if n == 1 else "s")
        if r["q"]:
            conta += " · %s&nbsp;questões" % _n(r["q"])
        semanas.append('<details class="rota-sem"><summary><span class="rota-tit">%s</span> '
                       '<span class="rota-n">%s</span></summary><ol class="tarefas">%s</ol></details>'
                       % (tit, conta, "".join(_html_tarefa(t) for t in r["tarefas"])))
    return '<div class="rota"><h3>Até a prova</h3>%s</div>' % "".join(semanas)


def _html_semana(d):
    if d["semana"] is None:
        return '<h2>Semana</h2><p class="nota">Nenhuma tarefa pendente no plano.</p>'
    if d["inicio"]:
        janela = "%s a %s, %d dia(s) contando hoje." % (_dm(d["inicio"]), _dm(d["fim"]), d["dias"])
    else:
        janela = "Fora do calendário do plano: pela ordem das tarefas."
    if d["total"]:
        resumo = "%d tarefa(s) em aberto, %s questões." % (d["total"], _n(d["q"]))
    else:
        # s213 (audit R2): semana corrente sem pendencia nao desenha "0 tarefa(s)" nem lista vazia
        resumo = "Sem tarefa em aberto nesta semana."
    # s226 (part-3, P21): o atraso aparece UMA vez, no subtitulo "Atrasadas · N" (a ordem do plano
    # ja as traz primeiro); ⚰️ *era "vem atrasadas" no resumo e "da semana N" em toda linha*
    atrasadas = [t for t in d["tarefas"] if t["atrasada"]]
    correntes = [t for t in d["tarefas"] if not t["atrasada"]]
    primeira = d["tarefas"][0]["id"] if d["tarefas"] else None
    html_t = lambda t: _html_tarefa(t, proxima=t["id"] == primeira)
    prox = d.get("proxima")
    txt_prox = ""
    if d.get("rota"):
        # s213: a rota inteira ate a prova substitui a linha "Depois" (que so contava a S+1)
        txt_prox = _html_rota(d["rota"])
    elif prox:
        quando = " (%s a %s)" % (_dm(prox["inicio"]), _dm(prox["fim"])) if prox.get("inicio") else ""
        txt_prox = ('<p class="nota prox">Depois: semana %s%s, %d tarefa(s), %s questões.</p>'
                    % (_e(prox["semana"]), quando, prox["tarefas"], _n(prox["q"])))
    # A semana inteira passa de 20 tarefas: as primeiras (e todas as atrasadas) ficam a vista, o
    # resto recolhido na MESMA ordem do plano -- nada some, so para de gritar.
    lista = ""
    if atrasadas:
        lista += ('<h3 class="t-grupo atrasadas">Atrasadas · %d</h3><ol class="tarefas">%s</ol>'
                  % (len(atrasadas), "".join(html_t(t) for t in atrasadas)))
        if correntes:
            lista += '<h3 class="t-grupo">Desta semana · %d</h3>' % len(correntes)
    corte = max(0, VISIVEIS_SEMANA - len(atrasadas))
    itens = [html_t(t) for t in correntes]
    if itens[:corte]:
        lista += '<ol class="tarefas">%s</ol>' % "".join(itens[:corte])
    if len(itens) > corte:
        lista += ('<details class="mais"><summary>Ver as outras %d</summary>'
                  '<ol class="tarefas" start="%d">%s</ol></details>'
                  % (len(itens) - corte, corte + 1, "".join(itens[corte:])))
    return ('<h2>Semana %s do plano</h2>\n<p class="sub">%s %s</p>\n%s\n%s'
            % (_e(d["semana"]), _e(janela), _e(resumo), lista, txt_prox))


def _plural(n, um, varios):
    """"3&nbsp;listas": espaco duro entre numero e palavra (o resumo quebra entre os pares)."""
    return "%s&nbsp;%s" % (_n(n), um if n == 1 else varios)


def _conta_do_dia(tarefas):
    """"2 listas · 1 aula": o que o dia tem, pelo que se faz com cada tarefa (simulado pela area)."""
    from app.utils import areas
    nomes = (("simulado", "simulados"), ("lista", "listas"), ("aula", "aulas"), ("tarefa", "tarefas"))
    conta = {u: 0 for u, _v in nomes}
    for t in tarefas:
        if t.get("area") in areas.AREAS_AGREGADAS:
            conta["simulado"] += 1
        else:
            conta[{"lista": "lista", "caderno": "lista", "aula": "aula"}.get(t["classe"], "tarefa")] += 1
    return " · ".join(_plural(conta[u], u, v) for u, v in nomes if conta[u])


def _motivo_exibido(motivo):
    """O motivo gravado pelo plano (sem acento, como a nota) na grafia da tela."""
    return " ".join({"ate": "até", "ja": "já"}.get(p, p) for p in str(motivo or "").split(" "))


def _html_rd(rd):
    """A RD nao assinada mais antiga: a linha inteira abre o leitor (o atalho `data-hub-aula` do Painel;
    o hub a marca "assinado" ao vivo, como as outras linhas com aula)."""
    return ('<li class="tarefa rd"><a class="t-alvo" href="aulas/%s.html" data-hub-aula="%s" data-titulo="%s">'
            '<p class="t-tema">%s</p><p class="t-meta"><span class="t-rot">RD</span>'
            '<span>revisão direcionada ainda não assinada</span></p></a></li>'
            % (_e(rd["slug"]), _e(rd["slug"]), _e(rd["titulo"]), _e(rd["titulo"])))


def _html_sprint(s, cards):
    """s226 (sprint-final-uerj part-3): Hoje (as tarefas do dia, o total de questoes, os cards do dia e
    a RD nao assinada mais antiga) + Proximos dias (um dia por linha, recolhido) + Fora do sprint
    (recolhido, pelo motivo). Sem semana e sem atraso: a tarefa de dia que passou ja vem no Hoje.
    Cards = o que falta da dose do dia (`restantes`); sem contador, o teto."""
    hoje = s["hoje"]
    primeira = hoje[0]["id"] if hoje else None
    if hoje:
        resumo = "%s · %s" % (_plural(len(hoje), "tarefa", "tarefas"),
                              _plural(s["q_hoje"], "questão", "questões"))
    else:
        resumo = "Nenhuma tarefa do plano para hoje"
    n_cards = cards.get("restantes") if cards.get("consumo_hoje") is not None else cards.get("teto")
    if n_cards:
        resumo += " + %s" % _plural(n_cards, "card", "cards")
    itens = "".join(_html_tarefa(t, proxima=t["id"] == primeira) for t in hoje)
    if s.get("rd"):
        itens += _html_rd(s["rd"])
    corpo = '<h2>Plano de hoje</h2>\n<p class="sub">%s.</p>\n' % resumo
    if itens:
        corpo += '<ol class="tarefas">%s</ol>\n' % itens
    if s["proximos"]:
        dias = []
        for p in s["proximos"]:
            dia = date.fromisoformat(p["data"])
            conta = _conta_do_dia(p["tarefas"]) + (" · %s&nbsp;q" % _n(p["q"]) if p["q"] else "")
            dias.append('<details class="rota-sem"><summary><span class="rota-tit">%s %s</span> '
                        '<span class="rota-n">%s</span></summary><ol class="tarefas">%s</ol></details>'
                        % (DIAS_SEMANA[dia.weekday()], dia.strftime("%d/%m"), conta,
                           "".join(_html_tarefa(t) for t in p["tarefas"])))
        corpo += '<div class="rota"><h3>Próximos dias</h3>%s</div>\n' % "".join(dias)
    if s["fora"]:
        grupos = {}
        for t in s["fora"]:
            grupos.setdefault(_motivo_exibido(t["motivo"]), []).append(t)
        listas = "".join('<h3 class="t-grupo">%s · %d</h3><ol class="tarefas">%s</ol>'
                         % (_e(m), len(ts), "".join(_html_tarefa(t) for t in ts)) for m, ts in grupos.items())
        corpo += ('<details class="rota-sem fora"><summary><span class="rota-tit">Fora do sprint · %d</span>'
                  '</summary>%s</details>' % (len(s["fora"]), listas))
    return corpo


def _comparacao_meta(dif, quem="o plano"):
    return ("%s acima da meta" % _n(dif) if dif > 0 else
            "%s abaixo da meta: %s não cobre a meta" % (_n(-dif), quem) if dif < 0 else "exatamente a meta")


def _html_ritmo(r):
    alvo = r["alvo_marco"]
    atras = alvo is not None and (r["real_7d"] or 0) < alvo
    fig = []
    fig.append('<div class="fig%s"><p class="fig-n">%s</p><p class="fig-r">por dia nos '
               'últimos 7 dias</p>%s</div>' % (" abaixo" if atras else "", _n(r["real_7d"], 1),
                                            '<p class="fig-r"><b>abaixo do necessário</b></p>' if atras else ""))
    fig.append('<div class="fig"><p class="fig-n">%s</p><p class="fig-r">por dia nos '
               'últimos 14 dias</p></div>' % _n(r["real_14d"], 1))
    fig.append('<div class="fig alvo"><p class="fig-n">%s</p><p class="fig-r">por dia até a '
               'prova de 01/11 (faltam %s para %s)</p></div>'
               % (_n(alvo, 1), _n(r["faltam"]), _n(r["meta"])))
    fig.append('<div class="fig"><p class="fig-n">%s%%</p><p class="fig-r">de acerto em %s '
               'questões</p></div>' % (_n(r["acerto"], 1), _n(r["acumulado"])))
    nota = ""
    sp = r.get("sprint")
    if sp:
        # s226 (part-5): a cobertura do SPRINT -- o que tem dia ate o fim dele; o fora do sprint a parte
        sim = sp["simulados_q"] or 0
        partes = "%s questões nas listas" % _n(sp["q"] - sim) + (" e %s nos simulados" % _n(sim) if sim else "")
        nota = ('<p class="nota">O sprint até %s tem %s. Cumprindo o sprint, você chega a %s em %s (%s). '
                'Ficam fora do sprint %s em %s.</p>'
                % (_dm(sp["fim"]), partes, _n(sp["fechando_q"]), _dm(r["fim_fase1"]),
                   _comparacao_meta(sp["fechando_q"] - r["meta"], "o sprint"),
                   _plural(sp["q_fora"], "questão", "questões"), _plural(sp["fora"], "tarefa", "tarefas")))
    elif r["fechando_q"] is not None:
        sim = r["fase1_simulados_q"] or 0
        listas = (r["fase1_q"] or 0) - sim
        partes = "%s questões nas listas" % _n(listas) + (" e %s nos simulados" % _n(sim) if sim else "")
        nota = ('<p class="nota">O plano da Fase 1 tem %s em aberto. Fechando tudo, você chega a %s '
                'em %s (%s).</p>' % (partes, _n(r["fechando_q"]), _dm(r["fim_fase1"]),
                                     _comparacao_meta(r["fechando_q"] - r["meta"])))
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
/* Cor, tipo, espaco e raio: core/templates/tema.css (fonte unica, embutido logo depois deste bloco).
   Aqui so a estrutura do Painel (docs/UI.md): secoes com filete, numeros sem caixa, a proxima tarefa em
   destaque, atraso em ambar com texto (nunca so a cor). */
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{
  margin:0; background:var(--papel); color:var(--tinta);
  font-family:ui-sans-serif,system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  font-size:clamp(15px,.95rem + .2vw,17px); line-height:1.5; overflow-wrap:break-word;
}
.wrap{max-width:var(--wrap);margin:0 auto;padding:4px 2px 40px}
h2{font-size:var(--fs-secao);font-weight:700;line-height:1.25;margin:0 0 var(--esp-1);letter-spacing:-.01em;text-wrap:balance;color:var(--tinta)}
h3{font-size:var(--fs-legenda);font-weight:650;color:var(--tinta2);margin:0 0 var(--esp-1)}
p{margin:0}
a{color:var(--acento);text-underline-offset:2px}
.atualizado{color:var(--tinta3);font-size:var(--fs-meta);margin:0 0 var(--esp-2);text-align:right}
.bloco{padding:var(--esp-5) 0;border-top:1px solid var(--linha)}
.bloco:first-of-type{border-top:0;padding-top:var(--esp-1)}
.sub{color:var(--tinta2);font-size:var(--fs-legenda);margin:0 0 var(--esp-3)}
.nota{color:var(--tinta3);font-size:var(--fs-meta);margin-top:var(--esp-1)}
.tenue{color:var(--tinta3)}

/* Hoje: as duas doses do dia, o que o olho acha primeiro -- numero grande, barra fina, nota curta */
.dia h2{font-size:1.25rem;margin-bottom:var(--esp-4)}   /* abaixo do titulo da aba ("Painel"), acima das secoes */
.doses{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,15rem),1fr));gap:var(--esp-5) var(--esp-6)}
.dose{min-width:0}
.fracao{font-size:1rem;color:var(--tinta2)}
.fracao b{font-size:var(--fs-numero);line-height:1.1;color:var(--tinta);font-weight:700;letter-spacing:-.02em;margin-right:var(--esp-1)}
.barra{height:6px;background:var(--afundado);border-radius:var(--raio-pilula);margin:var(--esp-2) 0 var(--esp-1);overflow:hidden}
.barra i{display:block;height:100%;background:var(--acento);border-radius:inherit}
.ir{margin-top:var(--esp-2);font-weight:600}
.ir a{display:inline-flex;align-items:center;min-height:44px}
.agenda{margin-top:var(--esp-5)}
.ag-barras{list-style:none;margin:var(--esp-2) 0 0;padding:0;display:grid;grid-template-columns:repeat(7,minmax(0,4.5rem));
           gap:var(--esp-2);height:112px;align-items:end}
.ag-barras li{min-width:0;height:100%;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;gap:3px}
.ag-trilho{flex:1 1 auto;width:100%;display:flex;align-items:flex-end;justify-content:center}
/* previsao (dado, nao acao): roxo, a cor de detalhe visual do tema */
.ag-barras i{display:block;width:min(100%,28px);background:var(--roxo-fraco);border-top:2px solid var(--roxo);border-radius:var(--raio-p) var(--raio-p) 0 0}
.ag-n{font-size:var(--fs-meta);color:var(--tinta2)}
.ag-d{font-size:var(--fs-meta);color:var(--tinta3)}

/* Tarefas: o Hoje do sprint (ou, sem sprint, a semana do plano) */
.tarefas{list-style:none;margin:0;padding:0;display:grid;gap:0}
.tarefa{min-width:0;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:var(--esp-1) var(--esp-4);align-items:baseline;
        padding:var(--esp-3) 0;border-bottom:1px solid var(--linha)}
.t-tema{min-width:0;font-weight:600;line-height:1.35}
.t-meta{grid-column:1;min-width:0;color:var(--tinta3);font-size:var(--fs-meta);display:flex;flex-wrap:wrap;align-items:center;gap:var(--esp-1) var(--esp-3)}
.t-rot{color:var(--tinta2);font-weight:600;background:var(--afundado);padding:1px var(--esp-2);border-radius:var(--raio-pilula)}
.t-acao{grid-column:2;grid-row:1 / span 2;align-self:center;font-size:var(--fs-legenda);display:flex;flex-wrap:wrap;justify-content:flex-end;gap:0 var(--esp-4)}
.t-acao br{display:none}   /* as acoes ficam lado a lado (o <br> separa no texto puro) */
.t-acao a{display:inline-flex;align-items:center;min-height:44px;font-weight:600}
/* s226 (P21): com questoes no hub, tema + meta sao UM alvo (a linha abre a lista); a aula fica ao lado, pequena */
.t-alvo{grid-column:1 / -1;grid-row:1 / span 2;min-width:0;display:grid;gap:var(--esp-1);align-content:center;min-height:44px;
        position:relative;padding-right:var(--esp-6);color:inherit;text-decoration:none;-webkit-tap-highlight-color:transparent}
.t-alvo:not(:last-child){grid-column:1}
.t-alvo::after{content:"›";position:absolute;right:var(--esp-1);top:50%;transform:translateY(-50%);font-size:1.5em;line-height:1;color:var(--tinta3)}
.t-alvo:hover .t-tema{color:var(--acento-tinta)}
.t-alvo:hover::after{color:var(--acento)}
.t-alvo:focus-visible{outline:3px solid var(--acento);outline-offset:2px;border-radius:var(--raio-p)}
.t-sec{font-size:var(--fs-meta)}
.t-sec a{font-weight:500}
/* sem sprint, o atraso aparece UMA vez: no subtitulo do grupo das atrasadas (ambar + a palavra, nunca so cor) */
.t-grupo{margin:var(--esp-4) 0 0;font-size:var(--fs-legenda);font-weight:700;color:var(--tinta2)}
.t-grupo.atrasadas{color:var(--aviso)}
/* o proximo passo: a 1a tarefa da semana (a ordem e a do plano) -- so o rotulo "Proxima", o mesmo controle das outras */
.tarefa.proxima .t-tema::before{content:"Próxima";display:inline-block;margin-right:var(--esp-2);padding:0 var(--esp-2);border-radius:var(--raio-pilula);background:var(--acento-fraco);color:var(--acento-tinta);font-size:var(--fs-meta);font-weight:650;vertical-align:1px}
.prox{margin-top:var(--esp-3)}
.mais{margin-top:var(--esp-2)}
.mais summary{cursor:pointer;color:var(--acento);font-weight:600;padding:var(--esp-2) 0;min-height:44px}
.mais .tarefas{margin-top:var(--esp-1)}
/* A rota ate a prova (s213): cada semana futura recolhida; o resumo quebra linha, nunca alarga */
.rota{margin-top:var(--esp-5)}
.rota h3{margin-bottom:2px}
.rota-sem{border-top:1px solid var(--linha)}
.rota-sem:last-child{border-bottom:1px solid var(--linha)}
.rota-sem>summary{cursor:pointer;padding:var(--esp-3) 0;min-height:44px}
.rota-tit{font-weight:650}
.rota-n{color:var(--tinta3);font-size:var(--fs-meta);margin-left:var(--esp-1)}
.rota-sem .tarefas{margin:var(--esp-1) 0 var(--esp-3)}
/* s226 (sprint final): o que nao coube no plano, recolhido abaixo dos proximos dias, agrupado pelo motivo */
.rota-sem.fora{margin-top:var(--esp-5)}
.rota-sem.fora .t-grupo{margin-top:var(--esp-2)}

/* Ritmo: quatro numeros sem caixa; o necessario por dia e a referencia (ciano); abaixo dele = ambar + texto */
.figs{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,9.5rem),1fr));gap:var(--esp-4) var(--esp-5);margin-top:var(--esp-3)}
.fig{min-width:0}
.fig-n{font-size:1.5rem;font-weight:700;line-height:1.2;color:var(--tinta)}
.fig-r{font-size:var(--fs-meta);color:var(--tinta3)}
.fig.abaixo .fig-n,.fig.abaixo .fig-r b{color:var(--aviso)}
.fig.alvo .fig-n{color:var(--acento)}

/* Blocos */
table{width:100%;border-collapse:collapse;font-size:var(--fs-legenda);margin-top:var(--esp-2)}
th,td{text-align:left;padding:var(--esp-2);border-bottom:1px solid var(--linha)}
thead th{font-size:var(--fs-meta);color:var(--tinta3);font-weight:600}
tbody th{font-weight:650}
tr.sim th,tr.sim td{color:var(--tinta2)}

@media (max-width:520px){
  .tarefa{grid-template-columns:minmax(0,1fr)}
  .t-acao{grid-column:1;grid-row:auto;justify-content:flex-start}
  th,td{padding:6px 5px}
  table{font-size:var(--fs-meta)}
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


#: O tema escuro unico (s224): o MESMO `core/templates/tema.css` que o hub injeta no shell e no leitor.
_TEMA_FONTE = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
               '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
               '<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible+Next:'
               'wght@300;400;500;600;650;700&display=swap" rel="stylesheet">\n')


def _tema_css():
    return (ROOT / "core" / "templates" / "tema.css").read_text(encoding="utf-8")


def render_html(d):
    """Pagina autocontida. UM `.wrap`, tokens em `:root` (os MESMOS do hub), dark por
    `prefers-color-scheme` GUARDADO + `[data-theme]`, `body` com background explicito, 360px sem
    scroll horizontal. Nada de bastidor na tela: sem CLI, tabela ou fonte citada."""
    gerado = d["gerado_em"]
    fallback = "atualizado em %s, %s" % (_dm(gerado[:10]), gerado[11:16])
    corpo = "\n".join([
        _sec("dia", _html_dia(d["dia"], d["data"])),
        # s221 (pedido dele, 08/10): o Ritmo sobe para logo abaixo de "Hoje"
        _sec("ritmo", _html_ritmo(d["ritmo"])),
        # s226 (sprint-final-uerj part-3): com sprint, o bloco da semana vira Hoje / Proximos dias /
        # Fora do sprint (o `data-bloco` segue "semana": o hub e os testes o acham pelo nome antigo)
        _sec("semana", _html_sprint(d["sprint"], d["dia"]["cards"]) if d.get("sprint")
             else _html_semana(d["semana"])),
        _sec("blocos", _html_blocos(d["blocos"])),
    ] + ([_sec(BLOCO_DOCS, _html_docs(d[BLOCO_DOCS]))] if d.get(BLOCO_DOCS) else []))
    return ("<!DOCTYPE html>\n<html lang=\"pt-BR\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n"
            "<title>%s</title>\n%s<style>%s</style>\n<style id=\"medhub-tema\">%s</style>\n"
            "</head>\n<body>\n<div class=\"wrap\">\n"
            "<p class=\"atualizado\">%s<span data-gerado=\"%s\" data-gerado-iso=\"%s\" data-fallback=\"%s\">%s</span>%s</p>\n"
            "%s\n</div>\n%s</body>\n</html>\n"
            % (_e(TITULO), _TEMA_FONTE, CSS, _tema_css(), MARCA_GERADO_ABRE, _e(gerado), _e(gerado),
               _e(fallback), _e(fallback), MARCA_GERADO_FECHA, corpo, SCRIPT_ATUALIZADO))


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
                    help="imprime o dado estruturado dos blocos: os 4 fixos + Documentacao "
                         "(contrato testavel)")
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
