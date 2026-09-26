#!/usr/bin/env python3
"""emed_banco.py -- banco de questões EMED no ipub.db: ingere questões e respostas da Bancada EMED, poda o buffer, exporta e lista erros.

A Bancada EMED (artifact privado, capability `db`) é BUFFER: o Claude no Chrome grava
as questões capturadas na coleção `questoes` e a página grava as respostas do operador
na coleção `respostas`. O principal exporta as coleções com `ArtifactData list ...
out_dir` para uma pasta `DIR` no layout `<DIR>/<colecao>/<doc_id>.json` (cada arquivo é
o objeto `data` do documento). `DIR` também pode apontar direto para a pasta da coleção.

Rito (AGENTE.md secao 10.7): dry-run é o default; `--apply` grava; `--expect N` é
COUNT-ASSERT sobre `novas + atualizadas` (diverge -> nada gravado, exit 2).

Uso:
    python tools/emed_banco.py --ingerir tmp/bancada
    python tools/emed_banco.py --ingerir tmp/bancada --apply --expect 19
    python tools/emed_banco.py --registrar tmp/bancada --apply
    python tools/emed_banco.py --podar tmp/bancada --colecao respostas
    python tools/emed_banco.py --exportar t26 --out tmp/emed_export
    python tools/emed_banco.py --erros t26
    python tools/emed_banco.py --status --lista t26 --json

Camada fina sobre `app.utils.db` -- não abre `sqlite3` próprio; toda escrita passa por
`emed_upsert_questoes` / `emed_upsert_respostas`.
Exit: 0 ok; 1 erro de uso/leitura; 2 COUNT-ASSERT falhou.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils import db  # noqa: E402

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PADRAO = os.path.join(ROOT, "tmp", "emed_export")

#: Campos do doc `questoes` do artifact, na ordem em que o `--exportar` os escreve.
CAMPOS_DOC_QUESTAO = ("lista", "tarefa", "num", "banca", "gabarito", "emed_id",
                      "enunciado", "alternativas", "solucao", "forum", "tags",
                      "estatistica", "capturado_em", "executor")


class ErroLeitura(Exception):
    """Pasta de entrada ausente ou ilegível (exit 1)."""


# ------------------------------------------------------------------ leitura

def pasta_colecao(dir_, colecao):
    """`DIR/<colecao>` se existir; senão o próprio `DIR` (já é a pasta da coleção)."""
    sub = os.path.join(dir_, colecao)
    if os.path.isdir(sub):
        return sub
    if os.path.isdir(dir_):
        return dir_
    raise ErroLeitura(f"pasta nao encontrada: {dir_}")


def ler_docs(dir_, colecao):
    """Lê `*.json` da coleção como `list[dict]` com `_doc_id` (stem do arquivo).

    JSON ilegível vira doc vazio (cai em `invalidas`, não aborta o lote). Arquivos
    `podar_*.json` são saída do `--podar` e ficam de fora.
    """
    pasta = pasta_colecao(dir_, colecao)
    docs = []
    for nome in sorted(os.listdir(pasta)):
        if not nome.endswith(".json") or nome.startswith("podar_"):
            continue
        caminho = os.path.join(pasta, nome)
        try:
            with open(caminho, encoding="utf-8") as fh:
                dado = json.load(fh)
        except (OSError, ValueError):
            dado = {}
        if not isinstance(dado, dict):
            dado = {}
        dado = dict(dado)
        dado["_doc_id"] = nome[:-5]
        docs.append(dado)
    return docs


# ------------------------------------------------------------------ helpers

def _emitir(obj, como_json):
    """Imprime `obj` em JSON (ensure_ascii=False) quando pedido."""
    if como_json:
        print(json.dumps(obj, ensure_ascii=False, indent=2, default=str))


def _upsert_com_rito(writer, docs, args):
    """Dry-run -> COUNT-ASSERT -> (se `--apply`) grava. Devolve (contagem, exit)."""
    medida = writer(docs, aplicar=False)
    mudam = medida["novas"] + medida["atualizadas"]
    if args.expect is not None and mudam != args.expect:
        medida["erro"] = (f"COUNT-ASSERT falhou: novas+atualizadas={mudam}, "
                          f"--expect {args.expect}. Nada gravado.")
        return medida, 2
    if args.apply:
        return writer(docs, aplicar=True), 0
    return medida, 0


def _linha_contagem(cont, aplicado):
    """Linha humana das contagens de um upsert."""
    modo = "APLICADO" if aplicado else "dry-run (nada gravado; use --apply)"
    inv = cont["invalidas"]
    txt = (f"{modo}: novas={cont['novas']} atualizadas={cont['atualizadas']} "
           f"iguais={cont['iguais']} invalidas={len(inv)}")
    if inv:
        txt += "\n  invalidas: " + ", ".join(str(i) for i in inv)
    return txt


def resumo_listas(docs):
    """Resumo por lista das respostas: banco sobreposto pelos docs do lote.

    Acerto = `correta == 1` (chute certo conta no volume e aparece em `chutes`).
    """
    listas = sorted({str(d.get("lista")).strip() for d in docs if d.get("lista")})
    saida = []
    for lista in listas:
        gabs = {q["num"]: q["gabarito"] for q in db.emed_listar_questoes(lista)}
        por_num = {r["num"]: dict(r) for r in db.emed_listar_respostas(lista)}
        for d in docs:
            num = db._int_ou_none(d.get("num"))
            if str(d.get("lista")).strip() != lista or num is None or not d.get("letra"):
                continue
            r = dict(d)
            r["num"] = num
            r["correta"] = db.emed_correta(d, gabs.get(num))
            r["confianca"] = (str(d.get("confianca") or "").strip().lower() or None)
            r["tempo_s"] = db._int_ou_none(d.get("tempo_s"))
            r["tarefa_id"] = db._int_ou_none(d.get("tarefa"))
            antigo = por_num.get(num)
            if antigo and str(d.get("respondido_em") or "") < str(antigo.get("respondido_em") or ""):
                continue
            if antigo and r["tarefa_id"] is None:
                r["tarefa_id"] = antigo.get("tarefa_id")
            por_num[num] = r
        rs = [por_num[n] for n in sorted(por_num)]
        tarefa = next((r.get("tarefa_id") for r in rs if r.get("tarefa_id")), None)
        plano = db.plano_obter(tarefa) if tarefa else None
        tempos = [r["tempo_s"] for r in rs if r.get("tempo_s") is not None]
        saida.append({
            "lista": lista, "tarefa_id": tarefa,
            "area": (plano or {}).get("area"), "tema": (plano or {}).get("tema"),
            "feitas": len(rs),
            "acertos": sum(1 for r in rs if r.get("correta") == 1),
            "solidas": sum(1 for r in rs if r.get("confianca") == "solida"),
            "duvidas": sum(1 for r in rs if r.get("confianca") == "duvida"),
            "chutes": sum(1 for r in rs if r.get("confianca") == "chute"),
            "erradas": [r["num"] for r in rs if r.get("correta") == 0],
            "tempo_medio_s": round(sum(tempos) / len(tempos)) if tempos else None,
        })
    return saida


def texto_resumo(r):
    """As 2 linhas do resumo de uma lista (quadro + comando sugerido)."""
    area = r["area"] or "?"
    tarefa = r["tarefa_id"] if r["tarefa_id"] is not None else "?"
    erradas = ", ".join(str(n) for n in r["erradas"]) or "nenhuma"
    tempo = f"{r['tempo_medio_s']}s" if r["tempo_medio_s"] is not None else "?"
    quadro = (f"{r['lista']} #{tarefa} {area} | feitas {r['feitas']} · acertos {r['acertos']} "
              f"(solidas {r['solidas']}, duvidas {r['duvidas']}, chutes {r['chutes']}) · "
              f"erradas: {erradas} · tempo medio {tempo}")
    cmd = (f'python tools/registrar_sessao_bulk.py --sessao NNN --area "{area}" '
           f"--feitas {r['feitas']} --acertos {r['acertos']} --tarefa {tarefa} "
           f'--obs "EMED {r["lista"]} via Bancada"')
    return quadro + "\n  " + cmd


# ------------------------------------------------------------------ modos

def cmd_ingerir(args):
    """`--ingerir DIR`: upsert das questões em `emed_questoes`."""
    docs = ler_docs(args.ingerir, "questoes")
    cont, code = _upsert_com_rito(db.emed_upsert_questoes, docs, args)
    if args.json:
        _emitir(dict(cont, aplicado=bool(args.apply and code == 0)), True)
    else:
        if code == 2:
            print(cont["erro"])
        print(_linha_contagem(cont, args.apply and code == 0))
    return code


def amostra_leitura(docs, n=2):
    """O que o principal LÊ a olho de um lote de soluções (s201, #7 do /ai-eng): por lista,
    todas as `divergente` + `n` aleatórias entre as outras. A semente é o conjunto de chaves do
    lote, então a mesma entrada dá a mesma amostra (reproduzível no log). PURA."""
    import hashlib
    import random
    por_lista = {}
    for d in docs:
        num = db._int_ou_none(d.get("num"))
        lista = str(d.get("lista") or "").strip()
        if not lista or num is None:
            continue
        g = por_lista.setdefault(lista, {"divergentes": set(), "outras": set()})
        g["divergentes" if db._bool01(d.get("divergente")) else "outras"].add(num)
    saida = {}
    for lista, g in sorted(por_lista.items()):
        outras = sorted(g["outras"] - g["divergentes"])
        semente = hashlib.sha1(f"{lista}:{outras}:{sorted(g['divergentes'])}".encode()).hexdigest()
        sorteio = random.Random(semente).sample(outras, min(n, len(outras)))
        saida[lista] = {"divergentes": sorted(g["divergentes"]), "aleatorias": sorted(sorteio)}
    return saida


def texto_amostra(amostra):
    """`ler a olho: t40 divergentes Q11 · aleatórias Q3, Q7` -- uma linha por lista."""
    linhas = []
    for lista, g in amostra.items():
        partes = [f"divergentes {', '.join(f'Q{x}' for x in g['divergentes'])}" if g["divergentes"] else "",
                  f"aleatórias {', '.join(f'Q{x}' for x in g['aleatorias'])}" if g["aleatorias"] else ""]
        linhas.append(f"ler a olho: {lista} " + " · ".join(p for p in partes if p))
    return linhas


def cmd_solucoes(args):
    """`--solucoes DIR`: upsert da solução própria do hub em `emed_solucoes` (s199). Traz a
    amostra que o principal lê a olho (`amostra_leitura`, s201)."""
    docs = ler_docs(args.solucoes, "solucoes")
    cont, code = _upsert_com_rito(db.emed_upsert_solucoes, docs, args)
    amostra = amostra_leitura(docs)
    if args.json:
        _emitir(dict(cont, aplicado=bool(args.apply and code == 0), leitura=amostra), True)
    else:
        if code == 2:
            print(cont["erro"])
        print(_linha_contagem(cont, args.apply and code == 0))
        for linha in texto_amostra(amostra):
            print(linha)
    return code


def cmd_registrar(args):
    """`--registrar DIR`: upsert das respostas + resumo por lista + comando sugerido."""
    docs = ler_docs(args.registrar, "respostas")
    cont, code = _upsert_com_rito(db.emed_upsert_respostas, docs, args)
    resumos = resumo_listas(docs)
    if args.json:
        _emitir(dict(cont, aplicado=bool(args.apply and code == 0), listas=resumos), True)
    else:
        if code == 2:
            print(cont["erro"])
        print(_linha_contagem(cont, args.apply and code == 0))
        for r in resumos:
            print(texto_resumo(r))
    return code


def cmd_podar(args):
    """`--podar DIR`: lista os doc_id seguros para apagar do artifact (read-only)."""
    docs = ler_docs(args.podar, args.colecao)
    seguros, nao_seguros = [], []
    if args.colecao == "questoes":
        banco = {(q["lista"], q["num"]): q["hash"] for q in db.emed_listar_questoes()}
        for d in docs:
            chave = (str(d.get("lista") or "").strip(), db._int_ou_none(d.get("num")))
            ok = chave in banco and banco[chave] == db.emed_hash_questao(d)
            (seguros if ok else nao_seguros).append(d["_doc_id"])
    else:
        banco = {(r["lista"], r["num"]): r["respondido_em"]
                 for r in db.emed_listar_respostas()}
        for d in docs:
            chave = (str(d.get("lista") or "").strip(), db._int_ou_none(d.get("num")))
            ok = (chave in banco and d.get("respondido_em") is not None
                  and banco[chave] == str(d["respondido_em"]).strip())
            (seguros if ok else nao_seguros).append(d["_doc_id"])
    saida = {"colecao": args.colecao, "ids": seguros, "n": len(seguros),
             "nao_seguros": nao_seguros}
    destino = os.path.join(args.podar, f"podar_{args.colecao}.json")
    with open(destino, "w", encoding="utf-8") as fh:
        json.dump(saida, fh, ensure_ascii=False, indent=2)
    if args.json:
        _emitir(dict(saida, arquivo=destino), True)
    else:
        print(f"podar {args.colecao}: {len(seguros)} seguros, "
              f"{len(nao_seguros)} nao seguros -> {destino}")
    return 0


def doc_lista(lista, n_questoes):
    """Doc `listas/<lista>` para semear o hub: tema/área/semana/url vêm de `plano_tarefas`."""
    st = [s for s in db.emed_status() if s["lista"] == lista]
    tarefa = st[0]["tarefa_id"] if st else db._int_ou_none(lista.lstrip("t"))
    plano = db.plano_obter(tarefa) if tarefa else None
    plano = plano or {}
    return {"tarefa": tarefa, "tema": plano.get("tema") or (st[0]["tema"] if st else None),
            "area": plano.get("area") or (st[0]["area"] if st else None),
            "semana": plano.get("semana_plano"), "seq": plano.get("ordem") or 0,
            "q": n_questoes, "q_previstas": plano.get("q_previstas"),
            "url": plano.get("url_lista"), "status": "capturada",
            "semeada_em": db.carimbo()}


def cmd_exportar(args):
    """`--exportar LISTA`: escreve `OUT/questoes/<lista>_<num>.json` (formato do doc) e
    `OUT/listas/<lista>.json` (cabeçalho da lista), para semear o buffer/hub por ArtifactData."""
    linhas = db.emed_listar_questoes(args.exportar)
    solucoes = {s["num"]: s for s in db.emed_listar_solucoes(args.exportar)}
    pasta = os.path.join(args.out, "questoes")
    os.makedirs(pasta, exist_ok=True)
    pasta_l = os.path.join(args.out, "listas")
    os.makedirs(pasta_l, exist_ok=True)
    with open(os.path.join(pasta_l, f"{args.exportar}.json"), "w", encoding="utf-8") as fh:
        json.dump(doc_lista(args.exportar, len(linhas)), fh, ensure_ascii=False, indent=2)
    for q in linhas:
        doc = {c: q.get("tarefa_id" if c == "tarefa" else c) for c in CAMPOS_DOC_QUESTAO}
        # `extras` volta a ser chaves soltas do doc (formato do artifact); o hash re-deriva igual.
        try:
            doc.update(json.loads(q.get("extras") or "{}"))
        except ValueError:
            pass
        sol = solucoes.get(q["num"])
        if sol:     # s199: a solução do hub viaja no doc; fora do hash e de `extras`
            # s200: a v2 (cadeia de elos) vai como OBJETO -- a página desenha a cadeia e marca
            # o elo em que a letra marcada cai; a v1 segue como texto
            v2 = db.solucao_estruturada(sol["solucao"])
            doc.update(solucao_medhub=v2 if v2 else sol["solucao"],
                       divergente=bool(sol["divergente"]), fontes_medhub=sol["fontes"] or "")
            if sol.get("objetivo"):
                doc["objetivo"] = sol["objetivo"]
        caminho = os.path.join(pasta, f"{q['lista']}_{q['num']}.json")
        with open(caminho, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=2)
    print(f"{len(linhas)} arquivos em {pasta} + listas/{args.exportar}.json")
    return 0


def texto_solucao(texto):
    """A solução do hub em texto corrido: v1 como está; v2 (cadeia) numerada, com a letra de
    cada alternativa errada apontando o elo em que ela cai. PURA."""
    v2 = db.solucao_estruturada(texto)
    if not v2:
        return texto or ""
    linhas = [f"Pede: {v2.get('pede', '')}"]
    for i, e in enumerate(v2.get("cadeia") or [], 1):
        linhas.append(f"{i}. {e.get('elo', '')} -- {e.get('chave', '')}")
    for letra in sorted(v2.get("alternativas") or {}):
        a = v2["alternativas"][letra]
        marca = "certa" if a.get("certa") is True else f"cai no elo {a.get('elo')}"
        linhas.append(f"{letra} ({marca}): {a.get('porque', '')}")
    if v2.get("conferir"):
        linhas.append(f"Conferir: {v2['conferir']}")
    return "\n".join(linhas)


def leitura_metacognitiva(resposta, solucao_texto, letras=None):
    """O rastro metacognitivo de UMA resposta contra a Solução v2 (s200, pedido do operador:
    "as alternativas riscadas e a dúvida entre duas sem dúvida contribuem para a análise"). PURA.

    - `riscadas`: letras que ele eliminou antes de marcar;
    - `restantes`: as que sobraram (na dúvida, o par em que hesitou);
    - `elos_ok`: elos que ele executou -- os de cada letra ERRADA que ele riscou;
    - `elo_letra`: o elo em que a letra marcada cai (None se acertou);
    - `riscou_certa`: eliminou o gabarito -- crença firme contra a resposta, não descuido.
    Sem Solução v2, os elos ficam vazios e o resto segue."""
    risc = [x for x in db.riscadas_norm(resposta.get("riscadas")).split(",") if x]
    v2 = db.solucao_estruturada(solucao_texto) or {}
    alts = v2.get("alternativas") or {}
    todas = sorted(alts) if alts else sorted(letras or [])
    gab = (resposta.get("gabarito") or "").upper()
    letra = (resposta.get("letra") or "").upper()
    elos_ok = sorted({alts[x]["elo"] for x in risc
                      if x in alts and not alts[x].get("certa") and alts[x].get("elo")})
    marcada = alts.get(letra) or {}
    return {"riscadas": risc, "restantes": [x for x in todas if x not in risc],
            "elos_ok": elos_ok,
            "elo_letra": None if marcada.get("certa") or not marcada else marcada.get("elo"),
            "riscou_certa": bool(gab and gab in risc)}


def texto_leitura(m, confianca):
    """A leitura metacognitiva em 1 linha, para o `--erros` e o log. PURA."""
    partes = []
    if m["riscadas"]:
        partes.append("riscou " + ", ".join(m["riscadas"]))
    if confianca == "duvida" and 1 < len(m["restantes"]) <= 3:
        partes.append("ficou entre " + " e ".join(m["restantes"]))
    if m["elos_ok"]:
        partes.append("executou o(s) elo(s) " + ", ".join(str(k) for k in m["elos_ok"]))
    if m["elo_letra"]:
        partes.append(f"a letra marcada cai no elo {m['elo_letra']}")
    if m["riscou_certa"]:
        partes.append("RISCOU A CERTA")
    return "; ".join(partes) or "(sem riscadas)"


def erros_da_lista(lista):
    """Respostas erradas OU chute da lista, cada uma com a questão em íntegra."""
    questoes = {q["num"]: q for q in db.emed_listar_questoes(lista)}
    solucoes = {s["num"]: s for s in db.emed_listar_solucoes(lista)}
    saida = []
    for r in db.emed_listar_respostas(lista):
        if r["correta"] != 0 and r["confianca"] != "chute":
            continue
        q = questoes.get(r["num"], {})
        saida.append({
            "num": r["num"], "banca": q.get("banca"), "letra": r["letra"],
            "gabarito": r["gabarito"] or q.get("gabarito"), "correta": r["correta"],
            "confianca": r["confianca"], "tempo_s": r["tempo_s"],
            "racional": r["racional"], "elo": r["elo"],
            "questao_erro_id": r["questao_erro_id"],
            "enunciado": q.get("enunciado"), "alternativas": q.get("alternativas"),
            "solucao": q.get("solucao"), "forum": q.get("forum"),
            "solucao_medhub": texto_solucao((solucoes.get(r["num"]) or {}).get("solucao")),
            "objetivo": (solucoes.get(r["num"]) or {}).get("objetivo") or "",
            "leitura": leitura_metacognitiva(r, (solucoes.get(r["num"]) or {}).get("solucao"))})
    return saida


def cmd_erros(args):
    """`--erros LISTA`: insumo do /analisar-questao (erradas e chutes, em íntegra)."""
    itens = erros_da_lista(args.erros)
    if args.json:
        _emitir(itens, True)
        return 0
    print(f"{args.erros}: {len(itens)} questoes (erradas ou chute)")
    for e in itens:
        status = "CERTA (chute)" if e["correta"] == 1 else "ERRADA"
        print("=" * 72)
        print(f"Q{e['num']} · {e['banca'] or '?'} · marcou {e['letra']} x gabarito "
              f"{e['gabarito'] or '?'} · {status} · confianca {e['confianca'] or '?'} · "
              f"tempo {e['tempo_s'] if e['tempo_s'] is not None else '?'}s")
        if e["questao_erro_id"] is not None:
            print(f"JA REGISTRADA como erro #{e['questao_erro_id']}")
        print(f"Racional declarado: {e['racional'] or '(vazio)'}")
        print(f"Elo declarado: {e['elo'] or '(vazio)'}")
        print(f"Objetivo: {e['objetivo'] or '(sem)'}")
        print(f"Leitura: {texto_leitura(e['leitura'], e['confianca'])}")
        for rotulo, campo in (("ENUNCIADO", "enunciado"), ("ALTERNATIVAS", "alternativas"),
                              ("SOLUCAO MEDHUB", "solucao_medhub"),
                              ("SOLUCAO", "solucao"), ("FORUM", "forum")):
            print(f"-- {rotulo}\n{e[campo] or '(vazio)'}")
    return 0


def por_objetivo(status, respostas, solucoes):
    """O mapa de fragilidade (s200): respostas agrupadas por (tema do plano, objetivo da
    questão), somando as listas do MESMO tema (t26 + t40 = DMG). PURA.

    Pedido do operador: "as questões eram de DMG, mas tinham objetivos diferentes -- avaliar
    tratamento, seguimento, cutoff de critério -- e isso aponta para as áreas com maior
    fragilidade". Chute certo NÃO conta como firme (é incerteza); questão sem objetivo
    cunhado cai em "(sem objetivo)", visível, nunca some."""
    tema_de = {s["lista"]: s["tema"] or s["lista"] for s in status}
    obj_de = {(s["lista"], s["num"]): s.get("objetivo") or "" for s in solucoes}
    grupos = {}
    for r in respostas:
        chave = (tema_de.get(r["lista"], r["lista"]),
                 obj_de.get((r["lista"], r["num"])) or "(sem objetivo)")
        g = grupos.setdefault(chave, {"tema": chave[0], "objetivo": chave[1], "feitas": 0,
                                      "firmes": 0, "chutes_certos": 0, "erradas": []})
        g["feitas"] += 1
        if r["correta"] == 1 and r["confianca"] != "chute":
            g["firmes"] += 1
        elif r["correta"] == 1:
            g["chutes_certos"] += 1
        else:
            g["erradas"].append(f"{r['lista']} Q{r['num']}")
    return sorted(grupos.values(), key=lambda g: (g["tema"], g["firmes"] / g["feitas"],
                                                  g["objetivo"]))


def cmd_status(args):
    """`--status`: tabela por lista de `emed_status()` (filtro `--lista`); com
    `--por-objetivo`, o mapa de fragilidade por tema e objetivo (`por_objetivo`)."""
    if args.por_objetivo:
        st = db.emed_status()
        listas = {s["lista"] for s in st if not args.lista or s["lista"] == args.lista}
        grupos = por_objetivo(st, [r for r in db.emed_listar_respostas() if r["lista"] in listas],
                              db.emed_listar_solucoes())
        if args.json:
            _emitir(grupos, True)
            return 0
        print("tema | objetivo | firmes/feitas | chutes certos | erradas")
        for g in grupos:
            print(f"{g['tema']} | {g['objetivo']} | {g['firmes']}/{g['feitas']} | "
                  f"{g['chutes_certos']} | {', '.join(g['erradas']) or '-'}")
        return 0
    linhas = [s for s in db.emed_status() if not args.lista or s["lista"] == args.lista]
    if args.json:
        _emitir(linhas, True)
        return 0
    if not linhas:
        print("nenhuma lista no banco EMED")
        return 0
    print("lista | tarefa | area | tema | capt | resp | acertos | sol/duv/chu | erradas | tempo")
    for s in linhas:
        print(f"{s['lista']} | {s['tarefa_id'] or '-'} | {s['area'] or '-'} | "
              f"{s['tema'] or '-'} | {s['capturadas']} | {s['respondidas']} | "
              f"{s['acertos']} | {s['solidas']}/{s['duvidas']}/{s['chutes']} | "
              f"{s['erradas']} | "
              f"{s['tempo_medio_s'] if s['tempo_medio_s'] is not None else '-'}")
    return 0


def main(argv=None):
    """Ponto de entrada: exatamente UM modo por chamada."""
    ap = argparse.ArgumentParser(
        description="Banco de questoes EMED no ipub.db (Bancada EMED): ingerir, "
                    "registrar, solucoes, podar, exportar, erros, status.")
    ap.add_argument("--ingerir", metavar="DIR", help="upsert de DIR/questoes/*.json")
    ap.add_argument("--registrar", metavar="DIR", help="upsert de DIR/respostas/*.json")
    ap.add_argument("--solucoes", metavar="DIR",
                    help="upsert de DIR/solucoes/*.json (solucao propria do hub, s199)")
    ap.add_argument("--podar", metavar="DIR",
                    help="lista os doc_id seguros para apagar do artifact (read-only)")
    ap.add_argument("--colecao", choices=["questoes", "respostas"], default="questoes",
                    help="colecao alvo do --podar (default questoes)")
    ap.add_argument("--exportar", metavar="LISTA", help="re-semeia OUT/questoes/*.json")
    ap.add_argument("--out", metavar="DIR", default=OUT_PADRAO,
                    help="pasta de saida do --exportar (default tmp/emed_export)")
    ap.add_argument("--erros", metavar="LISTA",
                    help="erradas e chutes da lista em integra (insumo do /analisar-questao)")
    ap.add_argument("--status", action="store_true", help="resumo por lista")
    ap.add_argument("--lista", metavar="LISTA", help="filtro do --status")
    ap.add_argument("--por-objetivo", dest="por_objetivo", action="store_true",
                    help="com --status: acerto por tema e objetivo da questao (s200)")
    ap.add_argument("--apply", action="store_true", help="grava (default = dry-run)")
    ap.add_argument("--expect", type=int, metavar="N",
                    help="COUNT-ASSERT: novas+atualizadas deve ser N, senao exit 2")
    ap.add_argument("--json", action="store_true", help="saida em JSON")
    args = ap.parse_args(argv)

    modos = {"--ingerir": args.ingerir, "--registrar": args.registrar,
             "--solucoes": args.solucoes,
             "--podar": args.podar, "--exportar": args.exportar,
             "--erros": args.erros, "--status": args.status}
    ligados = [m for m, v in modos.items() if v]
    if len(ligados) != 1:
        print("erro: informe exatamente UM modo (" + " | ".join(modos) + ")",
              file=sys.stderr)
        return 1
    acao = {"--ingerir": cmd_ingerir, "--registrar": cmd_registrar,
            "--solucoes": cmd_solucoes,
            "--podar": cmd_podar, "--exportar": cmd_exportar,
            "--erros": cmd_erros, "--status": cmd_status}[ligados[0]]
    try:
        return acao(args)
    except ErroLeitura as e:
        print(f"erro: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
