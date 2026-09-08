"""test_reforja_event_log.py — hotfix 2026-09-08 (s170): reforja executada deixa rastro.

Trava os DOIS caminhos de reescrita de flashcard (`db.update_flashcard_fields` e
`recurate_cards.aplicar`): reescrita que COMMITA emite exatamente 1 evento
`reforja` pos-commit; caminho que NAO commita (card inexistente, gate reprovado,
rollback do lote) emite ZERO -- sem isso nasce evento-fantasma.

Contratos preservados de `tools/event_log.py`: o evento carrega SO ids/contagens/
tags (nenhum texto clinico) e uma falha de log nunca derruba a escrita do card.

Tudo em db temp + log temp -- `ipub.db` e `history/generation_log.jsonl` reais
NUNCA sao tocados. Asserts nativos.
"""
import json
import os
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import pytest  # noqa: E402

import event_log  # noqa: E402
import recurate_cards  # noqa: E402
from app.utils import db  # noqa: E402

_DDL = """
CREATE TABLE flashcards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    questao_id INTEGER, tema_id INTEGER, tipo TEXT,
    frente_contexto TEXT, frente_pergunta TEXT, verso_resposta TEXT,
    verso_regra_mestre TEXT, verso_armadilha TEXT,
    quality_source TEXT DEFAULT 'legacy', card_version INTEGER DEFAULT 1,
    needs_qualitative INTEGER DEFAULT 0);
"""

# Conteudo que passa o gate de qualidade dos dois writers (encoding limpo, sem
# template banido, sem resposta embutida na frente).
_NOVA_PERGUNTA = "Qual o intervalo entre as doses de reforco?"
_NOVA_RESPOSTA = "Seis meses apos a primeira dose."


@pytest.fixture
def ambiente(tmp_path, monkeypatch):
    """DB temp com 1 card v1 + log de eventos temp. Devolve (db_path, log_path)."""
    db_path = str(tmp_path / "t.db")
    con = sqlite3.connect(db_path)
    con.executescript(_DDL)
    con.execute(
        "INSERT INTO flashcards (id, tipo, frente_pergunta, verso_resposta, "
        "quality_source, card_version) VALUES (1, 'conteudo', ?, ?, 'qualitative', 1)",
        ("Pergunta antiga?", "Resposta antiga."))
    con.commit()
    con.close()

    log_path = str(tmp_path / "generation_log.jsonl")
    monkeypatch.setattr(db, "DB_PATH", db_path)
    monkeypatch.setattr(event_log, "LOG_PATH", log_path)
    return db_path, log_path


def _eventos(log_path, tipo="reforja"):
    if not os.path.exists(log_path):
        return []
    linhas = [json.loads(l) for l in open(log_path, encoding="utf-8") if l.strip()]
    return [e for e in linhas if e.get("tipo") == tipo]


def _versao(db_path, cid=1):
    con = sqlite3.connect(db_path)
    try:
        return con.execute("SELECT card_version FROM flashcards WHERE id=?", (cid,)).fetchone()[0]
    finally:
        con.close()


# --- (i) reescrita que COMMITA -> exatamente 1 evento, pos-commit ------------

def test_update_flashcard_fields_emite_evento(ambiente):
    db_path, log_path = ambiente
    assert db.update_flashcard_fields(1, {"frente_pergunta": _NOVA_PERGUNTA}) is True

    evs = _eventos(log_path)
    assert len(evs) == 1, f"esperado 1 evento de reforja, veio {len(evs)}"
    ev = evs[0]
    assert ev["card_id"] == 1
    assert ev["writer"] == "db.update_flashcard_fields"
    assert ev["version_antes"] == 1
    assert ev["version_depois"] == 2 == _versao(db_path)
    assert ev["reason"]
    # contrato do event_log: so ids/contagens/tags, NUNCA texto clinico.
    assert _NOVA_PERGUNTA not in json.dumps(ev, ensure_ascii=False)


def test_recurate_aplicar_emite_evento(ambiente):
    db_path, log_path = ambiente
    plano = [("refazer", 1, {"frente_pergunta": _NOVA_PERGUNTA}, 1, "Pergunta antiga?")]
    con = sqlite3.connect(db_path)
    try:
        n_ref, _ = recurate_cards.aplicar(plano, con)
    finally:
        con.close()
    assert n_ref == 1

    evs = _eventos(log_path)
    assert len(evs) == 1, f"esperado 1 evento de reforja, veio {len(evs)}"
    ev = evs[0]
    assert ev["card_id"] == 1
    assert ev["writer"] == "recurate_cards"
    assert ev["version_antes"] == 1
    assert ev["version_depois"] == 2 == _versao(db_path)
    assert _NOVA_PERGUNTA not in json.dumps(ev, ensure_ascii=False)


# --- (ii) caminho que NAO commita -> ZERO eventos ---------------------------

def test_card_inexistente_nao_emite_evento(ambiente):
    _, log_path = ambiente
    assert db.update_flashcard_fields(999, {"frente_pergunta": _NOVA_PERGUNTA}) is False
    assert _eventos(log_path) == []


def test_gate_reprovado_nao_emite_evento(ambiente):
    db_path, log_path = ambiente
    # Seta unicode proibida (AGENTE.md 4.5) -> checar_encoding reprova e levanta
    # ANTES de abrir conexao: nao ha commit, logo nao pode haver evento.
    with pytest.raises(ValueError):
        db.update_flashcard_fields(1, {"verso_resposta": "Sobe → desce."})
    assert _eventos(log_path) == []
    assert _versao(db_path) == 1


def test_rollback_do_lote_nao_emite_evento(ambiente):
    db_path, log_path = ambiente
    # 2o item com coluna inexistente -> OperationalError no meio do lote ->
    # aplicar() faz rollback do lote INTEIRO. O 1o item nao pode ter deixado
    # evento: a emissao e pos-commit, e o commit nunca aconteceu.
    plano = [
        ("refazer", 1, {"frente_pergunta": _NOVA_PERGUNTA}, 1, "Pergunta antiga?"),
        ("refazer", 1, {"coluna_que_nao_existe": "x"}, 1, "Pergunta antiga?"),
    ]
    con = sqlite3.connect(db_path)
    try:
        with pytest.raises(sqlite3.OperationalError):
            recurate_cards.aplicar(plano, con)
    finally:
        con.close()
    assert _eventos(log_path) == []
    assert _versao(db_path) == 1


# --- contrato preservado: falha de log nao derruba a escrita ----------------

def test_falha_no_log_nao_derruba_a_escrita(ambiente, monkeypatch):
    db_path, _ = ambiente

    def _explode(*a, **kw):
        raise RuntimeError("disco cheio")

    monkeypatch.setattr(event_log, "registrar", _explode)
    # A escrita do card tem que sobreviver a um event_log quebrado.
    assert db.update_flashcard_fields(1, {"frente_pergunta": _NOVA_PERGUNTA}) is True
    assert _versao(db_path) == 2


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
