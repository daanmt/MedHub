"""emed_api.py -- lista do EMED -> docs `questoes/*` do hub pela API do EMED, SEM LLM (s202).

Decisao do operador (26/09/2026, confirmada por ele no canal do agente de estudo): a fonte do
gabarito das listas EMED e a API que a plataforma paga por ele ja expoe -- "extrair a questao,
alternativas e gabarito, que e dado publico". Reverte a recusa da s199 (token = credencial; risco
de bloqueio da conta), com o risco declarado e assumido por ele. O comentario do professor NAO
entra em PDF, disco, log ou db, nem transitoriamente por escrito. Endpoint e mapa de campos = o
relatorio do executor na s198 (`cic-0003`); o PDF segue sendo o caminho das provas de banca (UERJ).

WHITELIST NA FRONTEIRA: `extrair()` e a UNICA funcao que le um item da resposta; devolve um dict
NOVO so com o escopo publico, e o resto do item (solucao, forum, estatistica, video, percentuais,
resposta do usuario) morre em memoria. Nada da resposta crua e impresso ou gravado -- nem no erro:
a recusa cita numero, emed_id e NOME de chave, nunca valor. `--esquema` imprime so a arvore de
chaves e tipos, para manter o mapa de campos sem ler conteudo.

TOKEN: sessao do operador, posta por ELE em `.emed_token` (linha 1 = o Bearer; linha 2 opcional =
x-requester-id) ou na env EMED_TOKEN. Recusa se o arquivo estiver RASTREADO pelo git ou fora do
.gitignore; o token nunca e impresso. O agente nunca le o token do navegador.

RITMO: 1 lista por corrida, per_page 20 (o maximo da UI), pausa entre paginas. Sem `--apply` e
dry-run (busca, valida e resume; nada gravado). `--apply` exige `--expect` confirmado pelo operador.

TUDO OU NADA (as regras do prova_pdf): contagem != --expect; questao com 1-3 ou 6+ alternativas;
gabarito ausente ou duplo; enunciado ou alternativa vazia; emed_id repetido (inclusive API que
ignora `page`) -> recusa nomeada e a pasta nem e criada. DISCURSIVA (zero alternativas) SAI e e
DECLARADA por numero (decisao (b) do /ai-eng): achadas = gravadas + declaradas = --expect.

Saida = o formato da Bancada: `<OUT>/questoes/<lista>_<num>.json`, consumido por
`emed_banco.py --ingerir <OUT> --apply --expect N`. `num` = a posicao na lista do EMED (a mesma
numeracao "Questao N" da pagina): a discursiva deixa o buraco.

LIMITE DECLARADO: o mapa de campos de `exams[]` e `topics[]` e o do relatorio do executor, nao o de
um contrato publicado -- a API e interna e pode mudar sem aviso; campo ausente = recusa que manda
rodar `--esquema`. Figura: `<img>` no enunciado ou alternativa marca `figura`, a imagem nao viaja.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_PADRAO = os.path.join(ROOT, ".emed_token")
OUT_PADRAO = os.path.join(ROOT, "tmp", "emed_api")
API = "https://api.estrategia.com/bff/questions/notebooks/{caderno}/questions"
PER_PAGE = 20
MAX_PAGINAS = 30

#: O que um doc gravado pode carregar: o escopo publico (whitelist do operador/`/ai-eng`) ...
CHAVES_PUBLICAS = ("emed_id", "num", "banca", "ano", "enunciado", "alternativas", "gabarito", "tags")
#: ... e os metadados do pipeline, que nao vem da API (`figura` e derivado do enunciado).
CHAVES_META = ("lista", "tarefa", "capturado_em", "executor", "figura")
#: O que `extrair` devolve (antes de virar doc): `gabaritos` e a lista, para a recusa contar.
CHAVES_EXTRAIDAS = ("emed_id", "banca", "ano", "enunciado", "alternativas", "gabaritos", "tags", "figura")

RX_CADERNO = re.compile(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", re.I)


class Recusa(Exception):
    """Problema nomeado: nada e escrito. A mensagem nunca carrega valor da resposta nem o token."""


# ------------------------------------------------------------------ html -> texto

class _Texto(HTMLParser):
    """Texto de um trecho HTML por parser (nunca regex: '<190' e texto, nao tag -- licao F108)."""
    QUEBRA = {"p", "div", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "ul", "ol", "table"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.partes, self.figura = [], False

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            self.figura = True
        elif tag == "br" or tag in self.QUEBRA:
            self.partes.append("\n")

    def handle_endtag(self, tag):
        if tag in self.QUEBRA:
            self.partes.append("\n")
        elif tag in ("td", "th"):
            self.partes.append(" ")

    def handle_data(self, data):
        self.partes.append(data)


def html_para_texto(valor):
    """(texto, figura) de um campo HTML da API. PURA."""
    p = _Texto()
    p.feed(str(valor or ""))
    p.close()
    linhas = [re.sub(r"[ \t ]+", " ", ln).strip() for ln in "".join(p.partes).split("\n")]
    return "\n".join(ln for ln in linhas if ln), p.figura


# ------------------------------------------------------------------ whitelist na fronteira

def _campo(obj, chave, ref):
    if not isinstance(obj, dict) or chave not in obj:
        raise Recusa(f"campo '{chave}' ausente na resposta (emed_id {ref}) -- rode --esquema")
    return obj[chave]


def _banca_ano(exames, ref):
    """'<instituicao>, <ano>' (o formato da captura t3 da s199) e o ano, do 1o exame."""
    if not isinstance(exames, list) or not exames:
        raise Recusa(f"'exams' vazio (emed_id {ref}) -- questao sem banca fica fora do escopo publico")
    ex = exames[0]
    inst = _campo(ex, "institution", ref)
    nome = str(_campo(inst, "name", ref) if isinstance(inst, dict) else inst).strip()
    ano = str(_campo(ex, "year", ref) or "").strip()
    return (f"{nome}, {ano}" if ano else nome), ano


def _tags(topicos):
    nomes = [str(t.get("name", "")).strip() for t in (topicos or []) if isinstance(t, dict)]
    return " > ".join(n for n in nomes if n)


def extrair(item):
    """UM item cru da API -> dict NOVO com `CHAVES_EXTRAIDAS`. A unica leitura do item: nada
    fora da whitelist sai daqui. PURA."""
    ref = str(item.get("id", "?")) if isinstance(item, dict) else "?"
    emed_id = str(_campo(item, "id", ref))
    enunciado, figura = html_para_texto(_campo(item, "statement_text", ref))
    alternativas, gabaritos = [], []
    for i, alt in enumerate(_campo(item, "alternatives", ref) or []):
        texto, fig_alt = html_para_texto(_campo(alt, "sanitized_body", ref))
        letra = "ABCDEFGHIJ"[i] if i < 10 else "?"
        alternativas.append((letra, texto))
        figura = figura or fig_alt
        if _campo(alt, "correct", ref) is True:
            gabaritos.append(letra)
    banca, ano = _banca_ano(_campo(item, "exams", ref), ref)
    return {"emed_id": emed_id, "banca": banca, "ano": ano, "enunciado": enunciado,
            "alternativas": alternativas, "gabaritos": gabaritos,
            "tags": _tags(item.get("topics")), "figura": figura}


def esquema(resposta):
    """Arvore de CHAVES e tipos da resposta (uniao dos itens) -- nenhum valor. PURA."""
    caminhos = {}

    def andar(v, p):
        if isinstance(v, dict):
            if not v:
                caminhos.setdefault(p or "(raiz)", set()).add("dict vazio")
            for k, x in v.items():
                andar(x, f"{p}.{k}" if p else str(k))
        elif isinstance(v, list):
            if not v:
                caminhos.setdefault(p + "[]", set()).add("vazia")
            for x in v:
                andar(x, p + "[]")
        else:
            caminhos.setdefault(p or "(raiz)", set()).add(type(v).__name__)
    andar(resposta, "")
    return [f"{c}: {'|'.join(sorted(t))}" for c, t in sorted(caminhos.items())]


# ------------------------------------------------------------------ rede (a unica funcao que a toca)

def mensagem_http(codigo):
    dica = {401: " -- token expirado ou invalido: recopie a sessao para .emed_token",
            403: " -- acesso negado: token sem permissao para esta lista",
            429: " -- a plataforma pediu para ir mais devagar: PARE e relate"}
    return f"HTTP {codigo} da API do EMED{dica.get(codigo, '')}"


def _get_json(url, headers, timeout=30):
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise Recusa(mensagem_http(e.code)) from None
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        raise Recusa(f"falha de rede ou de formato: {type(e).__name__}") from None


def _dormir(segundos):
    time.sleep(segundos)


def _itens(resposta):
    if isinstance(resposta, list):
        return resposta
    if isinstance(resposta, dict):
        for k in ("data", "questions", "items", "results"):
            if isinstance(resposta.get(k), list):
                return resposta[k]
        raise Recusa(f"resposta sem lista de questoes (chaves: {sorted(resposta)[:12]}) -- rode --esquema")
    raise Recusa(f"resposta de tipo {type(resposta).__name__} -- rode --esquema")


def _url(caderno, pagina, per_page):
    return (API.format(caderno=caderno)
            + f"?page={pagina}&per_page={per_page}&order=asc&sort=order_index")


def coletar(caderno, headers, per_page=PER_PAGE, pausa=2.0):
    """Todas as paginas, na ordem da lista, JA passadas pela whitelist: o item cru nao sobrevive
    a iteracao. Devolve (questoes extraidas, paginas lidas)."""
    qs, vistos = [], set()
    for pagina in range(1, MAX_PAGINAS + 1):
        if pagina > 1:
            _dormir(pausa)
        itens = _itens(_get_json(_url(caderno, pagina, per_page), headers))
        for item in itens:
            q = extrair(item)
            if q["emed_id"] in vistos:
                raise Recusa(f"emed_id repetido ({q['emed_id']}, pagina {pagina}) -- a API ignorou "
                             "a paginacao ou a lista mudou durante a leitura")
            vistos.add(q["emed_id"])
            qs.append(q)
        if len(itens) < per_page:
            return qs, pagina
    raise Recusa(f"passou de {MAX_PAGINAS} paginas -- lista grande demais para 1 corrida")


# ------------------------------------------------------------------ validacao e docs

def problemas(qs, esperado=None):
    """Recusas nomeadas (lista vazia = ok) e as discursivas declaradas. PURA."""
    probs, discursivas = [], []
    for num, q in enumerate(qs, 1):
        n = len(q["alternativas"])
        if n == 0:
            discursivas.append(num)
            continue
        if not 4 <= n <= 5:
            probs.append(f"Q{num}: {n} alternativas (emed_id {q['emed_id']})")
        if len(q["gabaritos"]) != 1:
            probs.append(f"Q{num}: {len(q['gabaritos'])} alternativas corretas (emed_id {q['emed_id']})")
        if not q["enunciado"] or any(not t for _, t in q["alternativas"]):
            probs.append(f"Q{num}: enunciado ou alternativa vazia (emed_id {q['emed_id']})")
    if esperado is not None and len(qs) != esperado:
        probs.append(f"achadas {len(qs)} ({len(qs) - len(discursivas)} gravaveis + "
                     f"{len(discursivas)} discursiva(s) declarada(s)) != --expect {esperado}")
    return probs, discursivas


def montar_docs(qs, lista, tarefa, agora=None):
    """Docs `questoes/*` so com `CHAVES_PUBLICAS` + `CHAVES_META`; discursivas ficam fora. PURA."""
    agora = agora or datetime.datetime.now().replace(microsecond=0).isoformat()
    docs = []
    for num, q in enumerate(qs, 1):
        if not q["alternativas"]:
            continue
        doc = {"lista": lista, "tarefa": tarefa, "num": num, "emed_id": q["emed_id"],
               "banca": q["banca"], "ano": q["ano"], "enunciado": q["enunciado"],
               "alternativas": "\n".join(f"{a}) {t}" for a, t in q["alternativas"]),
               "gabarito": q["gabaritos"][0], "tags": q["tags"],
               "capturado_em": agora, "executor": "emed_api"}
        if q["figura"]:
            doc["figura"] = True
        docs.append(doc)
    return docs


def conferir(docs, banco):
    """Lente 2: emed_id e gabarito por numero contra o que o `ipub.db` ja tem da lista. PURA."""
    api = {int(d["num"]): d for d in docs}
    ja = {int(r["num"]): r for r in banco}
    iguais, divergentes = [], {}
    for n in sorted(set(api) & set(ja)):
        campos = [c for c in ("emed_id", "gabarito")
                  if str(api[n].get(c) or "").strip().upper() != str(ja[n].get(c) or "").strip().upper()]
        if campos:
            divergentes[n] = campos
        else:
            iguais.append(n)
    return {"iguais": iguais, "divergentes": divergentes,
            "so_no_banco": sorted(set(ja) - set(api)), "so_na_api": sorted(set(api) - set(ja))}


def _gravar(docs, lista, out):
    permitidas = set(CHAVES_PUBLICAS) | set(CHAVES_META)
    for d in docs:                            # a 2a trava da whitelist, antes de qualquer byte
        sobra = set(d) - permitidas
        if sobra:
            raise Recusa(f"Q{d.get('num')}: chave fora da whitelist {sorted(sobra)}")
    pasta = os.path.join(out, "questoes")
    os.makedirs(pasta, exist_ok=True)
    for d in docs:
        with open(os.path.join(pasta, f"{lista}_{d['num']}.json"), "w", encoding="utf-8") as fh:
            json.dump(d, fh, ensure_ascii=False, indent=2)
    return pasta


# ------------------------------------------------------------------ token e caderno

def _dentro(caminho, raiz):
    try:
        return os.path.commonpath([os.path.abspath(caminho), os.path.abspath(raiz)]) == os.path.abspath(raiz)
    except ValueError:                        # outro disco no Windows
        return False


def ler_credencial(caminho=TOKEN_PADRAO, env=None, raiz=ROOT):
    """Cabecalhos da sessao do operador. Env EMED_TOKEN vence o arquivo. Nunca imprime o token."""
    env = os.environ if env is None else env
    token = (env.get("EMED_TOKEN") or "").strip()
    req_id = (env.get("EMED_REQUESTER_ID") or "").strip()
    if not token:
        if not os.path.isfile(caminho):
            raise Recusa(f"sem token: o operador poe a sessao em {caminho} (linha 1) ou na env EMED_TOKEN")
        if _dentro(caminho, raiz):
            rastreado = subprocess.run(["git", "-C", raiz, "ls-files", "--error-unmatch", "--", caminho],
                                       capture_output=True).returncode == 0
            if rastreado:
                raise Recusa("o arquivo do token esta RASTREADO pelo git -- tire do indice "
                             "(git rm --cached) e troque a sessao no EMED")
            ignorado = subprocess.run(["git", "-C", raiz, "check-ignore", "-q", "--", caminho],
                                      capture_output=True).returncode == 0
            if not ignorado:
                raise Recusa("o arquivo do token nao esta no .gitignore -- nada lido")
        with open(caminho, encoding="utf-8") as fh:
            linhas = [ln.strip() for ln in fh.read().splitlines() if ln.strip()]
        token = linhas[0] if linhas else ""
        req_id = req_id or (linhas[1] if len(linhas) > 1 else "")
    token = re.sub(r"^(authorization:\s*)?bearer\s+", "", token, flags=re.I).strip()
    if not token:
        raise Recusa("token vazio")
    headers = {"Authorization": f"Bearer {token}", "x-vertical": "medicina",
               "Accept": "application/json", "User-Agent": "medhub-emed-api/1 (uso pessoal)"}
    req_id = re.sub(r"^x-requester-id:\s*", "", req_id, flags=re.I).strip()
    if req_id:
        headers["x-requester-id"] = req_id
    return headers


def caderno_da_lista(plano, caderno_arg):
    """UUID do caderno: o link da tarefa no plano manda; `--caderno` so vale igual a ele ou sem link."""
    do_plano = RX_CADERNO.search((plano or {}).get("url_lista") or "")
    do_arg = RX_CADERNO.search(caderno_arg or "")
    if do_plano and do_arg and do_plano.group(1).lower() != do_arg.group(1).lower():
        raise Recusa("--caderno difere do link da tarefa no plano -- conferir qual lista e")
    achado = do_plano or do_arg
    if not achado:
        raise Recusa("sem caderno: a tarefa nao tem link de lista no plano e --caderno nao veio")
    return achado.group(1).lower()


# ------------------------------------------------------------------ CLI

def main(argv=None):
    ap = argparse.ArgumentParser(
        description="lista do EMED -> docs questoes/* pela API (sem LLM; whitelist; tudo ou nada)")
    ap.add_argument("--lista", required=True, help="id da lista no hub: t<tarefa do plano> (ex.: t3)")
    ap.add_argument("--caderno", default=None, help="UUID ou URL do caderno (default: o link da tarefa no plano)")
    ap.add_argument("--expect", type=int, default=None,
                    help="questoes ACHADAS na lista, confirmado pelo operador (discursivas incluidas)")
    ap.add_argument("--apply", action="store_true", help="grava os docs em --out (sem ele: dry-run)")
    ap.add_argument("--out", default=None, help="pasta de saida (default tmp/emed_api/<lista>)")
    ap.add_argument("--token-arquivo", default=TOKEN_PADRAO, help="arquivo gitignored com a sessao (default .emed_token)")
    ap.add_argument("--pausa", type=float, default=2.0, help="segundos entre paginas (default 2)")
    ap.add_argument("--esquema", action="store_true", help="imprime so as chaves e tipos da 1a pagina e sai")
    ap.add_argument("--conferir", action="store_true", help="lente 2: emed_id e gabarito contra o ipub.db")
    ap.add_argument("--json", action="store_true", help="resumo em JSON no stdout")
    args = ap.parse_args(argv)
    lista = args.lista.strip()
    try:
        if not re.fullmatch(r"t\d+", lista):
            raise Recusa(f"--lista '{lista}' fora do formato t<tarefa>")
        if args.apply and args.expect is None:
            raise Recusa("--apply exige --expect (a contagem que o operador confirmou) -- nada buscado")
        sys.path.insert(0, ROOT)
        from app.utils import db
        tarefa = int(lista[1:])
        caderno = caderno_da_lista(db.plano_obter(tarefa), args.caderno)
        headers = ler_credencial(args.token_arquivo)
        if args.esquema:
            for linha in esquema(_get_json(_url(caderno, 1, PER_PAGE), headers)):
                print(linha)
            return 0
        qs, paginas = coletar(caderno, headers, pausa=args.pausa)
        probs, discursivas = problemas(qs, args.expect)
        if probs:
            raise Recusa("; ".join(probs[:8]) + (f" (+{len(probs) - 8})" if len(probs) > 8 else ""))
        docs = montar_docs(qs, lista, tarefa)
        conf = conferir(docs, db.emed_listar_questoes(lista)) if args.conferir else None
        out = args.out or os.path.join(OUT_PADRAO, lista)
        pasta = _gravar(docs, lista, out) if args.apply else None
    except Recusa as e:
        print(f"RECUSA: {e}")
        return 2
    resumo = {"lista": lista, "caderno": caderno, "paginas": paginas, "achadas": len(qs),
              "gravadas": len(docs), "discursivas": discursivas,
              "figuras": [d["num"] for d in docs if d.get("figura")],
              "aplicado": bool(args.apply), "out": pasta, "conferencia": conf}
    if args.json:
        print(json.dumps(resumo, ensure_ascii=False))
        return 0
    print(("" if args.apply else "dry-run (nada gravado; use --apply --expect N): ")
          + f"{len(qs)} achadas em {paginas} pagina(s) = {len(docs)} gravaveis"
          + (f" + discursivas declaradas {discursivas}" if discursivas else "")
          + (f"; com figura: {resumo['figuras']}" if resumo["figuras"] else ""))
    if conf is not None:
        print(f"conferencia com o ipub.db: {len(conf['iguais'])} iguais; divergentes {conf['divergentes'] or '-'}; "
              f"so no banco {conf['so_no_banco'] or '-'}; so na API {conf['so_na_api'] or '-'}")
    if pasta:
        print(f"gravado em {pasta}")
        print(f"proximo: python tools/emed_banco.py --ingerir {out} --apply --expect {len(docs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
