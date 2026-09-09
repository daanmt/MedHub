"""Regressao F88 (hotfix 2026-09-09, s174; destilado A5 + rider b do /ai-eng): UMA funcao
de calculo para "acumulado / meta / faltam / ritmo" chamada pelo boot (`day_plan`) e pelo
`cronograma --gap`, e UM leitor de `core/provas.json` para toda a camada.

Caso real: `--gap` imprimia meta 10.000 (literal de argparse envelhecido desde a s126) e
acumulado 6.305 (escopo que excluia Simulado) enquanto o `day_plan` do mesmo instante
imprimia 10.400 / 7.036 lidos do db. Dois leitores dos mesmos arquivos, duas contas (G4).

Fixtures sinteticas: db em tmp_path com linhas de area clinica E de Simulado; grade minima
em memoria. O `ipub.db` real nao e tocado.
"""
import ast
import inspect
import sqlite3
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import performance  # noqa: E402
import cronograma  # noqa: E402
import day_plan  # noqa: E402

HOJE = date(2026, 1, 10)


def _db(tmp_path):
    con = sqlite3.connect(tmp_path / "ipub.db")
    con.executescript("""
        CREATE TABLE sessoes_bulk (
            id INTEGER PRIMARY KEY AUTOINCREMENT, sessao_num INTEGER, area TEXT NOT NULL,
            questoes_feitas INTEGER DEFAULT 0, questoes_acertadas INTEGER DEFAULT 0,
            data_sessao DATE DEFAULT CURRENT_DATE, observacoes TEXT);
        INSERT INTO sessoes_bulk (sessao_num, area, questoes_feitas, questoes_acertadas, data_sessao)
        VALUES (1, 'Cirurgia', 300, 240, '2026-01-08'),
               (2, 'Pediatria', 200, 150, '2026-01-09'),
               (3, 'Simulado', 100, 70, '2026-01-09');
    """)
    con.commit()
    return con


GRADE = {"semanas": [
    {"semana": 1, "inicio": "2026-01-05", "fim": "2026-01-11", "total_questoes": 50},
    {"semana": 2, "inicio": "2026-01-12", "fim": "2026-01-18", "total_questoes": 70},
]}


def test_funcao_unica_le_total_oficial_e_marco(tmp_path):
    con = _db(tmp_path)
    vm = performance.volume_vs_marco(con, hoje=HOJE)
    con.close()
    assert vm["total"] == 600, "acumulado oficial INCLUI Simulado (s126)"
    assert vm["meta"] == performance.MARCOS[0][1]
    assert vm["marco"] == performance.MARCOS[0][0]
    assert vm["faltam"] == performance.MARCOS[0][1] - 600
    dias = (performance.MARCOS[0][2] - HOJE).days
    assert vm["dias"] == dias
    assert vm["ritmo_alvo"] == round(vm["faltam"] / dias, 1)


def test_gap_e_boot_devolvem_o_mesmo_par(tmp_path):
    """Mesma fixture, os dois comandos, o mesmo par (acumulado, meta)."""
    con = _db(tmp_path)
    vm = performance.volume_vs_marco(con, hoje=HOJE)
    gap = cronograma.gap_payload(con, GRADE, hoje=HOJE)
    con.close()
    assert (gap["acumulado"], gap["meta"]) == (vm["total"], vm["meta"])
    assert gap["marco"] == vm["marco"]
    # o 3o numero continua sendo do cronograma (semana corrente = 1 -> 50 + 70)
    assert gap["cronograma_restante"] == 120
    assert gap["projecao_se_100pct"] == 600 + 120


def test_meta_explicita_e_what_if_e_nao_muda_o_acumulado(tmp_path):
    con = _db(tmp_path)
    gap = cronograma.gap_payload(con, GRADE, hoje=HOJE, meta=9999)
    con.close()
    assert gap["meta"] == 9999 and gap["acumulado"] == 600


def test_nenhum_caller_tem_conta_propria():
    """Estrutural: `day_plan.build` e o `--gap` nao carregam meta literal nem `MARCOS[0]`
    proprio -- os dois passam por `volume_vs_marco`."""
    fonte_build = inspect.getsource(day_plan.build)
    assert "volume_vs_marco(" in fonte_build
    assert "MARCOS[0]" not in fonte_build
    fonte_gap = inspect.getsource(cronograma.gap_payload)
    assert "volume_vs_marco(" in fonte_gap
    tree = ast.parse(inspect.getsource(cronograma.main))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and any(
                isinstance(k.value, ast.Constant) and k.arg == "default"
                and isinstance(k.value.value, int) and k.value.value >= 1000
                for k in node.keywords):
            pytest.fail("meta literal >= 1000 como default de argparse em cronograma.main")


def test_leitor_unico_de_provas_json():
    """Rider b (F71 -> F88): `day_plan.carregar_provas` e `db.blackout_provas` sao a MESMA
    leitura -- ambos delegam a `app.utils.provas`."""
    from app.utils import provas, db
    assert day_plan.carregar_provas is provas.carregar_provas
    assert day_plan.PROVAS_PATH == provas.PROVAS_PATH
    fonte = inspect.getsource(db.blackout_provas)
    assert "from app.utils import provas" in fonte and "provas.blackout_provas(" in fonte
    assert "json.load" not in fonte and "open(" not in fonte


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
