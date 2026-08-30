"""Suite do F37 -- registro de sessao bulk NAO pode espalhar volume pelos temas.

F37 (AUDITORIA_MEDHUB, aberto desde a s127): `taxonomia_cronograma.questoes_
realizadas` estava inflado 5,9x (39.077 contra 6.631 reais em `sessoes_bulk`).
A causa, achada na s159: `registrar_sessao_bulk` fazia
`UPDATE ... SET questoes_realizadas = questoes_realizadas + ? WHERE area = ?`
-- **sem filtro de tema**. Uma sessao de 51 questoes de Pediatria somava 51 em
TODOS os temas de Pediatria (16 temas compartilhando 156/140, 14 de Cirurgia
compartilhando 56/49, etc.).

O dano nao era cosmetico: `app/memory/manager._load_ipub_error_counts` derivava
"erros por tema" desse campo, entao o ranking de fraquezas do boot media QUANTO
A AREA FOI ESTUDADA, nao quao fraco o tema e.

Uma sessao bulk e atribuida a AREA -- nao existe atribuicao por tema para
distribuir. O acumulado vai para a linha `[bulk] <area>` e para ai.

Fixtures 100% sinteticas (DB_PATH monkeypatchado para tmp_path).
Executavel standalone (python tools/test_bulk_fanout.py) e coletavel pelo pytest.
"""
import sqlite3

import pytest

from tools import registrar_sessao_bulk as rsb

SCHEMA = """
CREATE TABLE sessoes_bulk (
    id INTEGER PRIMARY KEY AUTOINCREMENT, sessao_num INTEGER, area TEXT,
    questoes_feitas INTEGER, questoes_acertadas INTEGER,
    data_sessao TEXT, observacoes TEXT);
CREATE TABLE taxonomia_cronograma (
    id INTEGER PRIMARY KEY AUTOINCREMENT, area TEXT NOT NULL, tema TEXT NOT NULL,
    questoes_realizadas INTEGER DEFAULT 0, questoes_acertadas INTEGER DEFAULT 0,
    percentual_acertos REAL DEFAULT 0, ultima_revisao TEXT);
"""


@pytest.fixture()
def db(tmp_path, monkeypatch):
    alvo = tmp_path / "ipub.db"
    con = sqlite3.connect(str(alvo))
    con.executescript(SCHEMA)
    con.executemany(
        "INSERT INTO taxonomia_cronograma (area, tema, questoes_realizadas, "
        "questoes_acertadas) VALUES (?,?,?,?)",
        [("Pediatria", "Imunizacoes", 10, 8),
         ("Pediatria", "Bronquiolite", 4, 3),
         ("Cirurgia", "Apendicite", 7, 5)])
    con.commit()
    con.close()
    monkeypatch.setattr(rsb, "DB_PATH", str(alvo))
    return str(alvo)


def _taxon(db_path):
    con = sqlite3.connect(db_path)
    try:
        return {(a, t): (r, ac) for a, t, r, ac in con.execute(
            "SELECT area, tema, questoes_realizadas, questoes_acertadas "
            "FROM taxonomia_cronograma")}
    finally:
        con.close()


def test_temas_reais_da_area_ficam_intocados(db):
    """O coracao do F37: 51 questoes de Pediatria nao viram +51 em cada tema."""
    antes = _taxon(db)
    rsb.registrar(160, "Pediatria", 51, 48, data="2026-08-30")
    depois = _taxon(db)
    assert depois[("Pediatria", "Imunizacoes")] == antes[("Pediatria", "Imunizacoes")]
    assert depois[("Pediatria", "Bronquiolite")] == antes[("Pediatria", "Bronquiolite")]


def test_outra_area_tambem_fica_intocada(db):
    antes = _taxon(db)
    rsb.registrar(160, "Pediatria", 51, 48, data="2026-08-30")
    assert _taxon(db)[("Cirurgia", "Apendicite")] == antes[("Cirurgia", "Apendicite")]


def test_volume_vai_para_a_linha_bulk_da_area(db):
    rsb.registrar(160, "Pediatria", 51, 48, data="2026-08-30")
    assert _taxon(db)[("Pediatria", "[bulk] Pediatria")] == (51, 48)


def test_duas_sessoes_acumulam_na_mesma_linha_bulk(db):
    rsb.registrar(160, "Pediatria", 51, 48, data="2026-08-30")
    rsb.registrar(161, "Pediatria", 20, 15, data="2026-08-31")
    assert _taxon(db)[("Pediatria", "[bulk] Pediatria")] == (71, 63)


def test_soma_da_taxonomia_nao_estoura_o_volume_real(db):
    """Regressao direta da inflacao: o delta em taxonomia tem que ser
    EXATAMENTE o volume registrado, nao volume x nº de temas da area."""
    antes = sum(r for r, _ in _taxon(db).values())
    rsb.registrar(160, "Pediatria", 51, 48, data="2026-08-30")
    assert sum(r for r, _ in _taxon(db).values()) - antes == 51


def test_area_nova_cria_a_linha_bulk(db):
    rsb.registrar(160, "Oftalmo", 12, 6, data="2026-08-30")
    assert _taxon(db)[("Oftalmo", "[bulk] Oftalmo")] == (12, 6)


def test_percentual_da_linha_bulk_e_coerente(db):
    rsb.registrar(160, "Pediatria", 50, 40, data="2026-08-30")
    con = sqlite3.connect(db)
    try:
        pct = con.execute(
            "SELECT percentual_acertos FROM taxonomia_cronograma "
            "WHERE area='Pediatria' AND tema='[bulk] Pediatria'").fetchone()[0]
    finally:
        con.close()
    assert abs(pct - 80.0) < 0.01


def test_sessoes_bulk_continua_sendo_o_ssot_de_volume(db):
    rsb.registrar(160, "Pediatria", 51, 48, data="2026-08-30")
    con = sqlite3.connect(db)
    try:
        assert con.execute(
            "SELECT SUM(questoes_feitas) FROM sessoes_bulk").fetchone()[0] == 51
    finally:
        con.close()


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
