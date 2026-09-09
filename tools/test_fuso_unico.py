"""Regressao F80 (hotfix 2026-09-09, s174): TODO writer de carimbo do `ipub.db` passa pelo
relogio unico `db.agora()` (naive LOCAL, a zona canonica -- a mesma que o nucleo FSRS ja usa).

Caso real (s169): as 21:30 locais o `fsrs_revlog` e o `questoes_erros` carimbaram
`2026-09-08 00:2x` (DEFAULT CURRENT_TIMESTAMP = UTC) e o `sessoes_bulk` carimbou
`2026-09-07` (local): quem leu o banco concluiu que "a sessao cruzou a meia-noite". Nao cruzou.

Tres provas: (1) instante CONGELADO -> os 4 writers gravam o mesmo carimbo; (2) o leitor que
junta revlog x sessoes_bulk (`day_plan.realizado_do_dia`) ve tudo no mesmo dia; (3) varredura
estrutural: nenhum INSERT nas 4 tabelas omite a coluna de carimbo (um writer novo que dependa
do DEFAULT do SQLite falha aqui, nomeando o arquivo).

Fixtures: schema canonico via `init_db` em tmp_path; `db.agora` monkeypatchado. Zero contato
com o `ipub.db` real.
"""
import contextlib
import io
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from app.utils import db  # noqa: E402
import init_db  # noqa: E402
import insert_questao as iq  # noqa: E402
import registrar_sessao_bulk as rsb  # noqa: E402
import day_plan  # noqa: E402

CONGELADO = datetime(2026, 9, 7, 21, 30, 0)     # 21:30 local = 00:30 UTC do dia seguinte (BRT)
CARIMBO = "2026-09-07 21:30:00"


@pytest.fixture
def banco(tmp_path, monkeypatch):
    caminho = str(tmp_path / "ipub.db")
    monkeypatch.setattr(init_db, "DB_PATH", caminho)
    with contextlib.redirect_stdout(io.StringIO()):
        init_db.init_db()
    for mod in (db, iq, rsb):
        monkeypatch.setattr(mod, "DB_PATH", caminho)
    monkeypatch.setattr(db, "agora", lambda: CONGELADO)
    con = sqlite3.connect(caminho)
    con.execute("INSERT INTO taxonomia_cronograma (id, area, tema) VALUES (1, 'Cirurgia', 'Apendicite Aguda')")
    con.execute("INSERT INTO flashcards (id, tema_id, tipo, frente_pergunta, verso_resposta, "
                "quality_source) VALUES (1, 1, 'conteudo', 'P?', 'R.', 'qualitative')")
    con.execute("INSERT INTO fsrs_cards (card_id, state, due) VALUES (1, 0, '2026-09-01 10:00:00')")
    con.commit()
    con.close()
    return caminho


def _um(caminho, sql):
    con = sqlite3.connect(caminho)
    try:
        return con.execute(sql).fetchone()[0]
    finally:
        con.close()


def _silencio(fn):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn()


def test_relogio_unico_existe_e_e_local_naive():
    agora = db.agora()
    assert isinstance(agora, datetime) and agora.tzinfo is None
    assert abs((agora - datetime.now()).total_seconds()) < 5
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", db.carimbo())


def test_quatro_writers_no_mesmo_instante_congelado(banco):
    _silencio(lambda: db.record_review(1, 3, selection_reason="vencido"))
    _silencio(lambda: iq.insert_questao(area="Cirurgia", tema="Apendicite Aguda",
                                 enunciado="Caso com detalhes suficientes.",
                                 correta="Apendicectomia", chamada="Antibiotico isolado",
                                 erro="Conceitual", elo="indicacao cirurgica na apendicite",
                                 armadilha="melhora parcial com ATB",
                                 cards=[{"tipo": "conteudo",
                                         "frente_contexto": "Paciente com dor em FID ha 24 h.",
                                         "frente_pergunta": "Qual a conduta definitiva?",
                                         "verso_resposta": "Apendicectomia.",
                                         "verso_regra_mestre": "Apendicite = cirurgia.",
                                         "verso_armadilha": "ATB isolado nao resolve."}]))
    _silencio(lambda: db.log_review(tema_id=1, kind="directed_review", note="t"))
    _silencio(lambda: rsb.registrar(999, "Cirurgia", 10, 8))

    assert _um(banco, "SELECT review_time FROM fsrs_revlog WHERE card_id = 1") == CARIMBO
    assert _um(banco, "SELECT data_registro FROM questoes_erros ORDER BY id DESC LIMIT 1") == CARIMBO
    assert _um(banco, "SELECT reviewed_at FROM review_log ORDER BY id DESC LIMIT 1") == CARIMBO
    assert _um(banco, "SELECT data_sessao FROM sessoes_bulk WHERE sessao_num = 999") == "2026-09-07"


def test_leitor_que_junta_revlog_x_sessoes_bulk_ve_o_mesmo_dia(banco):
    _silencio(lambda: db.record_review(1, 3))
    _silencio(lambda: rsb.registrar(999, "Cirurgia", 10, 8))
    con = sqlite3.connect(banco)
    try:
        r = day_plan.realizado_do_dia(con, "2026-09-07")
        r_seguinte = day_plan.realizado_do_dia(con, "2026-09-08")
    finally:
        con.close()
    assert (r["cards"], r["questoes"]) == (1, 10), r
    assert (r_seguinte["cards"], r_seguinte["questoes"]) == (0, 0), "cruzou a meia-noite fantasma"


def test_data_explicita_no_bulk_continua_vencendo(banco):
    _silencio(lambda: rsb.registrar(998, "Cirurgia", 5, 4, data="2026-08-30"))
    assert _um(banco, "SELECT data_sessao FROM sessoes_bulk WHERE sessao_num = 998") == "2026-08-30"


# --------------------------------------------------------------------------
# Estrutural: nenhum INSERT nas tabelas de carimbo omite a coluna
# --------------------------------------------------------------------------
COLUNA_DE = {"fsrs_revlog": "review_time", "questoes_erros": "data_registro",
             "review_log": "reviewed_at", "sessoes_bulk": "data_sessao"}
_INSERT = re.compile(r"INSERT\s+(?:OR\s+\w+\s+)?INTO\s+(\w+)\s*\(([^)]*)\)", re.I | re.S)


def _writers():
    for base in ("tools", "app"):
        for f in (ROOT / base).rglob("*.py"):
            rel = f.relative_to(ROOT).as_posix()
            if "_archive" in rel or "__pycache__" in rel or f.name.startswith("test_"):
                continue
            yield rel, f.read_text(encoding="utf-8-sig", errors="replace")


def test_nenhum_insert_depende_do_default_do_sqlite():
    faltas = []
    for rel, texto in _writers():
        for m in _INSERT.finditer(texto):
            tabela = m.group(1).lower()
            if tabela not in COLUNA_DE:
                continue
            colunas = {c.strip().lower() for c in m.group(2).split(",")}
            if COLUNA_DE[tabela] not in colunas:
                faltas.append(f"{rel}: INSERT INTO {tabela} sem `{COLUNA_DE[tabela]}` "
                              f"(cairia no DEFAULT CURRENT_TIMESTAMP = UTC)")
    assert not faltas, "F80: writer de carimbo fora do relogio unico:\n  " + "\n  ".join(faltas)


def test_varredura_reconhece_os_writers_conhecidos():
    """Contra-prova: o scanner VE os 4 writers (senao o teste acima passaria por cegueira)."""
    vistos = set()
    for rel, texto in _writers():
        for m in _INSERT.finditer(texto):
            if m.group(1).lower() in COLUNA_DE:
                vistos.add((rel, m.group(1).lower()))
    assert {("app/utils/db.py", "fsrs_revlog"), ("app/utils/db.py", "review_log"),
            ("tools/insert_questao.py", "questoes_erros"),
            ("tools/registrar_sessao_bulk.py", "sessoes_bulk")} <= vistos, vistos


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
