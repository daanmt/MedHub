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
import pathlib
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_ratchet_verso import _conn  # noqa: E402  -- mesma fixture do gemeo F84
ROOT = pathlib.Path(__file__).resolve().parent.parent

from app.utils import db  # noqa: E402


def _versao(tmp_path):
    con = sqlite3.connect(str(tmp_path / "t.db"))
    try:
        return con.execute("SELECT card_version FROM flashcards WHERE id=1").fetchone()[0]
    finally:
        con.close()


def test_gate_indisponivel_derruba_o_IMPORT_do_db(tmp_path):
    """⚰️ **Era `test_card_checks_indisponivel_recusa_qualquer_reescrita`.**

    Ate 17/09/2026 o gate era importado LAZY, dentro do writer, montando
    `sys.path` com `__file__` para achar `tools/` -- e o teste simulava a
    indisponibilidade com `sys.modules["card_checks"] = None`, esperando um
    `RuntimeError` por chamada.

    No 1.9a a seta foi invertida: `app/utils/db.py` importa
    `app.utils.card_checks` no TOPO. O estado "gate ausente e o writer decide o
    que fazer" deixou de existir -- se o gate nao carrega, **o proprio `db` nao
    importa**, e nenhum writer roda. A garantia do F85 ficou mais forte, e o
    teste tinha que subir junto: em vez de provar uma excecao por chamada, prova
    que a falha acontece **antes**, no import.

    Roda em SUBPROCESSO de proposito: envenenar o import de um modulo ja
    carregado neste processo nao reproduz o boot real.
    """
    codigo = (
        "import sys\n"
        "sys.modules['app.utils.card_checks'] = None\n"
        "import app.utils.db\n"
    )
    r = subprocess.run([sys.executable, "-X", "utf8", "-c", codigo],
                       cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8")
    assert r.returncode != 0, (
        "`import app.utils.db` passou com o gate quebrado -- fail-open no boot. "
        f"stdout={r.stdout!r}")
    assert "card_checks" in (r.stderr or ""), r.stderr


def test_db_nao_alcanca_tools_por_sys_path(tmp_path):
    """1.9a: a cirurgia de `sys.path` com `__file__` nao pode voltar.

    Guarda estrutural. `DB_PATH` usa `__file__` legitimamente (e a raiz do
    repo); o que morreu foi montar caminho ate `tools/` para importar gate.
    """
    fonte = inspect.getsource(db)
    for morto in ("sys.path.insert(0, _tools", "import card_checks as _cc\n    ",
                  "from audit_card_atomicity import"):
        assert morto not in fonte, f"cirurgia de sys.path de volta em db.py: {morto!r}"
    assert "from app.utils import card_checks as _cc" in fonte
    assert "from app.utils.card_atomicity import" in fonte


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
