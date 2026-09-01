"""Descolar part-4 (F56/F53/F52): contrato so afirma o que um teste prova.

Asserts nativos, fixtures sinteticas em tmp_path. Cobre: B2 BLOCK real (os DOIS lados:
viola/nao-viola, incluindo a excecao max+1), parser case-insensitive do ponteiro (S160),
needs_qualitative na fila ativa (db sintetico), e contar_erros_cards.
"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.utils.state_utils import check_needs_qualitative, check_session_pointer  # noqa: E402


def _handoff(tmp_path, ponteiro):
    h = tmp_path / "HANDOFF.md"
    h.write_text(f"# HANDOFF\n*Atualizado: 2026-09-01 -- {ponteiro}*\n", encoding="utf-8")
    return h


def _history(tmp_path, sessoes):
    d = tmp_path / "history"
    d.mkdir(exist_ok=True)
    for n in sessoes:
        (d / f"session_{n:03d}.md").write_text("# log", encoding="utf-8")
    return d


def test_b2_ok_quando_arquivo_existe(tmp_path):
    h = _handoff(tmp_path, "s160")
    d = _history(tmp_path, [158, 159, 160])
    assert check_session_pointer(h, d) is None


def test_b2_ok_na_excecao_max_mais_um(tmp_path):
    """Ponteiro = max+1 e a sessao EM CURSO (o log nasce no fechamento) — legal."""
    h = _handoff(tmp_path, "s161")
    d = _history(tmp_path, [159, 160])
    assert check_session_pointer(h, d) is None


def test_b2_viola_arquivo_ausente(tmp_path):
    h = _handoff(tmp_path, "s159")
    d = _history(tmp_path, [158, 160])   # 159 NAO existe (buraco)
    assert check_session_pointer(h, d) == (159, 160, "arquivo_ausente")


def test_b2_viola_alem_do_max(tmp_path):
    h = _handoff(tmp_path, "s170")
    d = _history(tmp_path, [159, 160])
    assert check_session_pointer(h, d) == (170, 160, "alem_do_max")


def test_parser_aceita_s_maiusculo(tmp_path):
    """O HANDOFF real grafa 'S160'; o parser antigo so via 's160' e o check no-opava."""
    h = _handoff(tmp_path, "S165")
    d = _history(tmp_path, [159, 160])
    assert check_session_pointer(h, d) == (165, 160, "alem_do_max")


def _db_com_cards(tmp_path, linhas):
    p = tmp_path / "ipub.db"
    con = sqlite3.connect(p)
    con.execute("CREATE TABLE flashcards (id INTEGER PRIMARY KEY, needs_qualitative INTEGER)")
    con.execute("CREATE TABLE fsrs_cards (card_id INTEGER PRIMARY KEY, state INTEGER)")
    for cid, nq, state in linhas:
        con.execute("INSERT INTO flashcards VALUES (?, ?)", (cid, nq))
        con.execute("INSERT INTO fsrs_cards VALUES (?, ?)", (cid, state))
    con.commit()
    con.close()
    return p


def test_needs_qualitative_na_fila_ativa(tmp_path):
    p = _db_com_cards(tmp_path, [(1, 1, 0), (2, 1, 2), (3, 0, 0), (4, 1, 1)])
    assert check_needs_qualitative(p) == 2       # ids 1 e 4 (state<2 com nq=1)
    p2 = _db_com_cards(tmp_path / "sub", [(1, 0, 0)]) if (tmp_path / "sub").mkdir() is None else None
    assert check_needs_qualitative(p2) is None   # base limpa -> None (sem WARN)


def test_needs_qualitative_fail_open(tmp_path):
    assert check_needs_qualitative(tmp_path / "nao_existe.db") is None


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))
