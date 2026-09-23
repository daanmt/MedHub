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
- DIFF (v1, s193, spec `medhub-hub-v1-manifesto-diff`): `files` leva so o que e NOVO ou MUDOU. O
  que ja esta no ar e intocado fica em `manifesto["mantidos"]` -- nao sobe e nao precisa ser relido
  antes do publish (a releitura das 6 aulas custou 378k tokens em 22/09). Base: o registro local
  `registro_publicado.json`, que so o `--confirmar` escreve, DEPOIS do publish aceito, a partir do
  `estado_pos_publish.json` do build.

Limites como DADO: 255 entradas por versao (contrato do Artifact), 8 reservadas, cap de 120 aulas
(mais novas primeiro, pela data de criacao no git).

O CLI NAO fala com a API de Artifact: ler a versao viva, listar os arquivos publicados, publicar e
ler o `db` sao atos do agente (rito em `.claude/commands/revisar.md`, "DRENAR no player").

Uso (assinatura canonica: `.claude/commands/engenharia-cli.md`, secao `tools/hub.py`):
    python tools/hub.py --build --lote tmp/player_<sessao>.json [--publicado LISTA] [--out DIR]
                        [--painel artifacts/painel.html] [--quadro-estado DIR]
    python tools/hub.py --check [--out DIR]
    python tools/hub.py --confirmar [--out DIR]
    python tools/hub.py --precisa-publicar --lote tmp/player_<sessao>.json [--notas DIR]
                        [--quadro-estado DIR] [--json] [--out DIR]
    python tools/hub.py --extrair-lote PAGINA.html [--out-lote ARQ.json]
"""
from __future__ import annotations

import argparse
import hashlib
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

from app.utils import db  # noqa: E402  -- relogio unico (F80) + plano_listar (read-only, s194)
from tools.fsrs_queue import (  # noqa: E402
    MARCA_ABRE,
    MARCA_FECHA,
    TEMPLATE_PLAYER,
    injetar_lote,
)

TEMPLATE_HUB = RAIZ / "core" / "templates" / "hub.html"
#: Registro do quadro da aba Aulas (s194): slug -> {tipo, titulo, tarefa_id?}.
QUADRO_REG = "core/hub_quadro.json"
#: Colunas do quadro, nesta ordem. Rotulos curtos (celular: etiqueta <= 15 chars).
TIPOS_QUADRO = (("aula", "Aulas-base"), ("revisao", "Revisões"), ("analise", "Análises"))
TIPO_PADRAO = "aula"
#: Colecao do db onde a pagina grava {feito, ts} por slug (doc `quadro/<slug>`). Regra de escrita
#: `{path: "quadro", write: "interact"}` na declaracao de capabilities (revisar.md).
COLECAO_QUADRO = "quadro"
PAGINA = "index.html"
MANIFESTO = "manifesto.json"
ESTADO_POS = "estado_pos_publish.json"
REGISTRO = "registro_publicado.json"
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
    ("aulas", "<!-- @hub:aulas -->"),
    ("painel", "<!-- @hub:painel -->"),
)

_RE_ESQUEMA = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
_RE_SLUG_RUIM = re.compile(r"[^a-z0-9._-]+")
_RE_PATH_PUBLICADO = re.compile(r"^[A-Za-z0-9._/-]+\.[A-Za-z0-9]+$")
_RE_BYTES = re.compile(r"\b(\d+)\s*bytes\b", re.I)


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


def ler_publicado_detalhado(texto):
    """[(path, bytes | None)] ja publicados no hub.

    Aceita JSON (lista de str, lista de {"path", "bytes"?}, ou objeto -- as chaves, ex. o `files`
    de um manifesto anterior) ou texto: 1 path por linha (`#` comenta; so o 1o token conta, para
    tolerar colunas extras), inclusive a listagem do `Artifact list scope=files` colada como sai
    (`- "aulas/x.html"  text/html  63060 bytes`): o tamanho vem do `N bytes`, e linha cujo 1o
    token nao e path de arquivo (o cabecalho e o rodape da listagem) e ignorada."""
    texto = (texto or "").strip()
    if not texto:
        return []
    if texto[0] in "[{":
        try:
            obj = json.loads(texto)
        except ValueError:
            obj = None
        if obj is not None:
            if isinstance(obj, dict):
                obj = list((obj.get("files") if isinstance(obj.get("files"), dict)
                            else obj).keys())
            saida = []
            for item in obj:
                tamanho = None
                if isinstance(item, dict):
                    tamanho = item.get("bytes")
                    item = item.get("path")
                if item:
                    saida.append((normalizar_path(item),
                                  None if tamanho is None else int(tamanho)))
            return saida
    saida = []
    for linha in texto.splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        tokens = linha.split()
        if tokens[0] == "-" and len(tokens) > 1:
            tokens = tokens[1:]
        token = tokens[0].strip("\"'")
        if not _RE_PATH_PUBLICADO.match(token):
            continue
        m = _RE_BYTES.search(linha)
        saida.append((normalizar_path(token), int(m.group(1)) if m else None))
    return saida


def ler_publicado(texto):
    """Paths ja publicados no hub (formatos em `ler_publicado_detalhado`)."""
    return [p for p, _ in ler_publicado_detalhado(texto)]


def aplicar_diff(files, fontes, registro, vivos):
    """O DIFF do publish (v1, s193). PURO.

    `files` = o manifesto COMPLETO ({publicado: fonte | None}, de `montar_manifesto`); `fontes` =
    {publicado: (sha256, bytes)} das fontes nao-nulas; `registro` = {publicado: {"sha256",
    "bytes", ...}} do ultimo publish CONFIRMADO; `vivos` = {publicado: bytes | None} da listagem
    viva. Um path fica MANTIDO (fora de `files` -- o runtime o mantem) so com TRES evidencias:
    a mesma sha256 no registro, o path na listagem viva e, se ela traz tamanho, o do registro.
    Omitir errado deixaria conteudo velho no ar em silencio; mandar a mais so custa upload.
    Devolve (files_enviar, mantidos, estado); `estado` = {publicado: {"sha256", "bytes", "fonte"}}
    de tudo que fica no ar depois do publish (enviados + mantidos; os nulos saem)."""
    enviar, mantidos, estado = {}, [], {}
    for pub, fonte in files.items():
        if fonte is None:
            enviar[pub] = None
            continue
        sha, n = fontes.get(pub) or (None, None)
        reg = registro.get(pub) or {}
        tamanho_vivo = vivos.get(pub)
        if (sha is not None and pub in vivos and reg.get("sha256") == sha
                and (tamanho_vivo is None or tamanho_vivo == reg.get("bytes"))):
            mantidos.append(pub)
        else:
            enviar[pub] = fonte
        if sha is not None:
            estado[pub] = {"sha256": sha, "bytes": n, "fonte": fonte}
    return enviar, sorted(mantidos), estado


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


def ler_quadro(caminho):
    """{slug: {"tipo", "titulo"?, "tarefa_id"?}} do registro versionado. Arquivo ausente = {}.
    Tipo fora de TIPOS_QUADRO falha ALTO: registro errado nao vira coluna inventada."""
    caminho = Path(caminho)
    if not caminho.is_file():
        return {}
    itens = json.loads(caminho.read_text(encoding="utf-8")).get("itens") or {}
    validos = {t for t, _ in TIPOS_QUADRO}
    for slug, item in itens.items():
        if (item or {}).get("tipo") not in validos:
            raise ValueError("%s: tipo %r da aula %r fora de %s"
                             % (caminho.name, (item or {}).get("tipo"), slug, sorted(validos)))
    return itens


def classificar(aulas_sel, quadro):
    """[(Aula, tipo, titulo, tarefa_id)] na ordem da selecao + avisos. Slug sem registro = tipo
    `aula` com WARN -- nunca silencioso (a aula nova aparece; o tipo e que fica a conferir)."""
    saida, avisos = [], []
    for a in aulas_sel:
        reg = quadro.get(a.slug)
        if reg is None:
            avisos.append("aula %r sem tipo em %s: entra como %r -- registre o tipo"
                          % (a.slug, QUADRO_REG, TIPO_PADRAO))
            reg = {}
        saida.append((a, reg.get("tipo") or TIPO_PADRAO, reg.get("titulo") or a.titulo,
                      reg.get("tarefa_id")))
    return saida, avisos


def ler_estado_quadro(caminho):
    """{slug: {"feito": bool, "ts": str|None}} a partir do que o `ArtifactData list` da colecao
    `quadro` deixa no disco: um DIRETORIO (1 arquivo `<slug>.json` por doc, em qualquer
    profundidade -- o `out_dir` espelha o path) ou um JSON ({slug: doc} ou [{id|slug, ...}]).
    None ou caminho inexistente = {} (nada feito)."""
    if not caminho:
        return {}
    caminho = Path(caminho)
    brutos = {}
    if caminho.is_dir():
        for arq in sorted(caminho.rglob("*.json")):
            try:
                brutos[arq.stem] = json.loads(arq.read_text(encoding="utf-8"))
            except ValueError:
                continue
    elif caminho.is_file():
        obj = json.loads(caminho.read_text(encoding="utf-8"))
        if isinstance(obj, dict):
            brutos = obj
        else:
            for item in obj or []:
                slug = (item or {}).get("slug") or (item or {}).get("id") or (item or {}).get("doc_id")
                if slug:
                    brutos[str(slug)] = item.get("data") if isinstance(item.get("data"), dict) else item
    return {str(slug): {"feito": bool((doc or {}).get("feito")), "ts": (doc or {}).get("ts")}
            for slug, doc in brutos.items() if isinstance(doc, dict)}


def _item_quadro(aula, tipo, titulo, feito, ordem):
    rotulo = ("Desmarcar %s" if feito else "Marcar %s como feita") % titulo
    return ('<li class="qd-item" data-slug="%s" data-tipo="%s" data-ordem="%d" data-titulo="%s"%s>'
            '<button type="button" class="qd-feito" aria-pressed="%s" aria-label="%s" '
            'title="%s" disabled><span aria-hidden="true"></span></button>'
            '<a class="hub-aula" href="%s" data-titulo="%s"><span class="hub-aula-t">%s</span>'
            '<span class="hub-aula-d">%s</span></a></li>'
            % (_e(aula.slug), _e(tipo), ordem, _e(titulo), ' data-feito="1"' if feito else "",
               "true" if feito else "false", _e(rotulo), _e(rotulo), _e(aula.publicado),
               _e(titulo), _e(titulo), _e(_data_curta(aula.data))))


def html_quadro(classificadas, estado=None):
    """O quadro da aba Aulas: uma coluna por tipo (empilhadas no celular), cada item com o
    controle "feito"; o que ja esta feito sai riscado para "Concluidas", recolhida. O estado do
    build e o do `db` no momento do tique; a pagina reconcilia ao vivo quando o `db` abre."""
    if not classificadas:
        return '<p class="hub-vazio">Nenhuma aula publicada neste hub ainda.</p>'
    estado = estado or {}
    feitos = {s for s, v in estado.items() if v.get("feito")}
    colunas = []
    for tipo, rotulo in TIPOS_QUADRO:
        itens = [_item_quadro(a, t, tit, False, i) for i, (a, t, tit, _) in enumerate(classificadas)
                 if t == tipo and a.slug not in feitos]
        colunas.append(
            '<section class="qd-col" data-tipo="%s" aria-label="%s"><h3 class="qd-titulo">%s '
            '<span class="qd-n">%d</span></h3><ul class="qd-lista">%s</ul>'
            '<p class="qd-vazio"%s>Nada em aberto.</p></section>'
            % (tipo, _e(rotulo), _e(rotulo), len(itens), "".join(itens),
               " hidden" if itens else ""))
    concluidas = [_item_quadro(a, t, tit, True, i) for i, (a, t, tit, _) in enumerate(classificadas)
                  if a.slug in feitos]
    return ('<div class="qd" id="hub-quadro">\n'
            '<p class="qd-aviso" id="hub-quadro-aviso" hidden>Marcar como feita não funciona '
            'nesta visualização.</p>\n'
            '<div class="qd-colunas">%s</div>\n'
            '<details class="qd-feitas" id="hub-quadro-feitas"><summary>Concluídas '
            '<span class="qd-n" id="hub-quadro-nfeitas">%d</span></summary>'
            '<ul class="qd-lista">%s</ul></details>\n</div>'
            % ("".join(colunas), len(concluidas), "".join(concluidas)))


def html_aulas(aulas_sel, quadro=None, estado=None):
    """Compatibilidade: o quadro sem registro (tudo `aula`) -- chamadores antigos e testes."""
    classificadas, _ = classificar(aulas_sel, quadro or {})
    return html_quadro(classificadas, estado)


def html_painel(tem_painel):
    """Bloco da aba Painel. Sem texto de bastidor (s194): nada de CLI, banco ou carimbo -- quem
    monta sem painel ve o AVISO do `--build` no terminal, nao na tela do operador."""
    if not tem_painel:
        return ('<h2 class="hub-titulo">Painel</h2>\n'
                '<p class="hub-vazio">O painel ainda nao esta disponivel.</p>')
    return ('<h2 class="hub-titulo">Painel</h2>\n'
            '<p class="hub-aviso" id="hub-painel-aviso" hidden>Nao consegui abrir o painel aqui '
            'dentro. <a href="%s">Abrir o painel em pagina inteira</a>.</p>\n'
            '<iframe class="hub-quadro" id="hub-painel-quadro" data-src="%s" title="Painel" '
            'hidden></iframe>' % (PUB_PAINEL, PUB_PAINEL))


def montar_index(template_hub, player_html, lote, aulas_sel, tem_painel, agora, quadro=None,
                 estado=None):
    """A pagina: casca do hub + as 3 regioes do player + aulas/painel + o lote.

    `agora` segue na assinatura (chamadores e testes), mas nao vai mais para a tela: a linha
    "montado ... lote ... cards" saiu na s194 (bastidor). O carimbo vive no manifesto."""
    del agora
    regioes = extrair_regioes_player(player_html)
    for _nome, marca in LUGARES_HUB:
        _exatamente_uma(template_hub, marca, "hub.html")
    trocas = {
        "player-css": regioes["css"],
        "player-corpo": regioes["corpo"],
        "player-js": regioes["js"],
        "aulas": html_quadro(classificar(aulas_sel, quadro or {})[0], estado),
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


def checar(pagina_html, files, raiz=RAIZ, mantidos=()):
    """Problemas do manifesto: fonte inexistente, link do index fora dele, teto de entradas.

    `mantidos` (DIFF, s193) = o que ja esta no ar e fica fora de `files`: conta como vivo para o
    link do index e para o teto -- o runtime o mantem."""
    raiz = Path(raiz)
    problemas = []
    vivos = {pub: fonte for pub, fonte in files.items() if fonte is not None}
    for pub, fonte in sorted(vivos.items()):
        if not (raiz / fonte).is_file():
            problemas.append("fonte inexistente: %s <- %s" % (pub, fonte))
    no_ar = set(vivos) | {normalizar_path(p) for p in mantidos}
    for href in sorted(hrefs_relativos(pagina_html)):
        if href not in no_ar:
            problemas.append("link morto no index: %s (fora do manifesto)" % href)
    if len(no_ar) + 1 > TETO_ENTRADAS:
        problemas.append("%d arquivos + a pagina > teto de %d entradas" % (len(no_ar), TETO_ENTRADAS))
    return problemas


_RE_GERADO = re.compile(r"<!--gerado-->.*?<!--/gerado-->", re.S)


def _sha(texto):
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def hash_painel(texto):
    """sha256 do painel SEM o carimbo de geracao (entre `<!--gerado-->` e `<!--/gerado-->`,
    `tools/painel.py`): regenerar o painel a cada tique nao pode, sozinho, pedir publish."""
    return _sha(_RE_GERADO.sub("", texto or ""))


def projecao(painel_texto, quadro_html, lote):
    """O que o operador VE e que muda sem lote novo: o painel, o quadro e qual lote esta no ar."""
    return {"painel": hash_painel(painel_texto) if painel_texto is not None else None,
            "quadro": _sha(quadro_html),
            "sessao": (lote or {}).get("sessao")}


def ids_com_nota(notas):
    """card_ids com doc na colecao `sessoes/<sessao>/notas`: DIRETORIO do `ArtifactData list`
    (1 arquivo `<card_id>.json` por doc), JSON {"notas": [...]} / lista de docs, ou iteravel."""
    if notas is None:
        return set()
    if isinstance(notas, (str, Path)):
        caminho = Path(notas)
        if caminho.is_dir():
            ids = set()
            for arq in caminho.rglob("*.json"):
                try:
                    doc = json.loads(arq.read_text(encoding="utf-8"))
                except ValueError:
                    doc = {}
                cid = (doc or {}).get("card_id", arq.stem)
                try:
                    ids.add(int(cid))
                except (TypeError, ValueError):
                    continue
            return ids
        if not caminho.is_file():
            return set()
        obj = json.loads(caminho.read_text(encoding="utf-8"))
        notas = obj.get("notas") if isinstance(obj, dict) else obj
    ids = set()
    for n in notas or []:
        cid = n.get("card_id") if isinstance(n, dict) else n
        try:
            ids.add(int(cid))
        except (TypeError, ValueError):
            continue
    return ids


def precisa_publicar(registro_projecao, atual, lote, com_nota):
    """A decisao do tique do /hub-backend, PURA. Devolve {"publicar", "acao", "motivos",
    "drenado", "notas", "total"}; `acao`:

    - `nova_fila`: o lote foi DRENADO (todo card tem doc) ou esta vazio -> gravar, exportar e
      publicar a proxima fila (lote vazio: conferir se o saldo do dia voltou);
    - `mesmo_lote`: lote em curso, mas o painel ou o quadro mudou (ou nao ha projecao confirmada,
      ou o lote no ar nao e o do registro) -> republicar com o MESMO lote -- mesmo `sessao`, mesmos
      cards; as notas ja dadas voltam do `db` no reload;
    - `nada`: lote em curso e projecao igual a do ultimo publish confirmado."""
    cards = [int(c["card_id"]) for c in (lote or {}).get("cards") or []]
    feitos = sum(1 for c in cards if c in com_nota)
    drenado = not cards or feitos == len(cards)
    motivos = []
    reg = registro_projecao or {}
    if not reg:
        motivos.append("sem projecao confirmada no registro")
    else:
        if reg.get("sessao") != atual.get("sessao"):
            motivos.append("lote no ar (%s) difere do registro (%s)"
                           % (atual.get("sessao"), reg.get("sessao")))
        if reg.get("painel") != atual.get("painel"):
            motivos.append("painel mudou")
        if reg.get("quadro") != atual.get("quadro"):
            motivos.append("quadro de aulas mudou")
    if drenado:
        acao = "nova_fila"
        motivos.insert(0, "lote drenado (%d/%d)" % (feitos, len(cards)) if cards
                       else "lote vazio: conferir se o saldo do dia voltou")
    elif motivos:
        acao = "mesmo_lote"
    else:
        acao = "nada"
        motivos.append("lote em curso (%d/%d) e projecao igual a publicada" % (feitos, len(cards)))
    return {"publicar": acao != "nada", "acao": acao, "motivos": motivos, "drenado": drenado,
            "notas": feitos, "total": len(cards)}


def tarefas_a_concluir(estado, quadro, plano_linhas):
    """Itens marcados como feitos no quadro cuja tarefa do plano ainda esta pendente. PURA.
    [{"slug", "tarefa_id", "tema"}] -- o tique so RELATA: o `plano.py --concluir` exige `--sessao`
    (volume em `sessoes_bulk`), que uma aula nao tem (pendencia de decisao, s194)."""
    por_id = {int(l["id"]): l for l in plano_linhas or [] if l.get("id") is not None}
    saida = []
    for slug, v in sorted((estado or {}).items()):
        tid = (quadro.get(slug) or {}).get("tarefa_id")
        if not v.get("feito") or tid is None:
            continue
        linha = por_id.get(int(tid))
        if linha and linha.get("status") == "pendente":
            saida.append({"slug": slug, "tarefa_id": int(tid), "tema": linha.get("tema")})
    return saida


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


def hash_de(path):
    """(sha256 hex, bytes) do conteudo -- o que o registro guarda por path publicado."""
    dados = Path(path).read_bytes()
    return hashlib.sha256(dados).hexdigest(), len(dados)


def _como_vivos(publicado):
    """{path: bytes | None} a partir de paths, de pares (path, bytes) ou de um dict."""
    if isinstance(publicado, dict):
        itens = publicado.items()
    else:
        itens = ((p, None) if isinstance(p, str) else tuple(p) for p in publicado or ())
    return {normalizar_path(p): b for p, b in itens if p}


def ler_projecao_registrada(out):
    """A projecao (painel, quadro, sessao) do ultimo publish CONFIRMADO; {} sem registro ou
    registro de antes da s194 (sem o campo) -- o que faz o proximo tique republicar uma vez."""
    caminho = Path(out) / REGISTRO
    if not caminho.is_file():
        return {}
    try:
        return dict(json.loads(caminho.read_text(encoding="utf-8")).get("projecao") or {})
    except (ValueError, AttributeError):
        return {}


def ler_registro(out):
    """({publicado: {"sha256", "bytes", "fonte"}}, aviso | None) do ultimo publish CONFIRMADO.
    Sem registro = {} (tudo vai, o v0); registro ilegivel = {} com aviso -- nunca omite as cegas."""
    caminho = Path(out) / REGISTRO
    if not caminho.is_file():
        return {}, None
    try:
        return dict(json.loads(caminho.read_text(encoding="utf-8")).get("arquivos") or {}), None
    except (ValueError, AttributeError) as e:
        return {}, "registro ilegivel (%s): tudo vai neste publish" % e


def confirmar(out, agora=None):
    """Depois do publish ACEITO: o estado que o ultimo build deixa no ar vira o registro.
    Devolve (n arquivos registrados, montado_em do build confirmado)."""
    out = Path(out)
    estado = json.loads((out / ESTADO_POS).read_text(encoding="utf-8"))
    agora = agora or db.agora()
    registro = {"confirmado_em": agora.strftime("%Y-%m-%d %H:%M:%S"),
                "montado_em": estado.get("montado_em"),
                "arquivos": estado.get("arquivos") or {},
                "projecao": estado.get("projecao") or {}}
    (out / REGISTRO).write_text(json.dumps(registro, ensure_ascii=False, indent=1) + "\n",
                                encoding="utf-8")
    return len(registro["arquivos"]), registro["montado_em"]


def construir(lote, raiz=RAIZ, out=None, painel=None, publicado=(), agora=None, data_fn=None,
              template_hub=None, template_player=None, registro=None, quadro=None,
              estado_quadro=None):
    """Monta `index.html` + `manifesto.json` + `estado_pos_publish.json` em `out`.

    `publicado` = a listagem viva: paths, pares (path, bytes) ou {path: bytes}. `registro` =
    injetavel; None = o `registro_publicado.json` de `out`. `quadro` = o registro do quadro de
    aulas (None = `core/hub_quadro.json` de `raiz`); `estado_quadro` = {slug: {feito, ts}} do `db`
    (`ler_estado_quadro`), None = nada feito. Devolve (manifesto, problemas, avisos)."""
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
    if quadro is None:
        quadro = ler_quadro(raiz / QUADRO_REG)
        if not quadro:
            avisos.append("registro do quadro ausente (%s): toda aula entra como %r"
                          % (QUADRO_REG, TIPO_PADRAO))
    classificadas, avisos_quadro = classificar(selecionadas, quadro)
    avisos.extend(avisos_quadro)
    tem_painel = painel_path.is_file()
    if not tem_painel:
        avisos.append("painel ausente (%s): a aba Painel sai com o aviso de 'nao gerado'"
                      % _rel(painel_path, raiz))
    vivos = _como_vivos(publicado)
    completo = montar_manifesto(selecionadas, _rel(painel_path, raiz) if tem_painel else None,
                                list(vivos))
    fontes = {pub: hash_de(raiz / fonte) for pub, fonte in completo.items()
              if fonte is not None and (raiz / fonte).is_file()}
    if registro is None:
        registro, aviso = ler_registro(out)
        if aviso:
            avisos.append(aviso)
    files, mantidos, estado = aplicar_diff(completo, fontes, registro, vivos)

    th = template_hub if template_hub is not None else TEMPLATE_HUB.read_text(encoding="utf-8")
    tp = (template_player if template_player is not None
          else TEMPLATE_PLAYER.read_text(encoding="utf-8"))
    agora = agora or db.agora()
    pagina = montar_index(th, tp, lote, selecionadas, tem_painel, agora, quadro, estado_quadro)
    proj = projecao(painel_path.read_text(encoding="utf-8") if tem_painel else None,
                    html_quadro(classificadas, estado_quadro), lote)

    out.mkdir(parents=True, exist_ok=True)
    (out / PAGINA).write_text(pagina, encoding="utf-8")
    montado_em = agora.strftime("%Y-%m-%d %H:%M:%S")
    manifesto = {
        "file_path": _rel(out / PAGINA, raiz),
        "files": files,
        "sessao": lote.get("sessao"),
        "total_cards": len(lote.get("cards") or []),
        "aulas": len(selecionadas),
        "montado_em": montado_em,
        "mantidos": mantidos,
    }
    (out / MANIFESTO).write_text(json.dumps(manifesto, ensure_ascii=False, indent=1) + "\n",
                                 encoding="utf-8")
    (out / ESTADO_POS).write_text(
        json.dumps({"montado_em": montado_em, "arquivos": estado, "projecao": proj},
                   ensure_ascii=False,
                   indent=1) + "\n", encoding="utf-8")
    return manifesto, checar(pagina, files, raiz, mantidos), avisos


def decidir(lote, out, raiz=RAIZ, painel=None, notas=None, estado_quadro=None, quadro=None,
            data_fn=None, plano_linhas=None):
    """O `--precisa-publicar`: a projecao ATUAL (painel em disco + quadro que o build montaria)
    contra a do registro, mais o estado do lote. Le o plano (`db.plano_listar`, read-only) so para
    as aulas feitas com tarefa. Devolve o dict de `precisa_publicar` + "concluir"."""
    raiz = Path(raiz)
    painel_path = Path(painel) if painel else raiz / "artifacts" / "painel.html"
    if not painel_path.is_absolute():
        painel_path = raiz / painel_path
    if quadro is None:
        quadro = ler_quadro(raiz / QUADRO_REG)
    estado = (estado_quadro if isinstance(estado_quadro, dict)
              else ler_estado_quadro(estado_quadro))
    aulas, _ = coletar_aulas(raiz, data_fn)
    classificadas, _ = classificar(selecionar_aulas(aulas), quadro)
    atual = projecao(painel_path.read_text(encoding="utf-8") if painel_path.is_file() else None,
                     html_quadro(classificadas, estado), lote)
    decisao = precisa_publicar(ler_projecao_registrada(out), atual, lote, ids_com_nota(notas))
    if plano_linhas is None:
        plano_linhas = db.plano_listar()
    decisao["concluir"] = tarefas_a_concluir(estado, quadro, plano_linhas)
    return decisao


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
    acao.add_argument("--precisa-publicar", dest="precisa_publicar", action="store_true",
                      help="decisao do tique do /hub-backend: compara o lote (drenado?), o "
                           "painel e o quadro com a projecao do ultimo publish confirmado e diz "
                           "sim/nao, a acao (nova_fila | mesmo_lote | nada) e o motivo; lista as "
                           "aulas marcadas como feitas cuja tarefa do plano segue pendente")
    acao.add_argument("--confirmar", action="store_true",
                      help="DEPOIS do publish aceito: o estado_pos_publish.json do ultimo "
                           "--build de --out vira o registro_publicado.json, a base do DIFF. "
                           "Publish recusado = nao confirmar")
    ap.add_argument("--lote", metavar="ARQ.json",
                    help="--build: o lote de fsrs_queue.py --export-player (ou o extraido "
                         "da pagina viva)")
    ap.add_argument("--publicado", metavar="LISTA",
                    help="--build: a listagem viva do hub (Artifact list scope=files colada "
                         "como sai, 1 path por linha, ou JSON com path/bytes); o que saiu da "
                         "selecao vira null, e so fica fora de files (mantido) o que esta nela "
                         "com a hash do registro e o mesmo tamanho")
    ap.add_argument("--notas", metavar="DIR|ARQ",
                    help="--precisa-publicar: as notas do lote no db (o out_dir do ArtifactData "
                         "list de sessoes/<sessao>/notas, ou o JSON {notas: [...]})")
    ap.add_argument("--quadro-estado", dest="quadro_estado", metavar="DIR|ARQ",
                    help="--build/--precisa-publicar: o estado 'feito' do quadro no db (o out_dir "
                         "do ArtifactData list da colecao quadro, ou JSON {slug: {feito, ts}})")
    ap.add_argument("--json", action="store_true", help="--precisa-publicar: saida em JSON")
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
        problemas = checar((out / PAGINA).read_text(encoding="utf-8"), manifesto["files"], RAIZ,
                           manifesto.get("mantidos") or ())
        for p in problemas:
            print("[hub] PROBLEMA: %s" % p)
        print("[hub] --check: %s" % ("OK" if not problemas else "%d problema(s)" % len(problemas)))
        return 1 if problemas else 0

    if args.precisa_publicar:
        if not args.lote:
            ap.error("--precisa-publicar exige --lote ARQ.json (o lote no ar)")
        lote = json.loads(Path(args.lote).read_text(encoding="utf-8"))
        decisao = decidir(lote, out, raiz=RAIZ, painel=args.painel, notas=args.notas,
                          estado_quadro=args.quadro_estado)
        if args.json:
            print(json.dumps(decisao, ensure_ascii=False, indent=1))
        else:
            print("[hub] precisa publicar: %s -- %s (%s)"
                  % ("sim" if decisao["publicar"] else "nao", decisao["acao"],
                     "; ".join(decisao["motivos"])))
            for t in decisao["concluir"]:
                print("[hub] aula feita no quadro com tarefa pendente: #%d (%s, aula %s) -- "
                      "pendencia de decisao: plano.py --concluir exige --sessao"
                      % (t["tarefa_id"], t["tema"], t["slug"]))
        return 0

    if args.confirmar:
        if not (out / ESTADO_POS).is_file():
            print("[hub] --confirmar: %s ausente em %s -- rode --build (e publique) antes"
                  % (ESTADO_POS, out))
            return 1
        n, montado_em = confirmar(out)
        print("[hub] registro: %d arquivo(s) no ar pelo build de %s -> %s"
              % (n, montado_em, _rel(out / REGISTRO, RAIZ)))
        return 0

    if not args.lote:
        ap.error("--build exige --lote ARQ.json")
    lote = json.loads(Path(args.lote).read_text(encoding="utf-8"))
    publicado = ler_publicado_detalhado(Path(args.publicado).read_text(encoding="utf-8")) \
        if args.publicado else []
    manifesto, problemas, avisos = construir(
        lote, out=out, painel=args.painel, publicado=publicado,
        estado_quadro=ler_estado_quadro(args.quadro_estado) if args.quadro_estado else None)
    files = manifesto["files"]
    nulos = sorted(p for p, f in files.items() if f is None)
    enviados = sorted(p for p, f in files.items() if f is not None)
    mantidos = manifesto["mantidos"]
    no_ar = len(enviados) + len(mantidos)
    kb = (out / PAGINA).stat().st_size / 1024.0
    print("[hub] pagina: %s (%.0f KB) -- lote %s, %d cards"
          % (manifesto["file_path"], kb, manifesto["sessao"], manifesto["total_cards"]))
    print("[hub] no ar depois do publish: %d arquivo(s) (aulas %d; cap %d) + pagina = %d/%d "
          "entradas" % (no_ar, manifesto["aulas"], CAP_AULAS, no_ar + 1, TETO_ENTRADAS))
    print("[hub] files (novos ou alterados -- LER INTEIROS antes do publish): %d%s"
          % (len(enviados), (" -- " + ", ".join(enviados)) if enviados else ""))
    print("[hub] mantidos (ja no ar, intocados -- fora de files): %d" % len(mantidos))
    print("[hub] null (saem do hub): %d%s" % (len(nulos), (" -- " + ", ".join(nulos)) if nulos else ""))
    for aviso in avisos:
        print("[hub] AVISO: %s" % aviso)
    print("[hub] manifesto: %s -- `file_path` + `files` do Artifact publish" % _rel(out / MANIFESTO, RAIZ))
    print("[hub] depois do publish ACEITO: python tools/hub.py --confirmar%s"
          % ("" if out == _saida_padrao() else " --out %s" % out))
    for p in problemas:
        print("[hub] PROBLEMA: %s" % p)
    print("[hub] --check: %s" % ("OK" if not problemas else "%d problema(s)" % len(problemas)))
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
