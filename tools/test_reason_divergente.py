"""Regressao F76 (hotfix 2026-09-09, s174): `--record --reason` divergente da proveniencia
real e AVISADO (stderr, nao bloqueia) e GRAVADO na propria linha do rating
(`fsrs_revlog.reason_servido`), consultavel por SQL -- o contador de gate-miss (B1) le dali.

Caso real (s167): #559 era `vencido` e foi gravado como `agendado`; o revlog mentia e nada
media. Fixtures em db temp (schema canonico via init_db); relogio congelado; nada toca o
`ipub.db` real.
"""
import contextlib
import io
import json
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from app.utils import db  # noqa: E402
import init_db  # noqa: E402
import fsrs_queue  # noqa: E402

AGORA = datetime(2026, 9, 9, 15, 0, 0)
ONTEM = AGORA - timedelta(days=1)
HOJE_10H = AGORA.replace(hour=10)
AMANHA = AGORA + timedelta(days=1)
FMT = "%Y-%m-%d %H:%M:%S"


@pytest.fixture
def banco(tmp_path, monkeypatch):
    caminho = str(tmp_path / "ipub.db")
    monkeypatch.setattr(init_db, "DB_PATH", caminho)
    with contextlib.redirect_stdout(io.StringIO()):
        init_db.init_db()
    monkeypatch.setattr(db, "DB_PATH", caminho)
    monkeypatch.setattr(db, "agora", lambda: AGORA)
    con = sqlite3.connect(caminho)
    con.execute("INSERT INTO taxonomia_cronograma (id, area, tema) VALUES (1, 'Cirurgia', 'T')")
    con.execute("INSERT INTO questoes_erros (id, tema_id, titulo, data_registro) "
                "VALUES (1, 1, 'q', ?)", (ONTEM.strftime(FMT),))
    linhas = [  # id, questao_id, state, due
        (1, None, 2, ONTEM),      # vencido
        (2, None, 2, HOJE_10H),   # agendado
        (3, 1, 0, ONTEM),         # fresh_error (erro, state 0, <48h)
        (4, None, 0, ONTEM),      # novo (sem questao_id)
        (5, None, 2, AMANHA),     # futuro (fora de qualquer bucket)
    ]
    for cid, qid, st, due in linhas:
        con.execute("INSERT INTO flashcards (id, questao_id, tema_id, tipo, frente_pergunta, "
                    "verso_resposta, quality_source) VALUES (?, ?, 1, 'conteudo', 'P?', 'R.', "
                    "'qualitative')", (cid, qid))
        con.execute("INSERT INTO fsrs_cards (card_id, state, due, stability, difficulty, "
                    "scheduled_days, last_review) VALUES (?, ?, ?, 5.0, 5.0, 10, ?)",
                    (cid, st, due.strftime(FMT),
                     (due - timedelta(days=10)).strftime(FMT) if st else None))
    con.commit()
    con.close()
    return caminho


def _linha(caminho, card_id):
    con = sqlite3.connect(caminho)
    try:
        return con.execute("SELECT selection_reason, reason_servido FROM fsrs_revlog "
                           "WHERE card_id = ? ORDER BY id DESC LIMIT 1", (card_id,)).fetchone()
    finally:
        con.close()


def _cli(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        sys.argv = ["fsrs_queue.py"] + argv
        try:
            fsrs_queue.main()
        except SystemExit as e:
            if e.code not in (0, None):
                raise
    return out.getvalue(), err.getvalue()


def test_bucket_de_e_puro_e_cobre_os_cinco_casos():
    b = db.bucket_de
    assert b(2, ONTEM, None, AGORA) == "vencido"
    assert b(2, HOJE_10H, None, AGORA) == "agendado"
    assert b(0, ONTEM, 1, AGORA) == "fresh_error"
    assert b(0, ONTEM - timedelta(days=5), 1, AGORA) == "novo"      # erro velho = novo
    assert b(0, ONTEM, None, AGORA) == "novo"
    assert b(2, AMANHA, None, AGORA) == "futuro"


def test_caso_real_vencido_gravado_como_agendado_e_avisado_e_gravado(banco):
    m = db.record_review(1, 3, selection_reason="agendado")
    assert m["reason_servido"] == "vencido" and m["reason_divergente"] is True
    assert _linha(banco, 1) == ("agendado", "vencido")


def test_reason_coerente_nao_diverge(banco):
    m = db.record_review(2, 3, selection_reason="agendado")
    assert m["reason_divergente"] is False
    assert _linha(banco, 2) == ("agendado", "agendado")


def test_pre_bloco_sobre_erro_fresco_nao_e_divergencia(banco):
    m = db.record_review(3, 4, selection_reason="pre_bloco")
    assert m["reason_servido"] == "fresh_error" and m["reason_divergente"] is False
    assert _linha(banco, 3) == ("pre_bloco", "fresh_error")


def test_reason_auto_grava_o_recomputado(banco):
    m = db.record_review(4, 3, selection_reason="auto")
    assert m["reason_divergente"] is False
    assert _linha(banco, 4) == ("novo", "novo")


def test_sem_reason_nao_e_divergencia_mas_servido_fica(banco):
    m = db.record_review(5, 3)
    assert m["reason_servido"] == "futuro" and m["reason_divergente"] is False
    assert _linha(banco, 5) == (None, "futuro")


def test_cli_avisa_em_stderr_e_mantem_stdout_json(banco):
    out, err = _cli(["--record", "1", "--rating", "3", "--reason", "agendado"])
    payload = json.loads(out)
    assert payload["recorded"] is True and payload["reason_servido"] == "vencido"
    assert payload["reason_divergente"] is True
    assert "[WARN] reason divergente" in err and "servido=vencido" in err and "recebido=agendado" in err


def test_cli_coerente_sem_warn(banco):
    out, err = _cli(["--record", "2", "--rating", "3", "--reason", "agendado"])
    assert json.loads(out)["reason_divergente"] is False
    assert "reason divergente" not in err


def test_divergencia_e_consultavel_por_sql(banco):
    db.record_review(1, 3, selection_reason="agendado")   # divergente
    db.record_review(2, 3, selection_reason="agendado")   # coerente
    db.record_review(5, 3)                                # sem reason
    con = sqlite3.connect(banco)
    try:
        n = con.execute("SELECT COUNT(*) FROM fsrs_revlog WHERE selection_reason IS NOT NULL "
                        "AND reason_servido IS NOT NULL AND selection_reason != reason_servido "
                        "AND NOT (selection_reason = 'pre_bloco' AND reason_servido IN "
                        "('fresh_error', 'novo'))").fetchone()[0]
    finally:
        con.close()
    assert n == 1


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
