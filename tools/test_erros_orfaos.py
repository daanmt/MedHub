"""Suite do invariante F38 -- erro analisado tem que persistir em `questoes_erros`.

F38 (AUDITORIA_MEDHUB, ALTA, aberto desde a s128): o pipeline de analise tem
DOIS finais -- `insert_questao.py` (erro completo + cards) e `habilidades.py
--add` (so a habilidade). Quando o agente substitui um pelo outro, o bloco entra
em `sessoes_bulk` com N erros de volume e `questoes_erros` nao recebe uma linha:
os cards nascem sem ancora e o substrato canonico so existe em prosa. Nenhum
invariante notava -- `auto_check` auditava arquivos, nao coerencia de dado.

Estes testes travam o guarda de regressao. Fixtures 100% sinteticas: bancos de
mentira em tmp_path, zero leitura do ipub.db real (exceto o teste de regressao
viva no fim, que e deliberado e documentado).

Executavel standalone (python tools/test_erros_orfaos.py) e coletavel pelo pytest.
"""
import sqlite3

import pytest

from tools.utils.state_utils import (
    JANELA_CREDITO_DIAS,
    PISO_ERROS_ORFAOS,
    check_erros_orfaos,
)

SCHEMA = """
CREATE TABLE sessoes_bulk (
    id INTEGER PRIMARY KEY, sessao_num INTEGER, area TEXT,
    questoes_feitas INTEGER, questoes_acertadas INTEGER,
    data_sessao TEXT, observacoes TEXT);
CREATE TABLE questoes_erros (
    id INTEGER PRIMARY KEY, tema_id INTEGER, data_registro TEXT);
"""


def _db(tmp_path, blocos=(), erros=(), nome="ipub.db"):
    """blocos: (data, feitas, acertadas, observacoes). erros: datetimes ISO."""
    alvo = tmp_path / nome
    con = sqlite3.connect(str(alvo))
    con.executescript(SCHEMA)
    for i, (data, feitas, acertadas, obs) in enumerate(blocos, 1):
        con.execute("INSERT INTO sessoes_bulk "
                    "(id, sessao_num, area, questoes_feitas, questoes_acertadas, "
                    "data_sessao, observacoes) VALUES (?,?,?,?,?,?,?)",
                    (i, 100 + i, "Pediatria", feitas, acertadas, data, obs))
    for i, quando in enumerate(erros, 1):
        con.execute("INSERT INTO questoes_erros (id, tema_id, data_registro) "
                    "VALUES (?,?,?)", (i, 1, quando))
    con.commit()
    con.close()
    return str(alvo)


# --------------------------------------------------------------------------
# Deteccao
# --------------------------------------------------------------------------

def test_bloco_sem_erro_registrado_e_orfao(tmp_path):
    db = _db(tmp_path, blocos=[("2026-06-18", 38, 23, "")])
    assert check_erros_orfaos(db) == [("2026-06-18", 15)]


def test_bloco_com_erro_no_mesmo_dia_passa(tmp_path):
    db = _db(tmp_path, blocos=[("2026-06-18", 38, 23, "")],
             erros=["2026-06-18 21:00:00"])
    assert check_erros_orfaos(db) is None


def test_registro_tardio_de_um_dia_conta_como_credito(tmp_path):
    """Registro no dia seguinte e a NORMA no fluxo real, nao a excecao."""
    db = _db(tmp_path, blocos=[("2026-06-18", 38, 23, "")],
             erros=["2026-06-19 01:29:00"])
    assert check_erros_orfaos(db) is None


def test_registro_dois_dias_depois_NAO_conta(tmp_path):
    """Calibracao medida: com d+2 o unico positivo verdadeiro do historico real
    (2026-06-18) desaparecia, porque os erros de d+2 eram de outros temas."""
    db = _db(tmp_path, blocos=[("2026-06-18", 38, 23, "")],
             erros=["2026-06-20 12:00:00"])
    assert check_erros_orfaos(db) == [("2026-06-18", 15)]


def test_soma_areas_do_mesmo_dia(tmp_path):
    db = _db(tmp_path, blocos=[("2026-08-19", 43, 33, ""), ("2026-08-19", 36, 30, "")])
    assert check_erros_orfaos(db) == [("2026-08-19", 16)]


def test_varios_dias_orfaos_saem_ordenados(tmp_path):
    db = _db(tmp_path, blocos=[("2026-07-10", 20, 10, ""), ("2026-06-18", 38, 23, "")])
    assert check_erros_orfaos(db) == [("2026-06-18", 15), ("2026-07-10", 10)]


# --------------------------------------------------------------------------
# Defesas contra falso positivo (ambas exigidas pelo proprio F38)
# --------------------------------------------------------------------------

def test_volume_importado_da_planilha_nao_e_defeito(tmp_path):
    """`/importar-planilha` traz feitas/acertos sem itemizar erro: ausencia
    ESPERADA. Sem este filtro o check acusaria toda a migracao historica."""
    db = _db(tmp_path, blocos=[("2026-05-01", 50, 20, "Migracao historica -- sessoes 001-066")])
    assert check_erros_orfaos(db) is None


def test_acento_no_marcador_de_migracao_tambem_filtra(tmp_path):
    db = _db(tmp_path, blocos=[("2026-05-01", 50, 20, "Migração histórica -- lote 2")])
    assert check_erros_orfaos(db) is None


def test_bloco_pequeno_fica_abaixo_do_piso(tmp_path):
    """2 erros e ruido de bloco curto, nao analise evaporada."""
    db = _db(tmp_path, blocos=[("2026-06-18", 10, 8, "")])
    assert check_erros_orfaos(db) is None


def test_piso_e_fronteira_inclusiva(tmp_path):
    db = _db(tmp_path, blocos=[("2026-06-18", 10, 10 - PISO_ERROS_ORFAOS, "")])
    assert check_erros_orfaos(db) == [("2026-06-18", PISO_ERROS_ORFAOS)]


def test_bloco_sem_erro_nenhum_nao_entra(tmp_path):
    """100% de acerto nao deve nada a questoes_erros."""
    db = _db(tmp_path, blocos=[("2026-06-18", 30, 30, "")])
    assert check_erros_orfaos(db) is None


# --------------------------------------------------------------------------
# Parametros e modo defensivo
# --------------------------------------------------------------------------

def test_piso_customizavel(tmp_path):
    db = _db(tmp_path, blocos=[("2026-06-18", 38, 23, "")])
    assert check_erros_orfaos(db, piso=100) is None
    assert check_erros_orfaos(db, piso=15) == [("2026-06-18", 15)]


def test_desde_limita_a_varredura(tmp_path):
    db = _db(tmp_path, blocos=[("2026-06-18", 38, 23, "")])
    assert check_erros_orfaos(db, desde="2026-07-01") is None
    assert check_erros_orfaos(db, desde="2026-01-01") == [("2026-06-18", 15)]


def test_db_ausente_e_silencioso(tmp_path):
    """Regra dos irmaos F1/POSICAO/B1: nunca falso-positivo barulhento."""
    assert check_erros_orfaos(str(tmp_path / "nao-existe.db")) is None


def test_db_sem_as_tabelas_e_silencioso(tmp_path):
    alvo = tmp_path / "vazio.db"
    sqlite3.connect(str(alvo)).close()
    assert check_erros_orfaos(str(alvo)) is None


def test_janela_de_credito_do_contrato_e_1():
    """Trava a calibracao: alargar a janela compra silencio, nao precisao."""
    assert JANELA_CREDITO_DIAS == 1


def test_piso_do_contrato_e_3():
    assert PISO_ERROS_ORFAOS == 3


# --------------------------------------------------------------------------
# Regressao viva sobre o banco real
# --------------------------------------------------------------------------

def test_db_real_nao_ganha_orfao_novo():
    """O historico tem 1 orfao conhecido (2026-06-18, s085, Ictericia e Sepse
    Neonatal: 15 erros esperados, 0 registrados, 26 cards sem ancora). Se
    aparecer um SEGUNDO, alguem voltou a substituir insert_questao por --add."""
    orfaos = check_erros_orfaos() or []
    novos = [o for o in orfaos if o[0] != "2026-06-18"]
    assert not novos, f"orfao novo detectado: {novos}"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
