"""Suite da aderencia planejado x real (spec telemetria-estudo-part-2).

classificar_dia e PURA (fixtures em memoria, sem db); aderencia() e testada
sobre db temporario. Trava anti-sycophancy provada: flags do plano nao mudam
a classificacao. Fixtures sinteticas (labels fake, zero conteudo clinico).

Executavel standalone (python tools/test_aderencia.py) e coletavel pelo pytest.
"""
import sqlite3
import sys
from datetime import date

import pytest

import app.utils.db as db
from tools.day_plan import (PLANO_DIA_DDL, aderencia, classificar_dia,
                            persistir_plano, realizado_do_dia)


def _bloco(ordem, tipo, qtd, alvo="Tema X", tempo_h=None, energia=None):
    return {"ordem": ordem, "task_tipo": tipo, "volume_planejado": qtd,
            "alvo_tema": alvo, "tempo_h": tempo_h, "energia": energia}


# --- classificar_dia (pura) ---

def test_cumprido_parcial_pulado():
    plano = [_bloco(1, "questoes", 40), _bloco(2, "fsrs", 30),
             _bloco(3, "simulado", 1)]
    real = {"questoes": 45, "cards": 10, "simulado": 0}
    r = classificar_dia(plano, real)
    por_tipo = {b["task_tipo"]: b["status"] for b in r["blocos"]}
    assert por_tipo == {"questoes": "cumprido", "fsrs": "parcial",
                        "simulado": "pulado"}


def test_pulado_quando_nada_realizado():
    r = classificar_dia([_bloco(1, "questoes", 20)],
                        {"questoes": 0, "cards": 0, "simulado": 0})
    assert r["blocos"][0]["status"] == "pulado"


def test_descanso_qtd_zero_e_cumprido_trivial():
    r = classificar_dia([_bloco(1, "descanso", 0, alvo=None)],
                        {"questoes": 0, "cards": 0, "simulado": 0})
    assert r["blocos"][0]["status"] == "cumprido"
    assert r["blocos"][0]["realizado"] is None  # sem medida; nunca fabricado


def test_alocacao_mini_drill_primeiro_na_familia_cards():
    plano = [_bloco(1, "mini-drill", 3), _bloco(2, "fsrs", 30)]
    r = classificar_dia(plano, {"questoes": 0, "cards": 5, "simulado": 0})
    md, fs = r["blocos"]
    assert md["status"] == "cumprido" and md["realizado"] == 3
    assert fs["status"] == "parcial" and fs["realizado"] == 2


def test_extra_realizado_sem_bloco_e_excedente():
    plano = [_bloco(1, "questoes", 10)]
    r = classificar_dia(plano, {"questoes": 25, "cards": 7, "simulado": 0})
    extras = {e["tipo"]: e["qtd"] for e in r["extra"]}
    assert extras == {"questoes": 15, "cards": 7}  # excedente + familia sem bloco


def test_anti_sycophancy_flags_nao_mudam_veredito():
    real = {"questoes": 5, "cards": 0, "simulado": 0}
    plano_a = [_bloco(1, "questoes", 20, tempo_h=1.0, energia="baixa")]
    plano_b = [_bloco(1, "questoes", 20, tempo_h=6.0, energia="alta")]
    ra, rb = classificar_dia(plano_a, real), classificar_dia(plano_b, real)
    assert ra["blocos"][0]["status"] == rb["blocos"][0]["status"] == "parcial"
    assert ra["blocos"][0]["realizado"] == rb["blocos"][0]["realizado"] == 5


# --- aderencia sobre db temporario ---

@pytest.fixture
def tmp_db(tmp_path, monkeypatch):
    caminho = str(tmp_path / "ipub.db")
    monkeypatch.setattr(db, "DB_PATH", caminho)
    con = sqlite3.connect(caminho)
    con.execute(PLANO_DIA_DDL)
    con.execute("CREATE TABLE sessoes_bulk (id INTEGER PRIMARY KEY, area TEXT, "
                "questoes_feitas INTEGER, data_sessao DATE)")
    con.execute("CREATE TABLE fsrs_revlog (id INTEGER PRIMARY KEY, "
                "review_time DATETIME)")
    con.commit()
    con.close()
    return caminho


def _plano_fake(data, blocos):
    return {"data": data,
            "recomendacao": {"blocos": blocos,
                             "contexto": {"tempo_h": 2.0, "energia": "media"},
                             "defaults_assumidos": False}}


def test_bloco_planejado_sem_realizacao_vira_pulado_no_dia_seguinte(tmp_db):
    ontem = date(2026, 7, 10)
    persistir_plano(_plano_fake("2026-07-10", [
        {"tipo": "questoes", "qtd": 30, "alvo": "Tema Y", "motivo": "m"}]))
    # relatorio "rodado em D+1" (fim = 2026-07-11), revlog/sessoes vazios
    dias = aderencia(fim=date(2026, 7, 11), semanas=1)
    dia = next(d for d in dias if d["data"] == ontem.isoformat())
    assert not dia["sem_plano"]
    assert dia["blocos"][0]["status"] == "pulado"  # sem input humano


def test_relatorio_deriva_so_do_db(tmp_db):
    persistir_plano(_plano_fake("2026-07-10", [
        {"tipo": "questoes", "qtd": 20, "alvo": "T", "motivo": "m"},
        {"tipo": "fsrs", "qtd": 10, "alvo": "fila", "motivo": "m"}]))
    con = sqlite3.connect(tmp_db)
    con.execute("INSERT INTO sessoes_bulk (area, questoes_feitas, data_sessao) "
                "VALUES ('Area F', 24, '2026-07-10')")
    for _ in range(4):
        con.execute("INSERT INTO fsrs_revlog (review_time) "
                    "VALUES ('2026-07-10 15:00:00')")
    con.commit()
    con.close()
    dias = aderencia(fim=date(2026, 7, 10), semanas=1)
    dia = next(d for d in dias if d["data"] == "2026-07-10")
    por_tipo = {b["task_tipo"]: (b["status"], b["realizado"]) for b in dia["blocos"]}
    assert por_tipo["questoes"] == ("cumprido", 20)
    assert por_tipo["fsrs"] == ("parcial", 4)
    extras = {e["tipo"]: e["qtd"] for e in dia["extra"]}
    assert extras == {"questoes": 4}


def test_dia_sem_plano_explicito_e_realizado_vira_extra(tmp_db):
    con = sqlite3.connect(tmp_db)
    con.execute("INSERT INTO sessoes_bulk (area, questoes_feitas, data_sessao) "
                "VALUES ('Area F', 12, '2026-07-09')")
    con.commit()
    con.close()
    dias = aderencia(fim=date(2026, 7, 9), semanas=1)
    dia = next(d for d in dias if d["data"] == "2026-07-09")
    assert dia["sem_plano"] is True and dia["blocos"] == []
    assert {e["tipo"]: e["qtd"] for e in dia["extra"]} == {"questoes": 12}


def test_simulado_nao_conta_como_questoes(tmp_db):
    con = sqlite3.connect(tmp_db)
    con.execute("INSERT INTO sessoes_bulk (area, questoes_feitas, data_sessao) "
                "VALUES ('Simulado', 100, '2026-07-08')")
    con.commit()
    real = realizado_do_dia(con, "2026-07-08")
    con.close()
    assert real == {"questoes": 0, "simulado": 1, "cards": 0}


def test_semana_vazia_nao_crasha(tmp_db):
    dias = aderencia(fim=date(2026, 7, 11), semanas=1)
    assert len(dias) == 7 and all(d["sem_plano"] for d in dias)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
