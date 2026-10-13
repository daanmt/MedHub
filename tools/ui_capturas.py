"""ui_capturas.py -- confere a UI do hub em navegador real: Edge headless + db falso, cena x largura (s225).

Regra da casa (s211): tela nova do hub so publica conferida em navegador real -- hub em scratch +
db falso + Edge a 390 px. Ate a s224 o kit vivia solto em `tmp/` (gitignorado) e cada sessao o
remontava a mao; agora e 1 comando:

    python tools/ui_capturas.py                                  # todas as cenas a 390, 768 e 1280
    python tools/ui_capturas.py --cenas revelada,fim --larguras 390

COMO: monta um site local em `<out>/site` -- `hub.html` = o cabecalho versionado
`core/templates/ui_harness.html` (db falso semeado + roteiro de cenas + medida) + o `index.html` do
build do hub (`--hub`); as aulas de `artifacts/aula-*.html`, os resumos do build e o painel
(manifesto do build ou `artifacts/painel.html`); `frame.html` = moldura com um iframe da largura
pedida. Serve por `http.server` em 127.0.0.1 e roda UMA vez o Edge headless por cena x largura,
com `--screenshot` (o PNG) e `--dump-dom` (a medida). O layout do Edge headless nao desce de ~500
px, por isso o iframe: a janela do tamanho exato do iframe recorta a foto nele. Cada corrida usa um
perfil novo (apagado no fim), entao o localStorage parte vazio e a cena e deterministica.

CENAS (o harness le `?cena=` e prepara o estado ANTES do hub rodar; depois toca a tela):
  painel · teoria · listas (aba Listas, modo Questoes) · simulados (modo Simulados) ·
  questao (1a lista com questoes, uma questao sem resposta; se a lista ja estava toda respondida, a
  resposta da 1a questao e podada no db falso) · revelada (questao respondida e revelada com a
  cadeia; prefere errada/duvida/chute com elos declarados) · fim (tela de fim da lista da
  `revelada`; questoes sem resposta saem do db falso) · cards (frente do 1o card; as notas da sessao
  saem do db falso) · verso (o card virado) · aula / resumo (leitor com o 1o link de cada tipo).
  Cena que o seed nao monta e dita com o motivo e as demais seguem.

MEDIDA (por cena x largura): rolagem horizontal do documento do hub dentro do iframe (scrollWidth >
clientWidth) e de cada iframe visivel (painel, leitor); havendo, os 5 elementos que passam da borda
direita -- pela caixa ou pelo texto (nowrap, palavra longa) -- fora de conteiner com overflow
proprio, com seletor curto. Mais os erros de JS da pagina.

SEED: docs JSON do db do hub baixados para `tmp/` (caminho relativo = id do doc). Default:
`tmp/hub_db`, `tmp/bancada` e o `tmp/player_*_db` de nome maior (a sessao mais recente), pulando o
que nao existe; `--seed` troca a lista inteira e a pasta posterior vence a anterior no mesmo id.
🔒 Tem conteudo do EMED: o seed so e lido de `tmp/` e tudo e escrito em `tmp/` (gitignorado) --
`--seed` e `--out` fora dele sao recusados. Nada e publicado e o db do hub nao e tocado.

SAIDA: tabela cena x largura -> PNG e `ok`/`ROLA` (+ elementos); `<out>/resultado.json` com tudo.
Exit 0 mesmo com rolagem ou cena nao montada (e sensor); exit 1 so para erro de uso ou de ambiente
(Edge ausente, `--hub` sem index.html, pasta fora de `tmp/`, porta reservada ou ocupada, nenhum PNG).

LIMITES DECLARADOS: a foto e a janela (ALTURA px a partir do topo), nao a pagina inteira; o estado
da cena sai de poda no db falso (e a tela, nao o dado); Google Fonts vem da rede (offline = fonte de
fallback); a medida ve a pagina e os iframes visiveis, nao a rolagem local de conteiner com overflow
proprio (ex.: tabela que rola por dentro).
"""
from __future__ import annotations

import argparse
import concurrent.futures
import functools
import html
import http.server
import json
import os
import re
import shutil
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode

RAIZ = Path(__file__).resolve().parents[1]
TMP = RAIZ / "tmp"
HARNESS = RAIZ / "core" / "templates" / "ui_harness.html"
MARCA_SEED = "/*@ui:seed*/null"

CENAS = ("painel", "teoria", "listas", "simulados", "questao", "revelada", "fim",
         "cards", "verso", "aula", "resumo")
LARGURAS_PADRAO = (390, 768, 1280)
ALTURA = 1800                  # altura da janela = da foto (2 telas de celular a 390)
ORCAMENTO_MS = 20000           # --virtual-time-budget: a cena mais lenta (leitor) pede ~5 s virtuais
PARALELO = 4                   # corridas do Edge ao mesmo tempo (cada uma com perfil proprio)
PORTAS_RESERVADAS = (8766, 8767)
EDGE_CANDIDATOS = (
    "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
)

FRAME_HTML = """<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8"><title>ui_capturas</title>
<style>html,body{margin:0;padding:0;overflow:hidden;background:#000}iframe{display:block;border:0}</style></head>
<body><iframe id="ui-quadro" title="MedHub"></iframe><pre id="ui-resultado" hidden></pre>
<script>
var P = new URLSearchParams(location.search), f = document.getElementById("ui-quadro");
f.style.width = (parseInt(P.get("w"), 10) || 390) + "px";
f.style.height = (parseInt(P.get("h"), 10) || 1800) + "px";
f.src = "hub.html" + location.search;
</script></body></html>
"""


class ErroDeUso(Exception):
    """Erro de uso ou de ambiente: o main imprime e sai 1."""


# ------------------------------------------------------------------ argumentos
def parse_larguras(texto):
    """'390,768,1280' -> [390, 768, 1280] (sem repetir, na ordem dada). ValueError se invalido."""
    out = []
    for parte in str(texto or "").split(","):
        parte = parte.strip()
        if not parte:
            continue
        if not parte.isdigit():
            raise ValueError("largura invalida: %r (inteiro em px)" % parte)
        n = int(parte)
        if not 200 <= n <= 4000:
            raise ValueError("largura fora de 200-4000 px: %d" % n)
        if n not in out:
            out.append(n)
    if not out:
        raise ValueError("nenhuma largura em %r" % texto)
    return out


def parse_cenas(texto):
    """'revelada,fim' -> ['revelada', 'fim']; vazio ou 'todas' -> todas. ValueError se desconhecida."""
    if texto is None or str(texto).strip().lower() in ("", "todas"):
        return list(CENAS)
    out = []
    for parte in str(texto).split(","):
        parte = parte.strip().lower()
        if not parte:
            continue
        if parte not in CENAS:
            raise ValueError("cena desconhecida: %r (validas: %s)" % (parte, ", ".join(CENAS)))
        if parte not in out:
            out.append(parte)
    if not out:
        raise ValueError("nenhuma cena em %r" % texto)
    return out


def dentro_de(caminho, raiz):
    """True se `caminho` (absoluto ou relativo ao cwd) fica DENTRO de `raiz`."""
    p = os.path.normcase(os.path.abspath(str(caminho)))
    r = os.path.normcase(os.path.abspath(str(raiz)))
    return p.startswith(r.rstrip("\\/") + os.sep)


def _resolver(p):
    """Caminho relativo vale a partir da raiz do repo (o tool roda de qualquer cwd)."""
    p = Path(p)
    return p if p.is_absolute() else RAIZ / p


# ----------------------------------------------------------------------- seed
def seeds_padrao(tmp=TMP):
    """tmp/hub_db, tmp/bancada e o tmp/player_*_db de nome maior -- so os que existem."""
    tmp = Path(tmp)
    out = [tmp / n for n in ("hub_db", "bancada") if (tmp / n).is_dir()]
    players = sorted(p for p in tmp.glob("player_*_db") if p.is_dir())
    if players:
        out.append(players[-1])
    return out


def montar_seed(pastas):
    """{id_do_doc: doc} das pastas, em ordem (a posterior vence). id = caminho relativo sem `.json`.

    So entra arquivo `.json` que e um objeto (doc do db); o resto e contado em `ignorados`.
    Devolve (seed, {"docs", "ignorados", "por_colecao"}).
    """
    seed, ignorados = {}, 0
    for raiz in pastas:
        raiz = Path(raiz)
        for dp, dns, fns in os.walk(raiz):
            dns.sort()
            for fn in sorted(fns):
                if not fn.endswith(".json"):
                    continue
                p = Path(dp) / fn
                try:
                    doc = json.loads(p.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    ignorados += 1
                    continue
                if not isinstance(doc, dict):
                    ignorados += 1
                    continue
                seed[p.relative_to(raiz).as_posix()[:-5]] = doc
    por = {}
    for k in seed:
        col = k.split("/")[0] if "/" in k else "(raiz)"
        por[col] = por.get(col, 0) + 1
    return seed, {"docs": len(seed), "ignorados": ignorados, "por_colecao": dict(sorted(por.items()))}


def seed_js(seed):
    """O seed como literal JS seguro dentro de <script>: JSON com < > & U+2028 U+2029 escapados."""
    txt = json.dumps(seed, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    for c, e in (("<", "\\u003c"), (">", "\\u003e"), ("&", "\\u0026"),
                 ("\u2028", "\\u2028"), ("\u2029", "\\u2029")):
        txt = txt.replace(c, e)
    return txt


def html_harness(seed, hub_index, cabeca):
    """A pagina de teste: cabecalho do harness com o SEED + <body> + o index.html do hub."""
    if cabeca.count(MARCA_SEED) != 1:
        raise ErroDeUso("%s precisa ter a marca %s exatamente 1x" % (HARNESS.name, MARCA_SEED))
    if "</head>" not in cabeca:
        raise ErroDeUso("%s precisa terminar o <head>" % HARNESS.name)
    return cabeca.replace(MARCA_SEED, seed_js(seed)) + "\n<body>\n" + hub_index + "\n</body></html>\n"


# ------------------------------------------------------------------- o build
_RE_LOTE = re.compile(r'<script id="lote" type="application/json">(.*?)</script>', re.S)
_RE_A = re.compile(r"<a\b[^>]*>", re.I)
_RE_CLASSE_AULA = re.compile(r'\bclass="[^"]*\bhub-aula\b')
_RE_HREF = re.compile(r'\bhref="([^"]*)"')
_RE_SLUG_RUIM = re.compile(r"[^a-z0-9._-]+")


def ler_lote(hub_index):
    """O lote embutido na aba Cards ({} se nao houver ou nao for JSON)."""
    m = _RE_LOTE.search(hub_index)
    if not m:
        return {}
    try:
        lote = json.loads(m.group(1))
    except ValueError:
        return {}
    return lote if isinstance(lote, dict) else {}


def primeiro_link(hub_index, prefixo):
    """href do 1o `a.hub-aula` da aba Teoria que comeca com `prefixo` (o que o harness clica)."""
    i = hub_index.find('id="aba-aulas"')
    if i < 0:
        return None
    j = hub_index.find('id="aba-cards"', i)
    trecho = hub_index[i:j if j > 0 else len(hub_index)]
    for tag in _RE_A.findall(trecho):
        h = _RE_HREF.search(tag)
        if h and _RE_CLASSE_AULA.search(tag) and h.group(1).startswith(prefixo):
            return h.group(1)
    return None


def slug_aula(nome):
    """`aula-hernias.html` -> `hernias` -- paridade com `tools/hub.py::slug_de` (o path publicado)."""
    base = nome[:-5] if nome.lower().endswith(".html") else nome
    if base.lower().startswith("aula-"):
        base = base[5:]
    return _RE_SLUG_RUIM.sub("-", base.lower()).strip("-") or "aula"


def _caminho_publicado_ok(pub):
    p = str(pub).replace("\\", "/")
    return bool(p) and not p.startswith("/") and ":" not in p and ".." not in p.split("/")


def montar_site(site, hub_dir, seed, cabeca):
    """Escreve o site em `site` (recriado). Devolve {"aulas", "resumos", "painel"}."""
    site, hub_dir = Path(site), Path(hub_dir)
    if site.exists():
        shutil.rmtree(site)
    (site / "aulas").mkdir(parents=True)
    (site / "resumos").mkdir()
    n_aulas = n_res = 0
    for f in sorted((RAIZ / "artifacts").glob("aula-*.html")):
        shutil.copyfile(f, site / "aulas" / (slug_aula(f.name) + ".html"))
        n_aulas += 1
    for f in sorted((hub_dir / "resumos").glob("*.html")):
        shutil.copyfile(f, site / "resumos" / f.name)
        n_res += 1
    files = {}
    man = hub_dir / "manifesto.json"
    if man.is_file():
        try:
            files = json.loads(man.read_text(encoding="utf-8")).get("files") or {}
        except (OSError, ValueError, AttributeError):
            files = {}
    for pub, fonte in sorted(files.items()):
        src = _resolver(fonte) if fonte else None
        if src is None or not src.is_file() or not _caminho_publicado_ok(pub):
            continue
        destino = site / pub
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, destino)
    painel = site / "painel.html"
    if not painel.exists() and (RAIZ / "artifacts" / "painel.html").is_file():
        shutil.copyfile(RAIZ / "artifacts" / "painel.html", painel)
    hub_index = (hub_dir / "index.html").read_text(encoding="utf-8")
    (site / "hub.html").write_text(html_harness(seed, hub_index, cabeca), encoding="utf-8")
    (site / "frame.html").write_text(FRAME_HTML, encoding="utf-8")
    return {"aulas": n_aulas, "resumos": n_res, "painel": painel.exists()}


# ------------------------------------------------------------------ o roteiro
def _num(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _diretos(seed, col):
    pre = col + "/"
    for k, d in seed.items():
        if k.startswith(pre) and "/" not in k[len(pre):]:
            yield k[len(pre):], d


def listas_visiveis(seed):
    """As listas que a aba Listas desenha (o filtro de `qzRenderListas`), na ordem da tela:
    Questoes antes de Simulados, abertas antes das resolvidas, depois semana, seq e id."""
    out = [(lid, d) for lid, d in _diretos(seed, "listas")
           if (d.get("status") or "pendente") not in ("pendente", "bloqueada", "em_curso")]
    out.sort(key=lambda x: (x[1].get("area") == "Simulado", x[1].get("status") == "resolvida",
                            _num(x[1].get("semana")) or 999, _num(x[1].get("seq")) or 0, x[0]))
    return out


def _por_lista(seed, col):
    """{lista: {num: doc}} de `questoes` ou `respostas` (pelo campo `lista`, como o hub consulta)."""
    m = {}
    for _id, d in _diretos(seed, col):
        lista, num = d.get("lista"), _num(d.get("num"))
        if isinstance(lista, str) and lista and num:
            m.setdefault(lista, {})[num] = d
    return m


def _cadeia(q):
    s = q.get("solucao_medhub")
    c = s.get("cadeia") if isinstance(s, dict) else None
    return c if isinstance(c, list) else []


def planejar(cenas, seed, hub_index, site):
    """[{cena, params, info} | {cena, motivo}] -- o que o harness monta, decidido sobre o seed. PURA
    salvo `site` (confere que o arquivo que a cena abre existe)."""
    site = Path(site)
    qs, rs = _por_lista(seed, "questoes"), _por_lista(seed, "respostas")
    com_q = [(lid, d) for lid, d in listas_visiveis(seed) if qs.get(lid)]

    def modo(d):
        return "simulados" if d.get("area") == "Simulado" else "questoes"

    alvo_rev = None
    cands = []
    for ordem, (lid, d) in enumerate(com_q):
        for num, q in qs[lid].items():
            r, cad = rs.get(lid, {}).get(num), _cadeia(q)
            if not r or not cad:
                continue
            declarar = (not r.get("correta")) or r.get("confianca") != "solida"
            declarados = isinstance(r.get("elos"), list) and len(r["elos"]) == len(cad)
            cands.append((0 if declarar and declarados else (1 if declarar else 2), ordem, num, lid))
    if cands:
        _, ordem, num, lid = min(cands)
        alvo_rev = (lid, num, com_q[ordem][1])
    lista_fim = None
    if alvo_rev:
        lista_fim = (alvo_rev[0], alvo_rev[2])
    else:
        for lid, d in com_q:
            if set(qs[lid]) & set(rs.get(lid, {})):
                lista_fim = (lid, d)
                break
    lote = ler_lote(hub_index)
    n_cards = len(lote.get("cards") or [])

    fixas = {"teoria": "aba Teoria", "listas": "aba Listas, modo Questoes", "simulados": "aba Listas, modo Simulados"}
    plano = []
    for cena in cenas:
        if cena in fixas:
            plano.append({"cena": cena, "params": {}, "info": fixas[cena]})
        elif cena == "painel":
            if (site / "painel.html").is_file():
                plano.append({"cena": cena, "params": {}, "info": "painel.html"})
            else:
                plano.append({"cena": cena, "motivo": "sem painel.html (nem no manifesto do build nem em artifacts/)"})
        elif cena == "questao":
            if not com_q:
                plano.append({"cena": cena, "motivo": "nenhuma lista visivel com questoes no seed (listas/* fora de pendente + questoes/* com o campo lista)"})
                continue
            lid, d = com_q[0]
            nums = sorted(qs[lid])
            livres = [n for n in nums if n not in rs.get(lid, {})]
            num = livres[0] if livres else nums[0]
            plano.append({"cena": cena, "params": {"lista": lid, "num": num, "modo": modo(d)},
                          "info": "lista %s, Q%d%s" % (lid, num, "" if livres else " (resposta podada no db falso)")})
        elif cena == "revelada":
            if not alvo_rev:
                plano.append({"cena": cena, "motivo": "nenhuma questao respondida com solucao_medhub.cadeia no seed"})
                continue
            lid, num, d = alvo_rev
            plano.append({"cena": cena, "params": {"lista": lid, "num": num, "modo": modo(d)},
                          "info": "lista %s, Q%d" % (lid, num)})
        elif cena == "fim":
            if not lista_fim:
                plano.append({"cena": cena, "motivo": "nenhuma lista visivel com questao respondida no seed"})
                continue
            lid, d = lista_fim
            plano.append({"cena": cena, "params": {"lista": lid, "modo": modo(d)}, "info": "lista %s" % lid})
        elif cena in ("cards", "verso"):
            if n_cards:
                plano.append({"cena": cena, "params": {}, "info": "lote %s, %d cards" % (lote.get("sessao", "?"), n_cards)})
            else:
                plano.append({"cena": cena, "motivo": "o lote embutido no build nao tem cards"})
        elif cena in ("aula", "resumo"):
            prefixo = "aulas/" if cena == "aula" else "resumos/"
            href = primeiro_link(hub_index, prefixo)
            if not href:
                plano.append({"cena": cena, "motivo": "a Teoria do build nao tem link de %s" % cena})
            elif not (site / href).is_file():
                plano.append({"cena": cena, "motivo": "o 1o link de %s (%s) nao tem arquivo no site" % (cena, href)})
            else:
                plano.append({"cena": cena, "params": {}, "info": href})
    return plano


# --------------------------------------------------------------- o navegador
def achar_edge():
    for c in EDGE_CANDIDATOS:
        if os.path.isfile(c):
            return c
    return shutil.which("msedge")


class _Calado(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def servir(site, porta):
    """http.server em 127.0.0.1 servindo `site`, numa thread (porta 0 = livre, escolhida pelo SO).
    Devolve o servidor; quem chama fecha com `shutdown()` + `server_close()`."""
    handler = functools.partial(_Calado, directory=str(site))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", porta), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


_RE_RESULTADO = re.compile(r'<pre id="ui-resultado"[^>]*>(.*?)</pre>', re.S)


def ler_resultado(dom):
    """O JSON que o harness deixou no <pre id="ui-resultado"> da moldura (None se nao ha)."""
    m = _RE_RESULTADO.search(dom or "")
    if not m or not m.group(1).strip():
        return None
    try:
        res = json.loads(html.unescape(m.group(1)))
    except ValueError:
        return None
    return res if isinstance(res, dict) else None


def capturar(edge, url, png, largura, altura, perfil, timeout=180):
    """1 corrida do Edge: PNG + DOM da moldura. Devolve (resultado|None, erro|None)."""
    cmd = [edge, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
           "--no-default-browser-check", "--disable-extensions", "--mute-audio",
           "--user-data-dir=%s" % perfil, "--virtual-time-budget=%d" % ORCAMENTO_MS,
           "--window-size=%d,%d" % (largura, altura), "--screenshot=%s" % png, "--dump-dom", url]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, "o Edge passou de %d s" % timeout
    except OSError as e:
        return None, "o Edge nao abriu: %s" % e
    finally:
        shutil.rmtree(perfil, ignore_errors=True)
    res = ler_resultado(r.stdout.decode("utf-8", errors="replace"))
    if r.returncode != 0:
        return res, "o Edge saiu com %d" % r.returncode
    if not Path(png).is_file():
        return res, "o Edge nao gravou o PNG"
    if res is None:
        return None, "sem medida: o roteiro nao terminou em %d s virtuais (erro de JS?)" % (ORCAMENTO_MS // 1000)
    return res, None


# --------------------------------------------------------------------- saida
def _elementos(els):
    return "; ".join("%s %dpx" % (e.get("sel", "?"), e.get("largura", 0)) for e in (els or []))


def medida_txt(res, erro=None):
    """`ok` | `ROLA +Npx: ...` (+ quadros e falha de montagem) -- a coluna da tabela."""
    if res is None:
        return "FALHOU: %s" % (erro or "sem resultado")
    partes = []
    if res.get("rola"):
        partes.append("ROLA +%dpx: %s" % (res.get("sw", 0) - res.get("cw", 0), _elementos(res.get("elementos")) or "?"))
    for q in res.get("quadros") or []:
        if q.get("rola"):
            partes.append("ROLA no %s +%dpx: %s" % (q.get("id"), q.get("sw", 0) - q.get("cw", 0), _elementos(q.get("elementos")) or "?"))
    txt = " | ".join(partes) or "ok"
    if not res.get("ok"):
        txt += " -- cena NAO montou: %s" % (res.get("erro") or "?")
    if erro:
        txt += " -- %s" % erro
    return txt


def tabela(linhas):
    """Texto alinhado: cena | largura | png | medida."""
    cab = ("cena", "largura", "png", "medida")
    ws = [max([len(cab[i])] + [len(str(l[i])) for l in linhas]) for i in range(3)]
    fmt = "%-{0}s  %-{1}s  %-{2}s  %s".format(*ws)
    out = [fmt % cab, fmt % ("-" * ws[0], "-" * ws[1], "-" * ws[2], "-" * 6)]
    out += [fmt % tuple(str(x) for x in l) for l in linhas]
    return "\n".join(out)


def _rel(p):
    try:
        return Path(p).resolve().relative_to(RAIZ).as_posix()
    except ValueError:
        return str(p)


# ---------------------------------------------------------------------- main
class _Parser(argparse.ArgumentParser):
    def error(self, message):                      # erro de uso = exit 1 (contrato do tool), nao 2
        self.print_usage(sys.stderr)
        self.exit(1, "%s: erro: %s\n" % (self.prog, message))


def _parser():
    ap = _Parser(
        prog="ui_capturas.py",
        description="Capturas da UI do MedHub HUB em navegador real (Edge headless + db falso), "
                    "cena x largura, com a medida de rolagem horizontal.",
        epilog="Cenas: %s. Exemplo: python tools/ui_capturas.py --cenas revelada,fim --larguras 390" % ", ".join(CENAS))
    ap.add_argument("--hub", default="tmp/hub", metavar="DIR",
                    help="build do hub com index.html (default tmp/hub; `hub.py --build --out DIR`)")
    ap.add_argument("--out", default=None, metavar="DIR",
                    help="pasta da saida, dentro de tmp/ (default tmp/ui_capturas/AAAAMMDD-HHMM)")
    ap.add_argument("--larguras", default=",".join(str(x) for x in LARGURAS_PADRAO), metavar="L1,L2",
                    help="larguras em px, separadas por virgula (default 390,768,1280)")
    ap.add_argument("--cenas", default=None, metavar="C1,C2",
                    help="cenas, separadas por virgula (default todas; lista abaixo)")
    ap.add_argument("--seed", action="append", default=None, metavar="DIR",
                    help="pasta de docs do db (repetivel, dentro de tmp/; troca a lista padrao inteira: "
                         "tmp/hub_db, tmp/bancada e o tmp/player_*_db mais novo)")
    ap.add_argument("--porta", type=int, default=0, metavar="N",
                    help="porta do http.server em 127.0.0.1 (default 0 = livre; 8766/8767 sao reservadas)")
    return ap


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    args = _parser().parse_args(argv)
    try:
        return _rodar(args)
    except ErroDeUso as e:
        print("ui_capturas: erro: %s" % e, file=sys.stderr)
        return 1


def _rodar(args):
    try:
        larguras = parse_larguras(args.larguras)
        cenas = parse_cenas(args.cenas)
    except ValueError as e:
        raise ErroDeUso(str(e))
    if args.porta in PORTAS_RESERVADAS:
        raise ErroDeUso("porta %d reservada (8766/8767 sao do operador); use outra ou 0" % args.porta)
    if not 0 <= args.porta <= 65535:
        raise ErroDeUso("porta invalida: %d" % args.porta)
    hub_dir = _resolver(args.hub)
    if not (hub_dir / "index.html").is_file():
        raise ErroDeUso("%s sem index.html -- monte com `python tools/hub.py --build --out DIR`" % hub_dir)
    if args.seed:
        pastas = [_resolver(s) for s in args.seed]
        for p in pastas:
            if not dentro_de(p, TMP):
                raise ErroDeUso("--seed fora de tmp/: %s (o seed tem conteudo do EMED)" % p)
            if not p.is_dir():
                raise ErroDeUso("--seed inexistente: %s" % p)
    else:
        pastas = seeds_padrao()
    out = _resolver(args.out) if args.out else TMP / "ui_capturas" / datetime.now().strftime("%Y%m%d-%H%M")
    if not dentro_de(out, TMP):
        raise ErroDeUso("--out fora de tmp/: %s (a pagina de teste carrega o seed)" % out)
    edge = achar_edge()
    if not edge:
        raise ErroDeUso("Edge nao encontrado (%s)" % " | ".join(EDGE_CANDIDATOS))
    if not HARNESS.is_file():
        raise ErroDeUso("harness ausente: %s" % HARNESS)

    seed, est = montar_seed(pastas)
    out.mkdir(parents=True, exist_ok=True)
    site = out / "site"
    info_site = montar_site(site, hub_dir, seed, HARNESS.read_text(encoding="utf-8"))
    hub_index = (hub_dir / "index.html").read_text(encoding="utf-8")
    plano = planejar(cenas, seed, hub_index, site)

    print("hub:  %s  (%d aulas, %d resumos, painel %s)" % (_rel(hub_dir), info_site["aulas"], info_site["resumos"],
                                                        "sim" if info_site["painel"] else "NAO"))
    print("seed: %d docs %s -- de %s" % (est["docs"], json.dumps(est["por_colecao"], ensure_ascii=False),
                                         ", ".join(_rel(p) for p in pastas) or "(nenhuma pasta)"))
    print("out:  %s" % _rel(out))
    for p in plano:
        print("  %-9s %s" % (p["cena"], p.get("info") or ("NAO MONTADA: " + p["motivo"] if "motivo" in p else "")))

    tarefas = [(p, w) for p in plano if "params" in p for w in larguras]
    perfis = out / ".perfis"
    resultados = {}
    try:
        srv = servir(site, args.porta)
    except OSError as e:
        raise ErroDeUso("nao consegui servir o site na porta %d: %s" % (args.porta, e))
    porta = srv.server_address[1]

    def uma(p, w):
        q = dict(p["params"], cena=p["cena"], w=w, h=ALTURA)
        url = "http://127.0.0.1:%d/frame.html?%s" % (porta, urlencode(q))
        png = out / ("%s-%d.png" % (p["cena"], w))
        if png.exists():
            png.unlink()
        return capturar(edge, url, str(png), w, ALTURA, str(perfis / ("%s-%d" % (p["cena"], w))))

    print("rodando %d capturas (Edge headless, %d em paralelo)..." % (len(tarefas), PARALELO), flush=True)
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=PARALELO) as ex:
            futs = {ex.submit(uma, p, w): (p["cena"], w) for p, w in tarefas}
            for f in concurrent.futures.as_completed(futs):
                resultados[futs[f]] = f.result()
    finally:
        srv.shutdown()
        srv.server_close()
        shutil.rmtree(perfis, ignore_errors=True)

    linhas, registro, pngs = [], [], 0
    for p in plano:
        if "motivo" in p:
            linhas.append((p["cena"], "-", "-", "NAO MONTADA: " + p["motivo"]))
            registro.append({"cena": p["cena"], "motivo": p["motivo"]})
            continue
        for w in larguras:
            res, erro = resultados.get((p["cena"], w), (None, "nao rodou"))
            png = out / ("%s-%d.png" % (p["cena"], w))
            tem_png = png.is_file()
            pngs += tem_png
            linhas.append((p["cena"], w, _rel(png) if tem_png else "-", medida_txt(res, erro)))
            registro.append({"cena": p["cena"], "largura": w, "params": p["params"], "png": _rel(png) if tem_png else None,
                             "erro": erro, "resultado": res})
    print()
    print(tabela(linhas))
    js = sorted({(r["cena"], e) for r in registro if r.get("resultado") for e in r["resultado"].get("erros_js") or []})
    if js:
        print("\nerros de JS na pagina:")
        for cena, e in js:
            print("  %-9s %s" % (cena, e))
    (out / "resultado.json").write_text(json.dumps({
        "gerado_em": datetime.now().isoformat(timespec="seconds"), "hub": _rel(hub_dir), "out": _rel(out),
        "larguras": larguras, "altura": ALTURA, "seed": dict(est, pastas=[_rel(p) for p in pastas]),
        "capturas": registro}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\nresultado: %s" % _rel(out / "resultado.json"))
    if tarefas and not pngs:
        print("ui_capturas: erro: nenhum PNG gravado -- o Edge nao rodou neste ambiente", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
