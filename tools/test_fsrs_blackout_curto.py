"""F98: card de intervalo CURTO ou em RELEARNING some do painel de blackout.
Mais a PARIDADE do `record_review`, que e a baseline do R2.

Escrito ANTES do fix (AGENTE.md 10.6).

🔴 O DEFEITO, medido na s183: ao gravar o bloco de drenagem, **9 cards** ficaram com
`due` em 2026-09-13 -- o dia do ENAMED -- e `fsrs_load.py --blackout` seguia reportando
`0 movidos / 19 overflow`, sem os 9. Eles "nunca foram candidatos".

🔴 A CAUSA REAL, medida em 18/09/2026 -- e NAO e a que o enunciado do F98 supos.
O `rebalancear_blackout` **ja trata** intervalo curto corretamente: `if not
folga_de(intervalo)` manda o card para `overflow` com motivo `"intervalo Nd sem folga"`.
O que o exclui e o **filtro `f.state = 2`** da consulta: nota 1 joga o card em
**relearning (state 3)** e ele desaparece da varredura inteira. Hoje ha 28 cards em
state 3. Nota 2 mantem state 2 mas com intervalo curto -- esse ja aparecia.

🔴 POR QUE O REMEDIO E VISIBILIDADE, E NAO MOVER. A primeira tentativa desta sessao foi
tirar a guarda de blackout de dentro da clausula de folga e recuar o card para antes da
prova. Isso **quebrou 4 testes do F71**, e eles estavam certos: o `AGENTE.md §6` diz
literalmente *"sem vaga na folga, fica onde esta e vira OVERFLOW declarado"*, e a
mitigacao que o operador ACEITOU na s183 foi justamente essa -- card parado em dia de
prova reaparece depois como atrasado, sem escrita nenhuma. O que faltava nunca foi o
movimento; era o card **aparecer no painel**. Mover seria trocar um gate-miss por uma
violacao de contrato.

CLASSE: gate-miss por ESCOPO de consulta (a varredura nao cobre a populacao que o
defeito habita), irma do "gate sem escopo de intencao" do F113 e do
`cli_signature_check` (presenca != cobertura). Serie §10.8.
"""

import os
import sqlite3
import sys
from datetime import date, datetime, timedelta

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from app.utils import db  # noqa: E402
from app.utils import fsrs_balance as fb  # noqa: E402

PROVA = date(2026, 11, 1)
BLACKOUT = fb.blackout_de([PROVA])            # {01/11, 02/11}
HOJE = date(2026, 10, 28)

_DDL = """
CREATE TABLE flashcards (id INTEGER PRIMARY KEY, needs_qualitative INTEGER DEFAULT 0);
CREATE TABLE fsrs_cards (card_id INTEGER PRIMARY KEY, state INTEGER, due TIMESTAMP,
                         scheduled_days INTEGER);
"""


def _conn(cards):
    """cards = [(card_id, state, due:date, scheduled_days)]"""
    con = sqlite3.connect(":memory:")
    con.executescript(_DDL)
    for cid, state, due, sched in cards:
        con.execute("INSERT INTO flashcards (id, needs_qualitative) VALUES (?, 0)", (cid,))
        con.execute("INSERT INTO fsrs_cards (card_id, state, due, scheduled_days) "
                    "VALUES (?,?,?,?)", (cid, state, datetime.combine(due, datetime.min.time()), sched))
    con.commit()
    return con


def _rodar(cards):
    con = _conn(cards)
    try:
        return db.rebalancear_blackout(con, hoje=HOJE, dias_evitar=BLACKOUT, aplicar=False)
    finally:
        con.close()


def _ids(lista):
    return {x["card_id"] for x in lista}


# ---- o caso literal do F98 --------------------------------------------------

def test_card_em_RELEARNING_no_dia_da_prova_aparece_no_painel():
    """Nota 1 joga o card em state 3, e a consulta filtrava `state = 2`."""
    r = _rodar([(1, 3, PROVA, 2)])
    assert _ids(r["overflow"]) == {1}, (
        f"F98: card em relearning com due no dia da prova sumiu do painel -- {r}")


def test_card_em_LEARNING_no_dia_da_prova_aparece_no_painel():
    r = _rodar([(2, 1, PROVA, 1)])
    assert _ids(r["overflow"]) == {2}


def test_motivo_do_overflow_nomeia_o_estado(self=None):
    r = _rodar([(3, 3, PROVA, 2)])
    assert r["overflow"], "sem achado"
    assert "relearning" in r["overflow"][0]["motivo"].lower() or \
           "state" in r["overflow"][0]["motivo"].lower(), (
        f"motivo nao diz por que o card nao se move: {r['overflow'][0]['motivo']}")


def test_populacao_mista_aparece_inteira():
    """O caso da s183: notas 1 e 2 no mesmo bloco."""
    r = _rodar([(10, 3, PROVA, 2),                      # nota 1 -> relearning
                (11, 2, PROVA, 3),                      # nota 2 -> revisao curta
                (12, 2, PROVA + timedelta(days=1), 2)])  # dia seguinte
    assert _ids(r["overflow"]) == {10, 11, 12}, f"faltou card no painel: {r}"


# ---- o que NAO pode mudar (o contrato do F71) -------------------------------

def test_card_nao_movivel_FICA_onde_esta():
    """`AGENTE.md §6`: sem vaga na folga, fica onde esta. Mover seria violar o
    contrato -- e foi o erro da 1a tentativa desta sessao."""
    r = _rodar([(20, 3, PROVA, 2)])
    assert r["movidos"] == [], "empurrou card nao-movivel"
    assert r["escritos"] == 0


def test_card_de_revisao_com_folga_continua_sendo_MOVIDO():
    r = _rodar([(30, 2, PROVA, 10)])
    assert _ids(r["movidos"]) == {30}, f"regressao no caminho que ja funcionava: {r}"
    assert r["movidos"][0]["para"] < PROVA, "moveu para depois da prova"


def test_fora_do_blackout_ninguem_e_tocado():
    r = _rodar([(40, 3, PROVA - timedelta(days=10), 2),
                (41, 2, PROVA + timedelta(days=10), 8)])
    assert r["movidos"] == [] and r["overflow"] == []


# ---- invariantes de `escolher_dia` que o F98 nao pode alterar ---------------

def test_folga_segue_exigindo_intervalo_4():
    """Sem blackout em jogo, card curto nao se move por carga -- mover 1 dia num
    card de 2 dias e erro de 50%, e essa justificativa continua de pe."""
    alvo = date(2026, 10, 20)
    carga = {alvo: 99, alvo - timedelta(days=1): 0}
    assert fb.escolher_dia(alvo, 2, carga, HOJE, state=2, dias_evitar=BLACKOUT) == (alvo, 0)


def test_state_diferente_de_2_nao_entra_no_balanceador():
    assert fb.escolher_dia(PROVA, 2, {}, HOJE, state=3, dias_evitar=BLACKOUT) == (PROVA, 0)


# ---- paridade do record_review: BASELINE do R2 ------------------------------

def test_baseline_do_R2_intervalo_por_nota():
    """🔴 BASELINE PARA O R2, nao um teste de defeito.

    Congela a relacao entre as quatro notas sob a regua ATUAL, para que a mudanca
    do R2 (opcao (b), decidida pelo operador em 17/09) seja medida contra numero
    escrito, e nao contra memoria. Quando o R2 pousar, este teste MUDA -- e o diff
    dele e a evidencia do que a regua nova fez.

    Nao afirma que os numeros de hoje sao bons: o F112 mediu que a regua esta
    deslocada um degrau. Afirma apenas QUAIS SAO hoje, para poder comparar.
    """
    from fsrs import Card, Rating, Scheduler
    sched = Scheduler(learning_steps=())
    base = Card()
    base, _ = sched.review_card(base, Rating.Good)     # entra em revisao
    dias = {}
    for nome, rating in (("1-again", Rating.Again), ("2-hard", Rating.Hard),
                         ("3-good", Rating.Good), ("4-easy", Rating.Easy)):
        c, _ = sched.review_card(base, rating)
        dias[nome] = (c.due - base.due).days
    assert dias["1-again"] <= dias["2-hard"] <= dias["3-good"] <= dias["4-easy"], (
        f"ordem monotonica quebrada -- a regua nao e mais interpretavel: {dias}")
    assert dias["4-easy"] >= dias["2-hard"] * 2, (
        f"BASELINE do R2 medida em 18/09/2026: {dias}. O 4 agenda MUITO alem do 2, "
        "que e o F112 em uma linha. Se esta assercao cair, foi o R2 que mudou a "
        "regua -- atualize com o numero novo e cite o commit.")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
