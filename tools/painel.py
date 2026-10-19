#!/usr/bin/env python3
"""Painel de progresso do MedHub -- pagina gerada do banco (part-7, s186; refeito na s194).

READ-ONLY ABSOLUTO. Nao abre `sqlite3` por conta propria (AGENTE.md secao 6: CLI nao faz SQL
direto) e nao aparece na allowlist de writers (F49). Todo numero sai de um leitor que JA existe e
que outra superficie tambem usa -- o painel nao tem regra propria de semana, de teto nem de ritmo:

    semana e listas   -> `plano.panorama` (o MESMO do `plano.py --panorama` do boot), sobre as linhas
                         com a contagem do banco do hub (`plano.linhas_com_q_hub`, P20 -- s219)
    meta do dia       -> `performance.volume_vs_marco` (a MESMA linha Meta do boot; s203); com sprint, a
                         TELA usa o `q_hoje` de `plano.agenda_sprint` e a `capacidade_q` (s226, contrato v1.7)
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
import re
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
#: s229 (pedido dele, 15/10: a RD aparecia "· assinado" E "ainda nao assinada" na mesma linha): a assinatura de
#: leitura `analises/pendencias/itens/doc_<slug>` (a MESMA que o hub le ao vivo no `painelAssinados`) tambem tira a
#: RD do "Hoje" -- o snapshot do `quadro/` pode estar velho; assinada OU absorvida = lida.
PEND_ESTADO = ROOT / "tmp" / "hub_db" / "analises" / "pendencias" / "itens"
STATUS_LIDO = ("assinado", "absorvida")

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
        cumpre = int(item["tarefa_id"]) if item.get("tarefa_id") is not None else None
        for tid in sorted(ids):
            saida.setdefault(tid, []).append({"slug": slug, "titulo": item.get("titulo") or slug,
                                              "cumpre": tid == cumpre})
    return saida


def _tarefa(t, aulas, no_hub):
    """Uma tarefa do panorama como o painel a desenha -- o MESMO construtor para a semana
    corrente e para a rota."""
    from app.utils import areas
    agregada = t.get("area") in areas.AREAS_AGREGADAS
    ligadas = aulas.get(t["id"]) or []
    # s229 (pedido dele, 15/10: a #5426 seguia "Revisao final por banca (LEITURA)..." com a aula "UERJ de Bolso"
    # no ar): a aula que CUMPRE a tarefa (`tarefa_id` no quadro) da o titulo -- o mesmo da Teoria e do leitor
    cumpre = next((a for a in ligadas if a.get("cumpre")), None)
    return {
        "id": t["id"], "semana": t["semana"], "atrasada": t["atrasada"],
        "tema": cumpre["titulo"] if cumpre else t["tema"], "q": t["q"], "classe": t["classe"],
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


def _lidos_por_pendencia(pasta=None):
    """{slug} com a assinatura de leitura `doc_<slug>` assinada ou absorvida no snapshot das pendencias
    (`PEND_ESTADO`). Pasta ausente ou arquivo ilegivel = nada (o quadro segue valendo)."""
    pasta = Path(pasta or PEND_ESTADO)
    lidos = set()
    if not pasta.is_dir():
        return lidos
    for arq in pasta.glob("doc_*.json"):
        try:
            doc = json.loads(arq.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(doc, dict) and doc.get("status") in STATUS_LIDO:
            lidos.add(str(doc.get("origem") or arq.stem[4:]))
    return lidos


def _aulas_lidas():
    """{slug} lidos: `feito` no estado do quadro OU a assinatura `doc_<slug>`; sem a pasta do estado, nada (o Painel
    nunca esconde no escuro)."""
    import hub
    if not Path(QUADRO_ESTADO).exists():
        return set()
    try:
        estado = hub.ler_estado_quadro(QUADRO_ESTADO)
    except (OSError, ValueError):
        return set()
    return {s for s, v in estado.items() if v.get("feito")} | _lidos_por_pendencia()


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
    lidos = _lidos_por_pendencia()
    arqs = {}
    for slug, item in reg.items():
        item = item or {}
        arq = ARTIFATOS / ("aula-%s.html" % slug)
        if (item.get("tipo") != "revisao" or not arq.is_file() or (estado.get(slug) or {}).get("feito")
                or slug in lidos):
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
    # s229 (rodada 4, pedido dele: "tarefa ASSINADA/concluida sai do Cronograma"): a tarefa cuja aula que a CUMPRE ja
    # foi lida (quadro `feito` ou `doc_<slug>` assinado) sai do Hoje e dos dias; ao vivo, o hub a esconde tambem
    lidas = _aulas_lidas()
    feita = lambda t: any(a.get("cumpre") and a["slug"] in lidas for a in aulas.get(t["id"]) or [])
    ag = dict(ag, hoje=[t for t in ag["hoje"] if not feita(t)],
              proximos=[dict(p, tarefas=[t for t in p["tarefas"] if not feita(t)]) for p in ag["proximos"]])
    ag["proximos"] = [p for p in ag["proximos"] if p["tarefas"]]
    return {
        "hoje": [tarefa(t) for t in ag["hoje"]], "q_hoje": ag["q_hoje"],
        "proximos": [{"data": p["data"], "q": p["q"], "tarefas": [tarefa(t) for t in p["tarefas"]]}
                     for p in ag["proximos"]],
        "fora": [dict(tarefa(t), motivo=t["motivo"]) for t in ag["fora"]],
        "rd": _rd_nao_assinada(),
    }


def _agenda_com_sessao(ag):
    """s229 (rodada 5, pedido dele: quantos cards de cada dia ENTRARAM por causa da ultima sessao): cada dia da
    agenda ganha `sessao` = os cards que vencem nele e cuja ultima revisao (`fsrs_cards.last_review`) e da ULTIMA
    sessao gravada -- o dia do `review_time` mais recente do `fsrs_revlog` (o `--record-lote` grava la). Os demais
    (`n - sessao`) ja estavam agendados antes dela. Mesmos filtros do `db.agenda_revisoes`; sem tabela nova.
    Falha de leitura = 0 em todo dia (a barra fica so rosa)."""
    datas = [x["data"] for x in ag.get("dias") or []]
    conta = dict.fromkeys(datas, 0)
    if datas:
        conn = db.get_connection()
        try:
            ultima = conn.execute("SELECT max(substr(review_time, 1, 10)) FROM fsrs_revlog").fetchone()[0]
            if ultima:
                linhas = conn.execute(
                    f"""SELECT substr(fc.due, 1, 10), count(*) FROM fsrs_cards fc JOIN flashcards f ON f.id = fc.card_id
                        WHERE {db.ativo_where('f.')}{db.retido_reforja_where(conn)}
                          AND fc.state > 0 AND substr(fc.last_review, 1, 10) = ?
                          AND substr(fc.due, 1, 10) BETWEEN ? AND ? GROUP BY 1""",
                    (ultima, datas[0], datas[-1])).fetchall()
                for dia, n in linhas:
                    if dia in conta:
                        conta[dia] = int(n)
        except Exception:  # noqa: BLE001 -- o bloco nunca derruba o Painel
            conta = dict.fromkeys(datas, 0)
        finally:
            conn.close()
    return dict(ag, dias=[dict(x, sessao=min(conta.get(x["data"], 0), x["n"])) for x in ag.get("dias") or []])


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
        "agenda": _agenda_com_sessao(db.agenda_revisoes(dias=7)),
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
    # s226 (painel-dashboard-sprint part-1): com sprint, o Ritmo compara o real com a capacidade do
    # sprint (`core/sprint.json`, lido pelo `plano.ler_sprint`); ilegivel = None (sem comparacao)
    capacidade = None
    if sp:
        import plano
        try:
            capacidade = int(plano.ler_sprint()["capacidade_q"])
        except Exception:  # noqa: BLE001 -- leitura de exibicao: sem config, o tile fica sem rotulo
            capacidade = None
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
                    "fim": sp["fim"], "fora": sp["fora"], "q_fora": sp["q_fora"],
                    "capacidade_q": capacidade} if sp else None),
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
    # s226 (sprint-final-uerj part-3): a agenda por dia; None = sem sprint (a pagina usa a semana)
    sprint = _bloco_sprint(linhas, hoje)
    dia = _bloco_dia(linhas, hoje)
    # s226 (painel-dashboard-sprint part-1): com sprint, o tile de Questoes conta contra o `q_hoje` do
    # sprint -- o MESMO do "Plano de hoje" e do boot (`plano.agenda_sprint`); None = o ritmo da meta
    dia["questoes"]["q_hoje"] = sprint["q_hoje"] if sprint else None
    return {
        "gerado_em": db.agora().isoformat(timespec="seconds"),
        "data": hoje.isoformat(),
        "titulo": TITULO,
        "dia": dia,
        "semana": _bloco_semana(linhas, hoje),
        "sprint": sprint,
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


def _botao_aula(slug, titulo, rotulo="Abrir aula", cumpre=False):
    """s229 (pedido dele, 15/10: "trocar o link 'abrir aula' por um BOTAO tematico que leva a aba Teoria ja naquela
    aula"): o MESMO botao no Painel e na Teoria (`.t-btn` aqui, `.hub-btn` no hub) -- o atalho `data-hub-aula` que o
    hub ja trata abre o leitor da Teoria direto. Secundario (contorno ciano); o primario da linha e o "Resolver"."""
    return ('<a class="t-btn" href="aulas/%s.html" data-hub-aula="%s" data-titulo="%s"%s>%s</a>'
            % (_e(slug), _e(slug), _e(titulo or slug), ' data-cumpre="1"' if cumpre else "", _e(rotulo)))


def _botao_resolver(t):
    """s229 (pedido dele, 15/10: a seta ">" que levava as Listas vira um botao): "Resolver" abre a aba Listas JA na
    lista da tarefa (`data-hub-tarefa`; o hub procura a lista pelo `tarefa`), no modo da area (`_modo_hub`). Primario
    (ciano cheio): a acao da linha."""
    return ('<a class="t-btn t-btn-prim" href="#questoes" data-hub-aba="questoes" data-hub-modo="%s" '
            'data-hub-tarefa="%s">Resolver</a>' % (_modo_hub(t), _e(t.get("id"))))


def _acao(t):
    """Os BOTOES da tarefa (s229): "Resolver" (com questoes no banco do hub), a lista externa ou a prova em PDF e
    cada aula ligada ("Abrir aula"; com 2+, o titulo de cada uma).

    s213 (D4-1, decisao do operador em 25/09: "nao sair do medhub"): tarefa com questoes no banco do hub (`no_hub`)
    abre a aba Listas e o link do EMED some; so fora do banco o "Abrir lista" externo aparece. ⚰️ *s226 (part-3,
    P21): a LINHA INTEIRA era o alvo das Listas, com a seta ">" no fim; s229 (pedido dele) virou o botao.* P20
    (s219): a tarefa sem acao diz a classe na META, apagada (`plano.meta_da_tarefa`, a regra da Teoria)."""
    partes = []
    if t.get("no_hub"):
        partes.append(_botao_resolver(t))
    elif t["url_lista"] and str(t["url_lista"]).startswith(("http://", "https://")):
        partes.append('<a class="t-btn t-btn-prim" href="%s" rel="noopener noreferrer">Abrir lista</a>'
                      % _e(t["url_lista"]))
    elif t["url_lista"]:
        partes.append('<span class="tenue">prova em PDF no computador</span>')
    # aula que CUMPRE (tarefa de aula) ou PREPARA (lista) -- o que a aba Aulas ja mostrava
    aulas = t.get("aulas") or ([{"slug": t["aula"], "titulo": None}] if t.get("aula") else [])
    varias = len(aulas) > 1
    for a in aulas:
        partes.append(_botao_aula(a["slug"], a.get("titulo"), (a.get("titulo") or a["slug"]) if varias else "Abrir aula",
                                  bool(a.get("cumpre"))))
    return "".join(partes)


#: Os quatro aneis do topo (s227, tema v4 part-5): um anel por meta, num viewBox de 120 com traco de 10
#: e raio 52 (3 de folga ate a borda); o centro leva o %.
ANEL_R = 52


def _razao(parte, todo):
    """O % de `parte` sobre `todo`, SEM teto (o feito acima da meta diz 112%); None = sem referencia."""
    if not todo:
        return None
    return max(0.0, 100.0 * float(parte or 0) / float(todo))


def _pct_anel(pct):
    """O % inteiro que o anel desenha e escreve: para baixo (99,6 nao fecha o anel nem diz 100%); 0 < % < 1
    vira 1 (o feito nao some); None = sem referencia."""
    if pct is None:
        return None
    return 0 if pct <= 0 else max(1, int(math.floor(pct)))


def _arco(classe, p, dica):
    """Um arco sobre o trilho. `pathLength="100"`: o traco E o % (ate 100). 0% = nenhum arco, sem o ponto
    solto que o `linecap` redondo desenharia num traco de comprimento 0. A dica (`<title>`) e o hover."""
    if not p:
        return ""
    return ('<circle class="an-arco %s" cx="60" cy="60" r="%d" pathLength="100" stroke-dasharray="%d 100" '
            'transform="rotate(-90 60 60)"><title>%s</title></circle>' % (classe, ANEL_R, min(100, p), _e(dica)))


def _texto(trecho):
    """O texto visivel de um trecho de HTML (para o `aria-label` e a dica dizerem o MESMO da legenda)."""
    return html.unescape(re.sub(r"<[^>]+>", "", trecho))


def _item_anel(nome, cor, pct, valor, dica, alt=None, sp=None, attrs=""):
    """Um anel do topo: o SVG (trilho, o 2o arco quando ha, o arco e o % no centro) e, ABAIXO, o rotulo e
    UMA linha de valor -- nada mais. `pct` None = sem referencia: so o trilho e "--" no centro. `sp` =
    (pct, dica) do 2o arco, mais claro e POR BAIXO do arco do feito (o Ate 01/11). O que nao cabe no valor
    (o estado, o 2o arco) vai no `aria-label` e na dica (`<title>`) do arco, nunca numa legenda.
    ⚰️ *Ate 13/10 (part-5) havia, sob o valor, as linhas curtas `kpi-r` (faltam, vencidos/novos/retencao,
    "abaixo de 80/dia", 14 dias e acerto, "cumprindo o sprint: N · fora: Q q") e o link "Ir para os cards".
    Sairam a pedido dele (13/10: "gostaria de remover esse 'Ir para os cards', bem como as legendas do
    dashboard").*"""
    p = _pct_anel(pct)
    centro = ('%d<tspan class="an-pc" dx="1">%%</tspan>' % p) if p is not None else "--"
    arcos = (_arco("an-sp", _pct_anel(sp[0]), sp[1]) if sp else "") + _arco(cor, p, dica)
    alt = alt or "%s: %s%s." % (nome, _texto(valor), "" if p is None else " (%d%%)" % p)
    svg = ('<svg class="anel" viewBox="0 0 120 120" role="img" aria-label="%s">'
           '<circle class="an-trilho" cx="60" cy="60" r="%d"/>%s'
           '<text class="an-pct" x="60" y="71" text-anchor="middle">%s</text></svg>'
           % (_e(alt), ANEL_R, arcos, centro))
    return ('<div class="an4"%s>%s<h3>%s</h3><p class="an-val">%s</p></div>\n'
            % (attrs, svg, _e(nome), valor))


def _anel_questoes(q):
    """Questoes: feitas contra o alvo do dia ("X de 76"). Com sprint (`q_hoje` nao-None), o `q_hoje` (o MESMO
    do "Plano de hoje" e do boot); sem sprint, o ritmo da meta (s203). A meta 10.000 nao aparece aqui: ela e
    o valor do anel Ate 01/11. Sem alvo, "X feitas" e o motivo no `aria-label`.
    ⚰️ *Ate 13/10 (part-5) levava a linha "faltam N" / "dose do dia cumprida" sob o valor (pedido dele de
    13/10: sem legendas).*"""
    # s216 (part-6, P08 v0): o numero publicado leva a ancora do "Hoje ao vivo" -- a pagina soma "+K"
    # AO LADO (o que ela gravou depois do publish), nunca o substitui
    b_q = '<b data-vivo="questoes" data-base="%s">%s</b>' % (_e(q["feitas_hoje"]), _n(q["feitas_hoje"]))
    feitas = q["feitas_hoje"] or 0
    q_hoje = q.get("q_hoje")
    motivo = None
    if q_hoje is not None:
        if q_hoje:
            valor, pct = '%s de %s' % (b_q, _n(q_hoje)), _razao(feitas, q_hoje)
        else:
            valor, pct, motivo = '%s feitas' % b_q, None, "nenhuma lista no plano de hoje"
    elif q["alvo_dia"] is not None:
        alvo = math.ceil(q["alvo_dia"])
        valor, pct = '%s de ~%s' % (b_q, _n(alvo)), _razao(feitas, alvo)
    elif q["faltam"] == 0:
        valor, pct, motivo = '%s feitas' % b_q, 100.0, "meta atingida"
    else:
        valor, pct, motivo = '%s feitas' % b_q, None, "a data da meta passou"
    alt = "Questões: %s; %s." % (_texto(valor), motivo) if motivo else None
    return _item_anel("Questões", "an-q", pct, valor, "Questões: %s" % _texto(valor), alt=alt)


def _anel_cards(c):
    """Cards: consumidos contra o teto do dia (P09), "X de 150". Sem contador, "-- de 150" e o motivo no
    `aria-label`. ⚰️ *Ate 13/10 (part-5) levava vencidos, novos, a retencao de 7 dias e o atalho "Ir para os
    cards" (pedido dele de 13/10: sem legendas e sem o atalho; a aba Cards segue no menu do hub).*"""
    if c["consumo_hoje"] is None:
        valor, pct = '<b>--</b> de %s' % _n(c["teto"]), None
        alt = "Cards: não consegui contar as revisões de hoje."
    else:
        valor = '<b data-vivo="cards" data-base="%s">%s</b> de %s' % (
            _e(c["consumo_hoje"]), _n(c["consumo_hoje"]), _n(c["teto"]))
        pct, alt = _razao(c["consumo_hoje"], c["teto"]), None
    return _item_anel("Cards", "an-c", pct, valor, "Cards: %s" % _texto(valor), alt=alt)


def _html_ritmo(r):
    """Ritmo: o real de 7 dias contra UMA referencia -- com sprint, a capacidade dele (`capacidade_q`, o UNICO
    por-dia da tela); sem sprint, o necessario por dia da meta (s203). O valor diz a comparacao ("35,4 de 80
    por dia"): o estado nunca fica so na cor do arco (abaixo = ambar, em dia = verde; sem estado, ciano), e o
    `aria-label` e a dica do arco dizem "abaixo de 80/dia" / "em dia". Sem referencia (sprint sem config), o
    anel fica no trilho e o valor e "35,4 por dia". O `data-bloco="ritmo"` mora aqui: o anel herdou o conteudo
    da placa Ritmo.
    s227 (tema v4 part-5, pedido dele: "Esses 4 blocos deveriam aparecer junto no topo, através desses anéis
    com percentual"). ⚰️ *Ate 13/10 era a placa "Ritmo de questões": a barra `.rb` contra a marca dos 80/dia
    e os tres numeros.* ⚰️ *Ate 13/10 (part-5) o anel levava, sob o valor, as linhas "abaixo de 80/dia" / "em
    dia" e "23,5 em 14 dias · 78,4% de acerto" -- sairam com as legendas (pedido dele, 13/10).*"""
    sp = r.get("sprint")
    real = float(r.get("real_7d") or 0)
    alvo = sp.get("capacidade_q") if sp else r.get("alvo_marco")
    cor, dica = "an-q", "%s por dia nos últimos 7 dias" % _n(real, 1)
    valor = "<b>%s</b> por dia" % _n(real, 1)
    if alvo:
        abaixo = real < alvo
        if sp:
            marca = "%s/dia" % _n(alvo)
            cor = "an-abaixo" if abaixo else "an-emdia"
            dica += ", %s %s" % ("abaixo de" if abaixo else "em dia com", marca)
            valor = "<b>%s</b> de %s por dia" % (_n(real, 1), _n(alvo))
        else:
            cor = "an-abaixo" if abaixo else cor
            dica += ", %s necessário até a prova: %s/dia" % ("abaixo do" if abaixo else "em dia com o", _n(alvo, 1))
            valor = "<b>%s</b> de %s por dia" % (_n(real, 1), _n(alvo, 1))
    return _item_anel("Ritmo em 7 dias", cor, _razao(real, alvo), valor, dica, alt="Ritmo: %s." % dica,
                      attrs=' data-bloco="ritmo"')


def _html_ate(r, data_meta):
    """Ate 01/11: o acumulado contra a meta (`--roxo`), "7.817 de 10.000", com um 2o arco MAIS CLARO no mesmo
    anel ate onde o acumulado chega cumprindo o sprint (`fechando_q`): a dica dele e o `aria-label` dizem o N
    e o fora do sprint. A meta 10.000 aparece aqui, UMA vez, no valor. Sem sprint, so o feito (o que falta vai
    no `aria-label`; o por-dia mora no Ritmo).
    ⚰️ *Ate 13/10 era a placa "Até 01/11" com a barra de projecao (`.proj-barra`: feito | cumprindo o sprint
    | fora do sprint).* ⚰️ *Ate 13/10 (part-5) o anel levava, sob o valor, a linha "cumprindo o sprint: N ·
    fora: Q q" (sem sprint, "faltam N em D dias") -- saiu com as legendas (pedido dele, 13/10).*"""
    sp = r.get("sprint")
    feito, meta = int(r.get("acumulado") or 0), int(r.get("meta") or 0)
    quando = _dm(data_meta) if data_meta else "a prova"
    pct = _razao(feito, meta)
    p = _pct_anel(pct)
    valor = "<b>%s</b> de %s" % (_n(feito), _n(meta))
    alt = "Até %s: %s de %s%s" % (quando, _n(feito), _n(meta), "" if p is None else " (%d%%)" % p)
    if sp:
        fecha = int(sp.get("fechando_q") or 0)
        segundo = (_razao(fecha, meta), "cumprindo o sprint até %s: %s" % (_dm(sp.get("fim")), _n(fecha)))
        alt += "; cumprindo o sprint, %s; fora do sprint, %s questões." % (_n(fecha), _n(sp.get("q_fora")))
    else:
        falta = max(0, meta - feito)
        nota = ("faltam %s em %s dias" % (_n(falta), _n(r.get("dias_marco"))) if falta and r.get("dias_marco")
                else "faltam %s" % _n(falta) if falta else "meta atingida")
        segundo = None
        alt += "; %s." % nota
    return _item_anel("Até %s" % quando, "an-meta", pct, valor, "feito: %s" % _n(feito), alt=alt, sp=segundo)


def _html_dia(d, data_iso, r=None):
    """O topo do Painel, UMA placa: "Hoje, <dia>" e os QUATRO aneis lado a lado -- Questoes, Cards, Ritmo e
    Ate 01/11 --, cada um com o % no centro e, abaixo, o rotulo e UMA linha de valor (s227, tema v4 part-5:
    pedido dele, "o 'Painel' ainda está muito disperso. Esses 4 blocos deveriam aparecer junto no topo,
    através desses anéis com percentual"; sem legendas desde o pedido de 13/10). Cada anel contra a PROPRIA
    meta: nenhum numero soma unidades (o "226" dos mockups). Sem `r` (o ritmo), so os dois do dia (Questoes e
    Cards).

    Hoje ao vivo: as ancoras `b[data-vivo]` ficam nos VALORES de Questoes e Cards (o hub poe o "+K" ao lado
    delas); o anel fica no valor PUBLICADO -- o hub so le a ancora, nao redesenha o SVG.
    ⚰️ *Ate 13/10 (part-2) eram dois aneis concentricos (questoes por fora, cards por dentro, o dia no
    centro), com as placas Ritmo e Ate 01/11 separadas abaixo.*"""
    hoje = date.fromisoformat(data_iso)
    itens = [_anel_questoes(d["questoes"]), _anel_cards(d["cards"])]
    if r is not None:
        itens += [_html_ritmo(r), _html_ate(r, d["questoes"].get("data_meta"))]
    return ('<div class="placa dash-hoje">\n<h2>Hoje, %s %s</h2>\n'
            '<div class="aneis4" data-sessao-gravada="%s">\n%s</div>\n</div>\n'
            % (DIAS_EXTENSO[hoje.weekday()], hoje.strftime("%d/%m"), _e(d.get("sessao_gravada") or ""),
               "".join(itens)))


def _html_agenda(ag):
    """Flashcards da semana: as revisoes previstas nos proximos 7 dias (`db.agenda_revisoes`), um dia por
    barra, com a dica ao passar o mouse. s227 (part-5, pedido dele): ⚰️ *era "Revisões nos próximos 7 dias".*
    s228 (pedido dele: "melhorar a estetica do bloco [...] com liberdade para rever a paleta"): paleta propria
    (`--fc*`, a familia rosa do anel de Cards), o total da semana no cabecalho e o PICO em barra cheia com o
    numero em destaque (rotulo "pico" na dica: nunca so a cor); os outros dias em lavagem."""
    maior = max([x["n"] for x in ag["dias"]] + [0])
    total = sum(x["n"] for x in ag["dias"])
    pico = next((x["data"] for x in ag["dias"] if maior and x["n"] == maior), None)

    def barra(x):
        e_pico = x["data"] == pico
        k = int(x.get("sessao") or 0)
        dica = "%s: %s%s%s" % (_dia_curto(x["data"]), _plural(x["n"], "card", "cards").replace("&nbsp;", " "),
                               ", %d da última sessão" % k if k else "", " (pico da semana)" if e_pico else "")
        # s229 (rodada 5): barra EMPILHADA -- em cima, em ciano, os que entraram pela ultima sessao; embaixo, na
        # paleta rosa, os que ja estavam agendados; o total em cima e o "+k" pequeno em ciano
        seg = ('<b class="ag-sessao" style="height:%.0f%%"></b>' % (100.0 * k / x["n"])) if k and x["n"] else ""
        mais = '<small class="ag-mais">+%d</small>' % k if k else ""
        return ('<li title="%s"%s><span class="ag-n">%d%s</span><span class="ag-trilho"><i style="height:%.0f%%">%s</i></span>'
                '<span class="ag-d">%s</span></li>'
                % (_e(dica), ' class="pico"' if e_pico else "", x["n"], mais, max(4.0, 100.0 * x["n"] / max(maior, 1)),
                   seg, DIAS_SEMANA[date.fromisoformat(x["data"]).weekday()]))
    return ('<div class="placa dash-sec agenda"><div class="ag-cab"><h3>Flashcards da semana</h3>'
            '<p class="ag-total"><b>%s</b> em 7 dias</p></div>'
            '<ol class="ag-barras" aria-label="Flashcards previstos por dia">%s</ol></div>'
            % (_n(total), "".join(barra(x) for x in ag["dias"])))


def _html_tarefa(t, proxima=False):
    """Um `<li class="tarefa">` -- s229 (pedido dele, 15/10: "estetica dos bloquinhos das tarefas melhorada (cartoes
    por tarefa, chip de area, contagem)"): um CARTAO por tarefa -- no topo o chip da area e a contagem (a meta de
    `plano.meta_da_tarefa`), depois o tema e, no pe, os botoes (`_acao`). O MESMO no Roadmap e na semana antiga.
    s216 (hub-integracao part-2): carrega `data-tarefa` (o id do plano) -- e por ele que o hub pinta, sem publish, a
    lista resolvida na aba Listas. P20 (s219): o titulo pela correcao de exibicao (`plano.tema_exibido`). `proxima` =
    a 1a tarefa do dia: so o rotulo "Proxima". ⚰️ *s226 (P21): a linha inteira era o alvo das Listas (`a.t-alvo`
    com a seta ">")*."""
    import plano
    meta = ['<span class="t-rot">%s</span>' % _e(t["rotulo"] or "?")]
    meta += ['<span class="t-n">%s</span>' % _e(x)
             for x in plano.meta_da_tarefa(t["q"], t["classe"], plano.tem_acao(t))]
    classes = "tarefa" + (" atrasada" if t["atrasada"] else "") + (" proxima" if proxima else "")
    acao = _acao(t)
    # s229 (rodada 3): a faixa colorida da area a esquerda da barra (`data-area`; a cor e o fundo tingido no CSS)
    return ('<li class="%s" data-tarefa="%s"><i class="t-faixa" data-area="%s" aria-hidden="true"></i>'
            '<p class="t-meta">%s</p><p class="t-tema">%s</p>%s</li>'
            % (classes, _e(t["id"]), _e(t["rotulo"] or ""), "".join(meta), _e(plano.tema_exibido(t["tema"]) or "(sem tema)"),
               '<p class="t-acao">%s</p>' % acao if acao else ""))


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
    """A RD nao assinada mais antiga, no cartao das tarefas: o chip "RD", o estado e o botao "Abrir aula" (o atalho
    `data-hub-aula`). s229 (pedido dele, 15/10: a linha dizia "· assinado" E "ainda nao assinada"): o estado mora
    num span SO (`t-rd-st`) que o hub reescreve ao vivo pela MESMA fonte do "assinado" (`quadro/<slug>` e
    `doc_<slug>`); nunca um segundo rotulo ao lado."""
    return ('<li class="tarefa rd"><i class="t-faixa" data-area="RD" aria-hidden="true"></i>'
            '<p class="t-meta"><span class="t-rot">RD</span>'
            '<span class="t-rd-st">revisão direcionada ainda não assinada</span></p><p class="t-tema">%s</p>'
            '<p class="t-acao">%s</p></li>' % (_e(rd["titulo"]), _botao_aula(rd["slug"], rd["titulo"])))


def _html_dia_roadmap(titulo, conta, itens, classe=""):
    """Um dia do Roadmap: o titulo (dia e data), a contagem e os cartoes; SEMPRE aberto (s229)."""
    return ('<section class="rm-dia%s"><h3 class="rm-tit"><span class="rm-d">%s</span>%s</h3>%s</section>'
            % ((" " + classe) if classe else "", titulo, ' <span class="rm-n">%s</span>' % conta if conta else "",
               '<ol class="tarefas">%s</ol>' % itens if itens else '<p class="nota">Nenhuma tarefa do plano.</p>'))


def _html_sprint(s, cards, hoje_iso=None):
    """O ROADMAP (s229, pedido dele em 15/10: "'Plano de hoje' + 'Proximos dias' vira 'Roadmap': todos os dias
    expandidos"): Hoje (as tarefas do dia e a RD nao assinada mais antiga) e cada dia seguinte, um por bloco, todos
    abertos, com os cartoes das tarefas; Fora do sprint segue recolhido, pelo motivo. O subtitulo diz o dia de
    hoje: tarefas, questoes e cards (o que falta da dose; sem contador, o teto).
    ⚰️ *s226 (part-3): "Plano de hoje" e "Proximos dias" com cada dia recolhido num `<details>`.*"""
    hoje = s["hoje"]
    primeira = hoje[0]["id"] if hoje else None
    if hoje:
        resumo = "Hoje: %s · %s" % (_plural(len(hoje), "tarefa", "tarefas"),
                                    _plural(s["q_hoje"], "questão", "questões"))
    else:
        resumo = "Nenhuma tarefa do plano para hoje"
    n_cards = cards.get("restantes") if cards.get("consumo_hoje") is not None else cards.get("teto")
    if n_cards:
        resumo += " + %s" % _plural(n_cards, "card", "cards")
    itens = "".join(_html_tarefa(t, proxima=t["id"] == primeira) for t in hoje)
    if s.get("rd"):
        itens += _html_rd(s["rd"])
    tit_hoje = "Hoje" + (" · %s" % _dia_curto(hoje_iso) if hoje_iso else "")
    conta_hoje = _conta_do_dia(hoje) + (" · %s&nbsp;q" % _n(s["q_hoje"]) if hoje and s["q_hoje"] else "")
    corpo = '<h2>Cronograma</h2>\n<p class="sub">%s.</p>\n' % resumo
    corpo += _html_dia_roadmap(tit_hoje, conta_hoje, itens, "hoje")
    for p in s["proximos"]:
        conta = _conta_do_dia(p["tarefas"]) + (" · %s&nbsp;q" % _n(p["q"]) if p["q"] else "")
        corpo += _html_dia_roadmap(_dia_curto(p["data"]), conta, "".join(_html_tarefa(t) for t in p["tarefas"]))
    if s["fora"]:
        grupos = {}
        for t in s["fora"]:
            grupos.setdefault(_motivo_exibido(t["motivo"]), []).append(t)
        listas = "".join('<h3 class="t-grupo">%s · %d</h3><ol class="tarefas">%s</ol>'
                         % (_e(m), len(ts), "".join(_html_tarefa(t) for t in ts)) for m, ts in grupos.items())
        corpo += ('<details class="rota-sem fora"><summary><span class="rota-tit">Fora do sprint · %d</span>'
                  '</summary>%s</details>' % (len(s["fora"]), listas))
    return corpo


def _html_blocos(b):
    """Por bloco: uma linha por bloco com a barra de acerto (0-100%) e as tarefas feitas/total; o bloco
    de MENOR acerto leva o rotulo "mais fraco" (nunca so a cor); Simulados na ultima linha (termometro,
    nao bloco: fora da disputa do mais fraco). ⚰️ *Ate 13/10 era uma `<table>` com 4 colunas.*"""
    com_acerto = [(v["acerto"], nome) for nome, v in b["blocos"].items() if v.get("acerto") is not None]
    fraco = min(com_acerto)[1] if com_acerto else None

    def linha(nome, v, classe=""):
        ac = v.get("acerto")
        dica = "%s: %s de acerto em %s questões · %d de %d tarefas feitas" % (
            nome, (_n(ac, 1) + "%") if ac is not None else "sem questões", _n(v.get("q_feitas")),
            v["feitas"], v["tarefas"])
        tag = '<span class="bl-tag">mais fraco</span>' if classe == "fraco" else ""
        return ('<li class="bl%s" title="%s"><span class="bl-nome">%s%s</span>'
                '<span class="bl-barra" aria-hidden="true"><i style="width:%.1f%%"></i></span>'
                '<span class="bl-pct">%s</span><span class="bl-t">%d/%d</span></li>'
                % ((" " + classe) if classe else "", _e(dica), _e(nome), tag, ac or 0.0,
                   (_n(ac, 1) + "%") if ac is not None else "--", v["feitas"], v["tarefas"]))
    linhas = [linha(nome, v, "fraco" if nome == fraco else "") for nome, v in b["blocos"].items()]
    linhas.append(linha("Simulados", b["simulados"], "sim"))
    # s226 (pedido dele, 13/10): a nota 'Fora da tabela' saiu (legenda) e nao volta
    return ('<div class="placa dash-sec" data-bloco="blocos"><h3>Por bloco</h3>'
            '<p class="bl bl-cab" aria-hidden="true"><span></span><span></span><span>acerto</span>'
            '<span>tarefas</span></p>'
            '<ol class="bls" aria-label="Acerto e tarefas feitas por bloco">%s</ol></div>\n' % "".join(linhas))


def _html_dash(d):
    """O dashboard do topo (s226, painel-dashboard-sprint part-1), numa secao so (`data-bloco="dia"`; o anel
    do Ritmo e o Por bloco mantem o `data-bloco` deles por dentro). Nenhuma legenda em prosa (`p.nota`).
    s227 (tema v4 part-5): TRES placas na grade -- o Hoje com os quatro aneis (inteiro), depois Por bloco |
    Flashcards da semana (lado a lado a partir de 760 px, mesma altura; empilhados no celular).
    ⚰️ *Ate 13/10 (part-2) eram cinco placas: Hoje | Ritmo, Ate 01/11 inteira, Por bloco | Revisoes.*"""
    return "".join([_html_dia(d["dia"], d["data"], d["ritmo"]), _html_blocos(d["blocos"]),
                    _html_agenda(d["dia"]["agenda"])])


def _sec(chave, corpo, extra=""):
    return ('<section class="bloco %s" data-bloco="%s">\n%s\n</section>'
            % (_e(extra or chave), _e(chave), corpo))


CSS = """
/* Cor, tipo, espaco e raio: core/templates/tema.css (fonte unica, embutido logo depois deste bloco).
   Aqui so a estrutura do Painel (DESIGN.md): uma placa por secao (a .placa do tema, composta, nunca
   redefinida), as do topo em grade; dentro da placa, linhas com filete e numeros sem caixa; a proxima
   tarefa em destaque, atraso em ambar com texto (nunca so a cor). */
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{
  margin:0; background:var(--papel); color:var(--tinta);
  font-family:ui-sans-serif,system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  font-size:clamp(15px,.95rem + .2vw,17px); line-height:1.5; overflow-wrap:break-word;
}
.wrap{max-width:var(--largura);margin:0 auto;padding:4px 2px 40px}
h2{font-size:var(--fs-secao);font-weight:700;line-height:1.25;margin:0 0 var(--esp-1);letter-spacing:-.01em;text-wrap:balance;color:var(--tinta)}
h3{font-size:var(--fs-legenda);font-weight:650;color:var(--tinta2);margin:0 0 var(--esp-1)}
p{margin:0}
a{color:var(--acento);text-underline-offset:2px}
.atualizado{color:var(--tinta3);font-size:var(--fs-meta);margin:0 0 var(--esp-2);text-align:right}
/* secoes: o dashboard (a grade das placas do topo), depois o Roadmap (s229), uma placa
   cada; entre elas o MESMO vao da grade (as bordas alinham), nunca filete */
.bloco{margin:0}
.bloco + .bloco{margin-top:var(--esp-4)}
/* o titulo da placa (o 1o filho): o mesmo em todas -- o Hoje se distingue pelos aneis, nao pelo titulo */
.placa > h2:first-child,.placa > h3:first-child{font-size:var(--fs-item);font-weight:650;line-height:1.3;color:var(--tinta);margin:0 0 var(--esp-3)}
.placa > h2:first-child + .sub{margin-top:calc(-1 * var(--esp-2))}
.sub{color:var(--tinta2);font-size:var(--fs-legenda);margin:0 0 var(--esp-3)}
.nota{color:var(--tinta3);font-size:var(--fs-meta);margin-top:var(--esp-1)}
.tenue{color:var(--tinta3)}

/* Dashboard do topo (s226; s227 em placas; s227 part-5 compacto): o Hoje com os QUATRO aneis, depois Por
   bloco e Flashcards da semana. Uma coluna no celular; com o iframe a partir de 760 px, o Hoje inteiro e as
   duas placas de grafico lado a lado, da mesma altura (a linha da grade estica as duas). Mesma grade e
   mesmo vao: as bordas alinham. A ousadia mora so nos aneis; o resto quieto. Sem caixa por numero e sem
   legenda em prosa. */
.dash{display:grid;grid-template-columns:minmax(0,1fr);gap:var(--esp-4)}
/* Hoje: Questoes · Cards · Ritmo · Ate 01/11, cada anel contra a propria meta (nada soma unidades). 2 x 2
   no celular, 4 em linha quando cabem. Todos do mesmo tamanho e no mesmo alinhamento: o anel, o rotulo e o
   valor na mesma altura em toda a linha. O % grande no centro; sob o anel so o rotulo e o valor (s227:
   sem legendas, pedido dele de 13/10) */
.aneis4{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:var(--esp-5) var(--esp-4)}
.an4{min-width:0;display:flex;flex-direction:column;align-items:center;text-align:center}
.anel{display:block;width:min(100%,7.5rem);height:auto;margin:0 0 var(--esp-2)}
.anel circle{fill:none;stroke-width:10}
.an-trilho{stroke:var(--trilho)}
.an-arco{stroke-linecap:round}
.an-arco.an-q{stroke:var(--acento)}
.an-arco.an-c{stroke:var(--rosa)}
.an-arco.an-abaixo{stroke:var(--aviso)}
.an-arco.an-emdia{stroke:var(--ok)}
.an-arco.an-meta{stroke:var(--roxo)}
/* o 2o arco do Ate 01/11 (cumprindo o sprint): o mesmo roxo, mais claro, POR BAIXO do feito */
.an-arco.an-sp{stroke:var(--roxo);stroke-opacity:.5}
.an-pct{font-size:30px;font-weight:700;fill:var(--tinta);letter-spacing:-.02em;font-variant-numeric:proportional-nums}
.an-pc{font-size:15px;font-weight:600;fill:var(--tinta2)}
.an4 h3{margin:0;font-size:var(--fs-legenda);font-weight:650;color:var(--tinta2)}
.an-val{margin-top:2px;font-size:var(--fs-legenda);color:var(--tinta2)}
.an-val b{font-size:var(--fs-secao);font-weight:700;color:var(--tinta)}
/* Por bloco: nome | barra de acerto (0-100%) | % | feitas/total; o mais fraco em ambar + o rotulo */
.bls{list-style:none;margin:0;padding:0}
.bl{display:grid;grid-template-columns:4.75rem minmax(0,1fr) 3.25rem 4rem;gap:var(--esp-2);align-items:center;
    padding:var(--esp-2) 0;border-bottom:1px solid var(--linha);font-size:var(--fs-legenda)}
.bl>span{min-width:0}
.bl-cab{padding:0;border:0;color:var(--tinta3);font-size:var(--fs-meta)}
.bl-nome{font-weight:650;color:var(--tinta)}
.bl-tag{display:block;font-size:var(--fs-meta);font-weight:600;color:var(--aviso)}
.bl-barra{display:block;height:6px;background:var(--trilho);border-radius:var(--raio-pilula);overflow:hidden}
.bl-barra i{display:block;height:100%;background:var(--acento);border-radius:inherit}
.bl-pct,.bl-t,.bl-cab span:nth-child(n+3){text-align:right;font-variant-numeric:tabular-nums}
.bl-pct{font-weight:650;color:var(--tinta)}
.bl-t{color:var(--tinta3);font-size:var(--fs-meta)}
.bl.fraco .bl-barra i{background:var(--aviso)}
.bl.fraco .bl-pct{color:var(--aviso)}
.bl.sim .bl-nome{color:var(--tinta2);font-weight:500}
.bl.sim .bl-barra i{background:var(--roxo)}   /* s228 (pedido dele): o roxo do anel Ate 01/11 (questoes) */
/* Flashcards da semana: as barras ocupam a placa (na grade, a altura da linha vem do Por bloco ao lado) */
.agenda{display:flex;flex-direction:column}
.ag-barras{list-style:none;margin:var(--esp-2) 0 0;padding:0;display:grid;grid-template-columns:repeat(7,minmax(0,1fr));
           gap:var(--esp-2);flex:1 1 auto;min-height:112px;align-items:stretch}
.ag-barras li{min-width:0;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;gap:3px}
.ag-trilho{flex:1 1 auto;width:100%;display:flex;align-items:flex-end;justify-content:center}
/* previsao (dado, nao acao): roxo, a cor de detalhe visual do tema */
/* s228 (pedido dele): paleta propria do bloco (--fc*, a familia rosa do anel de Cards): o total no cabecalho, os dias
   em lavagem, o PICO em barra cheia com o numero em destaque; uma linha de base sob as barras */
.ag-cab{display:flex;flex-wrap:wrap;align-items:baseline;justify-content:space-between;gap:var(--esp-1) var(--esp-3)}
.ag-cab h3{margin:0}
.ag-total{margin:0;font-size:var(--fs-meta);color:var(--tinta3)}
.ag-total b{font-size:var(--fs-secao);font-weight:700;color:var(--fc-tinta)}
.ag-trilho{border-bottom:1px solid var(--linha-forte)}
.ag-barras i{display:block;width:min(100%,32px);background:var(--fc-fraco);border-radius:var(--raio-p) var(--raio-p) 0 0}
.ag-barras .pico i{background:var(--fc)}
/* s229 (rodada 5): o segmento ciano (token de interacao) dos que entraram pela ultima sessao, no topo da barra */
.ag-barras i{display:flex;flex-direction:column;overflow:hidden}
.ag-sessao{display:block;width:100%;background:var(--acento)}
.ag-mais{display:block;font-size:.7rem;font-weight:650;color:var(--acento-tinta);line-height:1.1;text-align:center}
.ag-n{font-size:var(--fs-meta);font-weight:600;color:var(--tinta2)}
.ag-barras .pico .ag-n{color:var(--fc-tinta);font-weight:700}
.ag-d{font-size:var(--fs-meta);color:var(--tinta3)}

/* Roadmap (s229, pedido dele em 15/10): Hoje e cada dia seguinte SEMPRE abertos, um bloco por dia (titulo com
   filete e a contagem), as tarefas em CARTOES (o degrau --afundado dentro da placa, como o card do player): no
   topo o chip da area e a contagem, o tema, e no pe os botoes. Grade: 1 coluna no celular, quantas couberem acima */
.rm-dia{margin-top:var(--esp-5)}
.rm-tit{display:flex;flex-wrap:wrap;align-items:baseline;gap:var(--esp-1) var(--esp-3);margin:0 0 var(--esp-3);
        padding-bottom:var(--esp-2);border-bottom:1px solid var(--linha);font-size:var(--fs-legenda);font-weight:700;color:var(--tinta)}
.rm-dia.hoje .rm-d{color:var(--acento-tinta)}
.rm-n{color:var(--tinta3);font-size:var(--fs-meta);font-weight:500}
/* s229 (rodada 3, pedido dele: "tipo Google Calendar sem horas"): cada tarefa e uma BARRA na largura toda, empilhada
   no dia; a faixa a esquerda e o fundo tingido dizem a area (o chip segue com o nome: nunca so a cor); meta e tema a
   esquerda, os botoes a direita na mesma linha (no celular, quebram para baixo) */
.tarefas{list-style:none;margin:0;padding:0;display:grid;gap:var(--esp-2);grid-template-columns:minmax(0,1fr)}
.tarefa{--area:var(--linha-forte);position:relative;overflow:hidden;min-width:0;display:grid;grid-template-columns:minmax(0,1fr) auto;
        grid-template-areas:"meta acao" "tema acao";align-items:center;gap:2px var(--esp-4);padding:var(--esp-2) var(--esp-4) var(--esp-2) calc(var(--esp-4) + 4px);
        background:color-mix(in srgb,var(--area) 9%,var(--afundado));border:1px solid var(--linha);border-radius:var(--raio)}
.tarefa:has(> .t-faixa[data-area="CM"]){--area:var(--acento)}
.tarefa:has(> .t-faixa[data-area="CIR"]){--area:var(--rosa)}
.tarefa:has(> .t-faixa[data-area="MFC"]){--area:var(--ok)}
.tarefa:has(> .t-faixa[data-area="PED"]){--area:var(--roxo)}
.tarefa:has(> .t-faixa[data-area="GO"]){--area:var(--amarelo)}
.tarefa:has(> .t-faixa[data-area="Simulado"]){--area:var(--aviso)}
.tarefa:has(> .t-faixa[data-area="RD"]){--area:var(--roxo-tinta)}
.t-faixa{position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--area)}
.tarefa[hidden]{display:none}   /* s229 (rodada 4): assinada/resolvida ao vivo sai do Cronograma */
.tarefa > .t-meta{grid-area:meta;justify-content:flex-start}
.tarefa > .t-tema{grid-area:tema}
.tarefa > .t-acao{grid-area:acao;margin:0;padding:0;justify-content:flex-end}
@media (max-width:520px){
  .tarefa{grid-template-columns:minmax(0,1fr);grid-template-areas:"meta" "tema" "acao"}
  .tarefa > .t-acao{justify-content:flex-start;padding-top:var(--esp-1)}
}
.t-meta{min-width:0;color:var(--tinta3);font-size:var(--fs-meta);display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:var(--esp-1) var(--esp-3)}
.t-rot{color:var(--rosa);font-weight:650;background:var(--rosa-fraco);padding:1px var(--esp-2);border-radius:var(--raio-pilula)}
.t-n{font-variant-numeric:tabular-nums}
.t-tema{min-width:0;font-weight:600;line-height:1.35;color:var(--tinta)}
.t-acao{margin-top:auto;padding-top:var(--esp-1);display:flex;flex-wrap:wrap;align-items:center;gap:var(--esp-2);font-size:var(--fs-legenda)}
/* s229: os botoes do cartao -- o MESMO desenho do "Responder" das Listas (raio de controle, 44 px): o primario em
   ciano cheio (Resolver, Abrir lista), o secundario em contorno ciano (Abrir aula) */
.t-btn{display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:0 var(--esp-4);border-radius:var(--raio);
       border:1px solid var(--acento);color:var(--acento-tinta);background:transparent;font-weight:650;text-decoration:none;
       -webkit-tap-highlight-color:transparent;transition:filter var(--transicao),background var(--transicao)}
.t-btn:hover{background:var(--acento-fraco)}
.t-btn-prim{background:var(--acento);color:var(--sobre)}
.t-btn-prim:hover{background:var(--acento-tinta);border-color:var(--acento-tinta)}
.t-btn:focus-visible{outline:2px solid var(--acento);outline-offset:2px}
/* a assinatura ao vivo (o hub poe a classe e o rotulo): o cartao assinado apaga, o estado em verde */
.tarefa.qd-assinado{opacity:.72}
.t-assinado,.tarefa.qd-assinado .t-rd-st{color:var(--ok);font-weight:600}
/* sem sprint, o atraso aparece UMA vez: no subtitulo do grupo das atrasadas (ambar + a palavra, nunca so cor) */
.t-grupo{margin:var(--esp-4) 0 var(--esp-2);font-size:var(--fs-legenda);font-weight:700;color:var(--tinta2)}
.t-grupo.atrasadas{color:var(--aviso)}
/* o proximo passo: a 1a tarefa do dia (a ordem e a do plano) -- o rotulo "Proxima" e o contorno ciano */
.tarefa.proxima{border-color:var(--acento)}
.tarefa.proxima .t-tema::before{content:"Próxima";display:inline-block;margin-right:var(--esp-2);padding:0 var(--esp-2);border-radius:var(--raio-pilula);background:var(--acento-fraco);color:var(--acento-tinta);font-size:var(--fs-meta);font-weight:650;vertical-align:1px}
.prox{margin-top:var(--esp-3)}
.mais{margin-top:var(--esp-2)}
.mais summary{cursor:pointer;color:var(--acento);font-weight:600;padding:var(--esp-2) 0;min-height:44px}
.mais .tarefas{margin-top:var(--esp-1)}
/* sem sprint: a rota ate a prova (s213), cada semana futura recolhida; o resumo quebra linha, nunca alarga */
.rota{margin-top:var(--esp-5)}
.rota h3{margin-bottom:2px}
.rota-sem{border-top:1px solid var(--linha)}
.rota-sem:last-child{border-bottom:1px solid var(--linha)}
.rota-sem>summary{cursor:pointer;padding:var(--esp-3) 0;min-height:44px}
.rota-tit{font-weight:650}
.rota-n{color:var(--tinta3);font-size:var(--fs-meta);margin-left:var(--esp-1)}
.rota-sem .tarefas{margin:var(--esp-1) 0 var(--esp-3)}
/* s226 (sprint final): o que nao coube no plano, recolhido abaixo dos dias, agrupado pelo motivo */
.rota-sem.fora{margin-top:var(--esp-5)}
.rota-sem.fora .t-grupo{margin-top:var(--esp-2)}

/* os media medem o iframe (= a coluna larga do shell). Os quatro aneis em linha assim que cabem (4 x 7,5rem
   e os vaos); a partir de 760 px, a grade de duas colunas: o Hoje inteiro, Por bloco | Flashcards */
@media (min-width:600px){
  .aneis4{grid-template-columns:repeat(4,minmax(0,1fr))}
}
@media (min-width:760px){
  .dash{grid-template-columns:repeat(2,minmax(0,1fr))}
  .dash > .dash-hoje{grid-column:1 / -1}
  .aneis4{gap:var(--esp-5) var(--esp-5)}
  .anel{width:min(100%,8.5rem)}
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
        # s226 (painel-dashboard-sprint part-1): o dashboard so no topo; s227 (part-5): o Hoje com os quatro
        # aneis + Por bloco + Flashcards da semana (o anel do Ritmo e o Por bloco levam o `data-bloco` deles)
        _sec("dia", _html_dash(d), "dia dash"),
        # s226 (sprint-final-uerj part-3): com sprint, o bloco da semana vira Hoje / Proximos dias /
        # Fora do sprint (o `data-bloco` segue "semana": o hub e os testes o acham pelo nome antigo)
        # s227 (tema v4 part-2): o Plano de hoje (ou a semana) e a Documentacao, uma placa cada
        # s229 (pedido dele, 15/10): o Plano de hoje + Proximos dias viram o ROADMAP; a Documentacao saiu do
        # Painel (mora num eixo proprio da Biblioteca da Teoria: `hub.EIXO_DOC`); o JSON segue com a lista
        _sec("semana", _html_sprint(d["sprint"], d["dia"]["cards"], d.get("data")) if d.get("sprint")
             else _html_semana(d["semana"]), "semana placa"),
    ])
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
