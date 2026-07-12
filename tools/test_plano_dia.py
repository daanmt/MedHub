"""Suite da persistencia do plano do dia (spec telemetria-estudo-part-1).

Cobre: persistencia dos blocos com flags do run, idempotencia por dia
(delete+insert substitui, nunca acumula), leitura ordenada (ler_plano),
schema sem coluna de texto clinico e resiliencia (db indisponivel -> WARN,
plano segue). Fixtures 100%% sinteticas: labels/ids fake, zero conteudo real.

Executavel standalone (python tools/test_plano_dia.py) e coletavel pelo pytest.
"""
import sqlite3
import sys

import pytest

import app.utils.db as db
from tools.day_plan import ler_plano, persistir_plano

COLS_PERMITIDAS = {"id", "data", "ordem", "task_tipo", "alvo_tema",
                   "volume_planejado", "tempo_h", "energia",
                   "defaults_assumidos", "criado_em"}


def _plano_fake(data="2026-07-12", blocos=None, tempo_h=2.0, energia="baixa",
                defaults=False):
    if blocos is None:
        blocos = [
            {"tipo": "mini-drill", "qtd": 3, "alvo": "Tema A", "motivo": "m"},
            {"tipo": "questoes", "qtd": 40, "alvo": "Tema B", "motivo": "m"},
            {"tipo": "fsrs", "qtd": 30, "alvo": "fila do dia", "motivo": "m"},
        ]
    return {"data": data,
            "recomendacao": {"blocos": blocos,
                             "contexto": {"tempo_h": tempo_h, "energia": energia,
                                          "capacidade_q": 60},
                             "defaults_assumidos": defaults}}


@pytest.fixture
def tmp_db(tmp_path, monkeypatch):
    caminho = str(tmp_path / "ipub.db")
    monkeypatch.setattr(db, "DB_PATH", caminho)
    return caminho


def test_persiste_blocos_com_flags_do_run(tmp_db):
    persistir_plano(_plano_fake())
    rows = ler_plano("2026-07-12")
    assert len(rows) == 3
    assert [r["task_tipo"] for r in rows] == ["mini-drill", "questoes", "fsrs"]
    assert rows[0]["volume_planejado"] == 3 and rows[1]["alvo_tema"] == "Tema B"
    assert rows[0]["tempo_h"] == 2.0 and rows[0]["energia"] == "baixa"
    assert rows[0]["defaults_assumidos"] == 0 and rows[0]["criado_em"]


def test_re_run_mesmo_dia_substitui_nunca_acumula(tmp_db):
    persistir_plano(_plano_fake())
    persistir_plano(_plano_fake(blocos=[
        {"tipo": "descanso", "qtd": 0, "alvo": None, "motivo": "m"}]))
    rows = ler_plano("2026-07-12")
    assert len(rows) == 1  # substituiu os 3 blocos; zero orfaos
    assert rows[0]["task_tipo"] == "descanso" and rows[0]["alvo_tema"] is None


def test_dias_diferentes_coexistem(tmp_db):
    persistir_plano(_plano_fake(data="2026-07-12"))
    persistir_plano(_plano_fake(data="2026-07-13"))
    assert len(ler_plano("2026-07-12")) == 3
    assert len(ler_plano("2026-07-13")) == 3


def test_leitura_ordenada_por_ordem(tmp_db):
    persistir_plano(_plano_fake())
    assert [r["ordem"] for r in ler_plano("2026-07-12")] == [1, 2, 3]


def test_schema_sem_coluna_de_texto_clinico(tmp_db):
    persistir_plano(_plano_fake())
    con = sqlite3.connect(tmp_db)
    cols = {r[1] for r in con.execute("PRAGMA table_info(plano_dia)")}
    con.close()
    assert cols == COLS_PERMITIDAS  # ids/enums/contadores/flags apenas


def test_defaults_assumidos_registrado(tmp_db):
    persistir_plano(_plano_fake(defaults=True, tempo_h=3.0, energia="media"))
    rows = ler_plano("2026-07-12")
    assert all(r["defaults_assumidos"] == 1 for r in rows)


def test_data_sem_plano_retorna_vazio(tmp_db):
    assert ler_plano("2099-01-01") == []


def test_falha_de_db_warn_e_nao_lanca(monkeypatch, capsys):
    def _explode():
        raise RuntimeError("db indisponivel")
    monkeypatch.setattr(db, "get_connection", _explode)
    try:
        persistir_plano(_plano_fake())  # nao pode lancar
    finally:
        pass
    assert "PLANO_DIA" in capsys.readouterr().out


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
