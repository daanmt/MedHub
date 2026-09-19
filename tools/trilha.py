#!/usr/bin/env python3
"""trilha.py -- o GERADOR da trilha da Fase 1 (`core/cronograma/plano_trilha.json`), no repo.

s189 (spec `trilha-autoridade-unica`, decisao do `/ai-eng`). Ate a s188 o gerador vivia em
`scratch/s188_trilha/` -- gitignored, ~1.450 linhas fora do git ditando a UNICA autoridade da
Fase 1, re-executadas a cada prova UERJ -- e o `_doc` do arquivo gerado prometia "editavel a
mao" enquanto o `--gravar` o sobrescrevia: duas autoridades, a manual perdendo em silencio
(o defeito do `--mover`, F120, uma camada acima).

Autoridade em TRES camadas, todas DADO versionado:

    core/cronograma/trilha/parametros.json   a ESTRATEGIA: calendario, capacidade de listas por
                                             semana, piso/teto por bloco, simulados, pesos
    core/cronograma/trilha/custom.json       a UNICA camada editavel a mao: override por chave
                                             (fonte, ref_semana_fonte, tarefa_fonte), vence o gerado
    core/cronograma/trilha/entrada/          a entrada FIXADA (snapshot do plano e da cobertura
                                             do banco em 18/09; catalogo de temas) + o mapa UERJ
      -> tools/trilha.py                     -> core/cronograma/plano_trilha.json (GERADO)

entrada + parametros + custom + codigo = saida. `tools/test_trilha.py` prova, por GOLDEN, que
o arquivo gravado E a saida do gerador, e, por PROPRIEDADE, que a saida respeita o que os
parametros declaram (a mesma `verificar_propriedades` que o `--gravar` roda antes de escrever).

Uso:
    python tools/trilha.py              # gera e COMPARA com o gravado (read-only)
    python tools/trilha.py --tabela     # + a trilha semana a semana
    python tools/trilha.py --gravar     # escreve plano_trilha.json (RECUSA se violar propriedade)

Depois de gravar: `python tools/plano.py --semear --dry-run` -> `--apply --expect N`.
Assinatura canonica em `.claude/commands/engenharia-cli.md`.

⚠️ LIMITES DECLARADOS:
(a) a entrada e um snapshot de 18/09: progresso posterior nao muda a PRIORIDADE (muda o status,
    pelo re-seed). Re-snapshot = arquivos novos com data + apontar `parametros.entrada`; nao ha
    exportador (nao construido).
(b) REGRA DO BLOCO: bloco do TEMA = o bloco da prova UERJ com mais questoes dele, entre os blocos
    com >= 3 questoes; sem bloco forte, o bloco da AREA do EMED (`bloco_de_area`, CM por
    default). Bloco da LINHA = o mais comum entre os temas casados (empate: o primeiro). Tema
    cobrado em VARIOS blocos cai INTEIRO no majoritario -- o piso/teto fica levemente torto nos
    dois sentidos; atribuicao fracionada nao foi construida (ganho pequeno dentro de 6 pp).
(c) o piso/teto e verificado NA REGUA DO PROPRIO GERADOR (a regra acima): auto-consistencia,
    nao independencia. A lente independente -- o bloco pela area (`db.bloco_de`) -- sai no
    relatorio com as linhas em que as duas divergem, NOMINAIS; nao e gate.
(d) o casamento linha <-> tema e por tokens (`casa`): linha que nao casa com tema nenhum fica
    fora dos candidatos -- a mesma cegueira vale para quem reusar `casa` (ex.: a reserva).
"""
import argparse
import collections
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

DIR_TRILHA = os.path.join(ROOT, "core", "cronograma", "trilha")
P_PARAMETROS = os.path.join(DIR_TRILHA, "parametros.json")
P_CUSTOM = os.path.join(DIR_TRILHA, "custom.json")
P_SAIDA = os.path.join(ROOT, "core", "cronograma", "plano_trilha.json")

#: Blocos que o piso/teto governa. MFC entra por aula-base + o bloco de 20q das 6 provas.
BLOCOS_COM_PISO = ("CM", "CIR", "GO", "PED")
#: Ordem de intercalacao dos blocos dentro da semana (nenhum bloco abre a semana sempre).
RODIZIO = ("CIR", "GO", "PED", "CM", "MFC")
#: Primeira semana da Fase 2 (a fronteira mora em `plano.semana_fase2(21)`; o teste trava).
PRIMEIRA_SEMANA_FASE2 = 8

DOC_GERADO = (
    "GERADO por tools/trilha.py --gravar -- NAO EDITAR A MAO (a proxima gravacao sobrescreve, e o "
    "teste golden derruba o commit). TRILHA da Fase 1 (prova UERJ em 01/11) como DADO: overrides "
    "aplicados por tools/plano.py::aplicar_trilha POR CIMA das regras puras; com fase1_exclusiva, "
    "linha pendente das semanas 1-7 que nao esta aqui sai da fila (reserva: `plano.py --reserva`). "
    "Mudar a estrategia = core/cronograma/trilha/parametros.json; mover UMA linha a mao = "
    "core/cronograma/trilha/custom.json; depois `python tools/trilha.py --gravar` + "
    "`python tools/plano.py --semear --dry-run` -> `--apply --expect N`. Derivacao: incidencia por "
    "tema nas provas UERJ 2021-2026 x o que o operador ja estudou -> prioridade P = peso_uerj x "
    "lacuna; piso/teto por bloco CM/CIR/GO/PED sobre o orcamento de listas; MFC entra por sessoes "
    "de aula-base + o bloco de 20q das 6 provas inteiras. Status de linha ja existente muda por "
    "--reabrir/--cortar, nunca por aqui.")
GERADO_POR = "tools/trilha.py --gravar"


# ------------------------------------------------ casamento de nome (identico a s188)

STOP = set("de da do das dos e em na no a o as os ao aos para por com pt pts parte i ii iii iv v "
           "teoria revisao resumo introducao".split())


def toks(s):
    """Nome -> conjunto de tokens fortes (sem acento, sem parenteses, sem stopword, > 2 letras)."""
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\(.*?\)", " ", s)
    return frozenset(w for w in re.findall(r"[a-z]+", s) if w not in STOP and len(w) > 2)


def casa(a, b):
    """a, b = conjuntos de tokens. Casa se um contem o outro ou Jaccard >= 0,6."""
    if not a or not b:
        return False
    if a <= b or b <= a:
        return True
    return len(a & b) / len(a | b) >= 0.6


def partes_da_tarefa(tema):
    """Tema de tarefa agrupado pelo EMED ("A; B" ou "A | B") -> partes."""
    return [x.strip() for x in re.split(r"[;|]", tema or "") if x.strip()]


# --------------------------------------------------------------------- leitura

def _ler(caminho):
    with open(caminho, encoding="utf-8") as fh:
        return json.load(fh)


def _abs(rel):
    return rel if os.path.isabs(rel) else os.path.join(ROOT, rel)


def carregar_parametros(caminho=None):
    """`parametros.json` -> dict com chaves numericas ja convertidas (semana, edicao)."""
    p = _ler(caminho or P_PARAMETROS)
    fora = sorted({b for b in p["bloco_de_area"].values() if b not in RODIZIO})
    if fora:
        raise ValueError(f"parametros.bloco_de_area com bloco fora de {RODIZIO}: {fora}")
    if not 0 < p["piso"] <= p["teto"] < 1:
        raise ValueError(f"parametros: exige 0 < piso <= teto < 1 (piso={p['piso']}, "
                         f"teto={p['teto']})")
    sem_calendario = sorted(set(p["cap_listas"]) - set(p["calendario"]))
    if sem_calendario:
        raise ValueError(f"parametros: cap_listas com semana sem calendario: {sem_calendario}")
    return {**p,
            "_cap": {int(k): v for k, v in p["cap_listas"].items()},
            "_simulados": {int(k): v for k, v in p["simulados_uerj"].items()},
            "_peso_ed": {int(k): v for k, v in p["peso_edicao"].items()},
            "_teto_sessoes": {int(k): v for k, v in p["teto_sessoes"].items()},
            "_semanas": {int(k): (v["inicio"], v["fim"]) for k, v in p["calendario"].items()}}


def carregar_entrada(params):
    """Os arquivos FIXADOS que `parametros.entrada` nomeia."""
    e = params["entrada"]
    return {
        "mapa": _ler(_abs(e["mapa_uerj"]))["questoes"],
        "catalogo": dict((t, a) for t, a in _ler(_abs(e["catalogo"]))["temas"]),
        "dashboard": _ler(_abs(e["dashboard"])),
        "cobertura": _ler(_abs(e["cobertura"])),
        "plano": _ler(_abs(e["plano"]))["linhas"],
        "plano_custom": _ler(_abs(e["plano_custom"]))["tarefas"],
    }


def carregar_custom(caminho=None):
    return _ler(caminho or P_CUSTOM).get("overrides") or []


# ---------------------------------------------------------------- reconciliacao

def reconciliar(mapa, catalogo, dashboard, cobertura):
    """Incidencia UERJ x o que o operador ja estudou, por tema do catalogo. PURA.

    So os campos que `gerar` consome. A s188 calculava tambem cor do Drive, extensivo por
    tema e focos por edicao -- dado sem consumidor; ficou no scratch como registro."""
    vazio = lambda: dict(n=0, eds=set(), blocos=collections.Counter())  # noqa: E731
    inc = collections.defaultdict(vazio)
    for r in mapa:
        if r["tema"] == "FORA-DO-CATALOGO":
            continue
        d = inc[(catalogo.get(r["tema"], r["area"]), r["tema"])]
        d["n"] += 1
        d["eds"].add(r["edicao"])
        d["blocos"][r["bloco"]] += 1

    dsh = collections.defaultdict(lambda: dict(tarefas=0, feitas=0))
    for t in dashboard["tarefas"]:
        if "Quest" in t["tipo"]:
            continue
        d = dsh[(t["area"], t["assunto"])]
        d["tarefas"] += 1
        d["feitas"] += 1 if t["realizada"] else 0

    dbt = [(c["area"], toks(c["tema"]), c) for c in cobertura["temas"]]
    resumos = [toks(os.path.splitext(os.path.basename(p))[0]) for p in cobertura["resumos"]]
    temas = []
    for tema, area in catalogo.items():
        tk = toks(tema)
        i = inc.get((area, tema), vazio())
        d = dsh.get((area, tema), dict(tarefas=0, feitas=0))
        erros = cards = 0
        perf = None
        for a2, tk2, c in dbt:
            if casa(tk, tk2) and (a2 == area or a2 in ("GO", "Clínica Médica", "Clinica Medica")):
                erros += c["erros"]
                cards += c["n_cards"]
                if c["perf"]:
                    perf = c["perf"] if perf is None else max(perf, c["perf"])
        temas.append(dict(area=area, tema=tema, uerj_n=i["n"], uerj_eds=sorted(i["eds"]),
                          uerj_blocos=dict(i["blocos"]), dash_tarefas=d["tarefas"],
                          dash_feitas=d["feitas"], db_erros=erros, db_cards=cards, db_perf=perf,
                          tem_resumo=any(casa(tk, r) for r in resumos)))
    return temas


# ------------------------------------------------ prioridade (constantes do METODO)
# Nao sao estrategia: sao o metodo da s188. Mudar aqui muda a trilha E derruba o golden --
# a mudanca tem de vir com o `--gravar` no mesmo commit.

def estado(t):
    """FEITO / PARCIAL (Dashboard) > TOCADO (>= 5 cards, >= 3 erros ou resumo) > ZERO."""
    if t["dash_tarefas"] and t["dash_feitas"] >= t["dash_tarefas"]:
        return "FEITO"
    if t["dash_feitas"]:
        return "PARCIAL"
    if t["db_cards"] >= 5 or t["db_erros"] >= 3 or t["tem_resumo"]:
        return "TOCADO"
    return "ZERO"


def lacuna(t):
    """O quanto FALTA do tema (1 = nunca estudado). FEITO com desempenho fraco ainda pesa."""
    e = estado(t)
    if e == "ZERO":
        return 1.0
    if e == "TOCADO":
        return 0.7
    if e == "PARCIAL":
        return 0.55
    fraco = (t["db_perf"] is not None and t["db_perf"] < 75) or t["db_erros"] >= 10
    return 0.4 if fraco else 0.15


def bloco_tema(t, bloco_de_area):
    """Regra (b) do docstring do modulo: bloco UERJ majoritario entre os que tem >= 3 questoes."""
    fortes = {b: n for b, n in t["uerj_blocos"].items() if n >= 3}
    if fortes:
        return max(fortes.items(), key=lambda kv: kv[1])[0]
    return bloco_de_area.get(t["area"], "CM")


def pontuar(temas, mapa, params):
    """peso_uerj (2021-2022 valem 0,7) + heranca MFC-clinica -> lista EMED; P = peso x lacuna."""
    peso = collections.Counter()
    for r in mapa:
        if r["tema"] != "FORA-DO-CATALOGO":
            peso[r["tema"]] += params["_peso_ed"].get(r["edicao"], 1.0)
    for origem, destino in params["mfc_para_emed"].items():
        peso[destino] += peso.get(origem, 0.0)
    excluir = set(params["excluir_temas"])
    for t in temas:
        t["peso_uerj"] = round(peso.get(t["tema"], 0.0), 1)
        t["estado"] = estado(t)
        t["P"] = 0.0 if t["tema"] in excluir else round(t["peso_uerj"] * lacuna(t), 2)
        t["bloco"] = bloco_tema(t, params["bloco_de_area"])
    return temas


def bloco_linha(c):
    """Bloco da LINHA = o mais comum entre os temas casados (empate: o primeiro)."""
    return collections.Counter(t["bloco"] for t in c["temas"]).most_common(1)[0][0]


def _chave(o):
    return (o["fonte"], o["ref_semana_fonte"], o["tarefa_fonte"])


def candidatas(temas, plano):
    """Linhas rf/extensivo nao feitas que casam com algum tema -> V = media de P (x0,8 mista)."""
    cands = []
    for p in plano:
        if p["fonte"] not in ("rf", "extensivo") or p["status"] == "feita" or not p["area"]:
            continue
        if p["fonte"] == "extensivo" and p["ref_semana_fonte"] >= 49:
            continue
        tk_partes = [toks(x) for x in partes_da_tarefa(p["tema"])] or [toks(p["tema"])]
        casados = [t for t in temas
                   if t["area"] == p["area"] and any(casa(toks(t["tema"]), tp) for tp in tk_partes)]
        if not casados:
            continue
        # 'mista' = Revisao por Questoes (varios temas numa lista). Tema AGRUPADO pelo EMED numa
        # tarefa ("Doenca Celiaca | Febre Reumatica") e UMA lista de UM assunto: nao e mista.
        multi = p["tipo_norm"] in ("revisao_questoes", "outro")
        v = (sum(c["P"] for c in casados) / len(casados)) * (0.8 if multi else 1.0)
        cands.append(dict(p=p, temas=casados, V=round(v, 2), multi=multi))
    return cands


# ------------------------------------------------------------------- o gerador

def gerar(params, entrada, custom):
    """entrada + parametros + custom -> `{overrides, tabela, sobras, sessoes_fora, stats}`. PURA.

    Porte fiel do `gera_trilha.py` da s188 (o golden prova): escolha por valor com piso e
    teto por bloco, serie inteira ou nada, semanas por rodizio de blocos, mistas nas S6-S7,
    sessoes de aula-base de tema sem lista. A camada manual entra por ultimo e VENCE o
    gerado na mesma chave."""
    temas = pontuar(reconciliar(entrada["mapa"], entrada["catalogo"], entrada["dashboard"],
                                entrada["cobertura"]), entrada["mapa"], params)
    plano = entrada["plano"]
    cap = params["_cap"]
    piso, teto = params["piso"], params["teto"]
    cands = candidatas(temas, plano)

    tem_rf = {(c["p"]["area"], t["tema"]) for c in cands
              if c["p"]["fonte"] == "rf" and not c["multi"] for t in c["temas"]}
    tem_lista = set()          # tema com ALGUMA lista propria, em qualquer fonte, feita ou nao
    for p in plano:
        lista_propria = ((p["fonte"] in ("rf", "extensivo") and p["tipo_norm"] == "revisao")
                         or (p["fonte"] == "rf" and p["tipo_norm"] == "teoria"))  # RF: teoria vem com lista
        if lista_propria and p["area"]:
            tks = [toks(x) for x in partes_da_tarefa(p["tema"])]
            for t in temas:
                if t["area"] == p["area"] and any(casa(toks(t["tema"]), tp) for tp in tks):
                    tem_lista.add((t["area"], t["tema"]))

    escolhiveis, sessoes, vistos_sessao = [], [], set()
    for c in cands:
        p = c["p"]
        if p["fonte"] == "extensivo":
            if not c["multi"] and all((p["area"], t["tema"]) in tem_rf for t in c["temas"]):
                continue                        # a RF ja traz a lista deste tema
            if p["tipo_norm"] == "teoria":
                # leitura SEM lista propria no EMED: se a UERJ cobra, vira SESSAO de aula-base
                chave = tuple(sorted((t["area"], t["tema"]) for t in c["temas"]))
                if (c["V"] >= 2.0 and chave not in vistos_sessao
                        and not any(k in tem_lista for k in chave)):
                    vistos_sessao.add(chave)
                    c["sem_lista"] = True
                    sessoes.append(c)
                continue
        if c["V"] <= 0:
            continue
        escolhiveis.append(c)

    orc = sum(cap.values())
    escolhiveis.sort(key=lambda c: (-c["V"], c["p"]["ref_semana_fonte"], c["p"]["tarefa_fonte"]))
    escolhidas, usado = [], collections.Counter()
    for c in escolhiveis:                        # 1a passada: piso de cada bloco
        b = bloco_linha(c)
        if b in BLOCOS_COM_PISO and usado[b] < piso * orc:
            escolhidas.append(c)
            usado[b] += c["p"]["q_previstas"] or 0
    ids = {id(c) for c in escolhidas}
    for c in escolhiveis:                        # 2a passada: valor puro, respeitando o teto
        if id(c) in ids:
            continue
        b, q = bloco_linha(c), (c["p"]["q_previstas"] or 0)
        if sum(usado.values()) + q > orc or (b != "MFC" and usado[b] + q > teto * orc):
            continue
        escolhidas.append(c)
        usado[b] += q

    def chave_tema(c):
        return tuple(sorted((t["area"], t["tema"]) for t in c["temas"]))

    # tema com teoria escolhida leva junto a revisao do MESMO tema (e vice-versa): serie inteira
    ids = {id(c) for c in escolhidas}
    temas_escolhidos = {chave_tema(c) for c in escolhidas if not c["multi"]}
    for c in escolhiveis:
        if id(c) not in ids and not c["multi"] and chave_tema(c) in temas_escolhidos:
            escolhidas.append(c)
            usado[bloco_linha(c)] += c["p"]["q_previstas"] or 0

    # ---- semanas: valor alto primeiro; mistas guardadas para S6-S7; S7 sem tema novo
    ordem_tipo = {"teoria": 0, "revisao": 1, "revisao_questoes": 2, "outro": 2}
    series = collections.defaultdict(list)
    mistas = []
    for c in escolhidas:
        (mistas if c["multi"] else series[chave_tema(c)]).append(c)
    for k in series:
        series[k].sort(key=lambda c: (ordem_tipo.get(c["p"]["tipo_norm"], 1),
                                      c["p"]["ref_semana_fonte"], c["p"]["tarefa_fonte"]))
    filas = collections.defaultdict(list)
    for k, lst in series.items():
        filas[bloco_linha(lst[0])].append(lst)
    for b in filas:
        filas[b].sort(key=lambda lst: -max(c["V"] for c in lst))
    semana_de, carga = agendar_series(filas, cap)
    mistas.sort(key=lambda c: -c["V"])
    for c in mistas:                             # mistas: enchem S6 e S7, intercalando blocos
        s = 7 if carga[7] < cap[7] and carga[7] <= carga[6] - 250 else 6
        if carga[6] >= cap[6] + 120:
            s = 7
        if carga[s] >= cap[s] + 150:
            continue
        semana_de[id(c)] = s
        carga[s] += c["p"]["q_previstas"] or 0
    # sessoes de aula-base de tema SEM lista: por valor, com teto por semana
    sessoes.sort(key=lambda c: -c["V"])
    usadas = collections.Counter()
    for c in sessoes:
        for s in sorted(params["_teto_sessoes"]):
            if usadas[s] < params["_teto_sessoes"][s]:
                usadas[s] += 1
                semana_de[id(c)] = s
                escolhidas.append(c)
                break
    sessoes_fora = [c for c in sessoes if id(c) not in semana_de]
    sobras = [c for c in escolhidas if id(c) not in semana_de]

    overrides, tabela = [], []
    for s in range(1, 8):
        da_semana = [c for c in escolhidas if semana_de.get(id(c)) == s]
        por_b = collections.defaultdict(list)
        for c in sorted(da_semana, key=lambda c: (c["multi"], -c["V"],
                                                   ordem_tipo.get(c["p"]["tipo_norm"], 1))):
            por_b[bloco_linha(c)].append(c)
        # bloco fora do RODIZIO (rotulo novo num mapa futuro) entra no fim da volta: sem isto o
        # `while` girava para sempre com a linha dele parada (mesma classe do agendar_series)
        voltas = list(RODIZIO) + sorted(b for b in por_b if b not in RODIZIO)
        seq = []
        while any(por_b.values()):
            for b in voltas:
                if por_b[b]:
                    seq.append(por_b[b].pop(0))
        for k, c in enumerate(seq, start=10):
            p, t0 = c["p"], c["temas"][0]
            nota = "trilha UERJ: n=%d em %d ed. | %s%s" % (
                sum(t["uerj_n"] for t in c["temas"]), max(len(t["uerj_eds"]) for t in c["temas"]),
                "/".join(sorted({t["estado"] for t in c["temas"]})),
                (" | sem lista no EMED: aula-base + 10-15 questoes do banco pelo filtro do tema"
                 if c.get("sem_lista") else
                 " | tema-zero: aula-base antes da lista"
                 if t0["estado"] == "ZERO" and not c["multi"] else ""))
            overrides.append(dict(fonte=p["fonte"], ref_semana_fonte=p["ref_semana_fonte"],
                                  tarefa_fonte=p["tarefa_fonte"], semana_plano=s, ordem=k,
                                  status="pendente", nota=nota))
            tabela.append(dict(semana=s, ordem=k, id=p["id"], bloco=bloco_linha(c),
                               area=p["area"], tema=p["tema"], tipo=p["tipo_norm"],
                               q=p["q_previstas"] or 0, V=c["V"], fonte=p["fonte"],
                               estado=t0["estado"], uerj_n=sum(t["uerj_n"] for t in c["temas"]),
                               multi=c["multi"], sem_lista=bool(c.get("sem_lista")),
                               origem="gerador", _ref=p["ref_semana_fonte"],
                               _tf=p["tarefa_fonte"]))

    overrides, manual = aplicar_camada_manual(overrides, custom, entrada, params)
    # a tabela (relatorio) e da Fase 1: linha manual da Fase 2 nao entra, e linha gerada que
    # a camada manual reescreveu sai (a manual a substitui)
    tabela = [r for r in tabela if (r["fonte"], r["_ref"], r["_tf"]) not in manual] + [
        r for r in manual_tabela(custom, entrada) if r["semana"] < PRIMEIRA_SEMANA_FASE2]
    tabela.sort(key=lambda r: (r["semana"], r["ordem"]))
    blocos = {_chave(dict(fonte=c["p"]["fonte"], ref_semana_fonte=c["p"]["ref_semana_fonte"],
                          tarefa_fonte=c["p"]["tarefa_fonte"])): bloco_linha(c) for c in cands}
    stats = dict(candidatas=len(cands), escolhiveis=len(escolhiveis), escolhidas=len(escolhidas),
                 agendadas=len(tabela), sobras=len(sobras), orcamento=orc,
                 sessoes_agendadas=sum(usadas.values()), sessoes_fora=len(sessoes_fora))
    return dict(overrides=overrides, tabela=tabela, blocos=blocos, temas=temas, stats=stats,
                sobras=[dict(id=c["p"]["id"], tema=c["p"]["tema"], V=c["V"]) for c in sobras],
                sessoes_fora=[dict(tema=c["p"]["tema"], V=c["V"]) for c in sessoes_fora])


def agendar_series(filas, cap, folga=25):
    """Semanas 1-6: rodizio de blocos, UMA linha de serie por vez, ate a capacidade de listas
    (+ folga). CONSOME `filas` (bloco -> lista de series). Devolve `(semana_de, carga)`.

    🔴 s189 -- loop infinito herdado da s188, achado no porte: o contador `vazio` era zerado
    ASSIM que o bloco tinha serie, ANTES do teste de capacidade. Com dois ou mais blocos cuja
    proxima linha nao cabe, `vazio` oscilava 0 -> 1 e nunca chegava a 5: o `while` girava para
    sempre. Com os parametros da s188 o laco sempre terminava por sorte (sobrava linha pequena
    que cabia); com teto 20% ele trava. A recalibracao depois de cada prova muda exatamente
    esses parametros. Agora `vazio` so zera depois de uma linha AGENDADA: 5 tentativas seguidas
    sem agendar = uma volta inteira do rodizio sem mudanca de estado = parar. Nos casos em que
    o laco antigo terminava, a saida e identica (o golden prova)."""
    semana_de, carga = {}, collections.Counter()
    for s in range(1, 7):
        vazio, i = 0, 0
        while carga[s] < cap[s] and vazio < len(RODIZIO):
            b = RODIZIO[i % len(RODIZIO)]
            i += 1
            if not filas[b]:
                vazio += 1
                continue
            serie = filas[b][0]
            if carga[s] + (serie[0]["p"]["q_previstas"] or 0) > cap[s] + folga:
                vazio += 1
                continue
            vazio = 0
            c = serie.pop(0)                     # uma linha da serie por vez: atravessa semanas
            if not serie:
                filas[b].pop(0)
            semana_de[id(c)] = s
            carga[s] += c["p"]["q_previstas"] or 0
    return semana_de, carga


def aplicar_camada_manual(overrides, custom, entrada, params):
    """A camada manual VENCE o gerado por chave. PURA. Devolve `(overrides, chaves_manuais)`.

    Entrada sem `racional` e recusada: override manual sem motivo e a mao passando por cima
    do gerador sem ninguem saber por que (mesma regra do `--cortar` sem `--motivo`). Chave
    repetida DENTRO da camada manual tambem e recusada."""
    manual = {}
    for m in custom:
        k = _chave(m)
        if None in k:
            raise ValueError(f"custom.json: override sem chave completa: {m}")
        if not str(m.get("racional") or "").strip():
            raise ValueError(f"custom.json: override {k} sem `racional`")
        if k in manual:
            raise ValueError(f"custom.json: chave repetida {k}")
        o = dict(fonte=m["fonte"], ref_semana_fonte=m["ref_semana_fonte"],
                 tarefa_fonte=m["tarefa_fonte"], semana_plano=m["semana_plano"],
                 ordem=m["ordem"], status=m.get("status", "pendente"))
        if "nota" in m:
            o["nota"] = m["nota"]
        manual[k] = o
    saida = [o for o in overrides if _chave(o) not in manual] + list(manual.values())
    return saida, set(manual)


def manual_tabela(custom, entrada):
    """Linhas da tabela (relatorio) para a camada manual."""
    por_custom = {t["tarefa_fonte"]: t for t in entrada["plano_custom"]}
    por_chave = {_chave(p): p for p in entrada["plano"]}
    saida = []
    for m in custom:
        if m["fonte"] == "custom":
            t = por_custom.get(m["tarefa_fonte"])
            if t is None:
                raise ValueError(f"custom.json: tarefa custom {m['tarefa_fonte']} nao existe em "
                                 f"plano_custom.json")
        else:
            t = por_chave.get(_chave(m))
            if t is None:
                raise ValueError(f"custom.json: linha {_chave(m)} nao existe no snapshot do plano")
        eh_sim = t.get("area") == "Simulado"
        saida.append(dict(semana=m["semana_plano"], ordem=m["ordem"], id=t.get("id"),
                          bloco="SIM" if eh_sim else None, area=t.get("area"),
                          tema=t.get("tema"), tipo="simulado" if eh_sim else t.get("tipo_norm"),
                          q=t.get("q_previstas") or 0, V=None, fonte=m["fonte"], estado=None,
                          uerj_n=None, multi=False, sem_lista=False, origem="manual",
                          racional=m.get("racional"), _ref=m["ref_semana_fonte"],
                          _tf=m["tarefa_fonte"]))
    return saida


def documento(params, overrides):
    """O `plano_trilha.json` que `plano.py` consome -- com a marca de gerado."""
    return {
        "_doc": DOC_GERADO,
        "gerado_por": GERADO_POR,
        "versao": params["versao"],
        "fase1_exclusiva": params["fase1_exclusiva"],
        "calendario": params["calendario"],
        "simulados_uerj": params["simulados_uerj"],
        "overrides": sorted(overrides, key=lambda o: (o["semana_plano"], o["ordem"], o["fonte"],
                                                      o["ref_semana_fonte"], o["tarefa_fonte"])),
    }


# ------------------------------------------------------------------ propriedades

RX_PROVA_UERJ = re.compile(r"^UERJ (\d{4}) -- prova INTEIRA")


def verificar_propriedades(doc, params, entrada, blocos):
    """O que os PARAMETROS declaram, conferido na SAIDA. Devolve a lista de violacoes.

    Roda no `--gravar` (antes de escrever) e no teste sobre o arquivo gravado. Checa: chave
    unica; toda semana da Fase 1 dentro do calendario; cada prova UERJ inteira na semana que
    `simulados_uerj` declara, uma por semana; blocos CM/CIR/GO/PED entre piso e teto do
    orcamento de listas NA REGUA DO GERADOR (limite (c) do modulo); marca de gerado presente.
    Linha manual de rf/extensivo que o gerador nao casou cai no bloco da area (declarado)."""
    from app.utils.db import bloco_de
    erros = []
    ovs = doc.get("overrides") or []
    repetidas = [k for k, n in collections.Counter(_chave(o) for o in ovs).items() if n > 1]
    if repetidas:
        erros.append(f"chave repetida: {repetidas[:5]}")
    semanas_cal = {int(s) for s in params["calendario"]}
    for o in ovs:
        s = o.get("semana_plano")
        if not isinstance(s, int) or s < 1:
            erros.append(f"semana invalida em {_chave(o)}: {s!r}")
        elif s < PRIMEIRA_SEMANA_FASE2 and s not in semanas_cal:
            erros.append(f"semana {s} fora do calendario em {_chave(o)}")
    por_custom = {t["tarefa_fonte"]: t for t in entrada["plano_custom"]}
    provas = {}
    for o in ovs:
        if o["fonte"] != "custom":
            continue
        m = RX_PROVA_UERJ.match((por_custom.get(o["tarefa_fonte"]) or {}).get("tema") or "")
        if m:
            if o["semana_plano"] in provas:
                erros.append(f"duas provas UERJ inteiras na semana {o['semana_plano']}")
            provas[o["semana_plano"]] = int(m.group(1))
    if provas != params["_simulados"]:
        erros.append(f"provas UERJ por semana {dict(sorted(provas.items()))} != "
                     f"simulados_uerj {dict(sorted(params['_simulados'].items()))}")
    orc = sum(params["_cap"].values())
    q_por_chave = {_chave(p): (p["q_previstas"] or 0) for p in entrada["plano"]}
    area_por_chave = {_chave(p): p["area"] for p in entrada["plano"]}
    q = collections.Counter()
    for o in ovs:
        k = _chave(o)
        if o["fonte"] == "custom" or o["semana_plano"] >= PRIMEIRA_SEMANA_FASE2:
            continue
        q[blocos.get(k) or bloco_de(area_por_chave.get(k))] += q_por_chave.get(k, 0)
    for b in BLOCOS_COM_PISO:
        if not (params["piso"] * orc <= q[b] <= params["teto"] * orc):
            erros.append(f"bloco {b}: {q[b]:.0f}q = {100 * q[b] / orc:.1f}% do orcamento "
                         f"({orc}), fora de {100 * params['piso']:.0f}-"
                         f"{100 * params['teto']:.0f}%")
    if doc.get("gerado_por") != GERADO_POR or "NAO EDITAR" not in (doc.get("_doc") or ""):
        erros.append("marca de gerado ausente (gerado_por / _doc)")
    return erros


# ----------------------------------------------------------------------- relatorio

def lentes_de_bloco(doc, blocos, entrada):
    """q de lista por bloco nas DUAS reguas + as linhas em que divergem (nominais)."""
    from app.utils.db import bloco_de
    por_chave = {_chave(p): p for p in entrada["plano"]}
    gerador, area, divergem = collections.Counter(), collections.Counter(), []
    for o in doc["overrides"]:
        k = _chave(o)
        if o["fonte"] == "custom" or o["semana_plano"] >= PRIMEIRA_SEMANA_FASE2:
            continue
        p = por_chave.get(k) or {}
        q = p.get("q_previstas") or 0
        bg, ba = blocos.get(k) or bloco_de(p.get("area")), bloco_de(p.get("area"))
        gerador[bg] += q
        area[ba] += q
        if bg != ba:
            divergem.append(dict(id=p.get("id"), semana=o["semana_plano"], area=p.get("area"),
                                 tema=p.get("tema"), bloco_gerador=bg, bloco_area=ba, q=q))
    return gerador, area, divergem


def comparar(doc, gravado):
    """Diff por chave entre o gerado e o gravado: `(novas, removidas, mudadas)`."""
    a = {_chave(o): o for o in (gravado or {}).get("overrides") or []}
    b = {_chave(o): o for o in doc["overrides"]}
    return (sorted(set(b) - set(a)), sorted(set(a) - set(b)),
            sorted(k for k in set(a) & set(b) if a[k] != b[k]))


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Gerador da trilha da Fase 1: parametros + custom + entrada fixada -> "
                    "core/cronograma/plano_trilha.json (read-only por default).")
    ap.add_argument("--gravar", action="store_true",
                    help="escreve plano_trilha.json (recusa, exit 2, se violar propriedade)")
    ap.add_argument("--tabela", action="store_true",
                    help="imprime a trilha semana a semana (relatorio)")
    args = ap.parse_args(argv)

    try:
        params = carregar_parametros()
        entrada = carregar_entrada(params)
        custom = carregar_custom()
        r = gerar(params, entrada, custom)
    except ValueError as e:
        print(f"[trilha] RECUSADO: {e}")
        return 2
    doc = documento(params, r["overrides"])
    gravado = _ler(P_SAIDA) if os.path.exists(P_SAIDA) else None
    st = r["stats"]
    print(f"[trilha] candidatas {st['candidatas']} | escolhiveis {st['escolhiveis']} | "
          f"escolhidas {st['escolhidas']} | agendadas {st['agendadas']} | sobras {st['sobras']} "
          f"| sessoes de aula-base {st['sessoes_agendadas']} (fora: {st['sessoes_fora']})")
    print(f"  overrides: {len(doc['overrides'])} ({len(custom)} da camada manual)")
    orc = st["orcamento"]
    gerador, area, divergem = lentes_de_bloco(doc, r["blocos"], entrada)
    fmt = lambda c: ", ".join(f"{b} {c[b]:.0f}q ({100 * c[b] / orc:.1f}%)"  # noqa: E731
                              for b in ("CM", "CIR", "GO", "PED", "MFC"))
    print(f"  listas por bloco / orcamento {orc}q (piso {100 * params['piso']:.0f}%, teto "
          f"{100 * params['teto']:.0f}% p/ CM CIR GO PED):")
    print(f"    regua do GERADOR (bloco em que a UERJ cobra) : {fmt(gerador)}")
    print(f"    lente da AREA do EMED (declarada, nao gate)  : {fmt(area)}")
    if divergem:
        print(f"    {len(divergem)} linha(s) em que as duas lentes divergem:")
        for d in sorted(divergem, key=lambda d: (d["semana"], d["id"] or 0)):
            print(f"      #{d['id']} S{d['semana']} {d['area']} | {d['tema'][:60]} "
                  f"({d['q']:.0f}q): gerador {d['bloco_gerador']} x area {d['bloco_area']}")
    violacoes = verificar_propriedades(doc, params, entrada, r["blocos"])
    print(f"  propriedades: {'OK' if not violacoes else '; '.join(violacoes)}")
    novas, removidas, mudadas = comparar(doc, gravado)
    igual = gravado == doc
    print(f"  x plano_trilha.json gravado: "
          f"{'IDENTICO' if igual else 'DIFERE'} (overrides: +{len(novas)} -{len(removidas)} "
          f"~{len(mudadas)}{'' if gravado else '; nao existe'})")
    if args.tabela:
        for s in range(1, 8):
            rs = [x for x in r["tabela"] if x["semana"] == s]
            cal = params["_semanas"].get(s, ("?", "?"))
            sim = params["_simulados"].get(s)
            print(f"\n== S{s} {cal[0][5:]}..{cal[1][5:]} | {len(rs)} tarefa(s) | "
                  f"{sum(x['q'] for x in rs):.0f}q{f' | prova UERJ {sim}' if sim else ''} ==")
            for x in rs:
                v = f"{x['V']:.1f}" if x["V"] is not None else "-"
                print(f"  {x['ordem']:>3} #{x['id'] or '-':<5} {x['bloco'] or '-':<3} "
                      f"{(x['area'] or '')[:11]:<11} {(x['tema'] or '')[:54]:<54} "
                      f"{(x['tipo'] or '')[:9]:<9} q={x['q']:>3.0f} V={v:>4} {x['origem']}")
    if not args.gravar:
        if not igual:
            print("  (read-only) para gravar: python tools/trilha.py --gravar")
        return 0
    if violacoes:
        print("  RECUSADO: a saida viola propriedade declarada nos parametros. Nada gravado.")
        return 2
    with open(P_SAIDA, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print(f"  GRAVADO {os.path.relpath(P_SAIDA, ROOT)} ({len(doc['overrides'])} overrides). "
          f"Proximo: python tools/plano.py --semear --dry-run")
    return 0


if __name__ == "__main__":
    sys.exit(main())
