"""F113 (2a parte): o gate de atomicidade ganha ESCOPO DE INTENÇÃO.

Escrito ANTES do fix (AGENTE.md 10.6). Medido em 17/09/2026, no lote de restauração
de acentuação: `recurate_cards.py` reprovou **125 cards** com a mensagem *"reforja(s)
NÃO resolveram o defeito"* e matou o lote inteiro (ALL-OR-NOTHING). Mas a edição era
**só-acento** -- ela nunca se propôs a resolver atomicidade, e provadamente não a
altera em nenhuma direção.

🔴 A CLASSE: **gate sem escopo de intenção**. Os gates 4 e 6 perguntam *"a reforja
resolveu mesmo o defeito?"*, assumindo que toda edição que passa por este CLI é uma
reforja. Aplicado a uma edição que não mira defeito nenhum, o gate não mede o que
pensa medir -- é a mesma família do `cli_signature_check` casando flag por presença de
string ("string presente != coberto"). Série §10.8.

O invariante que dá o escopo: se `unidecode(antes) == unidecode(depois)` em **todo**
campo alterado, o texto é o mesmo a menos de acentuação. Uma mudança assim não pode
criar nem resolver pergunta composta, verso multifato ou contrafactual mal-formado.
A isenção é **verificada por item, nunca declarada por flag** -- flag se usa errado;
invariante se prova.
"""

import os
import sqlite3
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))

import recurate_cards  # noqa: E402

_DDL = """
CREATE TABLE flashcards (id INTEGER PRIMARY KEY, tipo TEXT, frente_contexto TEXT,
  frente_pergunta TEXT, verso_resposta TEXT, verso_regra_mestre TEXT,
  verso_armadilha TEXT, quality_source TEXT, needs_qualitative INTEGER,
  card_version INTEGER);
"""

# frente COMPOSTA de proposito: este card ja e nao-atomico HOJE, e continua sendo
# depois da edicao. E exatamente a populacao dos 125 que o gate travou.
_FRENTE_COMPOSTA = "Qual droga, dose e duracao -- e o que a gestacao muda nessa escolha?"
_FRENTE_ACENTUADA = "Qual droga, dose e duração -- e o que a gestação muda nessa escolha?"
_VERSO = "Azitromicina 1 g VO dose unica."


def _conn(tmp_path):
    con = sqlite3.connect(str(tmp_path / "t.db"))
    con.executescript(_DDL)
    con.execute(
        "INSERT INTO flashcards (id, tipo, frente_pergunta, verso_resposta, "
        "quality_source, card_version) VALUES (1, 'conteudo', ?, ?, 'qualitative', 3)",
        (_FRENTE_COMPOSTA, _VERSO))
    con.commit()
    return con


def _avisos(con, edit):
    _erros, avisos, _plano = recurate_cards.validar([edit], con)
    return avisos


# ---- o caso literal do F113 --------------------------------------------------

def test_edicao_so_acento_nao_dispara_gate_de_atomicidade(tmp_path):
    """Os 125 do lote B: card ja nao-atomico, edicao que so repoe acento."""
    con = _conn(tmp_path)
    try:
        avisos = _avisos(con, {"card_id": 1, "frente_pergunta": _FRENTE_ACENTUADA})
        assert not avisos, (
            "gate sem escopo de intencao: edicao so-acento foi cobrada por nao "
            f"'resolver' um defeito que ela nunca mirou -- {avisos}")
    finally:
        con.close()


def test_edicao_so_acento_e_APLICAVEL(tmp_path):
    """Nao basta calar o aviso: o item tem de entrar no plano."""
    con = _conn(tmp_path)
    try:
        erros, avisos, plano = recurate_cards.validar(
            [{"card_id": 1, "frente_pergunta": _FRENTE_ACENTUADA}], con)
        assert not erros and not avisos
        assert len(plano) == 1 and plano[0][1] == 1
    finally:
        con.close()


# ---- o gate NAO pode ficar cego ---------------------------------------------

def test_edicao_semantica_no_mesmo_card_segue_cobrada(tmp_path):
    """Muda o texto de verdade e ainda deixa a frente composta -> aviso fica."""
    con = _conn(tmp_path)
    try:
        nova = "Qual antibiotico e qual dose -- e a gestacao muda a escolha?"
        avisos = _avisos(con, {"card_id": 1, "frente_pergunta": nova})
        assert avisos, "o gate 4 nao pode ficar cego para reforja que nao resolveu"
    finally:
        con.close()


def test_acento_MAIS_uma_palavra_nao_ganha_isencao(tmp_path):
    """A isencao e do invariante, nao da intencao declarada: se mudou mais que
    acento, o item volta a ser tratado como reforja comum."""
    con = _conn(tmp_path)
    try:
        nova = _FRENTE_ACENTUADA.replace("droga", "medicacao")
        avisos = _avisos(con, {"card_id": 1, "frente_pergunta": nova})
        assert avisos, "edicao com mudanca semantica foi isentada indevidamente"
    finally:
        con.close()


def test_isencao_vale_por_ITEM_nao_por_lote(tmp_path):
    """Lote misto: o so-acento passa, o semantico e cobrado."""
    con = _conn(tmp_path)
    try:
        con.execute(
            "INSERT INTO flashcards (id, tipo, frente_pergunta, verso_resposta, "
            "quality_source, card_version) VALUES (2, 'conteudo', ?, ?, 'qualitative', 1)",
            (_FRENTE_COMPOSTA, _VERSO))
        con.commit()
        _erros, avisos, _plano = recurate_cards.validar(
            [{"card_id": 1, "frente_pergunta": _FRENTE_ACENTUADA},
             {"card_id": 2, "frente_pergunta": "Qual droga e dose -- e a gestacao?"}], con)
        assert avisos, "o item semantico devia ser cobrado"
        assert all("card 1" not in a for a in avisos), (
            f"o item so-acento foi cobrado junto: {avisos}")
    finally:
        con.close()


def test_invariante_cobre_todos_os_campos_editados(tmp_path):
    """Se QUALQUER campo do item muda alem de acento, o item inteiro perde a isencao."""
    con = _conn(tmp_path)
    try:
        avisos = _avisos(con, {"card_id": 1,
                               "frente_pergunta": _FRENTE_ACENTUADA,
                               "verso_resposta": "Azitromicina 2 g VO dose única."})
        assert avisos, "mudanca de dose no verso passou como 'so acento'"
    finally:
        con.close()


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
