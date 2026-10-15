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
    python tools/emed_banco.py --exportar t61 --sem-cadeia "motivo declarado"
    python tools/emed_banco.py --exportar t40 --so-figuras --out tmp/emed_export
    python tools/emed_banco.py --figuras tmp/emed_api/t40
    python tools/emed_banco.py --figuras tmp/emed_api/t40 --apply --expect 5
    python tools/emed_banco.py --reavaliar-sem-figura
    python tools/emed_banco.py --reavaliar-sem-figura --apply --expect 20
    python tools/emed_banco.py --erros t26
    python tools/emed_banco.py --elos t26 --json
    python tools/emed_banco.py --defeitos
    python tools/emed_banco.py --status --lista t26 --json
    python tools/emed_banco.py --referencias
    python tools/emed_banco.py --amostra-referencias 9a5963f
    python tools/emed_banco.py --referencias --regua tmp/lote2/amostra-9a5963f.json
    python tools/emed_banco.py --referencias --apply --expect 12 --regua tmp/lote2/amostra-9a5963f.json
    python tools/emed_banco.py --status --fontes --lista t26

Camada fina sobre `app.utils.db` -- não abre `sqlite3` próprio; toda escrita passa por
`emed_upsert_questoes` / `emed_upsert_respostas`.
Exit: 0 ok; 1 erro de uso/leitura; 2 COUNT-ASSERT falhou; 3 PARA da regua (part 2.3:
`--referencias --apply --regua ARQ` com veredito PARA -- nada gravado, nem o fixado).
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils import db  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import emed_api  # noqa: E402  (s219: a regra do spoiler UERJ e a mesma da importacao)

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


def _fixar_antes(ato):
    """F137 parte 2: o ponto de retorno FIXADO do proprio inicio do ato (`backup_db`). Levanta
    `SemPontoDeRetorno` quando nao ha -- quem chama RECUSA e nada e gravado."""
    _tools = os.path.dirname(os.path.abspath(__file__))
    if _tools not in sys.path:
        sys.path.insert(0, _tools)
    import backup_db
    return backup_db.fixar_antes_do_ato(ato, db=db.DB_PATH, out=lambda *_: None)


def _upsert_com_rito(writer, docs, args):
    """Dry-run -> COUNT-ASSERT -> (se `--apply`) grava. Devolve (contagem, exit).

    F137 parte 2: `--apply` que SOBRESCREVE (`atualizadas` > 0) so roda depois do backup FIXADO do
    proprio inicio; sem ele, recusa (exit 1) e nada e gravado. So `novas` nao e ato destrutivo."""
    medida = writer(docs, aplicar=False)
    mudam = medida["novas"] + medida["atualizadas"]
    if args.expect is not None and mudam != args.expect:
        medida["erro"] = (f"COUNT-ASSERT falhou: novas+atualizadas={mudam}, "
                          f"--expect {args.expect}. Nada gravado.")
        return medida, 2
    if args.apply:
        fixado = None
        if medida["atualizadas"]:
            try:
                fixado = _fixar_antes(f"emed_banco {writer.__name__}: "
                                      f"{medida['atualizadas']} atualizada(s) sobrescrita(s)")
            except Exception as e:  # noqa: BLE001 -- qualquer falha do ponto de retorno = recusa
                medida["erro"] = f"sem ponto de retorno FIXADO (F137): {e}. Nada gravado."
                return medida, 1
        cont = writer(docs, aplicar=True)
        if fixado:
            cont["fixado"] = {"arquivo": fixado["arquivo"], "sha256": fixado["sha256"]}
        return cont, 0
    return medida, 0


def _linha_contagem(cont, aplicado):
    """Linha humana das contagens de um upsert."""
    modo = "APLICADO" if aplicado else "dry-run (nada gravado; use --apply)"
    inv = cont["invalidas"]
    txt = (f"{modo}: novas={cont['novas']} atualizadas={cont['atualizadas']} "
           f"iguais={cont['iguais']} invalidas={len(inv)}")
    if inv:
        txt += "\n  invalidas: " + ", ".join(str(i) for i in inv)
    if cont.get("fixado"):
        txt += (f"\n  FIXADO antes do ato (ponto de retorno; arquivo + sha256 vao para o ledger): "
                f"{cont['fixado']['arquivo']} sha256 {cont['fixado']['sha256']}")
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
        if cont.get("erro"):
            print(cont["erro"])
        print(_linha_contagem(cont, args.apply and code == 0))
    return code


def mapa_figuras(docs):
    """`{emed_id: {chaves de figura}}` dos docs da recaptura (`emed_api --apply`), so dos que trazem
    ALGUMA chave de figura: doc sem nenhuma nao apaga a marca que o banco ja tem (1.1a). PURA."""
    mapa = {}
    for d in docs:
        emed_id = str(d.get("emed_id") or "").strip()
        figs = {k: d[k] for k in db.CHAVES_FIGURA_EMED if d.get(k) not in (None, "", False, [], {})}
        if emed_id and figs:
            mapa[emed_id] = figs
    return mapa


def mesclar_figuras(mapa, aplicar=True):
    """`db.emed_mesclar_figuras` na forma que o `_upsert_com_rito` le (`novas` 0: a mescla nunca cria)."""
    cont = db.emed_mesclar_figuras(mapa, aplicar=aplicar)
    return dict(cont, novas=0, invalidas=cont.get("invalidas", []))


def cmd_figuras(args):
    """`--figuras DIR`: mescla ESTREITA das chaves de figura da recaptura (DIR/questoes/*.json do
    `emed_api --apply`) nas linhas que ja existem, por `emed_id` (1.1a). Dry-run por padrao; `--apply`
    exige `--expect N` (o `atualizadas` do dry-run) e fixa o backup quando ha `atualizadas`."""
    if args.apply and args.expect is None:
        print("RECUSA: --figuras --apply exige --expect N (o `atualizadas` medido no dry-run). Nada gravado.")
        return 1
    mapa = mapa_figuras(ler_docs(args.figuras, "questoes"))
    cont, code = _upsert_com_rito(mesclar_figuras, mapa, args)
    if args.json:
        _emitir(dict(cont, aplicado=bool(args.apply and code == 0)), True)
        return code
    if cont.get("erro"):
        print(cont["erro"])
    print(_linha_contagem(cont, args.apply and code == 0))
    print(f"  ausentes (emed_id sem linha no banco; nada criado): {cont['ausentes'] or '-'}")
    return code


def _cita_figura(enunciado):
    """A regra VIGENTE de `sem_figura` (`emed_api.CITA_FIGURA`, hotfix 1.1b DoD 5) como bool."""
    _tools = os.path.dirname(os.path.abspath(__file__))
    if _tools not in sys.path:
        sys.path.insert(0, _tools)
    import emed_api
    return bool(emed_api.CITA_FIGURA.search(enunciado or ""))


def reavaliar_sem_figura(cita, aplicar=True):
    """`db.emed_reavaliar_sem_figura` na forma que o `_upsert_com_rito` le (`novas` 0: nunca cria)."""
    cont = db.emed_reavaliar_sem_figura(cita, aplicar=aplicar)
    return dict(cont, novas=0, invalidas=cont.get("invalidas", []))


def cmd_reavaliar_sem_figura(args):
    """`--reavaliar-sem-figura` (hotfix 1.1b DoD 5): re-roda a regra vigente sobre o enunciado das
    linhas com `sem_figura` e sem `figuras`, e tira a marca de quem ela nao marca mais (so essa chave
    de `extras`, e o `hash`). Dry-run por padrao; `--apply` exige `--expect N` e fixa o backup."""
    if args.apply and args.expect is None:
        print("RECUSA: --reavaliar-sem-figura --apply exige --expect N (o `atualizadas` do dry-run). "
              "Nada gravado.")
        return 1
    cont, code = _upsert_com_rito(reavaliar_sem_figura, _cita_figura, args)
    if args.json:
        _emitir(dict(cont, aplicado=bool(args.apply and code == 0)), True)
        return code
    if cont.get("erro"):
        print(cont["erro"])
    print(_linha_contagem(cont, args.apply and code == 0))
    print(f"  sem_figura retirado (lista_num): {', '.join(cont['listas']) or '-'}")
    print(f"  ainda marcadas pela regra nova: {cont['iguais']}")
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
        if cont.get("erro"):
            print(cont["erro"])
        print(_linha_contagem(cont, args.apply and code == 0))
        for linha in texto_amostra(amostra):
            print(linha)
    return code


# ------------------------------------------------------------------ amostra e régua das fontes (2.3)

#: Fase 0 Lote 2 part 2.3 (M-031): o arquivo da amostra fica SÓ aqui, dentro de `tmp/` (gitignored,
#: `.gitignore:66`): o conteúdo das Soluções é IP do EMED e o repo é público (TD 6). Os testes a apontam
#: para `tmp_path`.
PASTA_AMOSTRA = os.path.join(ROOT, "tmp", "lote2")
#: A régua de parada do apply do estoque: PARA quando `p` ou `a` passa ESTRITAMENTE deste limite.
REGUA_LIMITE = 0.10
#: Acima desta fração de `nota` (por ocorrência) sai um achado de CONTEÚDO (M-024/M-025), nunca PARA.
NOTA_ACHADO = 0.30
#: O vocabulário fechado da triagem: `ok` e `impreciso` não contam; `mal_atribuido:<campo>` conta.
CAMPOS_MAL_ATRIBUIDO = ("sigla", "ano", "documento", "tipo", "nao_referencia")
VEREDITOS = ("ok", "impreciso") + tuple(f"mal_atribuido:{c}" for c in CAMPOS_MAL_ATRIBUIDO)
#: As siglas que o parser DERIVA (R4); a D1 não as procura no rótulo.
SIGLAS_DERIVADAS = ("MEDHUB", "EMED")
RE_SEMENTE = re.compile(r"[0-9a-f]{7}")
#: O token de veredito da triagem: `lista_num#ordem=veredito[:campo]` (ex.: `t26_3#2=ok`).
RE_TOKEN_VEREDITO = re.compile(r"(?P<lista>\S+)_(?P<num>\d+)#(?P<ordem>\d+)=(?P<veredito>\S+)")


def _sha1_fontes(fontes):
    """sha1 do `fontes` como está no banco (None = "")."""
    import hashlib
    return hashlib.sha1(("" if fontes is None else str(fontes)).encode("utf-8")).hexdigest()


def amostra_referencias(solucoes, semente, por_lista=2):
    """O sorteio da amostra das fontes (part 2.3, DoD 2), PURO. Por lista, entre as Soluções com `fontes`
    não vazio (>= 1 rótulo no corte R0): `random.Random(f"{semente}:{lista}").sample(sorted(nums),
    min(por_lista, n))`. A semente por lista isola as listas (acrescentar uma não muda as outras); sem
    relógio nem estado global. Devolve `{listas: {lista: [num, ...]}, curtas: {lista: n}}`; em `curtas`
    fica a lista com menos de `por_lista` Soluções com fonte (ela entra com o que tem)."""
    import random
    por = {}
    for s in solucoes:
        num = db._int_ou_none(s.get("num"))
        lista = str(s.get("lista") or "").strip()
        if lista and num is not None and db.fonte_rotulos(s.get("fontes")):
            por.setdefault(lista, set()).add(num)
    listas, curtas = {}, {}
    for lista in sorted(por):
        nums = sorted(por[lista])
        listas[lista] = sorted(random.Random(f"{semente}:{lista}").sample(nums, min(por_lista, len(nums))))
        if len(nums) < por_lista:
            curtas[lista] = len(nums)
    return {"listas": listas, "curtas": curtas}


def _tokens_d1(texto):
    """Os tokens da D1: cada sequência máxima de letras ou de dígitos, em casefold (`SBX2019` dá `sbx` e
    `2019`; pontuação e parênteses não contam)."""
    return re.findall(r"[^\W\d_]+|\d+", str(texto).casefold())


def d1_ida_e_volta(rotulo, parse):
    """D1, a ida e volta do rótulo `ok` (part 2.3, DoD 3), PURA. Os tokens de `sigla` (salvo MEDHUB e EMED,
    que o parser deriva), de `ano` e de `documento` precisam aparecer, cada campo em ordem e em casefold,
    entre os tokens do rótulo (subsequência). Devolve None (passa) ou o 1º campo que falha."""
    toks = _tokens_d1(rotulo)
    for campo in ("sigla", "ano", "documento"):
        valor = parse.get(campo)
        if valor is None or (campo == "sigla" and str(valor) in SIGLAS_DERIVADAS):
            continue
        resto = iter(toks)
        if not all(tok in resto for tok in _tokens_d1(valor)):
            return campo
    return None


def amostra_arquivo(solucoes, semente_hex, por_lista=2):
    """O conteúdo do `amostra-<hex>.json` (part 2.3, DoD 3), PURO. Traz a semente (o hex gravado e o
    `int(hex, 16)` que sorteia) e, por Solução sorteada, `lista`, `num`, `sha1_fontes` e os rótulos:
    `ordem`, `rotulo`, o parse inteiro (`db.fonte_estruturada`), `d1` (`ok` / `falha:<campo>`; nulo fora
    de `ok`), `veredito` e `origem`. A D1 que falha já dá `mal_atribuido:<campo>` com `origem: D1`; o
    resto nasce nulo, para a triagem."""
    semente = int(semente_hex, 16)
    sorteio = amostra_referencias(solucoes, semente, por_lista)
    por_chave = {(str(s.get("lista") or "").strip(), db._int_ou_none(s.get("num"))): s for s in solucoes}
    saida = []
    for lista, nums in sorteio["listas"].items():
        for num in nums:
            fontes = por_chave[(lista, num)].get("fontes")
            rotulos = []
            for ordem, rotulo in enumerate(db.fonte_rotulos(fontes), 1):
                parse = db.fonte_estruturada(rotulo)
                d1 = veredito = origem = None
                if parse["status"] == "ok":
                    campo = d1_ida_e_volta(rotulo, parse)
                    d1 = f"falha:{campo}" if campo else "ok"
                    if campo:
                        veredito, origem = f"mal_atribuido:{campo}", "D1"
                rotulos.append({"ordem": ordem, "rotulo": rotulo, "parse": parse, "d1": d1,
                                "veredito": veredito, "origem": origem})
            saida.append({"lista": lista, "num": num, "sha1_fontes": _sha1_fontes(fontes), "rotulos": rotulos})
    return {"semente": semente_hex, "semente_int": semente, "por_lista": por_lista,
            "curtas": sorteio["curtas"], "token": "lista_num#ordem=veredito[:campo]",
            "vocabulario": list(VEREDITOS), "solucoes": saida}


def aplicar_vereditos(amostra, tokens):
    """A entrada dos vereditos da triagem no `amostra-<hex>.json` (part 2.3), PURA: devolve (uma cópia da
    amostra com os vereditos, `{aplicados, recusados: [(token, motivo)]}`).

    Token = `lista_num#ordem=veredito[:campo]` (ex.: `t26_3#2=ok`, `t26_3#1=mal_atribuido:documento`), no
    vocabulário fechado `VEREDITOS`. O aplicado ganha `origem: triagem`. Recusas: `forma`, `vocabulario`,
    `fora_da_amostra`, `d1_manda` (a D1 manda no veredito do campo dela), `nota_so_nao_referencia` (em
    `nota`, só `mal_atribuido:nao_referencia` conta) e `duplicado_divergente` (o mesmo rótulo com outro
    veredito no mesmo lote: vale o 1º)."""
    import copy
    nova = copy.deepcopy(amostra)
    idx = {}
    for s in nova.get("solucoes") or []:
        for r in s.get("rotulos") or []:
            idx[(str(s.get("lista")), db._int_ou_none(s.get("num")), db._int_ou_none(r.get("ordem")))] = r
    vistos, aplicados, recusados = {}, 0, []
    for token in tokens:
        token = str(token).strip()
        if not token:
            continue
        m = RE_TOKEN_VEREDITO.fullmatch(token)
        if not m:
            recusados.append((token, "forma"))
            continue
        v, chave = m["veredito"], (m["lista"], int(m["num"]), int(m["ordem"]))
        r = idx.get(chave)
        if v not in VEREDITOS:
            motivo = "vocabulario"
        elif r is None:
            motivo = "fora_da_amostra"
        elif r.get("origem") == "D1" and v != r.get("veredito"):
            motivo = "d1_manda"
        elif ((r.get("parse") or {}).get("classe") == "nota" and v.startswith("mal_atribuido:")
              and v != "mal_atribuido:nao_referencia"):
            motivo = "nota_so_nao_referencia"
        elif vistos.get(chave, v) != v:
            motivo = "duplicado_divergente"
        else:
            motivo = None
        if motivo:
            recusados.append((token, motivo))
            continue
        vistos[chave] = v
        if r.get("origem") != "D1":
            r["veredito"], r["origem"] = v, "triagem"
        aplicados += 1
    return nova, {"aplicados": aplicados, "recusados": recusados}


def _taxa(num, den):
    """`num/den` em %, 1 casa (0.0 sem denominador)."""
    return round(100 * num / den, 1) if den else 0.0


def _passa(num, den, limite):
    """`num/den > limite`, ESTRITO e exato (sem erro de float: 1/10 não passa de 0,10)."""
    from fractions import Fraction
    return Fraction(num, den) > Fraction(str(limite))


def regua_referencias(populacao, amostra):
    """A régua de parada do apply do estoque (part 2.3, DoD 4), PURA. Mede o PARSER só sobre `classe =
    citacao` (TD 2): a `nota` fica fora de `p` e de `a` e sai à parte (`n_nota`, `pct_nota`).

    `populacao` = linhas de `emed_solucoes` (`lista`, `num`, `fontes`), lidas do banco NO ATO; `amostra` =
    o `amostra-<hex>.json` triado. `p` = citações fora de `ok` / citações da população. `a` = (citações da
    amostra fora de `ok` + `ok` com `mal_atribuido:*` ou com a D1 falhando + `nota` marcada
    `mal_atribuido:nao_referencia`) / citações da amostra. Os dois saem como `(num, den)`.

    PARA quando: `p` ou `a` > `REGUA_LIMITE` (estrito); a taxa não tem denominador; um rótulo `ok` da
    amostra está sem veredito ("triagem incompleta"); há veredito fora do vocabulário; uma Solução da
    amostra tem o `fontes` mudado ou ausente, ou o parse mudado, desde o sorteio ("amostra velha": parser
    alterado queima a semente, TD 3). `nota` > `NOTA_ACHADO` vai para `achados` (conteúdo, M-024/M-025),
    nunca para PARA. Devolve `{veredito, motivos, p, a, p_distinto, n_nota, pct_nota, nota_solucao,
    rotulos, solucoes_amostra, histograma, achados, semente}`."""
    from collections import Counter
    pop_cit = pop_nok = pop_rot = pop_nota = sol_com = sol_nota = 0
    distintos, atuais = {}, {}
    for s in populacao:
        rotulos = db.fonte_rotulos(s.get("fontes"))
        parses = [db.fonte_estruturada(x) for x in rotulos]
        chave = (str(s.get("lista") or "").strip(), db._int_ou_none(s.get("num")))
        atuais[chave] = (_sha1_fontes(s.get("fontes")), list(zip(rotulos, parses)))
        if rotulos:
            sol_com += 1
            sol_nota += any(e["classe"] == "nota" for e in parses)
        for rotulo, e in zip(rotulos, parses):
            pop_rot += 1
            if e["classe"] == "nota":
                pop_nota += 1
                continue
            pop_cit += 1
            pop_nok += e["status"] != "ok"
            distintos[" ".join(rotulo.split()).casefold()] = e["status"] != "ok"
    sols = amostra.get("solucoes") if isinstance(amostra, dict) else None
    sols = [s for s in sols if isinstance(s, dict)] if isinstance(sols, list) else []
    hist = Counter()
    am_cit = am_def = am_rot = am_nota = am_sol_nota = sem_veredito = fora_vocab = velhas = parse_mudou = 0
    for s in sols:
        rotulos = [r for r in s.get("rotulos") or [] if isinstance(r, dict)]
        atual = atuais.get((str(s.get("lista") or "").strip(), db._int_ou_none(s.get("num"))))
        if atual is None or atual[0] != s.get("sha1_fontes"):
            velhas += 1
        elif [(r.get("rotulo"), r.get("parse")) for r in rotulos] != atual[1]:
            parse_mudou += 1
        am_sol_nota += any((r.get("parse") or {}).get("classe") == "nota" for r in rotulos)
        for r in rotulos:
            e, v = r.get("parse") or {}, r.get("veredito")
            am_rot += 1
            valido = v is None or v in VEREDITOS
            fora_vocab += not valido
            if e.get("classe") == "nota":
                am_nota += 1
                am_def += v == "mal_atribuido:nao_referencia"
                hist["nota" if v in (None, "ok", "impreciso") else
                     f"nota:{v if valido else 'fora_do_vocabulario'}"] += 1
                continue
            am_cit += 1
            if e.get("status") != "ok":
                am_def += 1
                hist[f"{e.get('status')}:{e.get('motivo')}"] += 1
                continue
            sem_veredito += v is None
            mal = valido and str(v or "").startswith("mal_atribuido:")
            d1 = d1_ida_e_volta(r.get("rotulo") or "", e)
            am_def += mal or d1 is not None
            if d1 is not None and not mal:
                hist[f"mal_atribuido:{d1}"] += 1           # a D1 manda no campo dela
            else:
                hist[v if valido and v else ("sem_veredito" if v is None else "fora_do_vocabulario")] += 1
    p, a = (pop_nok, pop_cit), (am_def, am_cit)
    motivos, achados = [], []
    for nome, (num, den), onde in (("p", p, "populacao"), ("a", a, "amostra")):
        if not den:
            motivos.append(f"{nome} sem citacao na {onde}: taxa indefinida")
        elif _passa(num, den, REGUA_LIMITE):
            motivos.append(f"{nome} {num}/{den} ({_taxa(num, den)}%) > {round(100 * REGUA_LIMITE)}%")
    if sem_veredito:
        motivos.append(f"triagem incompleta: {sem_veredito} rotulo(s) ok sem veredito")
    if fora_vocab:
        motivos.append(f"veredito fora do vocabulario: {fora_vocab}")
    if velhas:
        motivos.append(f"amostra velha: {velhas} Solucao(oes) com fontes mudado ou ausente desde o sorteio")
    if parse_mudou:
        motivos.append(f"amostra velha: o parse de {parse_mudou} Solucao(oes) mudou desde o sorteio "
                       f"(parser alterado = semente queimada)")
    for onde, num, den in (("populacao", pop_nota, pop_rot), ("amostra", am_nota, am_rot)):
        if den and _passa(num, den, NOTA_ACHADO):
            achados.append(f"nota {num}/{den} ({_taxa(num, den)}%) > {round(100 * NOTA_ACHADO)}% na {onde}: "
                           f"achado de conteudo (M-024/M-025), nao PARA")
    return {"veredito": "PARA" if motivos else "SEGUE", "motivos": motivos, "p": p, "a": a,
            "p_distinto": (sum(distintos.values()), len(distintos)),
            "n_nota": {"populacao": pop_nota, "amostra": am_nota},
            "pct_nota": {"populacao": _taxa(pop_nota, pop_rot), "amostra": _taxa(am_nota, am_rot)},
            "nota_solucao": {"populacao": (sol_nota, sol_com), "amostra": (am_sol_nota, len(sols))},
            "rotulos": {"populacao": pop_rot, "amostra": am_rot}, "solucoes_amostra": len(sols),
            "histograma": dict(sorted(hist.items())), "achados": achados,
            "semente": amostra.get("semente") if isinstance(amostra, dict) else None}


def _linhas_regua(r):
    """As linhas da régua no `--referencias --regua` (part 2.3): veredito, `p` e `a` (num/den), nota à
    parte, os motivos de PARA, os achados e o histograma da amostra. Só contagens e nomes de regra."""
    def fr(par):
        return f"{par[0]}/{par[1]} ({_taxa(*par)}%)"
    pn, an = r["nota_solucao"]["populacao"], r["nota_solucao"]["amostra"]
    linhas = [f"regua (semente {r['semente']}): {r['veredito']}",
              f"  p (populacao, so citacao): {fr(r['p'])} | por distinto: {fr(r['p_distinto'])}",
              f"  a (amostra, so citacao): {fr(r['a'])} | Solucoes {r['solucoes_amostra']}, "
              f"rotulos {r['rotulos']['amostra']}",
              f"  nota: populacao {fr((r['n_nota']['populacao'], r['rotulos']['populacao']))}, Solucoes {fr(pn)}"
              f" | amostra {fr((r['n_nota']['amostra'], r['rotulos']['amostra']))}, Solucoes {fr(an)}"]
    linhas += [f"  PARA: {m}" for m in r["motivos"]]
    linhas += [f"  achado: {m}" for m in r["achados"]]
    linhas += [f"  regua {k}: {n}" for k, n in r["histograma"].items()]
    return "\n".join(linhas)


def _regua_do_arquivo(caminho):
    """A régua (`regua_referencias`) sobre o `--regua ARQ` e as Soluções lidas do banco NO ATO."""
    try:
        with open(caminho, encoding="utf-8") as fh:
            amostra = json.load(fh)
    except (OSError, ValueError) as e:
        raise ErroLeitura(f"--regua ilegivel: {caminho} ({e.__class__.__name__})")
    return regua_referencias(db.emed_listar_solucoes(), amostra)


def cmd_amostra_referencias(args):
    """`--amostra-referencias HEX` (part 2.3, DoD 3): sorteia até 2 Soluções com fonte por lista com a
    semente `int(HEX, 16)` (HEX = o hash de 7 caracteres do commit que congelou o parser) e escreve SÓ
    `PASTA_AMOSTRA/amostra-<hex>.json` (gitignored). Só lê o banco. Não sobrescreve uma amostra que já
    existe: a triagem gravada nela se perderia."""
    hexa = (args.amostra_referencias or "").strip().lower()
    if not RE_SEMENTE.fullmatch(hexa):
        print("erro: --amostra-referencias exige a semente = hex de 7 caracteres (git log -1 --format=%h)",
              file=sys.stderr)
        return 1
    destino = os.path.join(PASTA_AMOSTRA, f"amostra-{hexa}.json")
    if os.path.exists(destino):
        print(f"RECUSA: {destino} ja existe (a triagem gravada nele se perderia). Nada escrito.")
        return 1
    am = amostra_arquivo(db.emed_listar_solucoes(), hexa)
    os.makedirs(PASTA_AMOSTRA, exist_ok=True)
    with open(destino, "w", encoding="utf-8") as fh:
        json.dump(am, fh, ensure_ascii=False, indent=1)
    rots = [r for s in am["solucoes"] for r in s["rotulos"]]
    cont = {"arquivo": destino, "semente": hexa, "listas": len({s["lista"] for s in am["solucoes"]}),
            "curtas": len(am["curtas"]), "solucoes": len(am["solucoes"]), "rotulos": len(rots),
            "ok": sum(1 for r in rots if r["parse"]["status"] == "ok"),
            "nota": sum(1 for r in rots if r["parse"]["classe"] == "nota"),
            "d1_falhas": sum(1 for r in rots if r["origem"] == "D1")}
    if args.json:
        _emitir(cont, True)
        return 0
    print(f"amostra-referencias {hexa}: listas={cont['listas']} curtas={cont['curtas']} "
          f"solucoes={cont['solucoes']} rotulos={cont['rotulos']} ok={cont['ok']} nota={cont['nota']} "
          f"d1_falhas={cont['d1_falhas']}\n  -> {destino} (triagem: tokens lista_num#ordem=veredito[:campo])")
    return 0


def _linha_referencias(c, aplicado):
    """As contagens do `--referencias` (part 2.1): a linha de rótulos, a de Soluções, o `nao_ok` e o
    histograma de `motivo`."""
    modo = "APLICADO" if aplicado else "dry-run (nada gravado; use --apply --expect N --regua ARQ)"
    nao_ok = c["nao_referencia"] + c["sem_parse"]
    pct = round(100 * nao_ok / c["rotulos"], 1) if c["rotulos"] else 0.0
    linhas = [f"{modo}: solucoes={c['solucoes']} com_fontes={c['com_fontes']} rotulos={c['rotulos']} "
              f"ok={c['ok']} nao_referencia={c['nao_referencia']} sem_parse={c['sem_parse']} "
              f"n_nota={c['n_nota']}",
              f"  referencias_novas={c['referencias_novas']} "
              f"referencias_sem_vinculo={c['referencias_sem_vinculo']} | Solucoes: novas={c['novas']} "
              f"atualizadas={c['atualizadas']} iguais={c['iguais']} sem_vinculo={c['sem_vinculo']}",
              f"  nao_ok: {nao_ok}/{c['rotulos']} ({pct}%)"]
    linhas += [f"  motivo {m}: {n}" for m, n in c["motivos"].items()]
    if c.get("fixado"):
        linhas.append(f"  FIXADO antes do ato (ponto de retorno; arquivo + sha256 vao para o ledger): "
                      f"{c['fixado']['arquivo']} sha256 {c['fixado']['sha256']}")
    return "\n".join(linhas)


def cmd_referencias(args):
    """`--referencias` (Fase 0 Lote 2 part 2.1, M-031): sincroniza `referencia` e `solucao_referencia`
    a partir de `emed_solucoes.fontes` (`db.referencias_sincronizar`; o `fontes` fica intacto).
    Dry-run por padrao; `--apply` exige `--expect N` (N = `novas + atualizadas`, em Solucoes) e FIXA o
    backup SEMPRE antes da 1a escrita (DDL + a 1a escrita em massa; sem fixado, exit 1).
    Part 2.3: com `--regua ARQ` imprime a regua (`regua_referencias`, sobre as Solucoes lidas no ato);
    o `--apply` exige `--regua` (sem ela, exit 1) com veredito SEGUE (PARA = exit 3, antes do
    COUNT-ASSERT); nos dois casos nada e gravado e o fixado nem sai."""
    if args.apply and args.expect is None:
        print("RECUSA: --referencias --apply exige --expect N (o `novas + atualizadas` do dry-run, em "
              "Solucoes). Nada gravado.")
        return 1
    if args.apply and not args.regua:
        print("RECUSA: --referencias --apply exige --regua ARQ (a amostra triada da part 2.3, com "
              "veredito SEGUE). Nada gravado.")
        return 1
    regua = _regua_do_arquivo(args.regua) if args.regua else None
    code = 0
    try:
        cont = db.referencias_sincronizar(aplicar=False)
        mudam = cont["novas"] + cont["atualizadas"]
        if regua is not None:
            cont["regua"] = regua
        if args.apply and regua["veredito"] != "SEGUE":
            cont["erro"] = f"PARA: {'; '.join(regua['motivos'])}. Nada gravado (nem o fixado)."
            code = 3
        elif args.expect is not None and mudam != args.expect:
            cont["erro"] = (f"COUNT-ASSERT falhou: novas+atualizadas={mudam}, --expect {args.expect}. "
                            f"Nada gravado.")
            code = 2
        elif args.apply:
            try:
                fixado = _fixar_antes(f"emed_banco --referencias: {mudam} Solucao(oes), "
                                      f"{cont['referencias_novas']} referencia(s) nova(s)")
            except Exception as e:  # noqa: BLE001 -- qualquer falha do ponto de retorno = recusa
                cont["erro"] = f"sem ponto de retorno FIXADO (F137): {e}. Nada gravado."
                code = 1
            else:
                cont = db.referencias_sincronizar(aplicar=True)
                cont["fixado"] = {"arquivo": fixado["arquivo"], "sha256": fixado["sha256"]}
                cont["regua"] = regua
    except ValueError as e:     # invariante quebrada: o writer ja voltou atras
        print(f"erro: {e}", file=sys.stderr)
        return 1
    aplicado = bool(args.apply and code == 0)
    if args.json:
        _emitir(dict(cont, aplicado=aplicado), True)
        return code
    if cont.get("erro"):
        print(cont["erro"])
    print(_linha_referencias(cont, aplicado))
    if regua is not None:
        print(_linhas_regua(regua))
    return code


def cmd_registrar(args):
    """`--registrar DIR`: upsert das respostas + resumo por lista + comando sugerido."""
    docs = ler_docs(args.registrar, "respostas")
    cont, code = _upsert_com_rito(db.emed_upsert_respostas, docs, args)
    resumos = resumo_listas(docs)
    if args.json:
        _emitir(dict(cont, aplicado=bool(args.apply and code == 0), listas=resumos), True)
    else:
        if cont.get("erro"):
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


def fora_do_hub(q):
    """A questão do banco que NÃO vai ao hub. PURA. s219: questão UERJ 2022-2026 de lista do EMED é
    spoiler dos simulados (a regra de `emed_api.spoiler_uerj`); a prova em si (`prova_pdf`) é o
    simulado e sai inteira. Uma regra só: o `--exportar` e a contagem da tela (P20) a chamam."""
    return q.get("executor") != "prova_pdf" and emed_api.spoiler_uerj(q.get("banca"))


def cobertura_cadeia(questoes, solucoes):
    """Cobertura da Solução em cadeia sobre `questoes` (linhas do banco), PURA (part 1.2, P2).

    Uma regra só para o gate do `--exportar` (que passa só as questões que vão ao hub, depois do
    `fora_do_hub`) e para o sensor do `--status` (todas as questões da lista, como `capturadas`).
    A versão vem de `db.versao_solucao`; `sem_obj` conta objetivo vazio OU Solução ausente.
    Devolve `{n, v3, v2, v1, sem, sem_obj, sem_cadeia: [num], sem_objetivo: [num]}`: em `sem_cadeia`
    cai quem tem versão < 2 (v1 ou sem Solução)."""
    sol = {(s["lista"], s["num"]): s for s in solucoes}
    c = {"n": 0, "v3": 0, "v2": 0, "v1": 0, "sem": 0, "sem_obj": 0,
         "sem_cadeia": [], "sem_objetivo": []}
    for q in questoes:
        s = sol.get((q["lista"], q["num"]))
        v = db.versao_solucao(s["solucao"]) if s else 0
        c["n"] += 1
        c[("v3" if v == 3 else "v2" if v == 2 else "v1") if s else "sem"] += 1   # linha vazia = v1
        if v < 2:
            c["sem_cadeia"].append(q["num"])
        if not s or not str(s.get("objetivo") or "").strip():
            c["sem_obj"] += 1
            c["sem_objetivo"].append(q["num"])
    return c


def _numeros_cadeia(c):
    """`v3 a | v2 b | v1 c | sem d | sem_obj e` -- os números da cobertura numa linha."""
    return " | ".join(f"{k} {c[k]}" for k in ("v3", "v2", "v1", "sem", "sem_obj"))


def cobertura_fontes(solucoes, vinculos):
    """Cobertura das fontes estruturadas por lista, PURA (part 2.1, sensor; molde do `fora_do_hub`).

    `solucoes` = linhas de `emed_solucoes` (`lista`, `num`, `fontes`); `vinculos` = o
    `db.referencias_por_solucao()` (`{}` sem as tabelas). Por lista: `rot` (rotulos do corte R0), `ok`,
    `nref` (nao_referencia), `sem` (sem_parse), `terc` (rotulos de `tipo` terceiro, qualquer status),
    `vinc` (vinculos gravados), `n_nota` e `pct_nota` (classe nota sobre `rot`, em %). Uma regra so:
    o `--status --fontes` e o WARN do `--status` chamam esta funcao."""
    por = {}
    for s in solucoes:
        d = por.setdefault(s["lista"], {"lista": s["lista"], "rot": 0, "ok": 0, "nref": 0, "sem": 0,
                                        "terc": 0, "vinc": 0, "n_nota": 0})
        for rotulo in db.fonte_rotulos(s.get("fontes")):
            e = db.fonte_estruturada(rotulo)
            d["rot"] += 1
            d[{"ok": "ok", "nao_referencia": "nref"}.get(e["status"], "sem")] += 1
            d["terc"] += 1 if e["tipo"] == "terceiro" else 0
            d["n_nota"] += 1 if e["classe"] == "nota" else 0
        d["vinc"] += len(vinculos.get((s["lista"], s["num"])) or [])
    saida = [por[k] for k in sorted(por)]
    for d in saida:
        d["pct_nota"] = round(100 * d["n_nota"] / d["rot"], 1) if d["rot"] else 0.0
    return saida


def questoes_no_hub_por_tarefa(questoes=None):
    """{tarefa_id: n} -- quantas questões de cada tarefa o `--exportar` manda ao hub (o que a aba
    Listas conta), pela MESMA regra (`fora_do_hub`). P20 (s219): a Teoria, o Painel e o boot contam
    por aqui. Read-only; tabela ausente = {}; tarefa só com spoiler não entra."""
    contagem = {}
    for q in db.emed_listar_questoes() if questoes is None else questoes:
        if q.get("tarefa_id") is None or fora_do_hub(q):
            continue
        t = int(q["tarefa_id"])
        contagem[t] = contagem.get(t, 0) + 1
    return contagem


#: s221 (P22): de onde a imagem pode vir -- as duas CDNs publicas do EMED (200 sem token, medido em
#: 08/10: o bucket S3 `images/<uuid>/<uuid>-400.png` e a CloudFront `image-file/<id>.png`).
HOSTS_FIGURA = ("estrategia-prod-questoes.s3.amazonaws.com", "d3typq4v571ghb.cloudfront.net")
PASTA_FIGURAS = os.path.join(ROOT, "tmp", "emed_figuras")
#: A figura vai ao hub em WebP de ate 900 px, qualidade 80: medido em 08/10 sobre 141 figuras, 13,4 MB
#: crus -> 1,9 MB (max 52 KB). Crua, a lista com figura pesava ate 875 KB por questao no banco do hub.
LARGURA_FIGURA, QUALIDADE_FIGURA = 900, 80


def _baixar(url, timeout=30):
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), (r.headers.get("Content-Type") or "").split(";")[0].strip()


def comprimir_figura(dados):
    """bytes da imagem -> (bytes, mime) em WebP <= `LARGURA_FIGURA` px, fundo branco no lugar da
    transparencia. Sem Pillow (ou imagem ilegivel) devolve None: quem chama embute a crua."""
    try:
        import io
        from PIL import Image
        im = Image.open(io.BytesIO(dados))
        if im.mode in ("P", "RGBA", "LA"):
            im = im.convert("RGBA")
            fundo = Image.new("RGB", im.size, "white")
            fundo.paste(im, mask=im.split()[-1])
            im = fundo
        else:
            im = im.convert("RGB")
        if im.width > LARGURA_FIGURA:
            im = im.resize((LARGURA_FIGURA, round(im.height * LARGURA_FIGURA / im.width)))
        out = io.BytesIO()
        im.save(out, "WEBP", quality=QUALIDADE_FIGURA)
        return out.getvalue(), "image/webp"
    except Exception:
        return None


def figura_data_uri(url, cache=PASTA_FIGURAS, baixar=_baixar):
    """data URI da imagem de `url` (host em `HOSTS_FIGURA`), ou None. Tenta antes a variante de
    800 px (`-400.` -> `-800.`, mais legivel para ECG e radiografia no celular) e cai na original;
    embute em WebP (`comprimir_figura`). Cache em disco por sha1 da URL (`<sha1>.raw` = o download,
    `<sha1>.mime` = o tipo dele): re-exportar nao baixa de novo."""
    import base64
    import hashlib
    import urllib.parse
    if urllib.parse.urlparse(url).netloc not in HOSTS_FIGURA:
        return None
    os.makedirs(cache, exist_ok=True)
    chave = hashlib.sha1(url.encode("utf-8")).hexdigest()
    cru, mime = os.path.join(cache, chave + ".raw"), os.path.join(cache, chave + ".mime")
    if os.path.exists(cru) and os.path.exists(mime):
        with open(cru, "rb") as fh:
            dados = fh.read()
        with open(mime, encoding="utf-8") as fh:
            tipo = fh.read().strip()
    else:
        dados = tipo = None
        candidatas = ([url.replace("-400.", "-800.")] if "-400." in url else []) + [url]
        for alvo in candidatas:
            try:
                d, t = baixar(alvo)
            except Exception:
                continue
            if t.startswith("image/") and d:
                dados, tipo = d, t
                break
        if dados is None:
            return None
        with open(cru, "wb") as fh:
            fh.write(dados)
        with open(mime, "w", encoding="utf-8") as fh:
            fh.write(tipo)
    menor = comprimir_figura(dados)
    if menor:
        dados, tipo = menor
    return f"data:{tipo};base64," + base64.b64encode(dados).decode("ascii")


#: 1.1a: o que o `--exportar --so-figuras` leva ao `batch update` do doc do hub -- as chaves de figura,
#: a imagem embutida e o `emed_id` (o join da 1.1b). Nunca enunciado, alternativas ou solucao.
CHAVES_SO_FIGURAS = ("emed_id",) + tuple(db.CHAVES_FIGURA_EMED) + ("figuras_img",)


def exportar_so_figuras(args, linhas):
    """`--exportar LISTA --so-figuras`: `OUT/upd/<lista>_<num>.json` so com `CHAVES_SO_FIGURAS`, e so
    dos docs com alguma chave de figura. Falha de download: o item e listado, sem `figuras_img` parcial."""
    pasta = os.path.join(args.out, "upd")
    os.makedirs(pasta, exist_ok=True)
    escritos, falhas = [], []
    for q in linhas:
        try:
            extras = json.loads(q.get("extras") or "{}")
        except ValueError:
            extras = {}
        doc = {k: extras[k] for k in db.CHAVES_FIGURA_EMED if k in extras}
        if not doc:
            continue
        if doc.get("figuras") and not getattr(args, "sem_figuras", False):
            imgs = [figura_data_uri(u) for u in doc["figuras"]]
            if all(imgs):
                doc["figuras_img"] = imgs
            else:
                falhas.append(f"{q['lista']}_{q['num']}")
        doc = dict({"emed_id": q.get("emed_id")}, **doc)
        with open(os.path.join(pasta, f"{q['lista']}_{q['num']}.json"), "w", encoding="utf-8") as fh:
            json.dump({k: doc[k] for k in CHAVES_SO_FIGURAS if k in doc}, fh, ensure_ascii=False, indent=2)
        escritos.append(q["num"])
    print(f"{len(escritos)} arquivos so de figura em {pasta}"
          + (f"; FIGURA NAO BAIXADA (o hub mostra o aviso): {falhas}" if falhas else ""))
    return 0


def gate_cadeia(args, cabecalho, c):
    """Gate de cadeia do `--exportar` (part 1.2, P2): a lista só chega ao hub com cadeia (v2/v3) e
    `objetivo` em toda questão que vai ao hub. Simulado (`area` do plano, a regra do hub) não se
    aplica; `--sem-cadeia MOTIVO` deixa passar declarado. True = segue; False = RECUSA impressa."""
    if cabecalho.get("area") == "Simulado":
        print("simulado: gate de cadeia nao se aplica")
        return True
    if c["sem_cadeia"] or c["sem_objetivo"]:
        motivo = getattr(args, "sem_cadeia", None)
        if motivo:
            print(f"SEM CADEIA declarado ({motivo}): {_numeros_cadeia(c)}")
            return True
        partes = [f"sem {nome} em " + ",".join(f"Q{n}" for n in sorted(nums))
                  for nome, nums in (("cadeia", c["sem_cadeia"]), ("objetivo", c["sem_objetivo"]))
                  if nums]
        print(f"RECUSA: {args.exportar} " + " / ".join(partes)
              + " -- cunhar v3 com objetivo (--solucoes --apply --expect N) ou --sem-cadeia MOTIVO")
        return False
    if c["v2"]:
        print(f"legado v2: {c['v2']}")
    return True


def cmd_exportar(args):
    """`--exportar LISTA`: escreve `OUT/questoes/<lista>_<num>.json` (formato do doc) e
    `OUT/listas/<lista>.json` (cabeçalho da lista), para semear o buffer/hub por ArtifactData.
    Com `--so-figuras` (1.1a), so `OUT/upd/` com as chaves de figura (`exportar_so_figuras`).
    Part 1.2: antes de escrever, o gate de cadeia (`gate_cadeia`) recusa a lista sem cadeia/objetivo."""
    todas = db.emed_listar_questoes(args.exportar)
    # s219: o spoiler UERJ de lista do EMED nao volta ao hub (`fora_do_hub`)
    spoiler = [q["num"] for q in todas if fora_do_hub(q)]
    linhas = [q for q in todas if q["num"] not in spoiler]
    if getattr(args, "so_figuras", False):
        return exportar_so_figuras(args, linhas)
    linhas_sol = db.emed_listar_solucoes(args.exportar)
    solucoes = {s["num"]: s for s in linhas_sol}
    cabecalho = doc_lista(args.exportar, len(linhas))
    if not gate_cadeia(args, cabecalho, cobertura_cadeia(linhas, linhas_sol)):
        return 1    # part 1.2: antes do makedirs -- recusa nao cria OUT
    falhas = []
    pasta = os.path.join(args.out, "questoes")
    os.makedirs(pasta, exist_ok=True)
    pasta_l = os.path.join(args.out, "listas")
    os.makedirs(pasta_l, exist_ok=True)
    with open(os.path.join(pasta_l, f"{args.exportar}.json"), "w", encoding="utf-8") as fh:
        json.dump(cabecalho, fh, ensure_ascii=False, indent=2)
    for q in linhas:
        doc = {c: q.get("tarefa_id" if c == "tarefa" else c) for c in CAMPOS_DOC_QUESTAO}
        # `extras` volta a ser chaves soltas do doc (formato do artifact); o hash re-deriva igual.
        try:
            doc.update(json.loads(q.get("extras") or "{}"))
        except ValueError:
            pass
        if doc.get("figuras") and not getattr(args, "sem_figuras", False):
            # s221 (P22): a figura do enunciado vai EMBUTIDA no doc do hub (decisao dele: opcao B)
            imgs = [figura_data_uri(u) for u in doc["figuras"]]
            if all(imgs):
                doc["figuras_img"] = imgs
            else:
                falhas.append(f"{q['lista']}_{q['num']}")
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
    print(f"{len(linhas)} arquivos em {pasta} + listas/{args.exportar}.json"
          + (f"; spoiler UERJ fora: {sorted(spoiler, key=int)}" if spoiler else "")
          + (f"; FIGURA NAO BAIXADA (o hub mostra o aviso): {falhas}" if falhas else ""))
    return 0


def texto_solucao(texto):
    """A solução do hub em texto corrido: v1 como está; v2/v3 (cadeia) numerada. PURA.

    v3 (s211): cada elo com o `tipo` (e a letra do `descartar`) e a `habilidade`; a alternativa só traz
    o próprio porquê. v2 (legado t26/t96): a letra errada ainda mostra o elo em que cai, rotulado legado.
    Nunca "cai no elo None": alternativa sem `elo` não aponta elo nenhum."""
    sol = db.solucao_estruturada(texto)
    if not sol:
        return texto or ""
    v3 = sol.get("versao") == 3
    linhas = [f"Pede: {sol.get('pede', '')}"]
    for i, e in enumerate(sol.get("cadeia") or [], 1):
        if v3:
            tipo = e.get("tipo", "") + (f" {e.get('letra')}" if e.get("tipo") == "descartar" else "")
            linhas.append(f"{i}. [{tipo}] {e.get('elo', '')} -- {e.get('chave', '')}"
                          + (f" (habilidade: {e['habilidade']})" if e.get("habilidade") else ""))
        else:
            linhas.append(f"{i}. {e.get('elo', '')} -- {e.get('chave', '')}")
    for letra in sorted(sol.get("alternativas") or {}):
        a = sol["alternativas"][letra]
        if a.get("certa") is True:
            marca = " (certa)"
        elif not v3 and a.get("elo"):
            marca = f" (legado: cai no elo {a.get('elo')})"
        else:
            marca = ""
        linhas.append(f"{letra}{marca}: {a.get('porque', '')}")
    if sol.get("conferir"):
        linhas.append(f"Conferir: {sol['conferir']}")
    return "\n".join(linhas)


#: s211 (feedback-cadeia-declarada part-5): o rótulo de cada estado declarado (vocabulário no brief
#: §Estado por elo; `db.ESTADOS_ELO_EMED` é o mesmo conjunto).
ROTULO_ESTADO = {"sim": "Sim", "incerteza": "Incerteza", "desatencao": "Desatenção", "nao": "Não"}
ORDEM_REVISAO = ("nao", "incerteza", "desatencao")


def _json_ou(valor, padrao):
    """Coluna JSON do banco (ou o próprio objeto) -> objeto; vazio/torto -> `padrao`. PURA."""
    if isinstance(valor, (list, dict)):
        return valor
    try:
        return json.loads(valor) if valor else padrao
    except (TypeError, ValueError):
        return padrao


def declaracao(resposta, solucao_texto):
    """Os elos da cadeia com o estado DECLARADO pelo aluno (s211). PURA.

    `elos` alinhado à cadeia = declarado; sem `elos`, certa e sólida = "presumido Sim" (regra só de
    leitura); o resto = "sem declaração". Conflito determinístico: elo `descartar` cuja `letra` é a
    marcada e declarado `sim` (só v3: a v2 não tem `tipo`)."""
    sol = db.solucao_estruturada(solucao_texto) or {}
    cad = sol.get("cadeia") or []
    elos = _json_ou(resposta.get("elos"), None)
    declarado = isinstance(elos, list) and len(elos) == len(cad) and bool(cad)
    presumido = (not declarado and resposta.get("correta") == 1
                 and resposta.get("confianca") == "solida")
    letra = (resposta.get("letra") or "").upper()
    itens, conflitos = [], []
    for i, e in enumerate(cad, 1):
        st = elos[i - 1] if declarado else ("sim" if presumido else "")
        rot = "presumido Sim" if presumido else (ROTULO_ESTADO.get(st) or "sem declaração")
        itens.append({"i": i, "estado": st, "rotulo": rot, "elo": e.get("elo", ""),
                      "habilidade": e.get("habilidade", ""), "tipo": e.get("tipo", "")})
        if (declarado and e.get("tipo") == "descartar" and st == "sim"
                and str(e.get("letra") or "").upper() == letra):
            conflitos.append(i)
    return {"versao": sol.get("versao"), "declarado": declarado, "presumido": presumido,
            "elos": itens, "conflitos": conflitos}


def alternativas_por_letra(texto):
    """"A) ..." por linha -> {letra: texto} (linha de continuação cola na anterior), o mesmo parser
    da página (`qzAlts`), para os offsets dos grifos baterem com o texto que ela mostrou. PURA."""
    out, ultima = {}, None
    for ln in str(texto or "").splitlines():
        m = re.match(r"^\s*\(?([A-Ea-e])\s*[\)\.\-:\]]\s*(.*)$", ln)
        if m:
            ultima = m.group(1).upper()
            out[ultima] = m.group(2)
        elif ultima and ln.strip():
            out[ultima] += "\n" + ln.strip()
    return out


def trechos_grifados(grifos, enunciado, alternativas):
    """Os trechos que ele grifou, em TEXTO (nunca offsets). Intervalo inválido ou texto ausente
    (questão podada) = cala. PURA."""
    g = _json_ou(grifos, {})
    if not isinstance(g, dict):
        return []
    textos = {"enun": enunciado or ""}
    textos.update(alternativas_por_letra(alternativas))
    saida = []
    for chave in ["enun"] + sorted(k for k in g if k != "enun"):
        texto = textos.get(chave) or ""
        for v in g.get(chave) or []:
            # s229: o grifo das Listas leva a cor no 3o campo ([ini, fim, "ciano"|"amarelo"]; sem = rosa)
            if (isinstance(v, list) and len(v) in (2, 3) and all(isinstance(x, int) for x in v[:2])
                    and 0 <= v[0] < v[1] <= len(texto)):
                saida.append({"onde": "enunciado" if chave == "enun" else chave,
                              "trecho": texto[v[0]:v[1]],
                              "cor": v[2] if len(v) == 3 and v[2] in ("ciano", "amarelo") else "rosa"})
    return saida


def leitura_metacognitiva(resposta, solucao_texto, letras=None, legado=True):
    """O rastro metacognitivo de UMA resposta contra a Solução v2 (s200, pedido do operador:
    "as alternativas riscadas e a dúvida entre duas sem dúvida contribuem para a análise"). PURA.

    - `riscadas`: letras que ele eliminou antes de marcar;
    - `restantes`: as que sobraram (na dúvida, o par em que hesitou);
    - `elos_ok`: elos que ele executou -- os de cada letra ERRADA que ele riscou;
    - `elo_letra`: o elo em que a letra marcada cai (None se acertou);
    - `riscou_certa`: eliminou o gabarito -- crença firme contra a resposta, não descuido.
    Sem Solução v2, os elos ficam vazios e o resto segue.
    ⚰️ s211: `elos_ok` e `elo_letra` são a leitura PELAS LETRAS, revogada em 02/10/2026 -- só saem com
    `legado=True` (solução v2 SEM declaração do aluno); fora disso ficam vazios."""
    risc = [x for x in db.riscadas_norm(resposta.get("riscadas")).split(",") if x]
    v2 = db.solucao_estruturada(solucao_texto) or {}
    if v2.get("versao") != 2:
        legado = False
    alts = v2.get("alternativas") or {}
    todas = sorted(alts) if alts else sorted(letras or [])
    gab = (resposta.get("gabarito") or "").upper()
    letra = (resposta.get("letra") or "").upper()
    elos_ok = sorted({alts[x]["elo"] for x in risc
                      if x in alts and not alts[x].get("certa") and alts[x].get("elo")})
    marcada = alts.get(letra) or {}
    return {"riscadas": risc, "restantes": [x for x in todas if x not in risc],
            "elos_ok": elos_ok if legado else [],
            "elo_letra": None if (not legado or marcada.get("certa") or not marcada) else marcada.get("elo"),
            "riscou_certa": bool(gab and gab in risc)}


def texto_leitura(m, confianca):
    """A leitura metacognitiva em 1 linha, para o `--erros` e o log. PURA."""
    partes = []
    if m["riscadas"]:
        partes.append("riscou " + ", ".join(m["riscadas"]))
    if confianca == "duvida" and 1 < len(m["restantes"]) <= 3:
        rest = m["restantes"]
        partes.append("ficou entre " + (", ".join(rest[:-1]) + " e " + rest[-1]))
    if m["elos_ok"]:
        partes.append("legado: executou o(s) elo(s) " + ", ".join(str(k) for k in m["elos_ok"]))
    if m["elo_letra"]:
        partes.append(f"legado: a letra marcada cai no elo {m['elo_letra']}")
    if m["riscou_certa"]:
        partes.append("RISCOU A CERTA")
    return "; ".join(partes) or "(sem riscadas)"


def erros_da_lista(lista):
    """Respostas erradas OU não-sólidas da lista (s211: a dúvida certa entra -- a declaração é
    obrigatória nela), cada uma com a questão em íntegra e o que o aluno DECLAROU."""
    questoes = {q["num"]: q for q in db.emed_listar_questoes(lista)}
    solucoes = {s["num"]: s for s in db.emed_listar_solucoes(lista)}
    saida = []
    for r in db.emed_listar_respostas(lista):
        if r["correta"] != 0 and r["confianca"] == "solida":
            continue
        q = questoes.get(r["num"], {})
        sol_texto = (solucoes.get(r["num"]) or {}).get("solucao")
        decl = declaracao(r, sol_texto)
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
            "modo": r.get("modo") or "",
            "declaracao": decl, "cadeia_defeito": r.get("cadeia_defeito") or "",
            "grifados": trechos_grifados(r.get("grifos"), q.get("enunciado"), q.get("alternativas")),
            "leitura": leitura_metacognitiva(r, sol_texto, legado=not decl["declarado"])})
    return saida


def cmd_erros(args):
    """`--erros LISTA`: insumo do /analisar-questao (erradas e não-sólidas, em íntegra, com a
    declaração do aluno por elo)."""
    itens = erros_da_lista(args.erros)
    if args.json:
        _emitir(itens, True)
        return 0
    print(f"{args.erros}: {len(itens)} questoes (erradas ou nao-solidas)")
    for e in itens:
        status = f"CERTA ({e['confianca']})" if e["correta"] == 1 else "ERRADA"
        print("=" * 72)
        print(f"Q{e['num']} · {e['banca'] or '?'} · marcou {e['letra']} x gabarito "
              f"{e['gabarito'] or '?'} · {status} · confianca {e['confianca'] or '?'} · "
              f"tempo {e['tempo_s'] if e['tempo_s'] is not None else '?'}s")
        if e["questao_erro_id"] is not None:
            print(f"JA REGISTRADA como erro #{e['questao_erro_id']}")
        print(f"Racional declarado: {e['racional'] or '(vazio)'}")
        if e["elo"]:
            print(f"Chip de causa (legado, antes de 02/10): {e['elo']}")
        print(f"Objetivo: {e['objetivo'] or '(sem)'} · modo {e['modo'] or '?'}")
        d = e["declaracao"]
        if d["elos"]:
            print("Elos (o DECLARADO pelo aluno):")
            for x in d["elos"]:
                print(f"  {x['i']}. [{x['rotulo']}] {x['elo']}")
        for k in d["conflitos"]:
            print(f"CONFLITO no elo {k}: declarou Sim no descarte da letra que marcou")
        if e["cadeia_defeito"]:
            print(f"Cadeia com defeito: {e['cadeia_defeito']}")
        if e["grifados"]:
            print("Grifou: " + " · ".join(f"{g['onde']} \"{g['trecho']}\"" for g in e["grifados"]))
        print(f"Leitura: {texto_leitura(e['leitura'], e['confianca'])}")
        for rotulo, campo in (("ENUNCIADO", "enunciado"), ("ALTERNATIVAS", "alternativas"),
                              ("SOLUCAO MEDHUB", "solucao_medhub"),
                              ("SOLUCAO", "solucao"), ("FORUM", "forum")):
            print(f"-- {rotulo}\n{e[campo] or '(vazio)'}")
    return 0


def elos_nao_sim(lista=None):
    """Um item por elo DECLARADO diferente de `sim` (s211): lista, questão, índice, estado, a
    `habilidade` (v3) ou o texto do elo (v2) e o objetivo; ordem `nao` -> `incerteza` -> `desatencao`.
    Read-only. Presumido não entra (é Sim por definição)."""
    sols = {(s["lista"], s["num"]): s for s in db.emed_listar_solucoes(lista)}
    saida = []
    for r in db.emed_listar_respostas(lista):
        s = sols.get((r["lista"], r["num"])) or {}
        d = declaracao(r, s.get("solucao"))
        if not d["declarado"]:
            continue
        for x in d["elos"]:
            if x["estado"] in ORDEM_REVISAO:
                saida.append({"lista": r["lista"], "num": r["num"], "i": x["i"], "estado": x["estado"],
                              "habilidade": x["habilidade"] or x["elo"], "objetivo": s.get("objetivo") or ""})
    return sorted(saida, key=lambda x: (ORDEM_REVISAO.index(x["estado"]), x["lista"], x["num"], x["i"]))


def cmd_elos(args):
    """`--elos [LISTA]`: os elos declarados Não / Incerteza / Desatenção (sem LISTA, todas)."""
    itens = elos_nao_sim(None if args.elos == "*" else args.elos)
    if args.json:
        _emitir(itens, True)
        return 0
    if not itens:
        print("nenhum elo declarado diferente de Sim")
        return 0
    print("lista | questao | elo | estado | habilidade | objetivo")
    for x in itens:
        print(f"{x['lista']} | Q{x['num']} | {x['i']} | {ROTULO_ESTADO[x['estado']]} | "
              f"{x['habilidade']} | {x['objetivo'] or '-'}")
    return 0


def defeitos_de_cadeia(lista=None):
    """As questões que o aluno sinalizou com "Erro na cadeia" (s211): a fila de correção. Read-only."""
    return [{"lista": r["lista"], "num": r["num"], "motivo": r["cadeia_defeito"]}
            for r in db.emed_listar_respostas(lista) if r.get("cadeia_defeito")]


def cmd_defeitos(args):
    """`--defeitos`: a fila de correção de cadeia (filtro `--lista`)."""
    itens = defeitos_de_cadeia(args.lista)
    if args.json:
        _emitir(itens, True)
        return 0
    if not itens:
        print("nenhuma cadeia sinalizada com defeito")
        return 0
    for x in itens:
        print(f"{x['lista']} Q{x['num']}: {x['motivo']}")
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
    if args.fontes:     # part 2.1: o sensor das fontes estruturadas, por lista (so le)
        linhas = cobertura_fontes([s for s in db.emed_listar_solucoes()
                                   if not args.lista or s["lista"] == args.lista],
                                  db.referencias_por_solucao())
        if args.json:
            _emitir(linhas, True)
            return 0
        cols = ("rot", "ok", "nref", "sem", "terc", "vinc", "n_nota")
        print("lista | " + " | ".join(cols) + " | pct_nota")
        for d in linhas:
            print(f"{d['lista']} | " + " | ".join(str(d[k]) for k in cols) + f" | {d['pct_nota']}")
        tot = {k: sum(d[k] for d in linhas) for k in cols}
        pct = round(100 * tot["n_nota"] / tot["rot"], 1) if tot["rot"] else 0.0
        print("total | " + " | ".join(str(tot[k]) for k in cols) + f" | {pct}")
        return 0
    linhas = [s for s in db.emed_status() if not args.lista or s["lista"] == args.lista]
    if linhas:      # part 1.2: o sensor de cadeia, sobre todas as questoes da lista (como `capturadas`)
        questoes, solucoes = db.emed_listar_questoes(), db.emed_listar_solucoes()
        for s in linhas:
            c = cobertura_cadeia([q for q in questoes if q["lista"] == s["lista"]],
                                 [x for x in solucoes if x["lista"] == s["lista"]])
            s.update({k: c[k] for k in ("v3", "v2", "v1", "sem", "sem_obj")})
    if args.json:
        _emitir(linhas, True)
        return 0
    if not linhas:
        print("nenhuma lista no banco EMED")
        return 0
    print("lista | tarefa | area | tema | capt | resp | acertos | sol/duv/chu | erradas | tempo"
          " | v3 | v2 | v1 | sem | sem_obj")
    for s in linhas:
        print(f"{s['lista']} | {s['tarefa_id'] or '-'} | {s['area'] or '-'} | "
              f"{s['tema'] or '-'} | {s['capturadas']} | {s['respondidas']} | "
              f"{s['acertos']} | {s['solidas']}/{s['duvidas']}/{s['chutes']} | "
              f"{s['erradas']} | "
              f"{s['tempo_medio_s'] if s['tempo_medio_s'] is not None else '-'} | "
              f"{s['v3']} | {s['v2']} | {s['v1']} | {s['sem']} | {s['sem_obj']}")
    for s in linhas:    # sensor, nao gate (warn-first): o estoque que ja esta no hub
        if s["area"] != "Simulado" and s["v1"] + s["sem"] > 0:
            print(f"[WARN] SEM_CADEIA: {s['lista']} ({s['v1'] + s['sem']}/{s['capturadas']})")
    fontes = cobertura_fontes([s for s in db.emed_listar_solucoes()
                               if not args.lista or s["lista"] == args.lista], {})
    fora = [d["nref"] + d["sem"] for d in fontes if d["nref"] + d["sem"]]
    if fora:            # part 2.1: sensor, nao gate -- fecha depois do WARN da 1.2
        print(f"[WARN] FONTES_SEM_ESTRUTURA: {sum(fora)} rótulos em {len(fora)} listas "
              f"(ver --status --fontes)")
    return 0


def main(argv=None):
    """Ponto de entrada: exatamente UM modo por chamada."""
    ap = argparse.ArgumentParser(
        description="Banco de questoes EMED no ipub.db (Bancada EMED): ingerir, "
                    "registrar, solucoes, podar, exportar, erros, elos, defeitos, status, "
                    "referencias, amostra-referencias.")
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
    ap.add_argument("--sem-figuras", action="store_true",
                    help="--exportar sem baixar/embutir a imagem do enunciado (s221, P22)")
    ap.add_argument("--sem-cadeia", dest="sem_cadeia", metavar="MOTIVO",
                    help="--exportar de lista sem cadeia v2/v3 ou sem objetivo, com o motivo declarado "
                         "(part 1.2; sem a flag, o gate recusa com exit 1)")
    ap.add_argument("--so-figuras", dest="so_figuras", action="store_true",
                    help="--exportar so OUT/upd/<lista>_<num>.json com as chaves de figura + emed_id (1.1a)")
    ap.add_argument("--figuras", metavar="DIR",
                    help="mescla so as chaves de figura de DIR/questoes/*.json (recaptura) por emed_id (1.1a)")
    ap.add_argument("--reavaliar-sem-figura", dest="reavaliar_sem_figura", action="store_true",
                    help="re-roda a regra vigente do sem_figura e tira a marca de quem ela nao marca "
                         "mais (hotfix 1.1b)")
    ap.add_argument("--erros", metavar="LISTA",
                    help="erradas e nao-solidas da lista em integra, com a declaracao por elo "
                         "(insumo do /analisar-questao)")
    ap.add_argument("--elos", nargs="?", const="*", metavar="LISTA",
                    help="elos declarados Nao/Incerteza/Desatencao (sem LISTA: todas) (s211)")
    ap.add_argument("--defeitos", action="store_true",
                    help="questoes com cadeia_defeito: a fila de correcao de cadeia (s211)")
    ap.add_argument("--referencias", action="store_true",
                    help="sincroniza referencia/solucao_referencia a partir de emed_solucoes.fontes "
                         "(part 2.1; dry-run; --apply exige --expect N e --regua ARQ, e fixa o backup)")
    ap.add_argument("--amostra-referencias", dest="amostra_referencias", metavar="HEX",
                    help="sorteia ate 2 Solucoes com fonte por lista (semente = o hex de 7 do commit "
                         "que congelou o parser) em tmp/lote2/amostra-<hex>.json (part 2.3; so le o banco)")
    ap.add_argument("--regua", metavar="ARQ",
                    help="com --referencias: a regua de parada sobre a amostra triada (part 2.3); "
                         "o --apply exige veredito SEGUE (PARA = exit 3)")
    ap.add_argument("--status", action="store_true", help="resumo por lista")
    ap.add_argument("--lista", metavar="LISTA", help="filtro do --status e do --defeitos")
    ap.add_argument("--por-objetivo", dest="por_objetivo", action="store_true",
                    help="com --status: acerto por tema e objetivo da questao (s200)")
    ap.add_argument("--fontes", action="store_true",
                    help="com --status: cobertura das fontes estruturadas por lista (part 2.1)")
    ap.add_argument("--apply", action="store_true", help="grava (default = dry-run)")
    ap.add_argument("--expect", type=int, metavar="N",
                    help="COUNT-ASSERT: novas+atualizadas deve ser N, senao exit 2")
    ap.add_argument("--json", action="store_true", help="saida em JSON")
    args = ap.parse_args(argv)

    modos = {"--ingerir": args.ingerir, "--registrar": args.registrar,
             "--solucoes": args.solucoes, "--figuras": args.figuras,
             "--reavaliar-sem-figura": args.reavaliar_sem_figura,
             "--podar": args.podar, "--exportar": args.exportar,
             "--erros": args.erros, "--elos": args.elos, "--defeitos": args.defeitos,
             "--status": args.status, "--referencias": args.referencias,
             "--amostra-referencias": args.amostra_referencias}
    ligados = [m for m, v in modos.items() if v]
    if len(ligados) != 1:
        print("erro: informe exatamente UM modo (" + " | ".join(modos) + ")",
              file=sys.stderr)
        return 1
    if args.sem_cadeia is not None and not args.sem_cadeia.strip():
        print("erro: --sem-cadeia exige um MOTIVO nao vazio", file=sys.stderr)
        return 1
    if args.regua is not None and not args.referencias:
        print("erro: --regua so vale com --referencias", file=sys.stderr)
        return 1
    acao = {"--ingerir": cmd_ingerir, "--registrar": cmd_registrar,
            "--solucoes": cmd_solucoes, "--figuras": cmd_figuras,
            "--reavaliar-sem-figura": cmd_reavaliar_sem_figura,
            "--podar": cmd_podar, "--exportar": cmd_exportar,
            "--erros": cmd_erros, "--elos": cmd_elos, "--defeitos": cmd_defeitos,
            "--status": cmd_status, "--referencias": cmd_referencias,
            "--amostra-referencias": cmd_amostra_referencias}[ligados[0]]
    try:
        return acao(args)
    except ErroLeitura as e:
        print(f"erro: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
