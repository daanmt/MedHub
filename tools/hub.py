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
  tarefa no plano ou, sem tarefa, pelo `bloco` do registro; s218 (pedido do operador em 07/10: "a
  biblioteca deveria cobrir os resumos, que sao as fontes de fato mais densas dos conteudos"): a
  Biblioteca vira o CORPO da aba, depois das semanas, por grande area (`<details>` com contagem) e,
  dentro dela, por DISCIPLINA (A-Z); dentro da disciplina, resumos (A-Z), aulas e revisoes (a mais
  nova primeiro; a RD ainda nao lida leva "nova" e sobe ao topo). Os RESUMOS do lote em
  `core/hub_resumos.json` viram paginas de leitura `resumos/<slug>.html` (conversor md -> HTML
  deste modulo, deterministico, todo texto escapado), no mesmo manifesto com diff por hash, e cada
  semana lista os "Resumos desta semana". A RD declara `disciplinas` (aparece em cada uma) e
  `resumos` (de onde saiu); o item de resumo mostra quem o cita (aula da tarefa, RD), tipo Obsidian.
  O cabecalho da semana conta o que a Teoria mostra e diz o total REAL de questoes pendentes da
  semana no plano (a regua `_q_de` do Painel), com atalho para a aba Listas. ⚰️ s218: a secao
  "Revisoes direcionadas" no topo da aba (a RD mora so na Biblioteca); ⚰️ "Varias areas" como destino
  de RD (o `bloco` VARIAS so vale como leitura antiga); ⚰️ o "N questoes" do cabecalho da semana, que
  somava so as tarefas mostradas ("69 questoes" para 2.750 pendentes, 07/10). P20 (s219, print do
  operador em 07/10): ⚰️ o quadrado "feito" (so a tarefa de classe `aula` o tinha; assinar a leitura ja
  conclui) -- o estado `quadro/<slug>` e o movimento para a Biblioteca seguem, pela assinatura; a
  linha de meta e a acao da tarefa seguem UMA regra com o Painel (`plano.meta_da_tarefa`), o titulo
  sai pela correcao de exibicao (`plano.tema_exibido`) e as questoes contam o banco do hub quando a
  tarefa tem questoes la (`plano.q_da_tarefa`);
- `resumos/<slug>.html` (s218): a pagina de leitura de cada resumo do registro, gerada em `--out`;
- `manifesto.json` = exatamente os argumentos do `Artifact publish`: `file_path` (a pagina) e
  `files` ({path publicado: fonte | null}). Painel e aulas vao DIRETO das fontes em `artifacts/`
  (sem copia); os resumos, da pagina gerada em `--out/resumos/`. Arquivo OMITIDO num update e MANTIDO pelo runtime; so `null` remove -- por isso o que
  saiu da selecao e consta em `--publicado` (a listagem do artifact) vira `null`.
- DIFF (v1, s193, spec `medhub-hub-v1-manifesto-diff`): `files` leva so o que e NOVO ou MUDOU. O
  que ja esta no ar e intocado fica em `manifesto["mantidos"]` -- nao sobe e nao precisa ser relido
  antes do publish (a releitura das 6 aulas custou 378k tokens em 22/09). Base: o registro local
  `registro_publicado.json`, que so o `--confirmar` escreve, DEPOIS do publish aceito, a partir do
  `estado_pos_publish.json` do build.

Limites como DADO: 255 entradas por versao (contrato do Artifact), 8 reservadas, cap de 200 aulas
(mais novas primeiro, pela data de criacao no git; era 120 ate a s216, quando a Biblioteca passou a
guardar tudo o que foi concluido). Os resumos (s218) nao tem cap proprio: aulas + resumos + painel +
pagina acima do teto = erro NOMEADO no build (nunca corte silencioso) -- o lote de resumos entra por
semana do plano justamente para caber.

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
import unicodedata
from dataclasses import dataclass, field
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath

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
    SEMANAS_FASE1, calendario_trilha, classe_da_tarefa, com_q_hub, meta_da_tarefa,
    q_da_tarefa, questoes_no_hub, tema_exibido)

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
#: O vocabulario do campo `bloco` do registro (o SEM e do build). s218: o `bloco` vale so como leitura
#: antiga (a RD declara `disciplinas`); VARIAS fica no vocabulario por isso, sem item no registro real.
BLOCOS_REGISTRO = tuple(a for a, _r in AREAS_BIBLIOTECA if a != AREA_SEM)

# s218 (pedido do operador em 07/10/2026): a Biblioteca por grande area -> DISCIPLINA, com os RESUMOS.
#: Registro dos resumos que entram no hub (lote por semana do plano; mapa resumo -> tarefas a mao).
RESUMOS_REG = "core/hub_resumos.json"
#: Pasta-fonte dos resumos e prefixo publicado das paginas de leitura geradas.
DIR_RESUMOS = "resumos"
PREFIXO_RESUMO = "resumos/"
#: Grande area do resumo pela pasta de topo de `resumos/`.
AREA_DA_PASTA = {"Clínica Médica": "CM", "Otorrino": "CM", "Cirurgia": "CIR", "Preventiva": "MFC",
                 "Pediatria": "PED", "GO": "GO"}
#: Disciplina do resumo pela pasta, quando o registro nao a declara (`Clínica Médica/<Esp>` -> <Esp>).
DISC_DA_PASTA = {"Cirurgia": "Cirurgia", "Pediatria": "Pediatria", "Preventiva": "Preventiva",
                 "Otorrino": "Otorrinolaringologia"}
#: A `area` da tarefa no plano (abreviada) -> o nome cheio da disciplina; as demais ficam iguais.
DISC_DA_AREA = {"Infecto": "Infectologia", "Hemato": "Hematologia", "Endocrino": "Endocrinologia",
                "Gastro": "Gastroenterologia", "Hepato": "Hepatologia", "Pneumo": "Pneumologia",
                "Reumato": "Reumatologia", "Otorrino": "Otorrinolaringologia", "Dermato": "Dermatologia",
                "Oftalmo": "Oftalmologia"}
#: Disciplina -> grande area (a RD e o resumo); fora daqui, CM.
AREA_DA_DISC = {"Obstetrícia": "GO", "Ginecologia": "GO", "Pediatria": "PED", "Cirurgia": "CIR",
                "Ortopedia": "CIR", "Preventiva": "MFC"}
#: O vocabulario dos campos `disciplinas` (RD, `core/hub_quadro.json`) e `disciplina` (resumo): nome fora
#: dele falha ALTO -- disciplina digitada errada viraria um grupo inventado na Biblioteca.
DISCIPLINAS = ("Cardiologia", "Cirurgia", "Dermatologia", "Endocrinologia", "Gastroenterologia",
               "Ginecologia", "Hematologia", "Hepatologia", "Infectologia", "Nefrologia", "Neurologia",
               "Obstetrícia", "Oftalmologia", "Ortopedia", "Otorrinolaringologia", "Pediatria",
               "Pneumologia", "Preventiva", "Psiquiatria", "Reumatologia")
#: Disciplina do item sem disciplina resolvivel (tarefa sem `area`, RD so com o `bloco` antigo): fica
#: por ultimo na grande area, nunca some.
DISC_OUTROS = "Outros"
#: O slug do resumo vira `doc_<slug>` (assinatura) e chave do grifo: `pendIdValido` aceita ate 120.
SLUG_RESUMO_MAX = 96
#: Quadro por semanas (s195): a ultima secao e a semana da PROVA (`plano.SEMANAS_FASE1`); a Fase 2
#: nao entra na aba -- e panorama de execucao, nao inventario.
SEMANA_FINAL_QUADRO = max(SEMANAS_FASE1)
#: ⚰️ P20 (s219): `ROTULO_CLASSE` ('aula' / 'caderno a criar' / 'sem lista' na meta, ao lado de 'aula a
#: preparar' / 'sem lista ainda' na acao). O vocabulario da tarefa sem acao e um so, com o Painel:
#: `plano.ROTULO_SEM_ACAO`, pela regra `plano.meta_da_tarefa`.
#: Colecao do db onde a pagina grava {feito, ts} por slug (doc `quadro/<slug>`) -- desde a P20 (s219), so
#: pela assinatura da leitura no rodape do leitor (o quadrado "feito" saiu). Regra de escrita
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
    # ⚰️ o lugar "ligacoes" (s216 part-2 -> P21, s220): o JSON tarefa -> aulas/resumos existia so para
    # os links debaixo das listas da aba Listas, que sairam
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


@dataclass(frozen=True)
class Resumo:
    """Um resumo do registro `core/hub_resumos.json` (s218), pronto para virar pagina de leitura."""
    caminho: str       # relativo a `resumos/`, posix (a chave do registro)
    slug: str          # `resumo-<nome>`: o arquivo publicado e a chave do grifo e da assinatura
    titulo: str        # o H1 do resumo (ou o nome do arquivo)
    area: str          # grande area (AREAS_BIBLIOTECA), pela pasta de topo
    disciplina: str    # a do registro ou a da pasta
    tarefas: tuple = ()
    texto: str = field(default="", repr=False, compare=False)

    @property
    def publicado(self):
        return PREFIXO_RESUMO + self.slug + ".html"


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


def montar_manifesto(aulas_sel, painel_fonte=None, publicado=(), resumos=()):
    """O argumento `files` do publish: {publicado: fonte}, + `null` para o que saiu.

    `index.html` e o `file_path` da pagina: nunca entra em `files` e nunca vira `null`. `resumos`
    (s218) = pares (publicado, fonte) das paginas geradas. Aulas + resumos + painel + a pagina acima
    do teto = ValueError que DIZ quanto de cada um -- nunca um corte silencioso."""
    files = {}
    if painel_fonte:
        files[PUB_PAINEL] = normalizar_path(painel_fonte)
    for a in aulas_sel:
        files[a.publicado] = normalizar_path(a.fonte)
    resumos = list(resumos)
    for pub, fonte in resumos:
        files[normalizar_path(pub)] = normalizar_path(fonte)
    if len(files) + 1 > TETO_ENTRADAS:
        raise ValueError("manifesto com %d arquivos (%d aulas, %d resumos, %d painel) + a pagina estoura "
                         "o teto de %d entradas (%d do contrato - %d reservadas): tire resumos do lote "
                         "em %s ou aulas da selecao"
                         % (len(files), len(aulas_sel), len(resumos), 1 if painel_fonte else 0,
                            TETO_ENTRADAS, LIMITE_ENTRADAS, RESERVADAS, RESUMOS_REG))
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
    """{slug: {"tipo", "titulo"?, "tarefa_id"?, "tarefas"?, "bloco"?, "disciplinas"?, "resumos"?}} do
    registro versionado. Arquivo ausente = {}. Tipo fora de TIPOS_QUADRO, `bloco` fora de
    BLOCOS_REGISTRO (s217), `disciplinas` fora de DISCIPLINAS ou `resumos` que nao e lista de .md (s218)
    falha ALTO: registro errado nao vira coluna nem grupo inventado. O resumo-fonte que nao existe no
    disco e AVISO do build (`avisos_fontes_rd`), nao erro de leitura."""
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
        # s218: a RD declara as disciplinas (aparece em cada uma) e os resumos de onde saiu
        discs = (item or {}).get("disciplinas")
        if discs is not None and (not isinstance(discs, list) or not discs
                                  or not all(d in DISCIPLINAS for d in discs)):
            raise ValueError("%s: `disciplinas` da aula %r tem de ser lista nao vazia de %s, veio %r"
                             % (caminho.name, slug, list(DISCIPLINAS), discs))
        fontes = (item or {}).get("resumos")
        if fontes is not None and (not isinstance(fontes, list) or not all(
                isinstance(f, str) and f.endswith(".md") and ".." not in f.split("/") for f in fontes)):
            raise ValueError("%s: `resumos` da aula %r tem de ser lista de caminhos .md relativos a "
                             "resumos/, veio %r" % (caminho.name, slug, fontes))
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


def disciplina_da_area(area):
    """A `area` de uma tarefa do plano -> o nome cheio da disciplina (s218); None/vazia = None. PURA."""
    if not area:
        return None
    return DISC_DA_AREA.get(area, area)


def area_da_disciplina(disc):
    """A grande area de uma disciplina (s218): Obstetricia/Ginecologia -> GO, Pediatria -> PED,
    Cirurgia/Ortopedia -> CIR, Preventiva -> MFC; o resto -> CM. PURA."""
    return AREA_DA_DISC.get(disc, "CM")


def lugares_do_registro(reg, blocos, discs=None):
    """[(grande area, disciplina)] de um item do registro na Biblioteca (s218), na ordem. PURA.

    A aula com tarefa resolvivel no plano mora no bloco da tarefa e na disciplina da `area` dela -- a
    de `tarefa_id` (a que ela CUMPRE) vence; senao, a primeira de `tarefas` que o plano conhece (s217).
    Sem tarefa resolvivel (a RD): um lugar por `disciplinas` declarada, a area pela disciplina; sem
    elas, o `bloco` antigo (leitura de fallback) com a disciplina 'Outros'; sem nada, [] (o "Sem
    area", acusado). `blocos`/`discs` = {tarefa_id: bloco | disciplina} do plano INTEIRO."""
    reg = reg or {}
    for tid in _tarefas_do_registro(reg):
        bloco = (blocos or {}).get(int(tid))
        if bloco in BLOCOS_REGISTRO:
            return [(bloco, (discs or {}).get(int(tid)) or DISC_OUTROS)]
    if reg.get("disciplinas"):
        lugares = []
        for d in reg["disciplinas"]:
            par = (area_da_disciplina(d), d)
            if par not in lugares:
                lugares.append(par)
        return lugares
    if reg.get("bloco") in BLOCOS_REGISTRO:
        return [(reg["bloco"], DISC_OUTROS)]
    return []


def grande_area(reg, blocos):
    """A grande area (chave de AREAS_BIBLIOTECA) de um item do registro, ou None. PURA. s217 (P17):
    a aula com tarefa herda o bloco da tarefa no plano -- a de `tarefa_id` (a que ela CUMPRE) vence;
    senao, a primeira de `tarefas` que o plano conhece. Sem tarefa resolvivel (a RD; a tarefa fora do
    plano): s218, a area da 1a das `disciplinas`; sem elas, o `bloco` declarado (leitura antiga).
    `blocos` = {tarefa_id: bloco} do plano INTEIRO (a tarefa concluida tambem conta)."""
    lugares = lugares_do_registro(reg, blocos)
    return lugares[0][0] if lugares else None


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
    """As questoes da tarefa pela regua do `plano.panorama` (P20, s219: `plano.q_da_tarefa` -- o banco
    do hub quando a linha traz `q_hub`, senao `q_previstas`): Teoria = Painel por construcao."""
    return q_da_tarefa(linha)


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
    `tarefa_id` = a aula CUMPRE a tarefa (custom de aula) -- so essa leva o `data-slug` no bloco: a
    assinatura da leitura risca o item e o tique a converte em `plano.py --concluir ID --leitura`
    (P20, s219: o quadrado 'feito' saiu)."""
    por_tarefa = {}
    for a, _tipo, titulo, tid in classificadas:
        reg = (quadro or {}).get(a.slug) or {}
        ids = {int(x) for x in (reg.get("tarefas") or [])}
        if tid is not None:
            ids.add(int(tid))
        for i in sorted(ids):
            por_tarefa.setdefault(i, []).append((a, titulo, tid is not None and int(tid) == i))
    return por_tarefa


def _chave_alfa(texto):
    """Chave de ordem A-Z sem acento e sem caixa (Úlceras entre Toxoplasmose e Vitalidade). PURA."""
    base = unicodedata.normalize("NFKD", str(texto or ""))
    return "".join(c for c in base if not unicodedata.combining(c)).casefold()


def _resumos_de(resumos, linhas):
    """Os resumos cujas `tarefas` cruzam as tarefas de `linhas`, A-Z pelo titulo. PURA."""
    ids = {int(l["id"]) for l in linhas if l.get("id") is not None}
    return sorted((r for r in resumos or () if ids & set(r.tarefas)),
                  key=lambda r: (_chave_alfa(r.titulo), r.slug))


def secoes_do_quadro(classificadas, plano_linhas=None, calendario=None, hoje=None, estado=None,
                     quadro=None, semana_final=SEMANA_FINAL_QUADRO, resumos=()):
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
    pendente. Nada vai mais para a pasta de arquivo: a aula concluida fica a um toque. A aula da
    Biblioteca tem `secao = "biblioteca"` (sem secao de origem: desmarcada, fica la).

    s217 (P17, pedido do operador em 06/10: "organize por grande area"): todo item leva `grupo` = a
    grande area -- a tarefa, o bloco dela no plano; a aula, `grande_area`. Item sem area = AVISO
    nomeando o slug (o --check repete pela pagina); com o plano fora, a aula com tarefa nao e defeito
    de registro (o build ja avisa "plano indisponivel").

    s218 (pedido do operador em 07/10): (1) o cabecalho da semana somava so as questoes das tarefas
    MOSTRADAS ("69 questoes" nas semanas 4 a 7, que tem 2.750 pendentes): cada secao leva `q_plano` =
    a soma de `_q_de` de TODAS as tarefas pendentes dela (a regua do Painel), e `resumos` = os resumos
    cujas tarefas estao pendentes nela; semana so com resumos tambem vira secao. (2) Todo item da
    Biblioteca leva `lugares` = [(grande area, disciplina)]: a tarefa, o bloco e a `area` dela; a aula,
    `lugares_do_registro` (a RD, um lugar por disciplina declarada). (3) ⚰️ a secao "Revisoes
    direcionadas" no topo: a RD mora so na Biblioteca; a nao feita leva `nova`. (4) Os `resumos` do
    lote entram na Biblioteca como itens `tipo: resumo`, com `citado` = as aulas e RDs que apontam para
    ele (a aula cuja tarefa esta nas `tarefas` dele; a RD que o declara em `resumos`)."""
    feitos = {s for s, v in (estado or {}).items() if v.get("feito")}
    hoje = hoje or date.today()
    pendentes = [l for l in plano_linhas or [] if l.get("status") == "pendente"
                 and l.get("semana_plano") is not None and int(l["semana_plano"]) <= semana_final]
    atual = semana_atual(calendario, hoje, pendentes)
    por_tarefa = ligacoes_do_quadro(classificadas, quadro)
    # o plano INTEIRO (a aula cuja tarefa ja foi feita tambem herda o bloco e a disciplina dela)
    linhas_id = {int(l["id"]): l for l in plano_linhas or [] if l.get("id") is not None}
    blocos = {tid: _bloco_da_linha(l) for tid, l in linhas_id.items()}
    discs = {tid: disciplina_da_area(l.get("area")) for tid, l in linhas_id.items()}

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
                "grupo": blocos.get(tid),
                "lugares": [(blocos.get(tid), discs.get(tid) or DISC_OUTROS)] if blocos.get(tid) else [],
                "secao": secao, "ordem": ordem()}

    def secao(chave, titulo, linhas, todas, q_atrasadas=0):
        itens = [item_tarefa(l, chave) for l in linhas]
        vivos = [i for i in itens if not (i["slug"] and i["slug"] in feitos)]
        concluidas.extend(dict(i, feito=True) for i in itens if i["slug"] and i["slug"] in feitos)
        q = sum(_q_de(l) for l in todas)
        # s218 (adendo do principal): a semana corrente do Painel (`plano.panorama`, `q_abertas`) soma as
        # atrasadas; a Teoria as mostra em secao propria -- a corrente diz TAMBEM o total com elas, o
        # mesmo numero do Painel, para as duas telas nunca discordarem
        secoes.append({"chave": chave, "titulo": titulo, "rotulo": "tarefa", "fixa": True, "q_plano": q,
                       "q_com_atrasadas": q + q_atrasadas if q_atrasadas else None,
                       "resumos": _resumos_de(resumos, todas), "itens": vivos})

    if atual is not None:
        atrasadas_todas = [l for l in pendentes if int(l["semana_plano"]) < atual]
        atrasadas = [l for l in atrasadas_todas if na_teoria(l)]
        if atrasadas or _resumos_de(resumos, atrasadas_todas):
            secao("atrasadas", "Atrasadas", atrasadas, atrasadas_todas)
        ultima = max([int(l["semana_plano"]) for l in pendentes] + [atual])
        for s in range(atual, ultima + 1):
            todas = [l for l in pendentes if int(l["semana_plano"]) == s]
            linhas = [l for l in todas if na_teoria(l)]
            if not linhas and not _resumos_de(resumos, todas) and s != atual:
                continue
            cal = (calendario or {}).get(s)
            # s216: " a " entre as datas, como no Painel (o travessao e proibido na pagina)
            titulo = "Semana %d" % s + (" · %s a %s" % (cal[0].strftime("%d/%m"),
                                                         cal[1].strftime("%d/%m")) if cal else "")
            secao(str(s), titulo, linhas, todas,
                  sum(_q_de(l) for l in atrasadas_todas) if s == atual else 0)

    # s216 (part-3): a aula avulsa (sem tarefa pendente, inclusive a de tarefa ja concluida) mora na
    # Biblioteca. s218: a RD tambem, sempre (⚰️ a secao "Revisoes direcionadas" do topo, s210-s217).
    por_caminho = {r.caminho: r for r in resumos or ()}
    avulsas = []
    for a, tipo, titulo, tid in classificadas:
        if a.slug in usadas or tipo == "analise":   # s216: a analise mora no Painel (Documentacao)
            continue
        reg = (quadro or {}).get(a.slug) or {}
        lugares = lugares_do_registro(reg, blocos, discs)
        fontes = [_caminho_resumo(f) for f in reg.get("resumos") or []]
        avulsas.append({"tipo": "aula", "slug": a.slug, "aula": a, "titulo": titulo, "tipo_aula": tipo,
                        "data": a.data, "grupo": lugares[0][0] if lugares else None, "lugares": lugares,
                        "secao": "biblioteca", "ordem": ordem(), "feito": a.slug in feitos,
                        "nova": tipo == "revisao" and a.slug not in feitos, "fontes": fontes,
                        # s218: a fonte publicada vira link para o leitor; a que nao esta no lote, texto
                        "fontes_html": [(por_caminho[f].publicado, por_caminho[f].titulo) if f in por_caminho
                                        else (None, _titulo_de_caminho(f)) for f in fontes]})
    # s218: o resumo na Biblioteca, com quem aponta para ele (backlinks, tipo Obsidian): a aula cuja
    # tarefa ele sustenta, depois a RD que o declara como fonte -- so documento publicado (o link abre)
    leitura = [(a, titulo, tipo, (quadro or {}).get(a.slug) or {}) for a, tipo, titulo, _t in classificadas
               if tipo != "analise"]
    itens_resumo = []
    for r in resumos or ():
        aulas = [(a, t) for a, t, tipo, reg in leitura if tipo != "revisao"
                 and {int(x) for x in _tarefas_do_registro(reg)} & set(r.tarefas)]
        rds = [(a, t) for a, t, tipo, reg in leitura if tipo == "revisao"
               and r.caminho in [_caminho_resumo(f) for f in reg.get("resumos") or []]]
        por_data = lambda xs: sorted(sorted(xs, key=lambda p: p[0].slug), key=lambda p: p[0].data, reverse=True)
        itens_resumo.append({"tipo": "resumo", "resumo": r, "titulo": r.titulo, "slug": None,
                             "grupo": r.area, "lugares": [(r.area, r.disciplina)],
                             "citado": por_data(aulas) + por_data(rds),
                             "secao": "biblioteca", "ordem": ordem()})
    biblioteca = concluidas + avulsas + itens_resumo
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
        motivo = ("tarefa %s fora do plano, sem `disciplinas` nem `bloco`"
                  % ", ".join("#%d" % int(t) for t in ids) if ids
                  else "sem tarefa, sem `disciplinas` e sem `bloco`")
    return ("item sem grande area na Biblioteca: %s (%s) -- registre `disciplinas` (%s) em %s; ate la ele "
            "fica no grupo 'Sem área'" % (nome, motivo, "|".join(DISCIPLINAS), QUADRO_REG))


def _ordem_na_disciplina(itens):
    """A ordem dentro de uma disciplina da Biblioteca (s218, pedido do operador): a RD nova (nao lida)
    no topo, a mais nova primeiro; os resumos A-Z; as aulas (e a tarefa feita), a mais nova primeiro;
    as revisoes ja lidas, a mais nova primeiro. PURA; empate pelo slug/titulo (deterministico)."""
    def classe(i):
        if i["tipo"] == "resumo":
            return 1
        if i.get("tipo_aula") == "revisao" and i["tipo"] == "aula":
            return 0 if i.get("nova") else 3
        return 2
    grupos = {0: [], 1: [], 2: [], 3: []}
    for i in itens:
        grupos[classe(i)].append(i)

    def por_data(xs):
        base = sorted(xs, key=lambda i: str(i.get("slug") or i.get("id") or ""))
        return sorted(base, key=lambda i: i.get("data") or "9999", reverse=True)
    return (por_data(grupos[0]) + sorted(grupos[1], key=lambda i: (_chave_alfa(i["titulo"]), i["resumo"].slug))
            + por_data(grupos[2]) + por_data(grupos[3]))


def _classe_bib(item):
    """`data-bib` do item (o mesmo criterio de `_ordem_na_disciplina`): a pagina reordena ao vivo."""
    if item["tipo"] == "resumo":
        return 1
    if item["tipo"] == "aula" and item.get("tipo_aula") == "revisao":
        return 0 if item.get("nova") else 3
    return 2


#: O chip de UM item da Biblioteca por tipo do registro (s218; TIPOS_QUADRO sao os rotulos de coluna).
ROTULO_ITEM = {"aula": "Aula-base", "revisao": "Revisão", "analise": "Análise"}


def _titulo_de_caminho(caminho):
    """'GO/[OBS] Sífilis na Gestação e Congênita.md' -> 'Sífilis na Gestação e Congênita' (o nome do
    resumo que nao esta publicado, na linha de fontes da RD). PURA."""
    stem = PurePosixPath(str(caminho)).stem
    return re.sub(r"^\[[^\]]*\]\s*", "", stem).strip() or stem


def _html_ligacoes_item(rotulo, pares):
    """A linha discreta de ligacoes do item da Biblioteca (s218, tipo Obsidian): o rotulo e cada
    documento -- com href, link para o leitor (o mesmo `a.hub-aula` da Teoria); sem, texto."""
    if not pares:
        return ""
    # conferido a 390 px (s218): itens em linha corrida, separados por " · " -- link e texto no mesmo fluxo
    # (em linhas de 44 px cada um, as 8 fontes da pilula viravam uma escada); o link ganha area de toque
    # pelo padding vertical, sem empurrar a linha
    itens = ['<a class="hub-aula" href="%s" data-titulo="%s">%s</a>' % (_e(href), _e(titulo), _e(titulo))
             if href else '<span>%s</span>' % _e(titulo) for href, titulo in pares]
    return '<p class="qd-lig"><span class="tenue">%s:</span> %s</p>' % (_e(rotulo), " · ".join(itens))


def _lugar_do_item(item, lugar=None):
    """(grande area, disciplina) do item NESTE lugar da pagina; o 1o dos `lugares` fora da Biblioteca."""
    if lugar:
        return lugar
    lugares = item.get("lugares") or [(item.get("grupo") or AREA_SEM, DISC_OUTROS)]
    return lugares[0]


def _html_resumo(item, lugar=None):
    """O resumo na Biblioteca (s218): titulo, o chip, "abrir resumo" no leitor e quem o cita."""
    r = item["resumo"]
    area, disc = _lugar_do_item(item, lugar)
    return ('<li class="qd-item qd-resumo" data-resumo="%s" data-area="%s" data-disc="%s" data-bib="1">'
            '<div class="qd-bloco"><p class="qd-tema">%s</p><p class="qd-meta"><span class="qd-bl">Resumo'
            '</span></p><p class="qd-acao"><a class="hub-aula" href="%s" data-titulo="%s">abrir resumo</a>'
            '</p>%s</div></li>'
            % (_e(r.slug), _e(area or AREA_SEM), _e(disc or DISC_OUTROS), _e(r.titulo), _e(r.publicado),
               _e(r.titulo), _html_ligacoes_item("Citado em", [(a.publicado, t) for a, t in item.get("citado") or []])))


def _html_item(item, feito=False, lugar=None):
    """Um bloco do quadro: tarefa (tema, peso, questoes, a aula), aula avulsa ou RD; o resumo (s218) em
    `_html_resumo`. O item com `slug` (a aula que CUMPRE uma tarefa de aula, ou a aula avulsa) leva a
    chave do `quadro/<slug>` -- a assinatura no leitor o marca feito (P20, s219: sem o quadrado).

    P21 (s220, pedido do operador em 07/10: "se estou na teoria, abro automaticamente a aula"): na
    tarefa, a unica acao da Teoria e a AULA -- com 1 aula, o bloco inteiro e o link dela
    (`a.qd-bloco.qd-alvo.hub-aula`); com 2+, o bloco mostra cada aula como alvo proprio (`.qd-aulas`);
    sem aula, o bloco nao tem acao nenhuma (`qd-sem-aula`, texto apagado) e a meta diz a classe
    (`plano.meta_da_tarefa` com a acao = ter aula: "aula a preparar"). ⚰️ na Teoria: "resolver no
    hub", "abrir lista" e "prova em PDF no computador" -- as questoes moram na aba Listas, e o Painel
    segue com os atalhos dele. `lugar` = (area, disciplina) do grupo da Biblioteca onde ele esta (a RD
    de varias disciplinas sai uma vez em cada); fora dela, o 1o dos `lugares` -- para onde o feito vai
    ao vivo."""
    if item["tipo"] == "resumo":
        return _html_resumo(item, lugar)
    slug = item.get("slug")
    classes = ["qd-item"]
    if item.get("atrasada"):
        classes.append("qd-atrasada")
    attrs = ' data-secao="%s" data-ordem="%d"' % (_e(item["secao"]), item["ordem"])
    if item.get("data"):   # s216 (part-3): a Biblioteca ordena por data de criacao, tambem ao vivo
        attrs += ' data-data="%s"' % _e(item["data"])
    # s217 (P17): o grupo da Biblioteca para onde o feito vai, tambem ao vivo (sem area = SEM, avisado);
    # s218: + a disciplina dentro dele e a classe de ordem (0 RD nova, 2 aula, 3 RD lida)
    area, disc = _lugar_do_item(item, lugar)
    nova = bool(item.get("nova")) and not feito
    attrs += ' data-area="%s" data-disc="%s" data-bib="%d"' % (
        _e(area or AREA_SEM), _e(disc or DISC_OUTROS), _classe_bib(dict(item, nova=nova)))
    if item["tipo"] == "tarefa":
        attrs += ' data-tarefa="%d" data-classe="%s"' % (item["id"], _e(item["classe"]))
    if slug:
        attrs += ' data-slug="%s" data-tipo="%s" data-titulo="%s"%s' % (
            _e(slug), _e(item.get("tipo_aula") or TIPO_PADRAO), _e(item["titulo"]),
            ' data-feito="1"' if feito else "")
    extra, acao = "", ""
    abre, fecha = '<div class="qd-bloco">', "</div>"
    if item["tipo"] == "tarefa":
        tema = tema_exibido(item["tema"])
        aulas = item["aulas"]
        meta = ['<span class="qd-bl">%s</span>' % _e(item["bloco"])] if item.get("bloco") else []
        # P21: na Teoria a acao e a aula -- sem ela, a classe vai para a meta (com ou sem questoes)
        meta += ['<span>%s</span>' % _e(t) for t in meta_da_tarefa(item["q"], item["classe"], bool(aulas))]
        prazo = item.get("prazo")
        if item.get("atrasada"):
            meta.append('<span class="qd-atraso">semana %d%s</span>'
                        % (item["semana"], " · venceu %s" % prazo.strftime("%d/%m") if prazo else ""))
        elif prazo:
            meta.append('<span class="qd-prazo">até %s</span>' % prazo.strftime("%d/%m"))
        # P21 (s220): ⚰️ na Teoria, "resolver no hub" (s201/s213), "abrir lista" e "prova em PDF no
        # computador" -- o toque na tarefa abre a AULA; as questoes moram na aba Listas (e no Painel)
        if len(aulas) == 1:
            a, tit = aulas[0]
            abre = ('<a class="qd-bloco qd-alvo hub-aula" href="%s" data-titulo="%s">'
                    % (_e(a.publicado), _e(tit)))
            fecha = "</a>"
        elif aulas:
            # 2+ aulas (a #811): o bloco nao e alvo; cada aula e um, com o titulo dela
            acao = '<div class="qd-aulas">%s</div>' % "".join(
                '<a class="hub-aula" href="%s" data-titulo="%s">%s</a>' % (_e(a.publicado), _e(tit), _e(tit))
                for a, tit in aulas)
        else:
            # sem aula: nada a tocar -- texto apagado, nada que pareca botao (P20 item 4: o rotulo na meta)
            classes.append("qd-sem-aula")
    else:
        a = item["aula"]
        tema = item["titulo"]
        # s218: a RD ainda nao lida leva "nova" (o feito a tira, tambem ao vivo)
        meta = (['<span class="qd-nova">nova</span>'] if nova else []) + [
            '<span class="qd-bl">%s</span>' % _e(ROTULO_ITEM.get(item["tipo_aula"], "Aula")),
            '<span>%s</span>' % _e(_data_curta(item["data"]))]
        acao = ('<p class="qd-acao"><a class="hub-aula" href="%s" data-titulo="%s">abrir aula</a></p>'
                % (_e(a.publicado), _e(item["titulo"])))
        # s218: a RD mostra os resumos de onde saiu (link para o leitor quando o resumo esta publicado)
        fontes = item.get("fontes_html") or []
        extra = _html_ligacoes_item("Fonte" if len(fontes) == 1 else "Fontes", fontes)
    # ⚰️ P20 (s219): o botao "feito" que morava DENTRO do bloco (s195) -- todo bloco tem a mesma largura
    return ('<li class="%s"%s>%s<p class="qd-tema">%s</p><p class="qd-meta">%s</p>%s%s%s</li>'
            % (" ".join(classes), attrs, abre, _e(tema), "".join(meta), acao, extra, fecha))


def _chave_item(item):
    """A identidade do item na contagem (a RD de 3 disciplinas conta 1): slug, resumo ou tarefa."""
    if item["tipo"] == "resumo":
        return "r:" + item["resumo"].slug
    return item.get("slug") or "t%d" % item["id"]


def _html_novas(n, id_=None):
    """A etiqueta "N novas" (s218): RDs ainda nao lidas; zero sai escondida (a pagina reconta)."""
    return '<span class="qd-novas"%s data-novas%s>%s</span>' % (
        ' id="%s"' % id_ if id_ else "", "" if n else " hidden",
        ("1 nova" if n == 1 else "%d novas" % n) if n else "")


def html_biblioteca(biblioteca):
    """O miolo da Biblioteca POR GRANDE AREA -> DISCIPLINA (s218; s217 era so por area). Pedido do
    operador em 07/10: "as revisoes ... devem estar com a taxonomia correta, integrando os respectivos
    blocos de disciplinas na biblioteca". Uma grande area por `<details>` (CM, CIR, MFC, PED, GO, e no
    fim "Varias areas"/"Sem area" so com item), com a contagem e as RDs novas; dentro, uma disciplina
    por bloco, A-Z ('Outros' por ultimo) -- area de uma disciplina so esconde o subtitulo pelo CSS
    (`:only-child`), entao a pagina pode criar a 2a ao vivo. A RD de varias disciplinas sai em CADA
    uma; a contagem da area e a do total contam o documento uma vez. Ordem dentro da disciplina:
    `_ordem_na_disciplina`. A ordem das areas vai em `data-areas` e a disciplina do fim em
    `data-disc-fim`: a pagina cria, ao vivo, o grupo que o feito pede."""
    rotulos = dict(AREAS_BIBLIOTECA)
    por_area = {}
    for i in biblioteca:
        for area, disc in i.get("lugares") or [(AREA_SEM, DISC_OUTROS)]:
            area = area if area in rotulos else AREA_SEM
            lista = por_area.setdefault(area, {}).setdefault(disc or DISC_OUTROS, [])
            if not any(x is i for x in lista):
                lista.append(i)
    grupos = []
    for chave, rotulo in AREAS_BIBLIOTECA:
        discs = por_area.get(chave)
        if not discs:
            continue
        unicos, partes = {}, []
        for disc in sorted(discs, key=lambda d: (d == DISC_OUTROS, _chave_alfa(d))):
            itens = _ordem_na_disciplina(discs[disc])
            for i in itens:
                unicos[_chave_item(i)] = i
            partes.append('<div class="qd-disc" data-disc="%s"><h4 class="qd-disc-tit">%s <span class="qd-n" '
                          'data-n>%d</span></h4><ul class="qd-lista">%s</ul></div>'
                          % (_e(disc), _e(disc), len(itens),
                             "".join(_html_item(i, i.get("feito", True), (chave, disc)) for i in itens)))
        grupos.append('<details class="qd-area" data-area="%s"><summary class="qd-area-tit"><span class="qd-seta" '
                      'aria-hidden="true"></span>%s <span class="qd-n" data-n>%d</span>%s</summary>'
                      '<div class="qd-area-corpo">%s</div></details>'
                      % (_e(chave), _e(rotulo), len(unicos),
                         _html_novas(sum(1 for i in unicos.values() if i.get("nova"))), "".join(partes)))
    ordem = json.dumps([list(p) for p in AREAS_BIBLIOTECA], ensure_ascii=False)
    return '<div class="qd-areas" data-areas="%s" data-disc-fim="%s">%s</div>' % (
        _e(ordem), _e(DISC_OUTROS), "".join(grupos))


def _html_resumos_semana(chave, resumos):
    """Os "Resumos desta semana" (s218): os resumos cujas tarefas estao pendentes na secao, A-Z, num
    `<details>` recolhido (31 links abertos empurravam as tarefas para fora da tela no celular)."""
    if not resumos:
        return ""
    return ('<details class="qd-resumos"><summary>%s <span class="qd-n">%d</span></summary>'
            '<ul class="qd-rlista">%s</ul></details>'
            % ("Resumos das atrasadas" if chave == "atrasadas" else "Resumos desta semana", len(resumos),
               "".join('<li><a class="hub-aula" href="%s" data-titulo="%s">%s</a></li>'
                       % (_e(r.publicado), _e(r.titulo), _e(r.titulo)) for r in resumos)))


def html_quadro(secoes, biblioteca=()):
    """A aba Teoria: secoes por semana (empilhadas), cada tarefa um bloco; depois, a BIBLIOTECA -- o
    corpo da aba desde a s218 (era um `<details>` recolhido no fim; s216 part-3 "Outras aulas" +
    "Concluidas"): o que esta feito no `db` (riscado), as aulas sem tarefa pendente, as RDs e os
    resumos, por grande area e disciplina (`html_biblioteca`). O estado do build e o do `db` no
    momento do tique; a pagina reconcilia ao vivo quando o `db` abre.

    s218: o cabecalho da semana conta o que a Teoria MOSTRA (tarefas + resumos) e, dentro, UMA linha
    com o total REAL de questoes pendentes da semana no plano (`q_plano`), com atalho para a aba
    Listas; o mapa caminho -> resumo publicado vai num `<script id="hub-resumos">` (a pagina liga a
    linha "Fonte: resumos/X.md" das RDs abertas no leitor)."""
    if not any(s["itens"] or s.get("resumos") for s in secoes) and not biblioteca:
        return '<p class="hub-vazio">Nada no quadro ainda: nem tarefa pendente, nem aula.</p>'
    partes = []
    for s in secoes:
        n = len(s["itens"])
        contagem = ('<span data-n>%d</span> <span data-nrot>%s</span>'
                    % (n, s["rotulo"] + ("" if n == 1 else "s")))
        nr = len(s.get("resumos") or ())
        if nr:
            contagem += " · %d %s" % (nr, "resumo" if nr == 1 else "resumos")
        q, qa = s.get("q_plano") or 0, s.get("q_com_atrasadas")
        qsem = ('<p class="qd-qsem">%s: <b>%d</b>%s, na <a href="#questoes" data-hub-aba="questoes" '
                'data-hub-modo="questoes">aba Listas</a></p>'
                % ("Questões atrasadas" if s["chave"] == "atrasadas" else "Questões da semana", q,
                   " · com as atrasadas: <b>%d</b>" % qa if qa else "")) if (q or qa) else ""
        partes.append(
            '<section class="qd-sem" data-secao="%s" data-rotulo="%s" aria-label="%s"%s%s>'
            '<h3 class="qd-titulo">%s <span class="qd-n">%s</span></h3>%s<ul class="qd-lista">%s</ul>'
            '<p class="qd-vazio"%s>Nada em aberto.</p>%s</section>'
            % (_e(s["chave"]), _e(s["rotulo"]), _e(s["titulo"]), ' data-fixa="1"' if s["fixa"] else "",
               "" if (s["itens"] or s["fixa"]) else " hidden", _e(s["titulo"]), contagem, qsem,
               "".join(_html_item(i) for i in s["itens"]), " hidden" if s["itens"] else "",
               _html_resumos_semana(s["chave"], s.get("resumos"))))
    unicos = {_chave_item(i): i for i in biblioteca}
    mapa = {i["resumo"].caminho: {"href": i["resumo"].publicado, "slug": i["resumo"].slug,
                                  "titulo": i["resumo"].titulo}
            for i in biblioteca if i["tipo"] == "resumo"}
    return ('<div class="qd" id="hub-quadro">\n'
            # P20 (s219): so o aviso de quando o db nao salvou a assinatura (o texto vem do JS)
            '<p class="qd-aviso" id="hub-quadro-aviso" role="status" hidden></p>\n'
            '<div class="qd-semanas">%s</div>\n'
            # s218: a Biblioteca e o corpo da aba (o id `hub-quadro-feitas` e o da s216, que o JS conhece)
            '<section class="qd-bib" id="hub-quadro-feitas" aria-labelledby="hub-bib-tit">'
            '<h3 class="qd-bib-tit" id="hub-bib-tit">Biblioteca <span class="qd-n" id="hub-quadro-nfeitas">%d'
            '</span>%s</h3>%s</section>\n'
            '<script type="application/json" id="hub-resumos">%s</script>\n</div>'
            % ("".join(partes), len(unicos),
               _html_novas(sum(1 for i in unicos.values() if i.get("nova")), "hub-quadro-novas"),
               html_biblioteca(biblioteca),
               json.dumps(dict(sorted(mapa.items())), ensure_ascii=False).replace("<", "\\u003c")))


def html_quadro_de(aulas_sel, quadro=None, estado=None, plano_linhas=None, calendario=None,
                   hoje=None, resumos=()):
    """(html do quadro, avisos) a partir das aulas selecionadas -- o MESMO caminho para a pagina
    (`montar_index`) e para a projecao (`construir`/`decidir`): um so quadro, nunca dois. `resumos`
    (s218) = os `Resumo` publicados (`coletar_resumos`)."""
    classificadas, avisos = classificar(aulas_sel, quadro or {})
    secoes, biblioteca, avisos_secoes = secoes_do_quadro(classificadas, plano_linhas, calendario,
                                                         hoje, estado, quadro, resumos=resumos)
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


# ⚰️ `dados_ligacoes` / `html_ligacoes` (s216 part-2, s218 P2 -> P21, s220): o `<script id="hub-ligacoes">`
# (tarefa -> aulas e resumos) so alimentava o "abrir aula" / "resumo: ..." debaixo das listas da aba Listas.
# Pedido do operador em 07/10: "se estou em listas e clico na tarefa ... devo ir especificamente para as
# questoes" -- a lista e so a lista; a aula da tarefa mora na Teoria (`ligacoes_do_quadro`).


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
                 estado=None, plano_linhas=None, calendario=None, resumos=()):
    """A pagina: casca do hub + as 3 regioes do player + aulas/painel + o lote.

    `agora` nao vai para a tela (a linha "montado ... lote ... cards" saiu na s194, bastidor;
    o carimbo vive no manifesto): so data a semana do quadro. `plano_linhas`/`calendario` =
    as tarefas pendentes e as datas das semanas (s195); sem eles, o quadro sai so com as aulas.
    `resumos` (s218) = os `Resumo` do lote publicado (Biblioteca e semanas)."""
    regioes = extrair_regioes_player(player_html)
    for _nome, marca in LUGARES_HUB:
        _exatamente_uma(template_hub, marca, "hub.html")
    trocas = {
        "player-css": regioes["css"],
        "player-corpo": regioes["corpo"],
        "player-js": regioes["js"],
        "aulas": html_quadro_de(aulas_sel, quadro, estado, plano_linhas, calendario,
                                _hoje_de(agora), resumos)[0],
        "painel": html_painel(tem_painel),
        "semanas": html_semanas(plano_linhas, calendario, _hoje_de(agora)),
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


def projecao(painel_texto, quadro_html, lote, resumos_hash=None):
    """O que o operador VE e que muda sem lote novo: o painel, o quadro, as paginas de resumo (s218,
    `hash_resumos`: o `.md` corrigido republica) e qual lote esta no ar. ⚰️ `ligacoes` (o hash do
    `#hub-ligacoes` da aba Listas, s216 part-2 -> P21, s220): o registro antigo que ainda a traz e
    ignorado por `precisa_publicar`."""
    return {"painel": hash_painel(painel_texto) if painel_texto is not None else None,
            "quadro": _sha(quadro_html),
            "resumos": resumos_hash,
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
        if reg.get("resumos") != atual.get("resumos"):
            motivos.append("resumos mudaram")
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


# ----------------------------------------------------------------------------- resumos (s218)
# Pedido do operador em 07/10/2026: "a biblioteca deveria cobrir os resumos, que sao as fontes de fato
# mais densas dos conteudos ... podemos fazer de acordo com o cronograma e, quando tivermos mais limite
# na conta, puxamos o restante". O registro `core/hub_resumos.json` diz QUAIS resumos entram (lote por
# semana do plano) e a que tarefas cada um serve (mapa feito a mao: o casamento automatico tema ->
# resumo erra ~metade dos pares, s214). Cada um vira uma pagina de leitura `resumos/<slug>.html`
# pelo conversor abaixo: Python puro, deterministico (mesma entrada, mesmos bytes: o diff do manifesto
# e por hash), sem dependencia nova, cobrindo o subconjunto do estilo dos resumos
# (`.claude/commands/estilo-resumo.md`). TODO texto e escapado antes de qualquer marcacao entrar
# (F108: "<190" e texto, nunca tag); nenhuma regex extrai tag.

def _nfc(texto):
    return unicodedata.normalize("NFC", str(texto or ""))


def _caminho_resumo(caminho):
    """Caminho de resumo como chave: posix, relativo a `resumos/`, sem o prefixo, em NFC. PURA."""
    p = normalizar_path(_nfc(caminho))
    return p[len(PREFIXO_RESUMO):] if p.startswith(PREFIXO_RESUMO) else p


def slug_resumo(caminho):
    """`Clínica Médica/Infectologia/Tuberculose.md` -> `resumo-tuberculose`. PURA e ESTAVEL: o nome do
    arquivo em ASCII (acento removido), minusculo, o resto vira hifen; ate SLUG_RESUMO_MAX caracteres,
    cortado no ultimo hifen. O mesmo nome em pastas diferentes colide -- o build acusa (erro)."""
    base = unicodedata.normalize("NFKD", PurePosixPath(_caminho_resumo(caminho)).stem)
    base = "".join(c for c in base if not unicodedata.combining(c)).encode("ascii", "ignore").decode("ascii")
    slug = "resumo-" + (re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-") or "sem-nome")
    if len(slug) > SLUG_RESUMO_MAX:
        corte = slug[:SLUG_RESUMO_MAX]
        slug = corte[:corte.rfind("-")] if corte.rfind("-") > len("resumo-") else corte
    return slug


def area_e_disciplina_do_resumo(caminho, disciplina=None):
    """(grande area, disciplina) de um resumo (s218). PURA. A area pela pasta de topo (`Clínica
    Médica`/`Otorrino` -> CM, `Cirurgia` -> CIR, `Preventiva` -> MFC, `Pediatria` -> PED, `GO` -> GO);
    a disciplina, a declarada ou a da pasta (`Clínica Médica/<Esp>` -> <Esp>). ValueError se nao der."""
    partes = _caminho_resumo(caminho).split("/")
    topo = partes[0]
    if topo not in AREA_DA_PASTA or len(partes) < 2:
        raise ValueError("resumo %r fora das pastas de resumos/ (%s)" % (caminho, ", ".join(AREA_DA_PASTA)))
    disc = disciplina or (partes[1] if topo == "Clínica Médica" and len(partes) > 2 else DISC_DA_PASTA.get(topo))
    if disc not in DISCIPLINAS:
        raise ValueError("resumo %r sem disciplina resolvivel (%r): declare `disciplina` (%s) em %s"
                         % (caminho, disc, "|".join(DISCIPLINAS), RESUMOS_REG))
    return AREA_DA_PASTA[topo], disc


def ler_resumos(caminho):
    """{caminho relativo a resumos/: {"tarefas": [int], "disciplina": str | None}} do registro
    `core/hub_resumos.json` (s218). Arquivo ausente = {}. Falha ALTO (registro errado nao vira grupo
    inventado nem semana errada): chave que nao e `.md` em pasta conhecida, `tarefas` que nao e lista
    de inteiros, `disciplina` fora de DISCIPLINAS, resumo de `GO/` sem `disciplina` (Obstetricia |
    Ginecologia: a pasta nao diz qual). O resumo que NAO existe no disco e AVISO do build
    (`coletar_resumos`), nao erro: um arquivo renomeado nao derruba o hub do dia."""
    caminho = Path(caminho)
    if not caminho.is_file():
        return {}
    itens = json.loads(caminho.read_text(encoding="utf-8")).get("itens") or {}
    saida = {}
    for rel, item in itens.items():
        item = item if isinstance(item, dict) else {}
        chave = _caminho_resumo(rel)
        if not chave.endswith(".md") or ".." in chave.split("/"):
            raise ValueError("%s: %r nao e um caminho .md relativo a resumos/" % (caminho.name, rel))
        tarefas = item.get("tarefas", [])
        if not isinstance(tarefas, list) or not all(isinstance(t, int) and not isinstance(t, bool)
                                                    for t in tarefas):
            raise ValueError("%s: `tarefas` do resumo %r tem de ser lista de ids inteiros, veio %r"
                             % (caminho.name, rel, tarefas))
        disc = item.get("disciplina")
        if chave.split("/", 1)[0] == "GO" and disc not in ("Obstetrícia", "Ginecologia"):
            raise ValueError("%s: resumo de GO sem `disciplina` (Obstetrícia | Ginecologia): %r, veio %r"
                             % (caminho.name, rel, disc))
        if disc is not None and disc not in DISCIPLINAS:
            raise ValueError("%s: `disciplina` %r do resumo %r fora de %s"
                             % (caminho.name, disc, rel, list(DISCIPLINAS)))
        area_e_disciplina_do_resumo(chave, disc)   # pasta desconhecida falha aqui, alto
        saida[chave] = {"tarefas": list(tarefas), "disciplina": disc}
    return saida


_RE_FRONT_FIM = re.compile(r"^(---|\.\.\.)\s*$")
_RE_CERCA = re.compile(r"^ {0,3}(`{3,}|~{3,})")
_RE_TITULO_MD = re.compile(r"^ {0,3}(#{1,6})\s+(.*?)\s*#*\s*$")
_RE_HR = re.compile(r"^ {0,3}([-*_])(?:\s*\1){2,}\s*$")
_RE_ITEM_MD = re.compile(r"^([ \t]*)([-*+]|\d{1,3}[.)])\s+(.*)$")
_RE_SEP_TABELA = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
_RE_COD_INL = re.compile(r"(`+)(.+?)\1")
_RE_ESCAPE_MD = re.compile(r"\\([\\`*_{}\[\]()#+\-.!|>~])")
_RE_WIKI = re.compile(r"\[\[([^\[\]|]+?)(?:\|([^\[\]]+?))?\]\]")
_RE_LINK_MD = re.compile(r"\[([^\[\]]+)\]\(([^()\s]+)\)")
_RE_NEG_ITAL = re.compile(r"\*\*\*(?=\S)(.+?)(?<=\S)\*\*\*")
_RE_NEG = re.compile(r"\*\*(?=\S)(.+?)(?<=\S)\*\*")
_RE_NEG_SUB = re.compile(r"(?<!\w)__(?=\S)(.+?)(?<=\S)__(?!\w)")
_RE_ITAL = re.compile(r"(?<![*\w])\*(?=[^\s*])(.+?)(?<=[^\s*])\*(?![*\w])")
_RE_ITAL_SUB = re.compile(r"(?<!\w)_(?=[^\s_])(.+?)(?<=[^\s_])_(?!\w)")
_RE_RESERVA = re.compile("\x00(\\d+)\x00")


def _sem_frontmatter(texto):
    """As linhas do resumo sem o frontmatter YAML do topo (`---` ... `---`). PURA."""
    linhas = _nfc(texto).lstrip("﻿").replace("\x00", "").replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if linhas and linhas[0].strip() == "---":
        for i in range(1, len(linhas)):
            if _RE_FRONT_FIM.match(linhas[i]):
                return linhas[i + 1:]
    return linhas


def titulo_md(texto):
    """O 1o titulo `# ` do resumo (fora do frontmatter e de cerca de codigo), sem marcacao; '' sem."""
    cerca = None
    for linha in _sem_frontmatter(texto):
        m = _RE_CERCA.match(linha)
        if m:
            cerca = None if cerca and m.group(1)[0] == cerca else (cerca or m.group(1)[0])
            continue
        if cerca:
            continue
        m = _RE_TITULO_MD.match(linha)
        if m and len(m.group(1)) == 1:
            return re.sub(r"[*_`]+", "", m.group(2)).strip()
    return ""


def _enfase(texto):
    """Negrito e italico sobre texto JA escapado (os marcadores nao mudam com o escape). PURA."""
    texto = _RE_NEG_ITAL.sub(r"<strong><em>\1</em></strong>", texto)
    texto = _RE_NEG.sub(r"<strong>\1</strong>", texto)
    texto = _RE_NEG_SUB.sub(r"<strong>\1</strong>", texto)
    texto = _RE_ITAL.sub(r"<em>\1</em>", texto)
    return _RE_ITAL_SUB.sub(r"<em>\1</em>", texto)


def _inline(texto, links):
    """Uma linha de markdown -> HTML de linha. PURA. Ordem: codigo (reservado, escapado, sem mais
    nada), escapes `\\*`, ESCAPE HTML de todo o resto, wikilinks e links (reservados: o `_` de uma URL
    nao vira italico), enfase; as reservas voltam no fim. `links` = {nome casefold: (href, slug,
    titulo)} dos resumos publicados: `[[X]]`/`[[X|Y]]` vira link para o leitor (`data-hub-aula`, o
    atalho que o hub ja intercepta) se X esta publicado, senao texto; `[t](u)` so vira link com u
    http(s)/mailto -- o resto fica texto (nada de link morto dentro do artifact)."""
    reservas = []

    def reservar(h):
        reservas.append(h)
        return "\x00%d\x00" % (len(reservas) - 1)

    texto = _RE_COD_INL.sub(lambda m: reservar("<code>%s</code>" % html.escape(m.group(2), quote=False)),
                            str(texto))
    texto = _RE_ESCAPE_MD.sub(lambda m: reservar(html.escape(m.group(1), quote=False)), texto)
    texto = html.escape(texto, quote=False)

    def wiki(m):
        alvo = html.unescape(m.group(1)).split("#", 1)[0].strip()
        mostra = (m.group(2) or m.group(1)).strip()
        dest = (links or {}).get(_nfc(alvo).casefold())
        if not dest:
            return reservar(mostra)
        return reservar('<a href="%s" data-hub-aula="%s" data-titulo="%s">%s</a>'
                        % (_e(dest[0]), _e(dest[1]), _e(dest[2]), mostra))

    def link(m):
        url = html.unescape(m.group(2))
        if re.match(r"(?i)^(https?://|mailto:)", url):
            return reservar('<a href="%s" rel="noopener noreferrer">%s</a>' % (_e(url), _enfase(m.group(1))))
        return reservar(_enfase(m.group(1)))

    texto = _RE_WIKI.sub(wiki, texto)
    texto = _RE_LINK_MD.sub(link, texto)
    texto = _enfase(texto)
    for _ in range(len(reservas) + 1):
        if "\x00" not in texto:
            break
        texto = _RE_RESERVA.sub(lambda m: reservas[int(m.group(1))], texto)
    return texto


def _celulas(linha):
    """As celulas de uma linha de tabela pipe; `|` dentro de `[[...]]` ou escapado nao divide. PURA."""
    s = linha.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    celulas, atual, dentro, i = [], [], 0, 0
    while i < len(s):
        c = s[i]
        if s.startswith("[[", i):
            dentro += 1
            atual.append("[[")
            i += 2
            continue
        if s.startswith("]]", i) and dentro:
            dentro -= 1
            atual.append("]]")
            i += 2
            continue
        if c == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            atual.append("|")
            i += 2
            continue
        if c == "|" and not dentro:
            celulas.append("".join(atual).strip())
            atual = []
        else:
            atual.append(c)
        i += 1
    celulas.append("".join(atual).strip())
    return celulas


def _html_lista(itens, links):
    """[(indent, ordenada, numero, texto)] -> `<ul>`/`<ol>` aninhadas pela indentacao (2 ou 4 espacos,
    tanto faz: vale o maior/menor que o nivel aberto). PURA."""
    out, pilha, ultimo = [], [], None
    for indent, ordenada, numero, texto in itens:
        tag = "ol" if ordenada else "ul"
        while pilha and indent < pilha[-1][0]:
            out.append("</li></%s>" % pilha.pop()[1])
        if pilha and indent == pilha[-1][0]:
            if pilha[-1][1] != tag:
                out.append("</li></%s>" % pilha.pop()[1])
            else:
                out.append("</li>")
        if not pilha or indent > pilha[-1][0]:
            if pilha and ultimo is not None:
                # conferido no navegador (s218): o texto do item que tem sublista vai num <div> -- o grifo do
                # leitor ancora em bloco-FOLHA, e o <li> com <ul> dentro nao e folha (o texto nao grifava)
                out[ultimo] = "<li><div>%s</div>" % out[ultimo][len("<li>"):]
            out.append("<%s%s>" % (tag, ' start="%d"' % numero if ordenada and numero != 1 else ""))
            pilha.append((indent, tag))
        ultimo = len(out)
        out.append("<li>" + _inline(texto, links))
    while pilha:
        out.append("</li></%s>" % pilha.pop()[1])
    return "".join(out)


def _indent(espacos):
    return len(espacos.replace("\t", "    "))


def _blocos_md(linhas, links):
    """Linhas de markdown -> [blocos HTML]. PURA. Titulos `#`..`######`, `---` (regua), cerca de codigo
    (em `div.cod > pre`, rolagem propria e grifavel), `>` citacao (recursiva), tabela pipe (em
    `div.tab`, rolagem horizontal propria), listas aninhadas (`-`/`*`/`+`/`1.`; a linha recuada que nao
    e item continua o item; linha em branco entre itens nao quebra a lista) e paragrafos."""
    out, par, i, n = [], [], 0, len(linhas)

    def fechar_par():
        if par:
            out.append("<p>%s</p>" % "\n".join(
                _inline(l.strip(), links) + ("<br>" if l.endswith("  ") else "") for l in par).rstrip())
            del par[:]

    while i < n:
        linha = linhas[i]
        if not linha.strip():
            fechar_par()
            i += 1
            continue
        m = _RE_CERCA.match(linha)
        if m:
            fechar_par()
            marca, corpo = m.group(1), []
            i += 1
            while i < n and not (linhas[i].strip().startswith(marca[0] * 3) and not linhas[i].strip().strip(marca[0])):
                corpo.append(linhas[i])
                i += 1
            i += 1
            out.append('<div class="cod"><pre><code>%s</code></pre></div>'
                       % html.escape("\n".join(corpo), quote=False))
            continue
        m = _RE_TITULO_MD.match(linha)
        if m:
            fechar_par()
            nivel = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (nivel, _inline(m.group(2), links), nivel))
            i += 1
            continue
        if _RE_HR.match(linha):
            fechar_par()
            out.append("<hr>")
            i += 1
            continue
        if linha.lstrip().startswith(">"):
            fechar_par()
            dentro = []
            while i < n and linhas[i].lstrip().startswith(">"):
                dentro.append(re.sub(r"^\s*> ?", "", linhas[i]))
                i += 1
            out.append("<blockquote>%s</blockquote>" % "\n".join(_blocos_md(dentro, links)))
            continue
        if linha.lstrip().startswith("|") and i + 1 < n and _RE_SEP_TABELA.match(linhas[i + 1]):
            fechar_par()
            cab = _celulas(linha)
            i += 2
            corpo = []
            while i < n and linhas[i].strip() and "|" in linhas[i]:
                corpo.append(_celulas(linhas[i]))
                i += 1
            out.append('<div class="tab"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
                       % ("".join("<th>%s</th>" % _inline(c, links) for c in cab),
                          "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % _inline(c, links) for c in row)
                                  for row in corpo)))
            continue
        m = _RE_ITEM_MD.match(linha)
        if m:
            fechar_par()
            itens = []
            while i < n:
                atual = linhas[i]
                mi = _RE_ITEM_MD.match(atual)
                if mi:
                    marca = mi.group(2)
                    ordenada = marca[0].isdigit()
                    itens.append([_indent(mi.group(1)), ordenada, int(marca[:-1]) if ordenada else 0,
                                  mi.group(3).strip()])
                    i += 1
                    continue
                if not atual.strip():
                    # linha em branco: a lista segue se a proxima nao vazia e item
                    j = i
                    while j < n and not linhas[j].strip():
                        j += 1
                    if j < n and _RE_ITEM_MD.match(linhas[j]):
                        i = j
                        continue
                    break
                if (_indent(re.match(r"^[ \t]*", atual).group(0)) > 0 and not _RE_CERCA.match(atual)
                        and not atual.lstrip().startswith((">", "|"))):
                    itens[-1][3] += " " + atual.strip()   # continuacao do item
                    i += 1
                    continue
                break
            out.append(_html_lista([tuple(x) for x in itens], links))
            continue
        par.append(linha)
        i += 1
    fechar_par()
    return out


def md_para_html(texto, links=None):
    """O corpo HTML de um resumo em markdown (s218): sem o frontmatter, todo texto escapado. PURA e
    deterministica (o diff do manifesto e por hash)."""
    return "\n".join(_blocos_md(_sem_frontmatter(texto), links or {}))


#: A pagina de leitura do resumo (s218): CSS proprio, minimalista, os tokens do hub (claro e escuro;
#: `data-theme` do hub vence a preferencia do aparelho), UM `.wrap`, nada sem quebra no celular; o
#: codigo e a tabela rolam na propria caixa. Sem DOCTYPE no leitor o srcdoc cairia em quirks mode.
CSS_RESUMO = (
    ":root{--papel:#f6f4f0;--card:#ffffff;--afundado:#edeae4;--tinta:#191817;--tinta2:#54504a;"
    "--tinta3:#8b857b;--linha:#e0dbd2;--acento:#0e6b5c;--acento-fraco:#d9ece7;color-scheme:light}\n"
    "@media (prefers-color-scheme:dark){:root:not([data-theme=\"light\"]){--papel:#131519;--card:#1b1e24;"
    "--afundado:#23272f;--tinta:#edeff3;--tinta2:#b4bac4;--tinta3:#7e8794;--linha:#2d323b;--acento:#4fd0b3;"
    "--acento-fraco:#123630;color-scheme:dark}}\n"
    ":root[data-theme=\"dark\"]{--papel:#131519;--card:#1b1e24;--afundado:#23272f;--tinta:#edeff3;"
    "--tinta2:#b4bac4;--tinta3:#7e8794;--linha:#2d323b;--acento:#4fd0b3;--acento-fraco:#123630;"
    "color-scheme:dark}\n"
    "*{box-sizing:border-box}\n"
    "html,body{margin:0;padding:0}\n"
    "body{background:var(--papel);color:var(--tinta);font:16px/1.6 ui-sans-serif,system-ui,\"Segoe UI\","
    "Roboto,Helvetica,Arial,sans-serif;-webkit-text-size-adjust:100%;overflow-wrap:break-word}\n"
    ".wrap{max-width:46rem;margin:0 auto;padding:18px 16px 40px;min-width:0}\n"
    ".rs-olho{margin:0 0 6px;font-size:.8rem;font-weight:650;color:var(--acento)}\n"
    "h1{font-size:clamp(1.4rem,1.15rem + 1.2vw,1.9rem);line-height:1.2;margin:0 0 18px;"
    "letter-spacing:-.01em;text-wrap:balance}\n"
    "h2{font-size:1.18rem;line-height:1.3;margin:28px 0 10px}\n"
    "h3{font-size:1.04rem;line-height:1.35;margin:22px 0 8px}\n"
    "h4,h5,h6{font-size:1rem;line-height:1.4;margin:18px 0 6px;color:var(--tinta2)}\n"
    "p{margin:0 0 12px}\n"
    "ul,ol{margin:0 0 12px;padding-left:1.3em}\n"
    "li{margin:4px 0}\n"
    "li > ul,li > ol{margin:4px 0 0}\n"
    "strong{font-weight:650}\n"
    "a{color:var(--acento);font-weight:600;text-underline-offset:2px}\n"
    "code{font:.88em ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:var(--afundado);"
    "border-radius:4px;padding:1px 5px}\n"
    "blockquote{margin:0 0 14px;padding:10px 14px;border-left:3px solid var(--acento);"
    "background:var(--acento-fraco);border-radius:0 8px 8px 0}\n"
    "blockquote > :last-child{margin-bottom:0}\n"
    "hr{border:0;border-top:1px solid var(--linha);margin:22px 0}\n"
    ".cod,.tab{margin:0 0 14px;border:1px solid var(--linha);border-radius:8px;background:var(--card)}\n"
    ".tab{overflow-x:auto}\n"
    ".cod pre{margin:0;padding:10px 12px;overflow-x:auto;tab-size:4;"
    "font:.82em/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}\n"
    ".cod code{background:none;padding:0;font-size:1em}\n"
    ".tab table{border-collapse:collapse;min-width:100%;font-size:.92em}\n"
    ".tab th,.tab td{border-bottom:1px solid var(--linha);padding:8px 10px;text-align:left;"
    "vertical-align:top;min-width:7rem}\n"
    ".tab th{background:var(--afundado);font-weight:650}\n")


def pagina_resumo(resumo, corpo):
    """O documento HTML completo da pagina de leitura do resumo (s218). PURA."""
    return ('<!DOCTYPE html>\n<html lang="pt-BR">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1">\n<title>%s</title>\n'
            '<style>\n%s</style>\n</head>\n<body>\n<main class="wrap">\n<p class="rs-olho">Resumo · %s</p>\n'
            '%s\n</main>\n</body>\n</html>\n'
            % (_e(resumo.titulo), CSS_RESUMO, _e(resumo.disciplina), corpo))


def links_dos_resumos(resumos):
    """{nome casefold: (href, slug, titulo)} -- o alvo dos wikilinks: o nome do arquivo (como no
    Obsidian) e o titulo do resumo publicado; o nome vence o titulo em caso de choque. PURA."""
    links = {}
    for r in resumos:
        links.setdefault(_nfc(r.titulo).casefold(), (r.publicado, r.slug, r.titulo))
    for r in resumos:
        links[_nfc(PurePosixPath(r.caminho).stem).casefold()] = (r.publicado, r.slug, r.titulo)
    return links


def paginas_resumos(resumos):
    """{publicado: html da pagina} dos resumos do lote (s218). PURA."""
    links = links_dos_resumos(resumos)
    return {r.publicado: pagina_resumo(r, md_para_html(r.texto, links)) for r in resumos}


def hash_resumos(paginas):
    """sha256 das paginas de resumo (s218) para a PROJECAO: resumo corrigido no `.md` republica sem
    lote novo. None sem resumo (o hub de antes da s218)."""
    if not paginas:
        return None
    return _sha("\n".join("%s %s" % (pub, _sha(txt)) for pub, txt in sorted(paginas.items())))


def avisos_fontes_rd(quadro, raiz):
    """AVISO nomeado de cada resumo-fonte de RD (`resumos` no registro, s218) que nao existe no disco
    -- a suite barra o registro real (`test_registro_real_rds_com_disciplinas_e_fontes_no_disco`). Sem a
    pasta `resumos/` em `raiz` (copia do repo so com as aulas, repo sintetico) nao ha o que conferir."""
    avisos = []
    if not (Path(raiz) / DIR_RESUMOS).is_dir():
        return avisos
    for slug, reg in sorted((quadro or {}).items()):
        for f in (reg or {}).get("resumos") or []:
            if not (Path(raiz) / DIR_RESUMOS / _caminho_resumo(f)).is_file():
                avisos.append("resumo-fonte inexistente na RD %s: resumos/%s -- corrija `resumos` em %s"
                              % (slug, _caminho_resumo(f), QUADRO_REG))
    return avisos


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


def coletar_resumos(raiz, registro=None, aulas=()):
    """([Resumo], avisos) do lote em `core/hub_resumos.json` (s218), com o texto, o titulo (o H1) e o
    lugar na Biblioteca. `registro` injetavel ({caminho: {tarefas, disciplina}}; None = o arquivo de
    `raiz`, por `ler_resumos`, que falha ALTO no schema). Resumo do registro que nao existe no disco =
    AVISO nomeado e fora do lote (um arquivo renomeado nao derruba o hub do dia; a suite barra o
    registro real). Dois resumos com o mesmo slug, ou um slug igual ao de uma aula (`aulas`: o grifo
    e a assinatura sao por slug), = ValueError: o build nao escolhe qual publicar."""
    raiz = Path(raiz)
    if registro is None:
        registro = ler_resumos(raiz / RESUMOS_REG)
    resumos, avisos, por_slug = [], [], {}
    slugs_aula = {a.slug for a in aulas or ()}
    for rel in sorted(registro):
        item = registro[rel] or {}
        caminho = raiz / DIR_RESUMOS / rel
        if not caminho.is_file():
            avisos.append("resumo do registro inexistente: resumos/%s -- fora da Biblioteca ate corrigir %s"
                          % (rel, RESUMOS_REG))
            continue
        slug = slug_resumo(rel)
        if slug in por_slug or slug in slugs_aula:
            raise ValueError("slug de resumo repetido: %r <- resumos/%s e %s -- renomeie um dos arquivos"
                             % (slug, rel, "resumos/" + por_slug[slug] if slug in por_slug else "a aula " + slug))
        por_slug[slug] = rel
        texto = caminho.read_text(encoding="utf-8")
        area, disc = area_e_disciplina_do_resumo(rel, item.get("disciplina"))
        resumos.append(Resumo(caminho=rel, slug=slug, titulo=titulo_md(texto) or _titulo_de_caminho(rel),
                              area=area, disciplina=disc, tarefas=tuple(int(t) for t in item.get("tarefas") or ()),
                              texto=texto))
    return resumos, avisos


def escrever_resumos(paginas, out):
    """Grava as paginas de resumo em `out/resumos/` e apaga a pagina `resumo-*.html` que saiu do lote
    (so arquivo que este build gera). Devolve {publicado: caminho no disco}."""
    pasta = Path(out) / DIR_RESUMOS
    pasta.mkdir(parents=True, exist_ok=True)
    saida = {}
    for pub, texto in sorted(paginas.items()):
        destino = Path(out) / pub
        if not destino.is_file() or destino.read_text(encoding="utf-8") != texto:
            destino.write_text(texto, encoding="utf-8", newline="\n")
        saida[pub] = destino
    for velho in pasta.glob("resumo-*.html"):
        if PREFIXO_RESUMO + velho.name not in paginas:
            velho.unlink()
    return saida


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
    # computador" do simulado por um atalho. P20 (s219): a marca (`no_hub`) e a contagem (`q_hub`) saem
    # da MESMA leitura, o criterio do `emed_banco --exportar` (o que a aba Listas recebe), a mesma do
    # Painel e do boot. Banco sem a tabela = ninguem marcado e a tela conta `q_previstas`.
    try:
        contagem = questoes_no_hub()
    except Exception:  # noqa: BLE001
        contagem = {}
    return [dict(l, no_hub=bool(l.get("q_hub"))) for l in com_q_hub(linhas, contagem)], None


def _ler_calendario():
    """(calendario da trilha, aviso | None): `plano.calendario_trilha`; ilegivel = ({}, aviso),
    e as secoes saem 'Semana N' sem datas."""
    try:
        return calendario_trilha(), None
    except Exception as e:  # noqa: BLE001
        return {}, "calendario da trilha ilegivel (%s): semanas sem datas" % e


def construir(lote, raiz=RAIZ, out=None, painel=None, publicado=(), agora=None, data_fn=None,
              template_hub=None, template_player=None, registro=None, quadro=None,
              estado_quadro=None, plano_linhas=None, calendario=None, resumos=None):
    """Monta `index.html` + `manifesto.json` + `estado_pos_publish.json` em `out`.

    `publicado` = a listagem viva: paths, pares (path, bytes) ou {path: bytes}. `registro` =
    injetavel; None = o `registro_publicado.json` de `out`. `quadro` = o registro do quadro de
    aulas (None = `core/hub_quadro.json` de `raiz`); `estado_quadro` = {slug: {feito, ts}} do `db`
    (`ler_estado_quadro`), None = nada feito. `plano_linhas`/`calendario` (s195) = o plano e as
    datas das semanas; None = `db.plano_listar()` / `plano.calendario_trilha()`, read-only.
    `resumos` (s218) = [Resumo] injetavel; None = `coletar_resumos` do `core/hub_resumos.json` de
    `raiz` -- as paginas vao para `out/resumos/` e entram no manifesto com o mesmo diff por hash.
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
    # s218: os resumos do lote viram paginas de leitura em `out/resumos/`, no mesmo manifesto
    if resumos is None:
        resumos, avisos_res = coletar_resumos(raiz, aulas=aulas)
        avisos.extend(avisos_res)
    avisos.extend(avisos_fontes_rd(quadro, raiz))
    paginas = paginas_resumos(resumos)
    agora = agora or db.agora()
    quadro_html, avisos_quadro = html_quadro_de(selecionadas, quadro, estado_quadro, plano_linhas,
                                                calendario, _hoje_de(agora), resumos)
    avisos.extend(avisos_quadro)
    tem_painel = painel_path.is_file()
    if not tem_painel:
        avisos.append("painel ausente (%s): a aba Painel sai com o aviso de 'nao gerado'"
                      % _rel(painel_path, raiz))
    vivos = _como_vivos(publicado)
    gravadas = escrever_resumos(paginas, out)
    completo = montar_manifesto(selecionadas, _rel(painel_path, raiz) if tem_painel else None,
                                list(vivos), [(pub, _rel(p, raiz)) for pub, p in sorted(gravadas.items())])
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
                          plano_linhas, calendario, resumos)
    proj = projecao(painel_path.read_text(encoding="utf-8") if tem_painel else None,
                    quadro_html, lote, hash_resumos(paginas))

    out.mkdir(parents=True, exist_ok=True)
    (out / PAGINA).write_text(pagina, encoding="utf-8")
    montado_em = agora.strftime("%Y-%m-%d %H:%M:%S")
    manifesto = {
        "file_path": _rel(out / PAGINA, raiz),
        "files": files,
        "sessao": lote.get("sessao"),
        "total_cards": len(lote.get("cards") or []),
        "aulas": len(selecionadas),
        "resumos": len(resumos),
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
            data_fn=None, plano_linhas=None, calendario=None, agora=None, resumos=None):
    """O `--precisa-publicar`: a projecao ATUAL (painel em disco + quadro que o build montaria +
    as paginas de resumo, s218) contra a do registro, mais o estado do lote. Le o plano
    (`db.plano_listar`, read-only): e o dado do quadro por semanas e, nas aulas feitas com tarefa, o
    que ha a concluir. Devolve o dict de `precisa_publicar` + "concluir"."""
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
    if resumos is None:
        resumos, _ = coletar_resumos(raiz, aulas=aulas)
    quadro_html, _ = html_quadro_de(selecionadas, quadro, estado, plano_linhas,
                                    calendario, _hoje_de(agora or db.agora()), resumos)
    atual = projecao(painel_path.read_text(encoding="utf-8") if painel_path.is_file() else None,
                     quadro_html, lote, hash_resumos(paginas_resumos(resumos)))
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
    print("[hub] no ar depois do publish: %d arquivo(s) (aulas %d; cap %d; resumos %d) + pagina = %d/%d "
          "entradas" % (no_ar, manifesto["aulas"], CAP_AULAS, manifesto.get("resumos", 0), no_ar + 1,
                        TETO_ENTRADAS))
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
