"""hub.py -- monta o MedHub HUB: UMA pagina (Cards + Aulas + Painel) e o manifesto do publish.

Spec: .vibeflow/specs/medhub-hub-v0-part-1.md (PRD .vibeflow/prds/medhub-hub-2026-09-22.md).

Por que existe: cada aula-base, player e painel virava um artifact NOVO na conta claude.ai, que e
compartilhada com o time de conteudo; o operador apagava por higiene e os links do HANDOFF morriam
no mesmo dia (medido em 22/09/2026). O hub e UM artifact, republicado no lugar.

O que ele monta, em `--out` (default `tmp/hub/`):
- `index.html` a partir de `core/templates/hub.html`, com o player INLINE composto das tres regioes
  marcadas de `core/templates/player.html` (a fonte UNICA do player) e o lote injetado por
  `fsrs_queue.injetar_lote` (mesmo marcador unico, mesmo escape de `</script>`);
- `manifesto.json` = exatamente os argumentos do `Artifact publish`: `file_path` (a pagina) e
  `files` ({path publicado: fonte | null}). Painel e aulas vao DIRETO das fontes em `artifacts/`
  (sem copia). Arquivo OMITIDO num update e MANTIDO pelo runtime; so `null` remove -- por isso o que
  saiu da selecao e consta em `--publicado` (a listagem do artifact) vira `null`.

Limites como DADO: 255 entradas por versao (contrato do Artifact), 8 reservadas, cap de 120 aulas
(mais novas primeiro, pela data de criacao no git).

O CLI NAO fala com a API de Artifact: ler a versao viva, listar os arquivos publicados, publicar e
ler o `db` sao atos do agente (rito em `.claude/commands/revisar.md`, "DRENAR no player").

Uso (assinatura canonica: `.claude/commands/engenharia-cli.md`, secao `tools/hub.py`):
    python tools/hub.py --build --lote tmp/player_<sessao>.json [--publicado LISTA] [--out DIR]
                        [--painel artifacts/painel.html]
    python tools/hub.py --check [--out DIR]
    python tools/hub.py --extrair-lote PAGINA.html [--out-lote ARQ.json]
"""
from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from app.utils import db  # noqa: E402  -- so o relogio unico (F80), nenhuma consulta
from tools.fsrs_queue import (  # noqa: E402
    MARCA_ABRE,
    MARCA_FECHA,
    TEMPLATE_PLAYER,
    injetar_lote,
)

TEMPLATE_HUB = RAIZ / "core" / "templates" / "hub.html"
PAGINA = "index.html"
MANIFESTO = "manifesto.json"
PUB_PAINEL = "painel.html"
PREFIXO_AULA = "aulas/"
PADRAO_AULAS = "aula-*.html"

#: Contrato do Artifact: no maximo 255 entradas por versao. 8 ficam de folga (RD e o que vier
#: no v1). A pagina conta como entrada, por isso o teto de ARQUIVOS e 247 - 1.
LIMITE_ENTRADAS = 255
RESERVADAS = 8
TETO_ENTRADAS = LIMITE_ENTRADAS - RESERVADAS
#: Decisao do /ai-eng (22/09): cap como DADO; folga 2x sobre o que cabe ate 01/11.
CAP_AULAS = 120

#: Regioes do player (fonte unica em core/templates/player.html), cada marcador exatamente 1x.
REGIOES_PLAYER = (
    ("css", "/* @player:css:inicio */", "/* @player:css:fim */"),
    ("corpo", "<!-- @player:corpo:inicio -->", "<!-- @player:corpo:fim -->"),
    ("js", "<!-- @player:js:inicio -->", "<!-- @player:js:fim -->"),
)
#: Lugares do template do hub, cada um exatamente 1x.
LUGARES_HUB = (
    ("player-css", "/* @hub:player-css */"),
    ("player-corpo", "<!-- @hub:player-corpo -->"),
    ("player-js", "<!-- @hub:player-js -->"),
    ("status", "<!-- @hub:status -->"),
    ("aulas", "<!-- @hub:aulas -->"),
    ("painel", "<!-- @hub:painel -->"),
)

_RE_ESQUEMA = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
_RE_SLUG_RUIM = re.compile(r"[^a-z0-9._-]+")


# ----------------------------------------------------------------------------- nucleo puro

@dataclass(frozen=True)
class Aula:
    slug: str
    titulo: str
    data: str    # AAAA-MM-DD (criacao no git)
    fonte: str   # path posix relativo a raiz do repo

    @property
    def publicado(self):
        return PREFIXO_AULA + self.slug + ".html"


def _exatamente_uma(texto, marca, onde):
    """Posicao do marcador; ausente ou repetido falha ALTO (licao do marcador ambiguo, s183)."""
    n = texto.count(marca)
    if n != 1:
        raise ValueError("%s: marcador %r aparece %d vez(es) -- tem de ser exatamente 1"
                         % (onde, marca, n))
    return texto.index(marca)


def extrair_regioes_player(player_html):
    """{'css','corpo','js'} recortados entre os marcadores do player (exclusive)."""
    regioes = {}
    for nome, abre, fecha in REGIOES_PLAYER:
        i = _exatamente_uma(player_html, abre, "player.html")
        j = _exatamente_uma(player_html, fecha, "player.html")
        if j < i:
            raise ValueError("player.html: %r fecha antes de abrir" % nome)
        regioes[nome] = player_html[i + len(abre):j].strip("\n")
    return regioes


def slug_de(nome_arquivo):
    """`aula-hernias.html` -> `hernias` (segmento seguro para path publicado)."""
    base = nome_arquivo[:-5] if nome_arquivo.lower().endswith(".html") else nome_arquivo
    if base.lower().startswith("aula-"):
        base = base[5:]
    return _RE_SLUG_RUIM.sub("-", base.lower()).strip("-") or "aula"


def selecionar_aulas(aulas, cap=CAP_AULAS):
    """Mais novas primeiro (data de criacao desc; empate por slug), cortadas no cap."""
    por_slug = sorted(aulas, key=lambda a: a.slug)
    return sorted(por_slug, key=lambda a: a.data, reverse=True)[:cap]


def normalizar_path(p):
    p = str(p).strip().replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    return p.lstrip("/")


def ler_publicado(texto):
    """Paths ja publicados no hub. Aceita JSON (lista de str, lista de {"path"}, ou objeto --
    as chaves, ex. o `files` de um manifesto anterior) ou texto (1 path por linha; `#` comenta;
    so o 1o token da linha conta, para tolerar colunas extras da listagem)."""
    texto = (texto or "").strip()
    if not texto:
        return []
    if texto[0] in "[{":
        obj = json.loads(texto)
        if isinstance(obj, dict):
            obj = list((obj.get("files") if isinstance(obj.get("files"), dict) else obj).keys())
        saida = []
        for item in obj:
            if isinstance(item, dict):
                item = item.get("path")
            if item:
                saida.append(normalizar_path(item))
        return saida
    saida = []
    for linha in texto.splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        saida.append(normalizar_path(linha.split()[0]))
    return saida


def montar_manifesto(aulas_sel, painel_fonte=None, publicado=()):
    """O argumento `files` do publish: {publicado: fonte}, + `null` para o que saiu.

    `index.html` e o `file_path` da pagina: nunca entra em `files` e nunca vira `null`."""
    files = {}
    if painel_fonte:
        files[PUB_PAINEL] = normalizar_path(painel_fonte)
    for a in aulas_sel:
        files[a.publicado] = normalizar_path(a.fonte)
    if len(files) + 1 > TETO_ENTRADAS:
        raise ValueError("manifesto com %d arquivos + a pagina estoura o teto de %d entradas "
                         "(%d do contrato - %d reservadas)"
                         % (len(files), TETO_ENTRADAS, LIMITE_ENTRADAS, RESERVADAS))
    for p in publicado:
        p = normalizar_path(p)
        if p and p != PAGINA and p not in files:
            files[p] = None
    return dict(sorted(files.items()))


def _e(valor):
    return html.escape("" if valor is None else str(valor), quote=True)


def _data_curta(iso):
    try:
        return date.fromisoformat(str(iso)[:10]).strftime("%d/%m")
    except ValueError:
        return str(iso or "")


def html_aulas(aulas_sel):
    if not aulas_sel:
        return '<p class="hub-vazio">Nenhuma aula publicada neste hub ainda.</p>'
    itens = [
        '<li><a class="hub-aula" href="%s" data-titulo="%s"><span class="hub-aula-t">%s</span>'
        '<span class="hub-aula-d">%s</span></a></li>'
        % (_e(a.publicado), _e(a.titulo), _e(a.titulo), _e(_data_curta(a.data)))
        for a in aulas_sel
    ]
    return '<ul class="hub-aulas">\n' + "\n".join(itens) + "\n</ul>"


def html_painel(tem_painel):
    if not tem_painel:
        return ('<h2 class="hub-titulo">Painel</h2>\n'
                '<p class="hub-vazio">Painel nao gerado nesta montagem -- o rito roda '
                '<code>tools/painel.py --html</code> antes do <code>hub.py --build</code>.</p>')
    return ('<h2 class="hub-titulo">Painel</h2>\n'
            '<p class="hub-sub">Progresso, FSRS e proximas tarefas, gerado do banco no ultimo '
            'fechamento.</p>\n'
            '<p class="hub-aviso" id="hub-painel-aviso" hidden>Nao consegui abrir o painel aqui '
            'dentro. <a href="%s">Abrir o painel em pagina inteira</a>.</p>\n'
            '<iframe class="hub-quadro" id="hub-painel-quadro" data-src="%s" title="Painel" '
            'hidden></iframe>' % (PUB_PAINEL, PUB_PAINEL))


def html_status(lote, agora):
    cards = lote.get("cards") or []
    return "montado %s &#183; lote %s &#183; %d cards" % (
        _e(agora.strftime("%d/%m %H:%M")), _e(lote.get("sessao") or "-"), len(cards))


def montar_index(template_hub, player_html, lote, aulas_sel, tem_painel, agora):
    """A pagina: casca do hub + as 3 regioes do player + estado/aulas/painel + o lote."""
    regioes = extrair_regioes_player(player_html)
    for _nome, marca in LUGARES_HUB:
        _exatamente_uma(template_hub, marca, "hub.html")
    trocas = {
        "player-css": regioes["css"],
        "player-corpo": regioes["corpo"],
        "player-js": regioes["js"],
        "status": html_status(lote, agora),
        "aulas": html_aulas(aulas_sel),
        "painel": html_painel(tem_painel),
    }
    pagina = template_hub
    for nome, marca in LUGARES_HUB:
        pagina = pagina.replace(marca, trocas[nome], 1)
    sobra = [marca for _n, marca in LUGARES_HUB if marca in pagina]
    if sobra:
        raise ValueError("lugar(es) do hub sobraram depois da montagem: %s" % sobra)
    return injetar_lote(pagina, lote)


def extrair_lote(pagina_html):
    """O inverso de `injetar_lote`: o JSON do `<script id="lote">` de uma pagina montada."""
    i = _exatamente_uma(pagina_html, MARCA_ABRE, "pagina")
    ini = i + len(MARCA_ABRE)
    fim = pagina_html.find(MARCA_FECHA, ini)
    if fim < 0:
        raise ValueError("pagina sem </script> depois do marcador do lote")
    return json.loads(pagina_html[ini:fim])


class _ColetorHref(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.hrefs.extend(v for k, v in attrs if k == "href" and v is not None)


def hrefs_relativos(pagina_html):
    """Links `<a href>` da pagina que apontam para arquivo do PROPRIO artifact.

    Fora: ancora pura (`#x`), esquema (`https:`, `mailto:`...), `//host`. Fragmento e query saem."""
    coletor = _ColetorHref()
    coletor.feed(pagina_html)
    coletor.close()
    saida = set()
    for href in coletor.hrefs:
        href = href.strip()
        if not href or href.startswith("#") or href.startswith("//") or _RE_ESQUEMA.match(href):
            continue
        href = href.split("#", 1)[0].split("?", 1)[0]
        if href:
            saida.add(normalizar_path(href))
    return saida


def checar(pagina_html, files, raiz=RAIZ):
    """Problemas do manifesto: fonte inexistente, link do index fora dele, teto de entradas."""
    raiz = Path(raiz)
    problemas = []
    vivos = {pub: fonte for pub, fonte in files.items() if fonte is not None}
    for pub, fonte in sorted(vivos.items()):
        if not (raiz / fonte).is_file():
            problemas.append("fonte inexistente: %s <- %s" % (pub, fonte))
    for href in sorted(hrefs_relativos(pagina_html)):
        if href not in vivos:
            problemas.append("link morto no index: %s (fora do manifesto)" % href)
    if len(vivos) + 1 > TETO_ENTRADAS:
        problemas.append("%d arquivos + a pagina > teto de %d entradas" % (len(vivos), TETO_ENTRADAS))
    return problemas


# ----------------------------------------------------------------------------- casca

class _ColetorTitulo(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._dentro = False
        self._feito = False
        self.partes = []

    def handle_starttag(self, tag, attrs):
        if tag == "title" and not self._feito:
            self._dentro = True

    def handle_endtag(self, tag):
        if tag == "title" and self._dentro:
            self._dentro = False
            self._feito = True

    def handle_data(self, data):
        if self._dentro:
            self.partes.append(data)


def titulo_de(pagina_html):
    """Texto do 1o `<title>` (parser, nunca regex -- licao do F108)."""
    coletor = _ColetorTitulo()
    coletor.feed(pagina_html[:65536])
    coletor.close()
    return " ".join("".join(coletor.partes).split())


def data_de_criacao(path, raiz):
    """(AAAA-MM-DD, aviso|None): 1o commit que ADICIONOU o arquivo; sem git, a data do arquivo."""
    path, raiz = Path(path), Path(raiz)
    try:
        rel = path.resolve().relative_to(raiz.resolve()).as_posix()
        saida = subprocess.run(
            ["git", "log", "--follow", "--diff-filter=A", "--format=%as", "--", rel],
            cwd=str(raiz), capture_output=True, text=True, timeout=30)
        linhas = [linha.strip() for linha in saida.stdout.splitlines() if linha.strip()]
        if saida.returncode == 0 and linhas:
            return linhas[-1], None
    except (OSError, ValueError, subprocess.SubprocessError):
        pass
    return (date.fromtimestamp(path.stat().st_mtime).isoformat(),
            "sem registro no git, data do arquivo: %s" % path.name)


def _rel(path, raiz):
    path, raiz = Path(path).resolve(), Path(raiz).resolve()
    try:
        return path.relative_to(raiz).as_posix()
    except ValueError:
        return path.as_posix()


def coletar_aulas(raiz, data_fn=None):
    """Aulas de `artifacts/aula-*.html`, com titulo e data. `data_fn(path, raiz)` e injetavel."""
    raiz = Path(raiz)
    data_fn = data_fn or data_de_criacao
    aulas, avisos = [], []
    for p in sorted((raiz / "artifacts").glob(PADRAO_AULAS)):
        slug = slug_de(p.name)
        titulo = titulo_de(p.read_text(encoding="utf-8", errors="replace")) or slug
        data, aviso = data_fn(p, raiz)
        if aviso:
            avisos.append(aviso)
        aulas.append(Aula(slug=slug, titulo=titulo, data=data, fonte=_rel(p, raiz)))
    return aulas, avisos


def construir(lote, raiz=RAIZ, out=None, painel=None, publicado=(), agora=None, data_fn=None,
              template_hub=None, template_player=None):
    """Monta `index.html` + `manifesto.json` em `out`. Devolve (manifesto, problemas, avisos)."""
    raiz = Path(raiz)
    out = Path(out) if out else raiz / "tmp" / "hub"
    painel_path = Path(painel) if painel else raiz / "artifacts" / "painel.html"
    if not painel_path.is_absolute():
        painel_path = raiz / painel_path

    aulas, avisos = coletar_aulas(raiz, data_fn)
    selecionadas = selecionar_aulas(aulas)
    if len(aulas) > len(selecionadas):
        avisos.append("%d aula(s) fora do cap de %d (seguem no repo, saem do hub)"
                      % (len(aulas) - len(selecionadas), CAP_AULAS))
    tem_painel = painel_path.is_file()
    if not tem_painel:
        avisos.append("painel ausente (%s): a aba Painel sai com o aviso de 'nao gerado'"
                      % _rel(painel_path, raiz))
    files = montar_manifesto(selecionadas, _rel(painel_path, raiz) if tem_painel else None,
                             publicado)

    th = template_hub if template_hub is not None else TEMPLATE_HUB.read_text(encoding="utf-8")
    tp = (template_player if template_player is not None
          else TEMPLATE_PLAYER.read_text(encoding="utf-8"))
    agora = agora or db.agora()
    pagina = montar_index(th, tp, lote, selecionadas, tem_painel, agora)

    out.mkdir(parents=True, exist_ok=True)
    (out / PAGINA).write_text(pagina, encoding="utf-8")
    manifesto = {
        "file_path": _rel(out / PAGINA, raiz),
        "files": files,
        "sessao": lote.get("sessao"),
        "total_cards": len(lote.get("cards") or []),
        "aulas": len(selecionadas),
        "montado_em": agora.strftime("%Y-%m-%d %H:%M:%S"),
    }
    (out / MANIFESTO).write_text(json.dumps(manifesto, ensure_ascii=False, indent=1) + "\n",
                                 encoding="utf-8")
    return manifesto, checar(pagina, files, raiz), avisos


def _saida_padrao():
    return RAIZ / "tmp" / "hub"


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    ap = argparse.ArgumentParser(
        description="Monta o MedHub HUB (pagina unica Cards + Aulas + Painel) e o manifesto do "
                    "Artifact publish. Nao publica nada.")
    acao = ap.add_mutually_exclusive_group(required=True)
    acao.add_argument("--build", action="store_true",
                      help="monta index.html + manifesto.json em --out e roda o --check no fim")
    acao.add_argument("--check", action="store_true",
                      help="confere o manifesto de --out: fonte inexistente, link morto no "
                           "index, teto de entradas (exit 1 se acusar)")
    acao.add_argument("--extrair-lote", dest="extrair_lote", metavar="PAGINA.html",
                      help="recupera o lote injetado numa pagina salva (ex.: a versao viva "
                           "lida por Artifact read)")
    ap.add_argument("--lote", metavar="ARQ.json",
                    help="--build: o lote de fsrs_queue.py --export-player (ou o extraido "
                         "da pagina viva)")
    ap.add_argument("--publicado", metavar="LISTA",
                    help="--build: paths ja publicados no hub (transcritos do Artifact list "
                         "scope=files), 1 por linha ou JSON; o que saiu da selecao vira null")
    ap.add_argument("--out", metavar="DIR", help="diretorio de saida (default tmp/hub)")
    ap.add_argument("--painel", metavar="PATH",
                    help="--build: HTML do painel (default artifacts/painel.html)")
    ap.add_argument("--out-lote", dest="out_lote", metavar="ARQ.json",
                    help="--extrair-lote: onde gravar o lote (default: imprime na saida)")
    args = ap.parse_args(argv)
    out = Path(args.out) if args.out else _saida_padrao()

    if args.extrair_lote:
        lote = extrair_lote(Path(args.extrair_lote).read_text(encoding="utf-8"))
        texto = json.dumps(lote, ensure_ascii=False, indent=1)
        if args.out_lote:
            Path(args.out_lote).parent.mkdir(parents=True, exist_ok=True)
            Path(args.out_lote).write_text(texto + "\n", encoding="utf-8")
            print("[hub] lote %s (%d cards) -> %s"
                  % (lote.get("sessao"), len(lote.get("cards") or []), args.out_lote))
        else:
            print(texto)
        return 0

    if args.check:
        man_path = out / MANIFESTO
        if not man_path.is_file() or not (out / PAGINA).is_file():
            print("[hub] --check: %s ou %s ausente em %s -- rode --build antes"
                  % (PAGINA, MANIFESTO, out))
            return 1
        manifesto = json.loads(man_path.read_text(encoding="utf-8"))
        problemas = checar((out / PAGINA).read_text(encoding="utf-8"), manifesto["files"], RAIZ)
        for p in problemas:
            print("[hub] PROBLEMA: %s" % p)
        print("[hub] --check: %s" % ("OK" if not problemas else "%d problema(s)" % len(problemas)))
        return 1 if problemas else 0

    if not args.lote:
        ap.error("--build exige --lote ARQ.json")
    lote = json.loads(Path(args.lote).read_text(encoding="utf-8"))
    publicado = ler_publicado(Path(args.publicado).read_text(encoding="utf-8")) \
        if args.publicado else []
    manifesto, problemas, avisos = construir(lote, out=out, painel=args.painel,
                                             publicado=publicado)
    files = manifesto["files"]
    nulos = sorted(p for p, f in files.items() if f is None)
    vivos = len(files) - len(nulos)
    kb = (out / PAGINA).stat().st_size / 1024.0
    print("[hub] pagina: %s (%.0f KB) -- lote %s, %d cards"
          % (manifesto["file_path"], kb, manifesto["sessao"], manifesto["total_cards"]))
    print("[hub] arquivos: %d (painel %d, aulas %d; cap %d) + pagina = %d/%d entradas"
          % (vivos, 1 if PUB_PAINEL in files and files[PUB_PAINEL] else 0, manifesto["aulas"],
             CAP_AULAS, vivos + 1, TETO_ENTRADAS))
    print("[hub] null (saem do hub): %d%s" % (len(nulos), (" -- " + ", ".join(nulos)) if nulos else ""))
    for aviso in avisos:
        print("[hub] AVISO: %s" % aviso)
    print("[hub] manifesto: %s -- `file_path` + `files` do Artifact publish" % _rel(out / MANIFESTO, RAIZ))
    for p in problemas:
        print("[hub] PROBLEMA: %s" % p)
    print("[hub] --check: %s" % ("OK" if not problemas else "%d problema(s)" % len(problemas)))
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
