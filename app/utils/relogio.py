"""O DIA LOGICO do MedHub -- a funcao unica que responde "que dia foi esta revisao" (F141, s207).

## O problema (F141)

Dois relogios diziam "um dia": o py-fsrs mede o decorrido por 24 h truncadas
(`(review_datetime - last_review).days`) e a fila serve por dia-calendario (o bucket
`hoje` entrega desde 00:00 tudo que vence ate 23:59). Card de intervalo 1 visto as 16:56
e servido na manha seguinte (21,5 h depois) caia no ramo de "mesmo dia" da biblioteca --
estabilidade subestimada, card de volta mais cedo, teto consumido. Em 29/09, 21 de 37
revisoes com historico (57%).

## A regra

`dia_logico(ts)` = a DATA LOCAL do instante (virada a 00:00, sem hora de corte). E o
mesmo dia que a fila, o teto e o `sessoes_bulk` ja usam (relogio unico do F80:
`app.utils.db.agora()`, local naive). Quem precisa de "quantos dias se passaram" subtrai
dois `dia_logico`, nunca dois instantes. Consumidores: o adapter (`app.utils.fsrs`), a
entrada do Optimizer (`tools/fsrs_optimize.py`) e a trava de 2a nota do dia
(`app.utils.notas_player`, F142).

Modulo PURO: sem banco, sem relogio de parede.
"""
from datetime import date, datetime


def dia_logico(ts):
    """Instante -> `date` do dia logico (data local).

    Aceita `datetime` naive (lido como LOCAL, a zona do banco -- F80), `datetime` tz-aware
    (convertido para a zona local antes) ou o carimbo do banco em texto
    (`YYYY-MM-DD HH:MM:SS[.ffffff]`, com `T` ou espaco). `date` passa direto.
    ValueError em valor ausente ou ilegivel: adivinhar o dia de uma revisao desloca o
    intervalo em silencio.
    """
    if isinstance(ts, datetime):
        return (ts.astimezone() if ts.tzinfo is not None else ts).date()
    if isinstance(ts, date):
        return ts
    if ts is None or (isinstance(ts, str) and not ts.strip()):
        raise ValueError("instante ausente -- sem ele nao ha dia logico")
    if not isinstance(ts, str):
        raise ValueError("instante ilegivel: %r" % (ts,))
    try:
        return dia_logico(datetime.fromisoformat(ts.strip().replace(" ", "T", 1)))
    except ValueError:
        raise ValueError("instante ilegivel: %r" % ts) from None


def dias_entre(antes, depois):
    """Dias LOGICOS decorridos de `antes` a `depois` (inteiro; 0 = mesmo dia)."""
    return (dia_logico(depois) - dia_logico(antes)).days
