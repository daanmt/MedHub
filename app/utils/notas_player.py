"""Notas do player: as regras PURAS do `--record-lote` (spec medhub-hub-v0-part-2, s193).

## O problema

O player (aba Cards do MedHub HUB) guarda a 1a nota de cada card no `db` da pagina, e o
`--record-lote` a grava no FSRS. Com UM artifact permanente a mesma sessao de notas e
relida -- e o writer de 22/09/2026 nao sabia dizer o que ja tinha gravado (o #92 precisou
de marca manual `gravado_em` no `db`), gravava no relogio da GRAVACAO (a nota das 07:17
gravada as 19:37 deslocou o `due` do #92 em 12h) e um doc torto recusava o lote inteiro.

## As regras, uma funcao cada

- `relogio(ts)`: QUANDO a revisao aconteceu. O `ts` ISO UTC da pagina vira hora LOCAL
  naive (a zona do banco, F80) TRUNCADA AO SEGUNDO (a largura do carimbo). E o UNICO
  conversor: o que se grava (`record_review(quando=...)`) e o que se compara
  (`situacao`) saem daqui. Dois conversores divergiriam no milissegundo, e 07:17:50 <
  07:17:50.144 regravaria a mesma nota.
- `validar_nota(nota, cards, agora)`: a QUARENTENA. A pagina e input nao confiavel e, na
  conta compartilhada, quem abre e OWNER -- as regras do `db` nao o limitam. A fronteira
  que protege o dado e o writer: doc estranho sai com motivo, os validos seguem.
- `situacao(quando, revisoes)`: a IDEMPOTENCIA, derivada do revlog (SSOT) sem estado
  novo. Linha com `review_time` IGUAL = JA GRAVADA; revisao mais nova sem a igual = FORA
  DE ORDEM (gravar a velha por cima faria o card andar para tras); senao, NOVA.
- `defeito_ja_marcado(quando, marca_player)`: o mesmo para o defeito, por `>=` -- marca
  de reforja nao tem ordem de FSRS a preservar.

Modulo PURO: sem banco, sem relogio de parede (`agora` e injetado), sem I/O. A leitura
do revlog vive em `app.utils.db.estado_gravacao_player`.
"""
from datetime import datetime

JA_GRAVADA = "ja_gravada"
FORA_DE_ORDEM = "fora_de_ordem"
NOVA = "nova"


def relogio(ts, fuso=None):
    """`ts` ISO da pagina -> datetime LOCAL naive, truncado ao segundo.

    `fuso` = tzinfo de destino, injetavel nos testes; None = o fuso do sistema, o mesmo
    de `db.agora()`. ValueError com o motivo quando o ts e ausente, ilegivel ou SEM
    fuso: a pagina grava `toISOString()` (UTC com `Z`), e hora sem fuso nao diz se
    07:17 e local ou UTC -- adivinhar deslocaria a revisao em 3h sem ninguem ver.
    """
    if ts is None or (isinstance(ts, str) and not ts.strip()):
        raise ValueError("ts ausente (a nota nao diz quando foi dada)")
    if not isinstance(ts, str):
        raise ValueError("ts ilegivel: %r" % (ts,))
    texto = ts.strip()
    if texto[-1] in "Zz":
        texto = texto[:-1] + "+00:00"
    try:
        instante = datetime.fromisoformat(texto)
    except ValueError:
        raise ValueError("ts ilegivel: %r" % ts) from None
    if instante.tzinfo is None:
        raise ValueError("ts sem fuso: %r (a pagina grava ISO UTC)" % ts)
    return instante.astimezone(fuso).replace(tzinfo=None, microsecond=0)


def validar_nota(nota, cards, agora, fuso=None):
    """Quarentena de UMA nota: `(registro, None)` se valida, `(None, motivo)` se nao.

    `cards` = {card_id: card do lote exportado}; `agora` = o relogio do banco (LOCAL
    naive, `db.agora()`). O `registro` leva `quando` (o relogio da revisao) e o
    `selection_reason` do EXPORT -- nunca o que a pagina disser.
    """
    if not isinstance(nota, dict):
        return None, "nota nao e objeto"
    try:
        cid = int(nota.get("card_id"))
    except (TypeError, ValueError):
        return None, "sem card_id inteiro"
    if cid not in cards:
        return None, "card_id %d fora do lote exportado" % cid
    cru = nota.get("rating_primeira", nota.get("rating"))
    rating = None
    if cru is not None:
        try:
            rating = int(cru)
        except (TypeError, ValueError):
            rating = None
        if rating not in (1, 2, 3, 4):
            return None, "card_id %d com rating invalido: %r" % (cid, cru)
    defeito = bool(nota.get("defeito"))
    motivo = (nota.get("motivo") or "").strip()
    if defeito and not motivo:
        return None, ("card_id %d marcado como defeito SEM motivo "
                      "(marca sem motivo nao fecha nem audita)" % cid)
    if rating is None and not defeito:
        return None, "card_id %d sem rating e sem defeito" % cid
    try:
        quando = relogio(nota.get("ts"), fuso)
    except ValueError as e:
        return None, "card_id %d com %s" % (cid, e)
    if quando > agora:
        return None, "card_id %d com ts no futuro: %s > agora %s" % (
            cid, quando, agora.replace(microsecond=0))
    return {"card_id": cid, "rating": rating, "defeito": defeito, "motivo": motivo,
            "selection_reason": cards[cid].get("selection_reason"),
            "quando": quando}, None


def _instante(valor):
    """Carimbo do banco (str) ou datetime -> datetime naive truncado ao segundo.

    Linha ilegivel no revlog NAO e pulada: pular deixaria uma revisao mais nova
    invisivel e a nota velha seria gravada por cima. ValueError, alto.
    """
    if isinstance(valor, datetime):
        return valor.replace(microsecond=0)
    if valor is None:
        raise ValueError("linha do revlog sem review_time -- nao da para ordenar a nota")
    return datetime.fromisoformat(str(valor).strip()).replace(microsecond=0)


def situacao(quando, revisoes):
    """JA_GRAVADA | FORA_DE_ORDEM | NOVA de uma nota contra o revlog do card.

    `quando` = `relogio(ts)`; `revisoes` = os `review_time` do card, em qualquer ordem.
    Igualdade no SEGUNDO -- nunca `>=`: com `>=`, a 2a nota do mesmo card sumiria em
    silencio (objecao do `/ai-eng`, 22/09).
    """
    tempos = [_instante(r) for r in revisoes or ()]
    if quando in tempos:
        return JA_GRAVADA
    if any(t > quando for t in tempos):
        return FORA_DE_ORDEM
    return NOVA


def ultima_revisao(revisoes):
    """A revisao mais nova do card (datetime) ou None -- o que o FORA DE ORDEM reporta."""
    tempos = [_instante(r) for r in revisoes or ()]
    return max(tempos) if tempos else None


def defeito_ja_marcado(quando, marca_player):
    """A marca de reforja `origem='player'` mais recente (`criado_em`) e de `quando` em
    diante: esta nota ja virou marca. A marca carimba a hora da GRAVACAO, que e sempre
    >= a da nota que a gerou."""
    return marca_player is not None and _instante(marca_player) >= quando
