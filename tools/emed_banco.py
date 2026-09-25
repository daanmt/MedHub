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


def cmd_exportar(args):
    """`--exportar LISTA`: escreve `OUT/questoes/<lista>_<num>.json` no formato do doc."""
    linhas = db.emed_listar_questoes(args.exportar)
    pasta = os.path.join(args.out, "questoes")
    os.makedirs(pasta, exist_ok=True)
    for q in linhas:
        doc = {c: q.get("tarefa_id" if c == "tarefa" else c) for c in CAMPOS_DOC_QUESTAO}
        caminho = os.path.join(pasta, f"{q['lista']}_{q['num']}.json")
        with open(caminho, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=2)
    print(f"{len(linhas)} arquivos em {pasta}")
    return 0


def erros_da_lista(lista):
    """Respostas erradas OU chute da lista, cada uma com a questão em íntegra."""
    questoes = {q["num"]: q for q in db.emed_listar_questoes(lista)}
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
            "enunciado": q.get("enunciado"), "alternativas": q.get("alternativas"),
            "solucao": q.get("solucao"), "forum": q.get("forum")})
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
        print(f"Racional declarado: {e['racional'] or '(vazio)'}")
        print(f"Elo declarado: {e['elo'] or '(vazio)'}")
        for rotulo, campo in (("ENUNCIADO", "enunciado"), ("ALTERNATIVAS", "alternativas"),
                              ("SOLUCAO", "solucao"), ("FORUM", "forum")):
            print(f"-- {rotulo}\n{e[campo] or '(vazio)'}")
    return 0


def cmd_status(args):
    """`--status`: tabela por lista de `emed_status()` (filtro `--lista`)."""
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
                    "registrar, podar, exportar, erros, status.")
    ap.add_argument("--ingerir", metavar="DIR", help="upsert de DIR/questoes/*.json")
    ap.add_argument("--registrar", metavar="DIR", help="upsert de DIR/respostas/*.json")
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
    ap.add_argument("--apply", action="store_true", help="grava (default = dry-run)")
    ap.add_argument("--expect", type=int, metavar="N",
                    help="COUNT-ASSERT: novas+atualizadas deve ser N, senao exit 2")
    ap.add_argument("--json", action="store_true", help="saida em JSON")
    args = ap.parse_args(argv)

    modos = {"--ingerir": args.ingerir, "--registrar": args.registrar,
             "--podar": args.podar, "--exportar": args.exportar,
             "--erros": args.erros, "--status": args.status}
    ligados = [m for m, v in modos.items() if v]
    if len(ligados) != 1:
        print("erro: informe exatamente UM modo (" + " | ".join(modos) + ")",
              file=sys.stderr)
        return 1
    acao = {"--ingerir": cmd_ingerir, "--registrar": cmd_registrar,
            "--podar": cmd_podar, "--exportar": cmd_exportar,
            "--erros": cmd_erros, "--status": cmd_status}[ligados[0]]
    try:
        return acao(args)
    except ErroLeitura as e:
        print(f"erro: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
