"""prova_pdf.py -- caderno de prova em PDF -> docs `questoes/*` do hub (caminho PDF, s201).

Decisao do operador (26/09/2026): a captura pelo Chrome sai do fluxo (F135: clique na conta dele,
500-700k tokens por lista); as provas e listas entram por PDF. Primeiro formato: o caderno oficial
da UERJ Acesso Direto (Cepuerj, 2021-2026), que alimenta a secao Simulados da aba Listas. O
gabarito vem do JSON versionado (`simulados/uerj/gabaritos_2021-2026.json`), nunca do PDF.

Saida = o MESMO formato da Bancada (`<OUT>/questoes/<lista>_<num>.json` + `<OUT>/listas/<lista>.json`),
consumido por `emed_banco.py --ingerir <OUT> --apply --expect N`. Escopo PUBLICO: enunciado,
alternativas, gabarito, banca e o bloco da prova (o cabecalho impresso no caderno). O mapa tematico
(`uerj_mapa_questoes_*.json`) e SPOILER e nao entra.

TUDO OU NADA (DoD do /ai-eng): qualquer problema = recusa NOMEADA e nenhum arquivo escrito --
contagem diferente da capa, do gabarito ou do `--expect`; numeracao com buraco; questao com menos
de 4 ou mais de 5 alternativas (discursiva cai aqui); gabarito ausente ou fora de A-E; parser que
passa do `--timeout`. Anulada (gabarito `ANULADA`) sai da prova e e declarada na saida.

Regras de leitura, cada uma nascida de um defeito medido:
- so comeca no 1o cabecalho de BLOCO: a capa tem instrucoes numeradas "1)" a "8)" (o F128 foi
  a folha de instrucoes sequestrando a Q8);
- numero de questao so vale se for o SEGUINTE ao anterior (item "3)" dentro de enunciado nao abre questao);
- cabecalho/rodape de pagina e o aviso final ("PROIBIDO DESTACAR...") sao descartados;
- figura: imagem cuja caixa nao e o logo do cabecalho (que se repete em toda pagina) marca a
  questao com `figura` + `pagina` -- o texto nao carrega a imagem, a pagina do hub avisa.

LIMITE DECLARADO: tabela impressa vira texto corrido (o parser nao reconstroi colunas); a figura e
sinalizada, nao desenhada. Formato EMED (lista exportada pelo operador) ainda nao existe: sem
amostra real, nao se escreve parser.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GABARITOS_UERJ = os.path.join(ROOT, "simulados", "uerj", "gabaritos_2021-2026.json")

RX_QUESTAO = re.compile(r"^\s*(\d{1,3})\)\s+(.*)$")
RX_ALT = re.compile(r"^\s*([a-eA-E])\)\s+(.*)$")
RX_DESCARTE = re.compile(
    r"RESID[ÊE]NCIA M[ÉE]DICA UERJ|P[ÁA]GINA \d+ DE \d+|^ORGANIZADOR$|^ACESSO DIRETO|"
    r"PROIBIDO DESTACAR|OUTRA FOLHA DOS CADERNOS|^RASCUNHO$", re.I)
RX_CAPA_N = re.compile(r"caderno de (\d+) quest", re.I)
RX_CAPA_H = re.compile(r"Dura[çc][ãa]o m[áa]xima da prova:\s*(\d+)\s*hora", re.I)

#: cabecalho impresso (normalizado: maiusculas, sem espaco em volta de "/") -> rotulo canonico,
#: o mesmo entre edicoes (2021 imprime "MEDICINA PREVENTIVA"; 2022+ "MEDICINA DE FAMILIA E COMUNIDADE")
BLOCOS_UERJ = {
    "CLÍNICA MÉDICA": "Clínica Médica",
    "CIRURGIA GERAL": "Cirurgia Geral",
    "GINECOLOGIA/OBSTETRÍCIA": "Ginecologia e Obstetrícia",
    "GINECOLOGIA E OBSTETRÍCIA": "Ginecologia e Obstetrícia",
    "PEDIATRIA": "Pediatria",
    "MEDICINA PREVENTIVA": "Medicina de Família e Comunidade",
    "MEDICINA DE FAMÍLIA E COMUNIDADE": "Medicina de Família e Comunidade",
}


class Recusa(Exception):
    """Problema nomeado: nada e escrito."""


def _norm_cabecalho(linha):
    return re.sub(r"\s*/\s*", "/", re.sub(r"\s+", " ", linha.strip().upper()))


def ler_pdf(caminho):
    """[(pagina 1-based, [(y, linha)], [caixas de imagem (x0,y0,x1,y1)])] -- a unica funcao que toca
    o PDF. `y` = topo da linha na pagina: e o que liga a figura a questao certa."""
    import fitz
    paginas = []
    with fitz.open(caminho) as doc:
        for i, pag in enumerate(doc):
            caixas = [tuple(round(v, 1) for v in info.get("bbox", (0, 0, 0, 0)))
                      for info in pag.get_image_info()]
            linhas = []
            for bloco in pag.get_text("dict").get("blocks", []):
                for ln in bloco.get("lines", []):
                    texto = "".join(sp.get("text", "") for sp in ln.get("spans", []))
                    linhas.append((round(ln["bbox"][1], 1), texto))
            paginas.append((i + 1, linhas, caixas))
    return paginas


def _caixas_de_figura(paginas):
    """Caixas de imagem que NAO sao o logo do cabecalho: a caixa que se repete em mais da metade
    das paginas e cabecalho. PURA."""
    contagem = {}
    for _, _, caixas in paginas:
        for c in set(caixas):
            contagem[c] = contagem.get(c, 0) + 1
    repetidas = {c for c, n in contagem.items() if n > len(paginas) / 2}
    return {p: [c for c in caixas if c not in repetidas] for p, _, caixas in paginas}


def _juntar(pedacos):
    """Linhas de um trecho -> texto corrido; hifen de quebra de linha cola sem espaco."""
    out = ""
    for p in pedacos:
        p = p.strip()
        if not p:
            continue
        if not out:
            out = p
        elif out.endswith("-") and not out.endswith(" -"):
            out += p
        else:
            out += " " + p
    return re.sub(r"\s+", " ", out).strip()


def parse_uerj(paginas):
    """Caderno UERJ -> `{capa_n, duracao_h, questoes: [{num, bloco, pagina, enunciado, alternativas,
    figura}]}`. PURA sobre a saida de `ler_pdf`."""
    capa = "\n".join(t for _, t in paginas[0][1]) if paginas else ""
    m_n, m_h = RX_CAPA_N.search(capa), RX_CAPA_H.search(capa)
    figuras = _caixas_de_figura(paginas)
    qs, atual, bloco = [], None, None
    inicio_na_pagina = {}               # pagina -> [(y, num)] das questoes que comecam nela
    conteudo_na_pagina = {}             # pagina -> linhas de questao lidas nela (0 = folha sem prova)
    for pagina, linhas, _ in paginas:
        for y, linha in linhas:
            s = linha.strip()
            if not s or RX_DESCARTE.search(s):
                continue
            cab = BLOCOS_UERJ.get(_norm_cabecalho(s))
            if cab:
                bloco = cab
                continue
            if bloco is None:                 # capa e instrucoes: nada conta antes do 1o bloco
                continue
            if atual is not None or RX_QUESTAO.match(s):
                conteudo_na_pagina[pagina] = conteudo_na_pagina.get(pagina, 0) + 1
            mq = RX_QUESTAO.match(s)
            if mq and int(mq.group(1)) == (qs[-1]["num"] + 1 if qs else 1):
                atual = {"num": int(mq.group(1)), "bloco": bloco, "pagina": pagina,
                         "_enun": [mq.group(2)], "_alts": [], "figura": False}
                qs.append(atual)
                inicio_na_pagina.setdefault(pagina, []).append((y, atual["num"]))
                continue
            ma = RX_ALT.match(s)
            if ma and atual is not None:
                atual["_alts"].append([ma.group(1).upper(), ma.group(2)])
                continue
            if atual is not None:
                (atual["_alts"][-1] if atual["_alts"] else atual["_enun"]).append(s)
    # a figura e da ultima questao que comeca ACIMA dela na pagina; sem nenhuma acima, e da que
    # vem continuando da pagina anterior (numeracao sequencial: a de numero anterior)
    por_num = {q["num"]: q for q in qs}
    for pagina, caixas in figuras.items():
        if not conteudo_na_pagina.get(pagina):     # folha sem questao (capa, aviso final): nao e figura
            continue
        inicios = sorted(inicio_na_pagina.get(pagina, []))
        anteriores = [n for p, lst in inicio_na_pagina.items() if p < pagina for _, n in lst]
        for caixa in caixas:
            acima = [n for y, n in inicios if y <= caixa[1]]
            dona = acima[-1] if acima else (max(anteriores) if anteriores else None)
            if dona in por_num:
                por_num[dona]["figura"] = True
    for q in qs:
        q["enunciado"] = _juntar(q.pop("_enun"))
        q["alternativas"] = [(a[0], _juntar(a[1:])) for a in q.pop("_alts")]
    return {"capa_n": int(m_n.group(1)) if m_n else None,
            "duracao_h": int(m_h.group(1)) if m_h else None, "questoes": qs}


def problemas(parse, gabarito, esperado=None):
    """Recusas nomeadas do parse contra o gabarito (lista vazia = ok). PURA."""
    qs = parse["questoes"]
    probs = []
    nums = [q["num"] for q in qs]
    if nums != list(range(1, len(nums) + 1)):
        probs.append(f"numeracao com buraco ou fora de ordem: {nums[:5]}...")
    if parse["capa_n"] is not None and len(qs) != parse["capa_n"]:
        probs.append(f"a capa diz {parse['capa_n']} questoes; o parser achou {len(qs)}")
    if len(gabarito) != len(qs):
        probs.append(f"o gabarito tem {len(gabarito)} respostas; o parser achou {len(qs)} questoes")
    if esperado is not None and len(qs) != esperado:
        probs.append(f"--expect {esperado}; o parser achou {len(qs)}")
    for q in qs:
        letras = [a for a, _ in q["alternativas"]]
        if not 4 <= len(letras) <= 5 or letras != list("ABCDE"[:len(letras)]):
            probs.append(f"Q{q['num']}: alternativas {letras or 'nenhuma'} (discursiva ou quebrada)")
        if not q["enunciado"] or any(not t for _, t in q["alternativas"]):
            probs.append(f"Q{q['num']}: enunciado ou alternativa vazia")
        g = str(gabarito.get(str(q["num"]), "")).strip().upper()
        if g != "ANULADA" and g not in letras:
            probs.append(f"Q{q['num']}: gabarito '{g or 'ausente'}' fora das alternativas {letras}")
    return probs


def montar_docs(parse, gabarito, lista, tarefa, banca, agora=None):
    """Docs `questoes/*` (formato da Bancada) e as anuladas que ficaram de fora. PURA."""
    agora = agora or datetime.datetime.now().replace(microsecond=0).isoformat()
    docs, anuladas = [], []
    for q in parse["questoes"]:
        g = str(gabarito[str(q["num"])]).strip().upper()
        if g == "ANULADA":
            anuladas.append(q["num"])
            continue
        doc = {"lista": lista, "tarefa": tarefa, "num": q["num"], "banca": banca, "gabarito": g,
               "emed_id": "", "enunciado": q["enunciado"],
               "alternativas": "\n".join(f"{a}) {t}" for a, t in q["alternativas"]),
               "tags": q["bloco"], "solucao": "", "forum": "", "estatistica": "",
               "capturado_em": agora, "executor": "prova_pdf", "pagina": q["pagina"]}
        if q["figura"]:
            doc["figura"] = True
        docs.append(doc)
    return docs, anuladas


def _com_timeout(func, segundos, *args):
    ex = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    fut = ex.submit(func, *args)
    try:
        return fut.result(timeout=segundos)
    except concurrent.futures.TimeoutError:
        raise Recusa(f"o parser passou de {segundos}s -- nada gravado")
    finally:
        ex.shutdown(wait=False, cancel_futures=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="caderno de prova em PDF -> docs questoes/* (tudo ou nada)")
    ap.add_argument("--pdf", required=True, help="caderno da prova (PDF)")
    ap.add_argument("--formato", choices=("uerj",), default="uerj", help="layout do caderno (so UERJ por ora)")
    ap.add_argument("--edicao", required=True, help="ano da edicao no JSON de gabaritos (ex.: 2021)")
    ap.add_argument("--lista", required=True, help="id da lista no hub: t<tarefa do plano> (ex.: t1793)")
    ap.add_argument("--out", required=True, help="pasta de saida (recebe questoes/ e listas/)")
    ap.add_argument("--gabaritos", default=GABARITOS_UERJ, help="JSON versionado de gabaritos")
    ap.add_argument("--expect", type=int, default=None, help="contagem esperada de questoes (COUNT-ASSERT)")
    ap.add_argument("--timeout", type=int, default=60, help="segundos maximos do parser")
    ap.add_argument("--json", action="store_true", help="resumo em JSON no stdout")
    args = ap.parse_args(argv)
    lista = args.lista.strip()
    if not re.fullmatch(r"t\d+", lista):
        print(f"RECUSA: --lista '{lista}' fora do formato t<tarefa>")
        return 2
    try:
        with open(args.gabaritos, encoding="utf-8") as fh:
            edicao = json.load(fh)["edicoes"].get(str(args.edicao))
        if not edicao:
            raise Recusa(f"edicao {args.edicao} ausente em {args.gabaritos}")
        gabarito = edicao["respostas"]
        parse = _com_timeout(lambda p: parse_uerj(ler_pdf(p)), args.timeout, args.pdf)
        probs = problemas(parse, gabarito, args.expect)
        if probs:
            raise Recusa("; ".join(probs[:8]) + (f" (+{len(probs) - 8})" if len(probs) > 8 else ""))
    except Recusa as e:
        print(f"RECUSA: {e}")
        return 2
    tarefa = int(lista[1:])
    docs, anuladas = montar_docs(parse, gabarito, lista, tarefa, f"UERJ {args.edicao}")
    pasta_q = os.path.join(args.out, "questoes")
    os.makedirs(pasta_q, exist_ok=True)
    for d in docs:
        with open(os.path.join(pasta_q, f"{lista}_{d['num']}.json"), "w", encoding="utf-8") as fh:
            json.dump(d, fh, ensure_ascii=False, indent=2)
    blocos = {}
    for d in docs:
        blocos[d["tags"]] = blocos.get(d["tags"], 0) + 1
    resumo = {"lista": lista, "edicao": str(args.edicao), "questoes": len(docs), "anuladas": anuladas,
              "capa_n": parse["capa_n"], "duracao_h": parse["duracao_h"], "blocos": blocos,
              "figuras": [d["num"] for d in docs if d.get("figura")], "out": args.out}
    if args.json:
        print(json.dumps(resumo, ensure_ascii=False))
    else:
        print(f"{len(docs)} questoes em {pasta_q} (capa {parse['capa_n']}, {parse['duracao_h']}h)"
              + (f"; anuladas fora: {anuladas}" if anuladas else "")
              + (f"; com figura: {resumo['figuras']}" if resumo["figuras"] else ""))
        print("blocos: " + ", ".join(f"{b} {n}" for b, n in blocos.items()))
        print(f"proximo: python tools/emed_banco.py --ingerir {args.out} --apply --expect {len(docs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
