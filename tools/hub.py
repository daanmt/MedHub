"""hub.py -- monta o MedHub HUB: UMA pagina (Cards + Aulas + Painel) e o manifesto do publish.

Spec: .vibeflow/specs/medhub-hub-v0-part-1.md (PRD .vibeflow/prds/medhub-hub-2026-09-22.md).

Por que existe: cada aula-base, player e painel virava um artifact NOVO na conta claude.ai, que e
compartilhada com o time de conteudo; o operador apagava por higiene e os links do HANDOFF morriam
no mesmo dia (medido em 22/09/2026). O hub e UM artifact, republicado no lugar.

O que ele monta, em `--out` (default `tmp/hub/`):
- `index.html` a partir de `core/templates/hub.html`, com o player INLINE composto das tres regioes
  marcadas de `core/templates/player.html` (a fonte UNICA do player) e o lote injetado por
  `fsrs_queue.injetar_lote` (mesmo marcador unico, mesmo escape de `</script>`);
- a aba Aulas como QUADRO POR SEMANAS (s195): as tarefas pendentes de `plano_tarefas` (read-only,
  `db.plano_listar`) em "Atrasadas" e "Semana N" ate a semana da prova, cada bloco com o peso, as
  questoes previstas e a acao; a aula ligada pelo registro `core/hub_quadro.json` (`tarefas` /
  `tarefa_id`) entra no bloco da tarefa. s216 (hub-integracao part-1): a aba se chama TEORIA (id
  `aulas` intacto) e mostra so a tarefa de aula e a tarefa com aula ligada -- o cronograma inteiro
  mora no Painel. s216 (part-3): nada concluido sai mais do hub -- a aula feita e a aula sem tarefa
  pendente moram na BIBLIOTECA da Teoria (o `git mv` para a pasta de arquivo acabou); s217 (P17): a
  Biblioteca em grupos por grande area (CM, CIR, MFC, PED, GO, "Varias areas"), a area pelo bloco da
  tarefa no plano ou, sem tarefa, pelo `bloco` do registro;
- `manifesto.json` = exatamente os argumentos do `Artifact publish`: `file_path` (a pagina) e
  `files` ({path publicado: fonte | null}). Painel e aulas vao DIRETO das fontes em `artifacts/`
  (sem copia). Arquivo OMITIDO num update e MANTIDO pelo runtime; so `null` remove -- por isso o que
  saiu da selecao e consta em `--publicado` (a listagem do artifact) vira `null`.
- DIFF (v1, s193, spec `medhub-hub-v1-manifesto-diff`): `files` leva so o que e NOVO ou MUDOU. O
  que ja esta no ar e intocado fica em `manifesto["mantidos"]` -- nao sobe e nao precisa ser relido
  antes do publish (a releitura das 6 aulas custou 378k tokens em 22/09). Base: o registro local
  `registro_publicado.json`, que so o `--confirmar` escreve, DEPOIS do publish aceito, a partir do
  `estado_pos_publish.json` do build.

Limites como DADO: 255 entradas por versao (contrato do Artifact), 8 reservadas, cap de 200 aulas
(mais novas primeiro, pela data de criacao no git; era 120 ate a s216, quando a Biblioteca passou a
guardar tudo o que foi concluido).

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
from datetime import date, datetime
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
# So leitores PUROS do plano (s195): a semana da prova, o calendario da trilha e a classe da
# tarefa -- a mesma regua do `plano.py --panorama`. O hub nunca grava o plano.
from tools.plano import (  # noqa: E402
    AREA_SIMULADO, SEMANAS_FASE1, calendario_trilha, classe_da_tarefa)

TEMPLATE_HUB = RAIZ / "core" / "templates" / "hub.html"
#: Registro do quadro da aba Aulas (s194): slug -> {tipo, titulo, tarefa_id?, tarefas?, bloco?}.
QUADRO_REG = "core/hub_quadro.json"
#: Tipos de aula do registro (validacao + etiqueta no bloco). Rotulos curtos (celular).
TIPOS_QUADRO = (("aula", "Aulas-base"), ("revisao", "Revisões"), ("analise", "Análises"))
TIPO_PADRAO = "aula"
#: Grandes areas da Biblioteca da Teoria (s217, P17; pedido do operador em 06/10/2026: "a biblioteca
#: nao tem como ser desorganizada. preciso que voce organize por grande area (CM, Cir, MFC, Ped ou
#: GO)"): chave e rotulo de tela, NA ORDEM DOS GRUPOS. As cinco primeiras sao os blocos do plano
#: (`db.bloco_de`); VARIAS = item de varias areas (as pilulas), grupo final so com item; SEM = defeito
#: (item sem area resolvivel), acusado pelo build e pelo --check -- valor do build, nunca do registro.
AREAS_BIBLIOTECA = (("CM", "Clínica Médica"), ("CIR", "Cirurgia"),
                    ("MFC", "Medicina de Família e Comunidade"), ("PED", "Pediatria"),
                    ("GO", "Ginecologia e Obstetrícia"), ("VARIAS", "Várias áreas"), ("SEM", "Sem área"))
AREA_SEM = "SEM"
#: O vocabulario do campo `bloco` do registro (o SEM e do build).
BLOCOS_REGISTRO = tuple(a for a, _r in AREAS_BIBLIOTECA if a != AREA_SEM)
#: Quadro por semanas (s195): a ultima secao e a semana da PROVA (`plano.SEMANAS_FASE1`); a Fase 2
#: nao entra na aba -- e panorama de execucao, nao inventario.
SEMANA_FINAL_QUADRO = max(SEMANAS_FASE1)
#: Etiqueta da tarefa sem lista, por classe do `plano.classe_da_tarefa`.
ROTULO_CLASSE = {"aula": "aula", "caderno": "caderno a criar", "sem_lista": "sem lista"}
#: Colecao do db onde a pagina grava {feito, ts} por slug (doc `quadro/<slug>`). Regra de escrita
#: `{path: "quadro", write: "interact"}` na declaracao de capabilities (revisar.md).
#: Aba Questoes (s197): `listas/*`, `questoes/*`, `respostas/*` e `analises/*` do MESMO db, com
#: read/write `admin` (conteudo do EMED nunca legivel por link); semeadas por `emed_banco.py
#: --exportar` + ArtifactData, nunca pelo build -- a pagina nao carrega questao inline.
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
#: Decisao do /ai-eng (22/09): cap como DADO; folga 2x sobre o que cabe ate 01/11. s216 (part-3): 120
#: -> 200 -- nada concluido sai mais do hub (Biblioteca); 24 aulas hoje, ~5 por semana, e cada aula e
#: um arquivo lido no publish (E01): 200 cobre ate 01/11 com folga, dentro do teto de 247 entradas.
CAP_AULAS = 200

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
    ("semanas", "<!-- @hub:semanas -->"),
    # s216 (hub-integracao part-2): tarefa -> aulas ligadas, para a aba Listas levar a aula que prepara
    ("ligacoes", "<!-- @hub:ligacoes -->"),
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
    """{slug: {"tipo", "titulo"?, "tarefa_id"?, "tarefas"?, "bloco"?}} do registro versionado.
    Arquivo ausente = {}. Tipo fora de TIPOS_QUADRO ou `bloco` fora de BLOCOS_REGISTRO (s217) falha
    ALTO: registro errado nao vira coluna nem grupo inventado."""
    caminho = Path(caminho)
    if not caminho.is_file():
        return {}
    itens = json.loads(caminho.read_text(encoding="utf-8")).get("itens") or {}
    validos = {t for t, _ in TIPOS_QUADRO}
    for slug, item in itens.items():
        if (item or {}).get("tipo") not in validos:
            raise ValueError("%s: tipo %r da aula %r fora de %s"
                             % (caminho.name, (item or {}).get("tipo"), slug, sorted(validos)))
        tarefas = (item or {}).get("tarefas")
        if tarefas is not None and (not isinstance(tarefas, list)
                                    or not all(isinstance(t, int) for t in tarefas)):
            raise ValueError("%s: `tarefas` da aula %r tem de ser lista de ids inteiros, veio %r"
                             % (caminho.name, slug, tarefas))
        bloco = (item or {}).get("bloco")
        if bloco is not None and bloco not in BLOCOS_REGISTRO:
            raise ValueError("%s: `bloco` %r da aula %r fora de %s"
                             % (caminho.name, bloco, slug, list(BLOCOS_REGISTRO)))
    return itens


def _bloco_da_linha(linha):
    """O bloco UERJ de uma linha do plano: o `bloco` que `db.plano_listar` deriva da area; linha sem
    ele (ou fora do vocabulario) deriva da `area` pela MESMA funcao (`db.bloco_de`); sem area, None."""
    bloco = linha.get("bloco")
    if bloco in BLOCOS_REGISTRO:
        return bloco
    return db.bloco_de(linha.get("area")) if linha.get("area") else None


def _tarefas_do_registro(reg):
    """Os ids de tarefa de um item do registro, a de `tarefa_id` primeiro (a que ele CUMPRE)."""
    return (([reg["tarefa_id"]] if reg.get("tarefa_id") is not None else [])
            + list(reg.get("tarefas") or []))


def grande_area(reg, blocos):
    """A grande area (chave de AREAS_BIBLIOTECA) de um item do registro, ou None. PURA. s217 (P17):
    a aula com tarefa herda o bloco da tarefa no plano -- a de `tarefa_id` (a que ela CUMPRE) vence;
    senao, a primeira de `tarefas` que o plano conhece. O `bloco` declarado no registro vale so sem
    tarefa resolvivel (a RD, que nao tem tarefa; a tarefa fora do plano). `blocos` = {tarefa_id:
    bloco} do plano INTEIRO (a tarefa concluida tambem conta)."""
    reg = reg or {}
    for tid in _tarefas_do_registro(reg):
        bloco = (blocos or {}).get(int(tid))
        if bloco in BLOCOS_REGISTRO:
            return bloco
    return reg.get("bloco") if reg.get("bloco") in BLOCOS_REGISTRO else None


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


def _q_de(linha):
    """`q_previstas` como inteiro (a mesma leitura do `plano.panorama`); ilegivel = 0."""
    try:
        return int(round(float(linha.get("q_previstas") or 0)))
    except (TypeError, ValueError):
        return 0


def semana_atual(calendario, hoje, pendentes):
    """A semana de HOJE pela regua do `plano.panorama`: a primeira do calendario cujo fim >= hoje;
    sem calendario (ou depois dele), a menor semana com pendencia; None sem nada. Nunca inventa."""
    futuras = [s for s in sorted(calendario or {}) if calendario[s][1] >= hoje]
    if futuras:
        return futuras[0]
    semanas = sorted({int(l["semana_plano"]) for l in pendentes})
    return semanas[0] if semanas else None


def ligacoes_do_quadro(classificadas, quadro):
    """{tarefa_id: [(Aula, titulo, cumpre)]}: `tarefas` = a aula PREPARA a tarefa (lista ou aula);
    `tarefa_id` = a aula CUMPRE a tarefa (custom de aula) -- so essa ganha o controle 'feito',
    que o tique converte em `plano.py --concluir ID --leitura`."""
    por_tarefa = {}
    for a, _tipo, titulo, tid in classificadas:
        reg = (quadro or {}).get(a.slug) or {}
        ids = {int(x) for x in (reg.get("tarefas") or [])}
        if tid is not None:
            ids.add(int(tid))
        for i in sorted(ids):
            por_tarefa.setdefault(i, []).append((a, titulo, tid is not None and int(tid) == i))
    return por_tarefa


def secoes_do_quadro(classificadas, plano_linhas=None, calendario=None, hoje=None, estado=None,
                     quadro=None, semana_final=SEMANA_FINAL_QUADRO):
    """O quadro por SEMANAS (pedido do operador, s195): (secoes, biblioteca, avisos). PURA.

    O defeito que encerra: a aba listava aulas por tipo, sem dizer de que tarefa eram nem quantas
    questoes esperavam -- ele nao via o que vinha depois. A unidade passa a ser a TAREFA pendente
    do plano, em "Atrasadas" e "Semana N" ate `semana_final` (a da prova), cada bloco com o peso,
    as questoes previstas e a acao (lista, aula, ou 'aula a preparar'). Aula ligada
    (`ligacoes_do_quadro`) vai DENTRO do bloco. `estado` (db) manda o item feito para a
    Biblioteca, riscado. Cada item guarda `secao` e `ordem` para a pagina devolve-lo ao lugar.

    s216 (hub-integracao part-1, pedido do operador em 05/10): a aba vira TEORIA -- o cronograma
    inteiro (92 tarefas) aparecia aqui e no Painel; so 12 eram de aula. Ficam a tarefa de aula
    (`classe_da_tarefa == "aula"`) e a tarefa de qualquer classe com aula ligada (prepara ou
    cumpre); a lista sem aula mora so no Painel. A analise (`tipo: analise`) sai de toda secao:
    mora na Documentacao do Painel. O filtro e de EXIBICAO: `semana_atual` ve TODOS os pendentes
    (uma regua so de semana, armadilha A2); semana futura sem nada a mostrar nao vira secao.

    s216 (part-3, decisao do operador em 05/10: "so daqui em diante"): "Outras aulas" e
    "Concluidas" viram UMA secao, a BIBLIOTECA -- os itens feitos (riscados) e as aulas sem tarefa
    pendente, por data de criacao (mais nova primeiro). Nada vai mais para a pasta de arquivo: a aula
    concluida fica a um toque. A aula da Biblioteca tem `secao = "biblioteca"` (sem secao de origem:
    desmarcada, fica la). Devolve (secoes, biblioteca, avisos).

    s217 (P17, pedido do operador em 06/10: "organize por grande area"): todo item leva `grupo` = a
    grande area -- a tarefa, o bloco dela no plano; a aula, `grande_area` (o bloco da tarefa; sem
    tarefa, o `bloco` do registro). A pagina le dele o grupo da Biblioteca para onde o feito vai. Item
    sem area = AVISO nomeando o slug (o --check repete pela pagina); com o plano fora, a aula com tarefa
    nao e defeito de registro (o build ja avisa "plano indisponivel")."""
    feitos = {s for s, v in (estado or {}).items() if v.get("feito")}
    hoje = hoje or date.today()
    pendentes = [l for l in plano_linhas or [] if l.get("status") == "pendente"
                 and l.get("semana_plano") is not None and int(l["semana_plano"]) <= semana_final]
    atual = semana_atual(calendario, hoje, pendentes)
    por_tarefa = ligacoes_do_quadro(classificadas, quadro)
    # o plano INTEIRO (a aula cuja tarefa ja foi feita tambem herda o bloco dela)
    blocos = {int(l["id"]): _bloco_da_linha(l) for l in plano_linhas or [] if l.get("id") is not None}

    def na_teoria(l):
        return classe_da_tarefa(l) == "aula" or int(l["id"]) in por_tarefa
    usadas, avisos, secoes, concluidas = set(), [], [], []
    contador = [0]

    def ordem():
        contador[0] += 1
        return contador[0] - 1

    def item_tarefa(l, secao):
        tid = int(l["id"])
        aulas = por_tarefa.get(tid, [])
        usadas.update(a.slug for a, _t, _c in aulas)
        classe = classe_da_tarefa(l)
        cumpre = next(((a, tit) for a, tit, c in aulas if c), None) if classe == "aula" else None
        cal = (calendario or {}).get(int(l["semana_plano"]))
        return {"tipo": "tarefa", "id": tid, "tema": l.get("tema") or "(sem tema)",
                "bloco": l.get("bloco"), "q": _q_de(l), "classe": classe,
                "url_lista": l.get("url_lista"), "semana": int(l["semana_plano"]),
                "no_hub": bool(l.get("no_hub")), "area": l.get("area"),
                "atrasada": int(l["semana_plano"]) < atual,
                # prazo = o fim da semana da tarefa no calendario da trilha (pedido dele, s195:
                # "o prazo da tarefa, para ajudar na gestao do cronograma"); sem calendario, None
                "prazo": cal[1] if cal else None,
                "aulas": [(a, tit) for a, tit, _c in aulas],
                "slug": cumpre[0].slug if cumpre else None,
                "tipo_aula": TIPO_PADRAO, "titulo": cumpre[1] if cumpre else None,
                "data": cumpre[0].data if cumpre else None,
                "grupo": blocos.get(tid), "secao": secao, "ordem": ordem()}

    def secao(chave, titulo, linhas, rotulo="tarefa", fixa=True):
        itens = [item_tarefa(l, chave) for l in linhas]
        vivos = [i for i in itens if not (i["slug"] and i["slug"] in feitos)]
        concluidas.extend(dict(i, feito=True) for i in itens if i["slug"] and i["slug"] in feitos)
        secoes.append({"chave": chave, "titulo": titulo, "rotulo": rotulo, "fixa": fixa,
                       "q": sum(i["q"] for i in itens), "itens": vivos})

    if atual is not None:
        atrasadas = [l for l in pendentes if int(l["semana_plano"]) < atual and na_teoria(l)]
        if atrasadas:
            secao("atrasadas", "Atrasadas", atrasadas)
        ultima = max([int(l["semana_plano"]) for l in pendentes] + [atual])
        for s in range(atual, ultima + 1):
            linhas = [l for l in pendentes if int(l["semana_plano"]) == s and na_teoria(l)]
            if not linhas and s != atual:
                continue
            cal = (calendario or {}).get(s)
            # s216: " a " entre as datas, como no Painel (o travessao e proibido na pagina)
            titulo = "Semana %d" % s + (" · %s a %s" % (cal[0].strftime("%d/%m"),
                                                         cal[1].strftime("%d/%m")) if cal else "")
            secao(str(s), titulo, linhas)

    # s210 (pedido do operador, 01/10): a revisao direcionada avulsa (tipo `revisao`, sem tarefa
    # pendente) ganha bloco PROPRIO no topo da aba -- em "Outras aulas" ela sumia no fim da lista.
    # s216 (part-3): a aula avulsa (sem tarefa pendente, inclusive a de tarefa ja concluida) mora na
    # Biblioteca; o aviso "candidata a arquivo" saiu junto com o `git mv`.
    avulsas, revisoes = [], []
    for a, tipo, titulo, tid in classificadas:
        if a.slug in usadas or tipo == "analise":   # s216: a analise mora no Painel (Documentacao)
            continue
        chave = "revisoes" if tipo == "revisao" else "biblioteca"
        item = {"tipo": "aula", "slug": a.slug, "aula": a, "titulo": titulo, "tipo_aula": tipo,
                "data": a.data, "grupo": grande_area((quadro or {}).get(a.slug), blocos),
                "secao": chave, "ordem": ordem(), "feito": a.slug in feitos}
        (avulsas if (a.slug in feitos or chave == "biblioteca") else revisoes).append(item)
    biblioteca = sorted(concluidas + avulsas, key=lambda i: i.get("data") or "", reverse=True)
    if any(i["tipo_aula"] == "revisao" for i in revisoes + biblioteca):
        secoes.insert(0, {"chave": "revisoes", "titulo": "Revisões direcionadas", "rotulo": "aula",
                          "fixa": False, "q": None, "itens": revisoes})
    for i in [i for s in secoes for i in s["itens"]] + biblioteca:
        aviso = _aviso_sem_area(i, quadro, blocos)
        if aviso:
            avisos.append(aviso)
    return secoes, biblioteca, avisos


def _aviso_sem_area(item, quadro, blocos):
    """O AVISO do item da Teoria sem grande area (s217), nomeando o slug e o motivo; None se tem area
    ou se a falta e do plano fora (aula com tarefa e plano vazio: degradado ja declarado)."""
    if item.get("grupo"):
        return None
    if item["tipo"] == "tarefa":
        nome = item.get("slug") or "tarefa #%d" % item["id"]
        motivo = "tarefa #%d sem bloco no plano" % item["id"]
    else:
        ids = _tarefas_do_registro((quadro or {}).get(item["slug"]) or {})
        if ids and not blocos:
            return None
        nome = item["slug"]
        motivo = ("tarefa %s fora do plano, sem `bloco`" % ", ".join("#%d" % int(t) for t in ids) if ids
                  else "sem tarefa e sem `bloco`")
    return ("item sem grande area na Biblioteca: %s (%s) -- registre `bloco` (%s) em %s; ate la ele "
            "fica no grupo 'Sem área'" % (nome, motivo, "|".join(BLOCOS_REGISTRO), QUADRO_REG))


def _html_item(item, feito=False):
    """Um bloco do quadro: tarefa (tema, peso, questoes, acao) ou aula avulsa. Botao 'feito' so
    no item com `slug` (a aula que CUMPRE uma tarefa de aula, ou a aula avulsa)."""
    slug = item.get("slug")
    classes = ["qd-item"]
    if item.get("atrasada"):
        classes.append("qd-atrasada")
    attrs = ' data-secao="%s" data-ordem="%d"' % (_e(item["secao"]), item["ordem"])
    if item.get("data"):   # s216 (part-3): a Biblioteca ordena por data de criacao, tambem ao vivo
        attrs += ' data-data="%s"' % _e(item["data"])
    # s217 (P17): o grupo da Biblioteca para onde o feito vai, tambem ao vivo (sem area = SEM, avisado)
    attrs += ' data-area="%s"' % _e(item.get("grupo") or AREA_SEM)
    if item["tipo"] == "tarefa":
        attrs += ' data-tarefa="%d" data-classe="%s"' % (item["id"], _e(item["classe"]))
    botao = ""
    if slug:
        titulo = item["titulo"]
        rotulo = ("Desmarcar %s" if feito else "Marcar %s como feita") % titulo
        attrs += ' data-slug="%s" data-tipo="%s" data-titulo="%s"%s' % (
            _e(slug), _e(item.get("tipo_aula") or TIPO_PADRAO), _e(titulo),
            ' data-feito="1"' if feito else "")
        botao = ('<button type="button" class="qd-feito" aria-pressed="%s" aria-label="%s" '
                 'title="%s" disabled><span aria-hidden="true"></span></button>'
                 % ("true" if feito else "false", _e(rotulo), _e(rotulo)))
    if item["tipo"] == "tarefa":
        tema = item["tema"]
        meta = ['<span class="qd-bl">%s</span>' % _e(item["bloco"])] if item.get("bloco") else []
        meta.append('<span>%s</span>' % ("%d questões" % item["q"] if item["q"]
                                         else _e(ROTULO_CLASSE.get(item["classe"], item["classe"]))))
        prazo = item.get("prazo")
        if item.get("atrasada"):
            meta.append('<span class="qd-atraso">semana %d%s</span>'
                        % (item["semana"], " · venceu %s" % prazo.strftime("%d/%m") if prazo else ""))
        elif prazo:
            meta.append('<span class="qd-prazo">até %s</span>' % prazo.strftime("%d/%m"))
        acoes = []
        url = item.get("url_lista")
        if url and item.get("no_hub"):
            # s201: as questoes ja estao no banco -> resolve na aba Listas. s213 (D4-1, decisao do
            # operador em 25/09: "nao sair do medhub"): vence o link do EMED, que some; o modo sai
            # da area (simulado -> Simulados; lista -> Questoes), a mesma regra do painel.
            modo = "simulados" if item.get("area") == AREA_SIMULADO else "questoes"
            acoes.append('<a href="#questoes" data-hub-aba="questoes" data-hub-modo="%s">'
                         'resolver no hub</a>' % modo)
        elif url and str(url).startswith(("http://", "https://")):
            acoes.append('<a href="%s" rel="noopener noreferrer">abrir lista</a>' % _e(url))
        elif url:
            # caminho LOCAL (a prova em PDF): resolve na maquina e morre na pagina publicada
            # (mesma regra do painel) -- texto, nao link quebrado
            acoes.append('<span class="tenue">prova em PDF no computador</span>')
        varias = len(item["aulas"]) > 1
        for a, tit in item["aulas"]:
            acoes.append('<a class="hub-aula" href="%s" data-titulo="%s">%s</a>'
                         % (_e(a.publicado), _e(tit), _e(tit) if varias else "abrir aula"))
        if not acoes:
            acoes.append('<span class="tenue">%s</span>'
                         % ("aula a preparar" if item["classe"] == "aula" else "sem lista ainda"))
    else:
        a = item["aula"]
        tema = item["titulo"]
        meta = ['<span class="qd-bl">%s</span>' % _e(dict(TIPOS_QUADRO).get(item["tipo_aula"], "Aula")),
                '<span>%s</span>' % _e(_data_curta(item["data"]))]
        acoes = ['<a class="hub-aula" href="%s" data-titulo="%s">abrir aula</a>'
                 % (_e(a.publicado), _e(item["titulo"]))]
    # O botao "feito" mora DENTRO do bloco (canto superior direito): fora dele, o item com botao
    # ficava 54 px mais estreito e desalinhado dos demais -- "o bloco de aulas esta bugado" (s195).
    return ('<li class="%s"%s><div class="qd-bloco">%s<p class="qd-tema">%s</p>'
            '<p class="qd-meta">%s</p><p class="qd-acao">%s</p></div></li>'
            % (" ".join(classes), attrs, botao, _e(tema), "".join(meta), "".join(acoes)))


def html_biblioteca(biblioteca):
    """O miolo da Biblioteca POR GRANDE AREA (s217, P17; pedido do operador em 06/10: "a biblioteca nao
    tem como ser desorganizada"): um grupo por area de AREAS_BIBLIOTECA, nessa ordem; grupo vazio nao
    sai; dentro do grupo, a ordem que a lista ja traz (data de criacao, a mais nova primeiro). A ordem
    e os rotulos vao em `data-areas`: a pagina cria, ao vivo, o grupo que o feito pede."""
    por_area = {}
    for i in biblioteca:
        por_area.setdefault(i.get("grupo") or AREA_SEM, []).append(i)
    grupos = "".join(
        '<div class="qd-area" data-area="%s"><h4 class="qd-titulo">%s <span class="qd-n" data-n>%d</span>'
        '</h4><ul class="qd-lista">%s</ul></div>'
        % (_e(chave), _e(rotulo), len(por_area[chave]),
           "".join(_html_item(i, i.get("feito", True)) for i in por_area[chave]))
        for chave, rotulo in AREAS_BIBLIOTECA if por_area.get(chave))
    ordem = json.dumps([list(p) for p in AREAS_BIBLIOTECA], ensure_ascii=False)
    return '<div class="qd-areas" data-areas="%s">%s</div>' % (_e(ordem), grupos)


def html_quadro(secoes, biblioteca=()):
    """A aba Teoria: secoes por semana (empilhadas), cada tarefa um bloco; a BIBLIOTECA (s216,
    part-3; era "Outras aulas" + "Concluidas"), recolhida, guarda o que esta feito no `db` (riscado)
    e as aulas sem tarefa pendente, em grupos por grande area (s217, `html_biblioteca`). O estado do
    build e o do `db` no momento do tique; a pagina reconcilia ao vivo quando o `db` abre."""
    if not any(s["itens"] for s in secoes) and not biblioteca:
        return '<p class="hub-vazio">Nada no quadro ainda: nem tarefa pendente, nem aula.</p>'
    partes = []
    for s in secoes:
        n = len(s["itens"])
        contagem = ('<span data-n>%d</span> <span data-nrot>%s</span>'
                    % (n, s["rotulo"] + ("" if n == 1 else "s")))
        if s["q"] is not None:
            contagem += ' · <span data-q>%d</span> questões' % s["q"]
        partes.append(
            '<section class="qd-sem" data-secao="%s" data-rotulo="%s" aria-label="%s"%s%s>'
            '<h3 class="qd-titulo">%s <span class="qd-n">%s</span></h3><ul class="qd-lista">%s</ul>'
            '<p class="qd-vazio"%s>Nada em aberto.</p></section>'
            % (_e(s["chave"]), _e(s["rotulo"]), _e(s["titulo"]), ' data-fixa="1"' if s["fixa"] else "",
               "" if (s["itens"] or s["fixa"]) else " hidden", _e(s["titulo"]), contagem,
               "".join(_html_item(i) for i in s["itens"]), " hidden" if s["itens"] else ""))
    return ('<div class="qd" id="hub-quadro">\n'
            '<p class="qd-aviso" id="hub-quadro-aviso" hidden>Marcar como feita não funciona '
            'nesta visualização.</p>\n'
            '<div class="qd-semanas">%s</div>\n'
            '<details class="qd-feitas" id="hub-quadro-feitas"><summary>Biblioteca '
            '<span class="qd-n" id="hub-quadro-nfeitas">%d</span></summary>'
            '%s</details>\n</div>'
            % ("".join(partes), len(biblioteca), html_biblioteca(biblioteca)))


def html_quadro_de(aulas_sel, quadro=None, estado=None, plano_linhas=None, calendario=None,
                   hoje=None):
    """(html do quadro, avisos) a partir das aulas selecionadas -- o MESMO caminho para a pagina
    (`montar_index`) e para a projecao (`construir`/`decidir`): um so quadro, nunca dois."""
    classificadas, avisos = classificar(aulas_sel, quadro or {})
    secoes, biblioteca, avisos_secoes = secoes_do_quadro(classificadas, plano_linhas, calendario,
                                                         hoje, estado, quadro)
    return html_quadro(secoes, biblioteca), avisos + avisos_secoes


def html_aulas(aulas_sel, quadro=None, estado=None):
    """Compatibilidade: o quadro sem plano (tudo na Biblioteca) -- chamadores antigos e testes."""
    return html_quadro_de(aulas_sel, quadro, estado)[0]


def html_semanas(plano_linhas=None, calendario=None, hoje=None, semana_final=SEMANA_FINAL_QUADRO):
    """O calendario das semanas para a aba Questoes, como JSON num `<script>` (s200). PURA.

    Pedido do operador ao fechar a 1a lista: as listas apareciam "soltas", sem ordem nem semana.
    A pagina le as listas do `db` em tempo real e agrupa por `semana`; para dizer o que esta
    atrasado e datar cada semana ela precisa da semana de HOJE -- a mesma regua do quadro
    (`semana_atual`, os mesmos pendentes), para as duas abas nunca discordarem."""
    hoje = hoje or date.today()
    pendentes = [l for l in plano_linhas or [] if l.get("status") == "pendente"
                 and l.get("semana_plano") is not None and int(l["semana_plano"]) <= semana_final]
    dados = {"atual": semana_atual(calendario, hoje, pendentes),
             "datas": {str(s): [ini.strftime("%d/%m"), fim.strftime("%d/%m")]
                       for s, (ini, fim) in sorted((calendario or {}).items())}}
    return ('<script type="application/json" id="hub-semanas">%s</script>'
            % json.dumps(dados, ensure_ascii=False).replace("<", "\\u003c"))


def dados_ligacoes(aulas_sel, quadro=None):
    """{str(tarefa_id): [{"href", "titulo"}]} das aulas ligadas a cada tarefa (prepara ou cumpre),
    pela MESMA regra do quadro (`ligacoes_do_quadro`). PURA. So aula selecionada (o href esta no
    manifesto). s216 (hub-integracao part-2)."""
    classificadas, _avisos = classificar(aulas_sel, quadro or {})
    return {str(tid): [{"href": a.publicado, "titulo": tit} for a, tit, _c in lst]
            for tid, lst in sorted(ligacoes_do_quadro(classificadas, quadro).items())}


def html_ligacoes(aulas_sel, quadro=None):
    """As ligacoes tarefa -> aula como JSON num `<script id="hub-ligacoes">` PROPRIO (s216, part-2).

    Pedido do operador (05/10): a lista da aba Listas leva a aula que a prepara -- antes so a Teoria
    sabia. JSON proprio, nao o `#hub-semanas`: aquele e a regua de semana, com teste de igualdade
    e semantica propria (armadilha A9). O hash entra na projecao: aula nova ligada republica."""
    return ('<script type="application/json" id="hub-ligacoes">%s</script>'
            % json.dumps(dados_ligacoes(aulas_sel, quadro), ensure_ascii=False).replace("<", "\\u003c"))


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


def _hoje_de(agora):
    """A data do quadro a partir do relogio recebido (datetime ou date); None = hoje."""
    if isinstance(agora, datetime):
        return agora.date()
    return agora or date.today()


def montar_index(template_hub, player_html, lote, aulas_sel, tem_painel, agora, quadro=None,
                 estado=None, plano_linhas=None, calendario=None):
    """A pagina: casca do hub + as 3 regioes do player + aulas/painel + o lote.

    `agora` nao vai para a tela (a linha "montado ... lote ... cards" saiu na s194, bastidor;
    o carimbo vive no manifesto): so data a semana do quadro. `plano_linhas`/`calendario` =
    as tarefas pendentes e as datas das semanas (s195); sem eles, o quadro sai so com as aulas."""
    regioes = extrair_regioes_player(player_html)
    for _nome, marca in LUGARES_HUB:
        _exatamente_uma(template_hub, marca, "hub.html")
    trocas = {
        "player-css": regioes["css"],
        "player-corpo": regioes["corpo"],
        "player-js": regioes["js"],
        "aulas": html_quadro_de(aulas_sel, quadro, estado, plano_linhas, calendario,
                                _hoje_de(agora))[0],
        "painel": html_painel(tem_painel),
        "semanas": html_semanas(plano_linhas, calendario, _hoje_de(agora)),
        "ligacoes": html_ligacoes(aulas_sel, quadro),
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


class _ColetorSemArea(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.itens = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "li" and "qd-item" in (a.get("class") or "").split() and a.get("data-area") == AREA_SEM:
            self.itens.append(a.get("data-slug") or "tarefa #%s" % a.get("data-tarefa"))


def sem_area_na_pagina(pagina_html):
    """Os itens do quadro da pagina MONTADA que cairam no grupo 'Sem área' (s217): slug, ou
    `tarefa #N` sem slug, na ordem da pagina. O --check os acusa como AVISO (warn-first: o exit nao
    muda); o --build ja os disse, com o motivo, ao montar."""
    coletor = _ColetorSemArea()
    coletor.feed(pagina_html)
    coletor.close()
    return coletor.itens


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


def projecao(painel_texto, quadro_html, lote, ligacoes_html=None):
    """O que o operador VE e que muda sem lote novo: o painel, o quadro, as ligacoes tarefa -> aula
    da aba Listas (s216, part-2) e qual lote esta no ar."""
    return {"painel": hash_painel(painel_texto) if painel_texto is not None else None,
            "quadro": _sha(quadro_html),
            "ligacoes": _sha(ligacoes_html) if ligacoes_html is not None else None,
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
        if reg.get("ligacoes") != atual.get("ligacoes"):
            motivos.append("ligacoes tarefa -> aula mudaram")
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


def _ler_plano():
    """(linhas do plano, aviso | None): `db.plano_listar`, read-only. Banco fora = ([], aviso):
    o quadro sai so com as aulas e o build DIZ isso -- nunca uma aba vazia em silencio."""
    try:
        linhas = db.plano_listar()
    except Exception as e:  # noqa: BLE001 -- degrada declarado (F60)
        return [], "plano indisponivel (%s): quadro so com as aulas, sem semanas" % e
    # s201: tarefa com questoes no banco se resolve na aba Listas -- o quadro troca o "PDF no
    # computador" do simulado por um atalho. Banco sem a tabela = ninguem marcado.
    try:
        no_hub = db.tarefas_com_questoes()
    except Exception:  # noqa: BLE001
        no_hub = set()
    return [dict(l, no_hub=int(l["id"]) in no_hub) for l in linhas], None


def _ler_calendario():
    """(calendario da trilha, aviso | None): `plano.calendario_trilha`; ilegivel = ({}, aviso),
    e as secoes saem 'Semana N' sem datas."""
    try:
        return calendario_trilha(), None
    except Exception as e:  # noqa: BLE001
        return {}, "calendario da trilha ilegivel (%s): semanas sem datas" % e


def construir(lote, raiz=RAIZ, out=None, painel=None, publicado=(), agora=None, data_fn=None,
              template_hub=None, template_player=None, registro=None, quadro=None,
              estado_quadro=None, plano_linhas=None, calendario=None):
    """Monta `index.html` + `manifesto.json` + `estado_pos_publish.json` em `out`.

    `publicado` = a listagem viva: paths, pares (path, bytes) ou {path: bytes}. `registro` =
    injetavel; None = o `registro_publicado.json` de `out`. `quadro` = o registro do quadro de
    aulas (None = `core/hub_quadro.json` de `raiz`); `estado_quadro` = {slug: {feito, ts}} do `db`
    (`ler_estado_quadro`), None = nada feito. `plano_linhas`/`calendario` (s195) = o plano e as
    datas das semanas; None = `db.plano_listar()` / `plano.calendario_trilha()`, read-only.
    Devolve (manifesto, problemas, avisos)."""
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
    if plano_linhas is None:
        plano_linhas, aviso = _ler_plano()
        if aviso:
            avisos.append(aviso)
    if calendario is None:
        calendario, aviso = _ler_calendario()
        if aviso:
            avisos.append(aviso)
    agora = agora or db.agora()
    quadro_html, avisos_quadro = html_quadro_de(selecionadas, quadro, estado_quadro, plano_linhas,
                                                calendario, _hoje_de(agora))
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
    pagina = montar_index(th, tp, lote, selecionadas, tem_painel, agora, quadro, estado_quadro,
                          plano_linhas, calendario)
    proj = projecao(painel_path.read_text(encoding="utf-8") if tem_painel else None,
                    quadro_html, lote, html_ligacoes(selecionadas, quadro))

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
            data_fn=None, plano_linhas=None, calendario=None, agora=None):
    """O `--precisa-publicar`: a projecao ATUAL (painel em disco + quadro que o build montaria)
    contra a do registro, mais o estado do lote. Le o plano (`db.plano_listar`, read-only): e o
    dado do quadro por semanas e, nas aulas feitas com tarefa, o que ha a concluir. Devolve o
    dict de `precisa_publicar` + "concluir"."""
    raiz = Path(raiz)
    painel_path = Path(painel) if painel else raiz / "artifacts" / "painel.html"
    if not painel_path.is_absolute():
        painel_path = raiz / painel_path
    if quadro is None:
        quadro = ler_quadro(raiz / QUADRO_REG)
    estado = (estado_quadro if isinstance(estado_quadro, dict)
              else ler_estado_quadro(estado_quadro))
    if plano_linhas is None:
        plano_linhas, _ = _ler_plano()
    if calendario is None:
        calendario, _ = _ler_calendario()
    aulas, _ = coletar_aulas(raiz, data_fn)
    selecionadas = selecionar_aulas(aulas)
    quadro_html, _ = html_quadro_de(selecionadas, quadro, estado, plano_linhas,
                                    calendario, _hoje_de(agora or db.agora()))
    atual = projecao(painel_path.read_text(encoding="utf-8") if painel_path.is_file() else None,
                     quadro_html, lote, html_ligacoes(selecionadas, quadro))
    decisao = precisa_publicar(ler_projecao_registrada(out), atual, lote, ids_com_nota(notas))
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
        pagina = (out / PAGINA).read_text(encoding="utf-8")
        problemas = checar(pagina, manifesto["files"], RAIZ, manifesto.get("mantidos") or ())
        for nome in sem_area_na_pagina(pagina):
            print("[hub] AVISO: item sem grande area na Biblioteca: %s -- registre `bloco` (%s) em %s "
                  "(o --build diz o motivo)" % (nome, "|".join(BLOCOS_REGISTRO), QUADRO_REG))
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
