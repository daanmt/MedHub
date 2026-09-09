"""Regressao F85 (hotfix 2026-09-09, s174): o gate de qualidade de `update_flashcard_fields`
nao pode ser fail-open. Se `card_checks` nao importa, a reescrita e RECUSADA (mesma forma do
gemeo F84, o ratchet do verso, na mesma funcao).

O `except` antigo era governado por uma justificativa orfa ("o app nao pode quebrar sem
tools/") cujo objeto -- a UI Streamlit -- foi removido. Reachability-Debt variante 3: le uma
razao que ja nao existe. Tudo em db temp; `ipub.db` real nunca e tocado.
"""
import contextlib
import inspect
import io
import os
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_ratchet_verso import _conn  # noqa: E402  -- mesma fixture do gemeo F84
from app.utils import db  # noqa: E402


def _versao(tmp_path):
    con = sqlite3.connect(str(tmp_path / "t.db"))
    try:
        return con.execute("SELECT card_version FROM flashcards WHERE id=1").fetchone()[0]
    finally:
        con.close()


def test_card_checks_indisponivel_recusa_qualquer_reescrita(tmp_path, monkeypatch):
    con = _conn(tmp_path)
    con.close()
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "t.db"))
    monkeypatch.setitem(sys.modules, "card_checks", None)   # -> ImportError
    antes = _versao(tmp_path)
    out = io.StringIO()
    with contextlib.redirect_stdout(out), pytest.raises(RuntimeError, match="RECUSADA"):
        db.update_flashcard_fields(1, {"frente_pergunta": "Qual o proximo passo?"})
    assert _versao(tmp_path) == antes, "fail-open: gravou sem gate"
    assert out.getvalue() == "", f"nada em stdout (contrato JSON dos CLIs); veio {out.getvalue()!r}"


def test_justificativa_orfa_removida():
    fonte = inspect.getsource(db.update_flashcard_fields)
    for morto in ("não pode quebrar sem tools", "nao pode quebrar sem tools",
                  "degradação anunciada", "degradacao anunciada", "reescrita sem gate"):
        assert morto not in fonte, f"justificativa orfa ainda governa o except: {morto!r}"


def test_claim_envelhecido_do_fsrs_queue_removido():
    """Classe 2 do F85: docstring citando o player Streamlit (removido)."""
    import fsrs_queue
    assert "Streamlit" not in (fsrs_queue.__doc__ or "")


def test_gate_disponivel_segue_reprovando_conteudo_ruim(tmp_path, monkeypatch):
    """Preservacao: com card_checks vivo, o gate continua sendo ValueError, nao RuntimeError."""
    con = _conn(tmp_path)
    con.close()
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "t.db"))
    with pytest.raises(ValueError, match="gate de qualidade"):
        db.update_flashcard_fields(1, {"frente_pergunta": "   "})


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
