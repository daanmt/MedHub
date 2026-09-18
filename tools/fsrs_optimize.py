#!/usr/bin/env python3
"""Otimizador READ-ONLY de parametros do FSRS sobre o revlog proprio (R1, s184).

O MedHub agenda com os parametros de REFERENCIA do py-fsrs e nunca mediu os
seus. Com ~3.067 revisoes proprias (minimo oficial do Optimizer = 512) da para
ajustar os 21 parametros do modelo DSR ao aluno real. Este CLI faz a medicao e
PARA AI: nao escreve no banco, nao toca `app/utils/fsrs.py`, nao muda o
agendamento de card nenhum. O que ele produz e um JSON versionado para o
operador decidir (R2 da fila). Numero reportado != numero adotado.

--------------------------------------------------------------------------
1. Por que DUAS visoes do mesmo revlog (o defeito F112)
--------------------------------------------------------------------------
A funcao de perda do Optimizer e BINARIA: `optimizer.py:86` faz
`recall = 0 if rating == Rating.Again else 1`, e o `BCELoss()` (`:116`, `:258`)
compara a retrievability prevista contra esse 0/1. Ou seja, para o Optimizer a
nota 2 e ACERTO. Segundo sitio, independente do primeiro:
`optimizer.py:476-478` calcula `num_recall = num_hard + num_good + num_easy` e
`prob_hard = num_hard / num_recall`, que alimenta o modelo de custo do
`compute_optimal_retention`.

No MedHub a nota 2 nao significa "recuperou com esforco". A regua de notas do
`/revisar` (passo 4) diz, LITERALMENTE (citacao transcrita para ASCII conforme
AGENTE.md 4.5 -- as setas do original sao Unicode, aqui viram `->`):

    "Criterio: cravou conceito + regra-mestre -> 4; acertou o nucleo, faltou
     detalhe -> 3; recall parcial/na zona mas sem o alvo -> 2; errou ou
     'nao sei' -> 1."

"Recall parcial/na zona mas SEM O ALVO" e falha de recuperacao, nao acerto com
esforco. Sao ~340 das ~3.067 revisoes (11%) entrando no fit com o rotulo
trocado -- ruido de rotulo que empurra a estabilidade para cima e faz o erro
sumir dentro do ajuste. Dai as duas visoes:

  (i)  cru   -- as notas como estao gravadas (o que o motor ve hoje).
  (ii) remap -- traduz a regua do MedHub para a semantica do FSRS, na ENTRADA
                do Optimizer e em lugar nenhum mais.

Mapeamento (ii), com justificativa por nota ancorada na citacao acima e na
semantica do motor (Again = unico lapso; Hard = recuperou COM ESFORCO; Good =
acerto padrao; Easy = SEM ESFORCO):

    1 -> 1  "errou ou 'nao sei'"                = Again (identidade)
    2 -> 1  "recall parcial ... SEM O ALVO"     = Again (OBRIGATORIO, F112)
    3 -> 2  "acertou o nucleo, faltou detalhe"  = Hard  (recuperou com esforco)
    4 -> 3  "cravou conceito + regra-mestre"    = Good  (acerto padrao)

Nada mapeia para 4 (Easy), de proposito: o topo da regua do MedHub descreve
COMPLETUDE da resposta ("conceito + regra-mestre"), nunca AUSENCIA DE ESFORCO,
que e o que Easy quer dizer. Degrau que a regua nao mede nao pode ser
inventado aqui.

O remap acontece SO na entrada do Optimizer. O `fsrs_revlog` e IMUTAVEL: a
conexao e `file:ipub.db?mode=ro` (uri=True) e este modulo nao tem uma unica
instrucao de escrita em banco. O mapeamento aplicado viaja como `metadata` no
JSON de saida -- parametro sem a regua que o gerou e numero orfao.

--------------------------------------------------------------------------
2. A metrica (uma so, a mesma nas duas visoes)
--------------------------------------------------------------------------
**log-loss** (entropia cruzada binaria) entre a retrievability prevista e o
recall observado, so nas revisoes da CAUDA TEMPORAL (ultimos ~20% por data).
Escolhida porque e exatamente o objetivo que `compute_optimal_parameters`
minimiza -- default x otimizado fica medido na mesma escala em que o ajuste
acontece -- e porque e regra de pontuacao PROPRIA: premia calibracao, nao so
ordenacao (AUC nao distingue "90% de chance" de "60% de chance" quando a ordem
e a mesma). Menor = melhor.

Como e computada: o replay percorre o historico COMPLETO de cada card em ordem
cronologica (o estado no ponto de hold-out tem de estar certo), mas so as
revisoes com `review_time >= corte` entram na soma. Convencao herdada do
proprio Optimizer (`optimizer.py:139`): revisao do mesmo dia e a 1a revisao de
cada card nao pontuam -- sem dias decorridos nao ha esquecimento a prever.
Cada visao pontua sob o SEU proprio rotulo (na visao remap a nota 2 conta como
falha), por isso as duas colunas NAO sao comparaveis entre si; a comparacao
valida e default x otimizado DENTRO de cada visao.

--------------------------------------------------------------------------
3. Limites DECLARADOS (AGENTE.md 10.8 -- verification-stack)
--------------------------------------------------------------------------
(a) **`review_duration` e sintetico.** `compute_optimal_retention` recusa
    ReviewLog com `review_duration is None` (`optimizer.py:638`) e o schema
    `fsrs_revlog` NAO grava duracao. Usa-se uma constante (default 16500 ms =
    16,5 min / 60 cards, o lote medido do player na s183; `--duracao-ms` para
    variar). Consequencia: no modelo de custo as 4 notas custam igual, entao a
    retencao otima devolvida minimiza REVISOES por unidade de conhecimento, e
    nao TEMPO. E numero honesto sob essa hipotese -- e so sob ela.
(b) **`compute_optimal_retention` tem grade grossa**: escolhe dentro de
    [0.70, 0.75, 0.80, 0.85, 0.90, 0.95] (`optimizer.py:648`). Nao ha
    resolucao para dizer "0.87".
(c) **Carimbo de tempo misto.** Ate o F80 o `review_time` vinha do DEFAULT do
    SQLite (UTC); depois passou a ser LOCAL explicito (`db.carimbo()`). Aqui
    todos sao lidos como UTC, convencao unica. O erro maximo e 3h e so muda o
    resultado quando cruza a virada do dia -- nao foi quantificado.
(d) **Assimetria de `learning_steps`.** O replay da metrica usa o Scheduler de
    PRODUCAO (`learning_steps=()`, igual a `app/utils/fsrs.py`); o Optimizer,
    por dentro, ajusta com `Scheduler(parameters=...)`, que carrega os
    learning_steps default. A diferenca so alcanca card em Learning com
    revisao no mesmo dia -- que a metrica ja descarta -- mas fica declarada.
(e) **O JSON e fit na serie inteira; a metrica e fit so no treino.** Sao dois
    ajustes por visao: `parametros` (revlog completo, o que o operador
    adotaria) e `parametros_holdout_fit` (so os ~80% iniciais), usado
    EXCLUSIVAMENTE para pontuar a cauda sem contaminacao. Reportar a metrica do
    fit completo seria medir o modelo nos dados dele.

--------------------------------------------------------------------------
4. Leech (R7 da fila) -- `--leech`
--------------------------------------------------------------------------
Leech e recurso do Anki, nao do algoritmo: o limiar e nosso. Mede quantos cards
tem `lapses >= N` e como e a `difficulty` deles -- x2, porque com a nota 2
contando como acerto o lapso fica SUBCONTADO e o limiar mente. Contagem crua =
`fsrs_cards.lapses` (o que o motor gravou) mais a reconstrucao pelo revlog como
prova de que a reconstrucao bate; contagem remap = mesma reconstrucao com
`2 -> Again`. Lapso = revisao com nota Again que NAO e a 1a do card (regra de
`app/utils/fsrs.py::evaluate`: `if rating == 1 and not is_new`). A `difficulty`
exibida e sempre a ARMAZENADA (produzida pelas notas cruas): o que muda entre
as visoes e QUAIS cards cruzam o limiar, nunca a dificuldade em si.

--------------------------------------------------------------------------
5. Acesso ao banco
--------------------------------------------------------------------------
Leitura direta em `file:<db>?mode=ro` (uri=True). `app/utils/db.py` nao tem
leitor de `fsrs_revlog` e o `get_connection()` dele abre em leitura-e-escrita;
abrir read-only aqui e garantia mais forte do que reusar o leitor errado. A
excecao esta prevista em `.vibeflow/conventions.md` ("standalone CLIs in tools/
open their own connection directly").

Uso:
  python tools/fsrs_optimize.py                  # dry-run (default): imprime, nao grava
  python tools/fsrs_optimize.py --write          # grava core/fsrs_params.json
  python tools/fsrs_optimize.py --holdout 0.3
  python tools/fsrs_optimize.py --duracao-ms 20000
  python tools/fsrs_optimize.py --leech          # painel R7 (nao roda o Optimizer)
  python tools/fsrs_optimize.py --leech --limiar-lapsos 4
"""
import argparse
import json
import math
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.utils import regua as _regua  # noqa: E402

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = Path(__file__).parent.parent.resolve()
DB_PATH = ROOT_DIR / 'ipub.db'
OUT_PATH = ROOT_DIR / 'core' / 'fsrs_params.json'

#: Gate do proprio py-fsrs (`optimizer.py:632`): abaixo disto o
#: `compute_optimal_retention` levanta ValueError e o
#: `compute_optimal_parameters` devolve os defaults sem ajustar nada.
MIN_REVLOG = 512

#: Duracao sintetica por revisao, em ms -- ver limite (a) da docstring.
DURACAO_MS_DEFAULT = 16500

#: Visao (ii). Chaves = nota da regua v1, valores = nota FSRS nativa.
#: 🔴 R2/F112 (s186): este mapa DEIXOU de nascer aqui. Ele vive em
#: `app/utils/regua.py`, o portador unico da regua, e este modulo o LE -- se as
#: duas copias divergissem, os numeros com que o operador decidiu a opcao (b)
#: deixariam de valer sem ninguem notar. Nome mantido por ser citado no ledger.
REMAP_F112 = _regua.MAPA_V1_PARA_NATIVO

CITACAO_REVISAR_PASSO4 = (
    "Criterio: cravou conceito + regra-mestre -> 4; acertou o nucleo, faltou "
    "detalhe -> 3; recall parcial/na zona mas sem o alvo -> 2; errou ou "
    "'nao sei' -> 1."
)

JUSTIFICATIVA_REMAP = _regua.JUSTIFICATIVA_V1

AVISO_RETENCAO = (
    "retencao otima e NUMERO REPORTADO, nunca adotado: a carga diaria de cards "
    "e decisao do operador (teto 60/dia), e este CLI nao agenda nada."
)


class RevlogInsuficiente(Exception):
    """Revlog abaixo do minimo de 512 exigido pelo Optimizer."""


# ---------------------------------------------------------------- leitura (ro)

def _parse_utc(valor):
    """'YYYY-MM-DD HH:MM:SS[.ffffff]' -> datetime tz-aware UTC. Ver limite (c)."""
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor if valor.tzinfo else valor.replace(tzinfo=timezone.utc)
    s = str(valor).strip().replace('T', ' ')
    if not s:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def _conectar_ro(db_path=None):
    """Conexao READ-ONLY. Unico ponto de acesso ao banco neste modulo."""
    p = Path(db_path) if db_path else DB_PATH
    return sqlite3.connect("file:%s?mode=ro" % p.as_posix(), uri=True)


def ler_revlog(db_path=None):
    """[(card_id, rating, datetime_utc, regua)] ordenado no tempo. Somente leitura.

    R2/F112 (s186): a **regua** entrou na tupla porque ela e propriedade da
    LINHA, nao do corpus. Antes do R2 todo o revlog foi gravado sob a v1; depois
    dele as duas safras convivem, e a mesma nota 2 significa coisas opostas em
    cada uma. Banco que ainda nao rodou o ALTER nao tem a coluna -- isso nao e
    erro, e o estado esperado, e le como v1 (`regua.regua_da_linha(None)`).
    """
    conn = _conectar_ro(db_path)
    try:
        tem_regua = any(r[1] == "regua_versao"
                        for r in conn.execute("PRAGMA table_info(fsrs_revlog)"))
        col = "regua_versao" if tem_regua else "NULL"
        cru = conn.execute(
            "SELECT card_id, rating, review_time, %s FROM fsrs_revlog "
            "WHERE review_time IS NOT NULL AND rating BETWEEN 1 AND 4 "
            "ORDER BY review_time, id" % col).fetchall()
    finally:
        conn.close()
    linhas = []
    for card_id, rating, rt, regua in cru:
        quando = _parse_utc(rt)
        if quando is not None:
            linhas.append((int(card_id), int(rating), quando,
                           _regua.regua_da_linha(regua)))
    linhas.sort(key=lambda x: x[2])
    return linhas


def ler_cards(db_path=None):
    """[(card_id, lapses, difficulty)] dos cards ATIVOS (aposentado fora)."""
    conn = _conectar_ro(db_path)
    try:
        linhas = conn.execute(
            "SELECT f.card_id, f.lapses, f.difficulty FROM fsrs_cards f "
            "JOIN flashcards l ON l.id = f.card_id "
            "WHERE COALESCE(l.needs_qualitative, 0) < 2").fetchall()
    finally:
        conn.close()
    return [(int(c), int(l or 0), float(d or 0.0)) for c, l, d in linhas]


# ------------------------------------------------------------------- remap

def aplicar_remap(rating, remap=None):
    """Nota -> nota FSRS por MAPA GLOBAL. `remap=None` = identidade.

    Caminho do R1, preservado porque o **gate de paridade** do R2 o usa como
    referencia: sobre um revlog 100% v1 o caminho novo (por linha) tem que
    devolver exatamente isto. Nao chamar em codigo novo -- use `nota_da_linha`.
    """
    if not remap:
        return int(rating)
    return int(remap[int(rating)])


def nota_da_linha(rating, regua, visao):
    """Nota efetiva de UMA linha sob a visao pedida. Delega ao portador unico."""
    return _regua.nota_efetiva(rating, regua, visao=visao)


def distribuicao(linhas, visao="nativo"):
    """{nota_efetiva: contagem} sob a visao pedida."""
    fora = {}
    for _cid, rating, _q, regua in linhas:
        n = nota_da_linha(rating, regua, visao)
        fora[n] = fora.get(n, 0) + 1
    return {str(k): fora[k] for k in sorted(fora)}


def construir_review_logs(linhas, visao="nativo", duracao_ms=DURACAO_MS_DEFAULT):
    """[(card_id, rating, dt, regua)] -> [ReviewLog] com a nota ja traduzida."""
    from fsrs import Rating, ReviewLog
    return [ReviewLog(card_id=cid,
                      rating=Rating(nota_da_linha(rating, regua, visao)),
                      review_datetime=quando,
                      review_duration=int(duracao_ms))
            for cid, rating, quando, regua in linhas]


# ----------------------------------------------------------- holdout + metrica

def corte_holdout(linhas, fracao=0.2):
    """Instante que abre a cauda de hold-out (ultimos ~`fracao` por data)."""
    if not linhas:
        return None
    idx = int(len(linhas) * (1.0 - fracao))
    idx = min(max(idx, 0), len(linhas) - 1)
    return linhas[idx][2]


def particionar(linhas, corte):
    """(treino, cauda) pelo instante de corte."""
    if corte is None:
        return list(linhas), []
    return ([l for l in linhas if l[2] < corte],
            [l for l in linhas if l[2] >= corte])


def _scheduler(parametros):
    """Scheduler de PRODUCAO com os parametros dados -- ver limite (d)."""
    from fsrs import Scheduler
    kwargs = dict(desired_retention=0.9, learning_steps=(), enable_fuzzing=False)
    if parametros is not None:
        kwargs['parameters'] = tuple(float(x) for x in parametros)
    return Scheduler(**kwargs)


def log_loss(linhas, parametros, corte=None, visao="nativo"):
    """(loss_media, n_pontos) na cauda. Menor = melhor. Ver secao 2.

    Replay cronologico por card sobre o historico COMPLETO; so as revisoes em
    `review_time >= corte` somam. Revisao do mesmo dia e 1a do card nao
    pontuam (convencao do proprio Optimizer, `optimizer.py:139`).
    """
    from fsrs import Card, Rating
    sched = _scheduler(parametros)
    por_card = {}
    for cid, rating, quando, regua in linhas:
        por_card.setdefault(cid, []).append((quando, rating, regua))
    eps = 1e-9
    soma, n = 0.0, 0
    for cid in sorted(por_card):
        historico = sorted(por_card[cid], key=lambda x: x[0])
        card = None
        for i, (quando, rating, regua) in enumerate(historico):
            if i == 0:
                card = Card(card_id=cid, due=quando)
            pontua = (card.last_review is not None
                      and (quando - card.last_review).days > 0
                      and (corte is None or quando >= corte))
            if pontua:
                p = sched.get_card_retrievability(card, current_datetime=quando)
                p = min(max(float(p), eps), 1.0 - eps)
                y = 0.0 if nota_da_linha(rating, regua, visao) == 1 else 1.0
                soma += -(y * math.log(p) + (1.0 - y) * math.log(1.0 - p))
                n += 1
            card, _ = sched.review_card(
                card=card, rating=Rating(nota_da_linha(rating, regua, visao)),
                review_datetime=quando)
    return (soma / n if n else None), n


# ------------------------------------------------------------------ optimizer

def exigir_minimo(n):
    """Gate <512 do py-fsrs, explicitado aqui em vez de deixar a lib levantar."""
    if n < MIN_REVLOG:
        raise RevlogInsuficiente(
            "revlog com %d revisao(oes); o Optimizer do py-fsrs exige pelo "
            "menos %d (optimizer.py:632). Nada a otimizar." % (n, MIN_REVLOG))
    return n


def otimizar(review_logs):
    """Parametros ajustados. Import tardio: torch e caro e so entra aqui."""
    from fsrs.optimizer import Optimizer
    exigir_minimo(len(review_logs))
    return [float(x) for x in Optimizer(review_logs).compute_optimal_parameters()]


def retencao_otima(review_logs, parametros):
    """Retencao-alvo de menor custo. REPORTADA, nunca adotada (ver AVISO)."""
    from fsrs.optimizer import Optimizer
    exigir_minimo(len(review_logs))
    return float(Optimizer(review_logs).compute_optimal_retention(parametros))


def parametros_default():
    from fsrs.scheduler import DEFAULT_PARAMETERS
    return [float(x) for x in DEFAULT_PARAMETERS]


# ----------------------------------------------------------------- leech (R7)

def _resumo_difficulty(valores):
    """n / min / quartis / max / media + bandas -- sem numpy."""
    if not valores:
        return {"n": 0}
    v = sorted(valores)

    def q(f):
        if len(v) == 1:
            return v[0]
        pos = f * (len(v) - 1)
        baixo = int(math.floor(pos))
        alto = min(baixo + 1, len(v) - 1)
        return v[baixo] + (v[alto] - v[baixo]) * (pos - baixo)

    bandas = {"<=3": 0, "3-5": 0, "5-7": 0, "7-9": 0, ">9": 0}
    for x in v:
        if x <= 3:
            bandas["<=3"] += 1
        elif x <= 5:
            bandas["3-5"] += 1
        elif x <= 7:
            bandas["5-7"] += 1
        elif x <= 9:
            bandas["7-9"] += 1
        else:
            bandas[">9"] += 1
    return {"n": len(v), "min": round(v[0], 2), "p25": round(q(0.25), 2),
            "mediana": round(q(0.5), 2), "p75": round(q(0.75), 2),
            "max": round(v[-1], 2), "media": round(sum(v) / len(v), 2),
            "bandas": bandas}


def contar_lapsos(linhas, visao="nativo"):
    """{card_id: lapsos} reconstruido do revlog.

    Lapso = nota Again que NAO e a 1a revisao do card -- exatamente a regra de
    `app/utils/fsrs.py::evaluate` (`if rating == 1 and not is_new`).
    """
    por_card = {}
    for cid, rating, quando, regua in linhas:
        por_card.setdefault(cid, []).append((quando, rating, regua))
    fora = {}
    for cid, hist in por_card.items():
        hist.sort(key=lambda x: x[0])
        fora[cid] = sum(1 for _q, r, g in hist[1:]
                        if nota_da_linha(r, g, visao) == 1)
    return fora


def medir_leech(linhas, cards, limiar=3):
    """Painel R7 x2: crua x remap. Read-only, nao grava nada."""
    dif = {cid: d for cid, _l, d in cards}
    ativos = set(dif)
    armazenado = {cid: l for cid, l, _d in cards}
    recon_cru = contar_lapsos(linhas, visao="cru")
    recon_remap = contar_lapsos(linhas, visao="nativo")

    def painel(cont):
        alvos = sorted(c for c in ativos if cont.get(c, 0) >= limiar)
        return {"limiar": limiar, "cards": len(alvos), "ids": alvos[:40],
                "difficulty": _resumo_difficulty([dif[c] for c in alvos])}

    divergencia = sorted(c for c in ativos
                         if armazenado.get(c, 0) != recon_cru.get(c, 0))
    return {
        "limiar_lapsos": limiar,
        "cards_ativos": len(ativos),
        "crua": painel({c: armazenado.get(c, 0) for c in ativos}),
        "crua_reconstruida": painel(recon_cru),
        "remap": painel(recon_remap),
        "reconstrucao": {
            "cards_divergentes": len(divergencia),
            "exemplos": divergencia[:10],
            "nota": "crua_reconstruida deve bater com crua; a divergencia mede "
                    "o quanto a reconstrucao pelo revlog e confiavel antes de "
                    "ler o numero do remap",
        },
    }


# -------------------------------------------------------------------- payload

def analisar_visao(linhas, visao, nome, fracao, duracao_ms):
    """Roda uma visao inteira: parametros, retencao, metrica default x otimizado."""
    corte = corte_holdout(linhas, fracao)
    treino, cauda = particionar(linhas, corte)
    logs_full = construir_review_logs(linhas, visao, duracao_ms)
    exigir_minimo(len(logs_full))

    parametros = otimizar(logs_full)
    retencao = retencao_otima(logs_full, parametros)

    # Ajuste auxiliar so no treino -- limite (e): a metrica nao pode ser medida
    # com parametros que ja viram a cauda.
    logs_treino = construir_review_logs(treino, visao, duracao_ms)
    if len(logs_treino) >= MIN_REVLOG:
        params_treino = otimizar(logs_treino)
        base_metrica = "fit nos ~%d%% iniciais" % round((1 - fracao) * 100)
    else:
        params_treino = parametros
        base_metrica = ("treino abaixo de %d revisoes -- metrica medida com o "
                        "fit COMPLETO (contaminada, declarada)" % MIN_REVLOG)

    m_default, n_pts = log_loss(linhas, None, corte, visao)
    m_otim, _ = log_loss(linhas, params_treino, corte, visao)
    reguas = sorted({g for _c, _r, _q, g in linhas})
    return {
        "visao": nome,
        "remap": ({str(k): v for k, v in REMAP_F112.items()}
                  if visao == "nativo" else None),
        # R2: sob QUAL regua este conjunto foi ajustado. E o campo que
        # `app/utils/regua.carregar_parametros` exige para permitir a adocao --
        # parametro sem a regua do fit e numero orfao (F114).
        "regua_do_fit": (_regua.REGUA_ATUAL if visao == "nativo"
                         else (reguas[0] if len(reguas) == 1 else None)),
        "reguas_no_corpus": reguas,
        "distribuicao_notas_efetivas": distribuicao(linhas, visao),
        "parametros": [round(x, 6) for x in parametros],
        "parametros_holdout_fit": [round(x, 6) for x in params_treino],
        "retencao_otima": retencao,
        "metrica": {
            "nome": "log_loss",
            "direcao": "menor e melhor",
            "escopo": "cauda temporal hold-out (ultimos ~%d%% por data)"
                      % round(fracao * 100),
            "base_dos_parametros": base_metrica,
            "n_pontos": n_pts,
            "default": (round(m_default, 6) if m_default is not None else None),
            "otimizado": (round(m_otim, 6) if m_otim is not None else None),
            "delta": (round(m_otim - m_default, 6)
                      if (m_default is not None and m_otim is not None) else None),
        },
        "n_revisoes_treino": len(treino),
        "n_revisoes_cauda": len(cauda),
    }


def construir_payload(linhas, visoes, fracao, duracao_ms, fsrs_version):
    """JSON versionado de `core/fsrs_params.json`. Dado, nunca decisao."""
    corte = corte_holdout(linhas, fracao)
    return {
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "gerado_por": "tools/fsrs_optimize.py (R1, read-only)",
        "py_fsrs_version": fsrs_version,
        "fonte": "ipub.db::fsrs_revlog (conexao mode=ro; zero escrita)",
        "revisoes_usadas": len(linhas),
        "cards_no_revlog": len({c for c, _r, _q, _g in linhas}),
        "janela": {
            "primeira_revisao": linhas[0][2].isoformat() if linhas else None,
            "ultima_revisao": linhas[-1][2].isoformat() if linhas else None,
        },
        "holdout": {
            "fracao": fracao,
            "corte": corte.isoformat() if corte else None,
            "metodo": "cauda temporal por data; o replay usa o historico "
                      "completo do card, so a cauda pontua",
        },
        "review_duration_ms_sintetico": duracao_ms,
        "metadata_remap": {
            "fonte_da_regua": ".claude/commands/revisar.md, passo 4",
            "citacao_literal": CITACAO_REVISAR_PASSO4,
            "transcricao": "setas Unicode do original transcritas como '->' "
                           "(AGENTE.md 4.5, encoding ASCII)",
            "mapa": {str(k): v for k, v in REMAP_F112.items()},
            "justificativa_por_nota": JUSTIFICATIVA_REMAP,
            "escopo": "aplicado SO na entrada do Optimizer; fsrs_revlog imutavel",
            "achado": "F112",
        },
        "visoes": {v["visao"]: v for v in visoes},
        "adotado": False,
        "aviso_retencao": AVISO_RETENCAO,
        "aviso_adocao": "parametros REPORTADOS. Adotar e o item R2 da fila e "
                        "exige decisao do operador; `app/utils/fsrs.py` nao le "
                        "este arquivo.",
    }


# ----------------------------------------------------------------- impressao

def _print_visao(v):
    m = v["metrica"]
    print("  [%s] remap = %s" % (v["visao"].upper(),
                                 v["remap"] or "nenhum (notas cruas)"))
    print("    notas efetivas   : %s" % v["distribuicao_notas_efetivas"])
    print("    parametros (21)  : %s" % [round(x, 4) for x in v["parametros"]])
    print("    retencao otima   : %s" % v["retencao_otima"])
    print("    log-loss default : %s" % m["default"])
    print("    log-loss otimiz. : %s   (delta %s, n=%s, %s)"
          % (m["otimizado"], m["delta"], m["n_pontos"], m["escopo"]))
    print("    base do fit      : %s" % m["base_dos_parametros"])
    print()


def _print_leech(rel):
    print()
    print("=" * 70)
    print("  LEECH (R7) -- cards com lapses >= %d -- READ-ONLY"
          % rel["limiar_lapsos"])
    print("=" * 70)
    print("  cards ativos: %d" % rel["cards_ativos"])
    for chave, rotulo in (("crua", "CRUA (fsrs_cards.lapses)"),
                          ("crua_reconstruida", "CRUA reconstruida do revlog"),
                          ("remap", "REMAP (2 -> Again)")):
        p = rel[chave]
        d = p["difficulty"]
        print()
        print("  %s: %d card(s)" % (rotulo, p["cards"]))
        if d["n"]:
            print("    difficulty  min %s | p25 %s | mediana %s | p75 %s | "
                  "max %s | media %s" % (d["min"], d["p25"], d["mediana"],
                                         d["p75"], d["max"], d["media"]))
            print("    bandas      %s" % d["bandas"])
        if p["ids"]:
            print("    ids         %s" % p["ids"])
    r = rel["reconstrucao"]
    print()
    print("  reconstrucao: %d card(s) com lapses armazenado != reconstruido %s"
          % (r["cards_divergentes"], r["exemplos"]))
    print("  difficulty exibida e sempre a ARMAZENADA; o remap muda QUAIS cards")
    print("  cruzam o limiar, nunca a dificuldade.")
    print()


def _rel(p):
    """Caminho legivel: relativo a raiz quando der, absoluto quando nao der."""
    try:
        return str(Path(p).relative_to(ROOT_DIR))
    except ValueError:
        return str(p)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Otimizador READ-ONLY de parametros do FSRS (R1) -- duas "
                    "visoes do revlog (cru x remap F112). Nada e adotado.")
    ap.add_argument("--write", action="store_true",
                    help="grava core/fsrs_params.json (sem ele, dry-run)")
    ap.add_argument("--dry-run", action="store_true",
                    help="(default) imprime sem gravar; vence --write se os "
                         "dois vierem juntos")
    ap.add_argument("--holdout", type=float, default=0.2,
                    help="fracao final do revlog reservada para a metrica "
                         "(default 0.2)")
    ap.add_argument("--duracao-ms", type=int, default=DURACAO_MS_DEFAULT,
                    help="review_duration sintetico em ms (limite (a); "
                         "default 16500)")
    ap.add_argument("--leech", action="store_true",
                    help="painel de leech R7 (x2: crua e remap); NAO roda o "
                         "Optimizer")
    ap.add_argument("--limiar-lapsos", type=int, default=3,
                    help="limiar de lapsos do painel --leech (default 3)")
    args = ap.parse_args(argv)

    if not DB_PATH.exists():
        print("[ERRO] banco nao encontrado: %s" % DB_PATH, file=sys.stderr)
        return 1

    linhas = ler_revlog()
    print()
    print("=" * 70)
    print("  FSRS OPTIMIZE (R1) -- READ-ONLY; zero escrita no ipub.db")
    print("=" * 70)
    print("  revisoes no revlog: %d   cards: %d"
          % (len(linhas), len({c for c, _r, _q, _g in linhas})))

    if args.leech:
        _print_leech(medir_leech(linhas, ler_cards(), args.limiar_lapsos))
        return 0

    try:
        exigir_minimo(len(linhas))
    except RevlogInsuficiente as e:
        print("\n[BLOQUEIO] %s" % e, file=sys.stderr)
        return 2

    try:
        from importlib.metadata import version as _v
        fsrs_version = _v("fsrs")
    except Exception:
        fsrs_version = "desconhecida"

    print("  py-fsrs           : %s" % fsrs_version)
    print("  hold-out          : ultimos %d%% por data" % round(args.holdout * 100))
    print("  duracao sintetica : %d ms/revisao (limite (a))" % args.duracao_ms)
    print("\n  Ajustando 2 visoes x 2 fits (pode levar minutos)...\n")

    visoes = []
    for nome, visao in (("cru", "cru"), ("remap", "nativo")):
        visoes.append(analisar_visao(linhas, visao, nome, args.holdout,
                                     args.duracao_ms))
    payload = construir_payload(linhas, visoes, args.holdout, args.duracao_ms,
                                fsrs_version)
    print()
    for v in visoes:
        _print_visao(v)
    print("  [!] %s" % AVISO_RETENCAO)
    print("  [!] %s" % payload["aviso_adocao"])
    print("  Nota: as duas visoes usam rotulos diferentes -- compare default x")
    print("  otimizado DENTRO de cada visao, nunca uma visao contra a outra.")
    print()

    gravar = args.write and not args.dry_run
    if gravar:
        OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")
        print("  [GRAVADO] %s" % _rel(OUT_PATH))
    else:
        motivo = ("--dry-run vence --write" if (args.write and args.dry_run)
                  else "dry-run (default)")
        print("  [DRY-RUN] nada gravado (%s). Use --write para persistir em %s."
              % (motivo, _rel(OUT_PATH)))
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
