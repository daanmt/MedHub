"""Suite do sensor de drift doc-vs-codigo (tools/doc_drift.py).

Cobre as 4 especies de anotacao (true -> silencio, false -> WARN), anotacao
malformada (sintaxe, nunca crash), e a allowlist (doc fora dela e ignorado --
prova da fronteira clinica por construcao).

Executavel standalone (python tools/test_doc_drift.py) e coletavel pelo pytest.
"""
import sqlite3
import sys

import pytest

from tools.doc_drift import ALLOWLIST, run_checks


def _mk_db(tmp_path, com_unique=True):
    db = tmp_path / "ipub.db"
    con = sqlite3.connect(str(db))
    con.execute("CREATE TABLE flashcards (id INTEGER PRIMARY KEY)")
    con.executemany("INSERT INTO flashcards (id) VALUES (?)",
                    [(i,) for i in range(797, 810)])
    con.execute("CREATE TABLE taxonomia_cronograma (area TEXT, tema TEXT)")
    if com_unique:
        con.execute("CREATE UNIQUE INDEX ux_tax ON taxonomia_cronograma(area, tema)")
    con.commit()
    con.close()
    return db


def _mk_doc(tmp_path, nome, anotacoes):
    (tmp_path / nome).write_text(
        "\n".join(anotacoes) + "\nprosa qualquer\n", encoding="utf-8")


def _roda(tmp_path):
    return run_checks(root=tmp_path, db_path=tmp_path / "ipub.db")


# --- especie sqlite ---

def test_sqlite_coerente_silencia(tmp_path):
    _mk_db(tmp_path)
    _mk_doc(tmp_path, "HANDOFF.md",
            ['<!-- drift-check: sqlite "SELECT COUNT(*) FROM flashcards" == 13 -->'])
    assert _roda(tmp_path) == []


def test_sqlite_divergente_acusa_drift(tmp_path):
    _mk_db(tmp_path)
    _mk_doc(tmp_path, "HANDOFF.md",
            ['<!-- drift-check: sqlite "SELECT COUNT(*) FROM flashcards" == 99 -->'])
    achados = _roda(tmp_path)
    assert len(achados) == 1 and achados[0]["tipo"] == "drift"
    assert "99" in achados[0]["msg"] and "13" in achados[0]["msg"]


def test_sqlite_nao_select_e_sintaxe_e_nao_escreve(tmp_path):
    db = _mk_db(tmp_path)
    _mk_doc(tmp_path, "HANDOFF.md",
            ['<!-- drift-check: sqlite "DELETE FROM flashcards" == 0 -->'])
    achados = _roda(tmp_path)
    assert len(achados) == 1 and achados[0]["tipo"] == "sintaxe"
    con = sqlite3.connect(str(db))
    assert con.execute("SELECT COUNT(*) FROM flashcards").fetchone()[0] == 13
    con.close()


# --- especie symbol ---

def test_symbol_absent_coerente_silencia(tmp_path):
    _mk_db(tmp_path)
    (tmp_path / "modulo.py").write_text("def funcao_viva():\n    pass\n",
                                        encoding="utf-8")
    _mk_doc(tmp_path, "ROADMAP.md",
            ["<!-- drift-check: symbol modulo.py::funcao_removida absent -->"])
    assert _roda(tmp_path) == []


def test_symbol_absent_mas_presente_acusa_drift(tmp_path):
    _mk_db(tmp_path)
    (tmp_path / "modulo.py").write_text("def funcao_zumbi():\n    pass\n",
                                        encoding="utf-8")
    _mk_doc(tmp_path, "ROADMAP.md",
            ["<!-- drift-check: symbol modulo.py::funcao_zumbi absent -->"])
    achados = _roda(tmp_path)
    assert len(achados) == 1 and achados[0]["tipo"] == "drift"


def test_symbol_exists_mas_ausente_acusa_drift(tmp_path):
    _mk_db(tmp_path)
    (tmp_path / "modulo.py").write_text("# vazio\n", encoding="utf-8")
    _mk_doc(tmp_path, "ROADMAP.md",
            ["<!-- drift-check: symbol modulo.py::funcao_prometida exists -->"])
    achados = _roda(tmp_path)
    assert len(achados) == 1 and achados[0]["tipo"] == "drift"


def test_symbol_arquivo_inexistente_e_sintaxe(tmp_path):
    _mk_db(tmp_path)
    _mk_doc(tmp_path, "ROADMAP.md",
            ["<!-- drift-check: symbol sumido.py::qualquer exists -->"])
    achados = _roda(tmp_path)
    assert len(achados) == 1 and achados[0]["tipo"] == "sintaxe"


# --- especie path ---

def test_path_exists_coerente_silencia(tmp_path):
    _mk_db(tmp_path)
    (tmp_path / "presente.py").write_text("", encoding="utf-8")
    _mk_doc(tmp_path, "ESTADO.md",
            ["<!-- drift-check: path presente.py exists -->"])
    assert _roda(tmp_path) == []


def test_path_exists_mas_sumido_acusa_drift(tmp_path):
    _mk_db(tmp_path)
    _mk_doc(tmp_path, "ESTADO.md",
            ["<!-- drift-check: path sumido.py exists -->"])
    achados = _roda(tmp_path)
    assert len(achados) == 1 and achados[0]["tipo"] == "drift"


# --- especie unique ---

def test_unique_exists_coerente_silencia(tmp_path):
    _mk_db(tmp_path, com_unique=True)
    _mk_doc(tmp_path, "ROADMAP.md",
            ["<!-- drift-check: unique taxonomia_cronograma (area, tema) exists -->"])
    assert _roda(tmp_path) == []


def test_unique_exists_mas_falta_acusa_drift(tmp_path):
    _mk_db(tmp_path, com_unique=False)
    _mk_doc(tmp_path, "ROADMAP.md",
            ["<!-- drift-check: unique taxonomia_cronograma (area, tema) exists -->"])
    achados = _roda(tmp_path)
    assert len(achados) == 1 and achados[0]["tipo"] == "drift"


def test_unique_absent_mas_existe_acusa_drift(tmp_path):
    _mk_db(tmp_path, com_unique=True)
    _mk_doc(tmp_path, "ROADMAP.md",
            ["<!-- drift-check: unique taxonomia_cronograma (area, tema) absent -->"])
    achados = _roda(tmp_path)
    assert len(achados) == 1 and achados[0]["tipo"] == "drift"


# --- sintaxe e robustez ---

def test_anotacao_malformada_e_sintaxe_nunca_crash(tmp_path):
    _mk_db(tmp_path)
    _mk_doc(tmp_path, "ROADMAP.md",
            ["<!-- drift-check: especie_inventada foo bar -->"])
    achados = _roda(tmp_path)
    assert len(achados) == 1 and achados[0]["tipo"] == "sintaxe"


def test_doc_sem_anotacao_silencia(tmp_path):
    _mk_db(tmp_path)
    _mk_doc(tmp_path, "ROADMAP.md", ["prosa sem anotacao"])
    assert _roda(tmp_path) == []


# --- allowlist (fronteira clinica por construcao) ---

def test_allowlist_e_exatamente_os_4_docs_de_estado():
    assert ALLOWLIST == ("ROADMAP.md", "HANDOFF.md", "ESTADO.md",
                         "AUDITORIA_MEDHUB.md")


def test_doc_fora_da_allowlist_e_ignorado(tmp_path):
    _mk_db(tmp_path)
    resumos = tmp_path / "resumos"
    resumos.mkdir()
    # anotacao FALHA plantada fora da allowlist: se o sensor a lesse, acusaria
    (resumos / "Tema Clinico.md").write_text(
        "<!-- drift-check: path nao_existe.py exists -->\n", encoding="utf-8")
    (tmp_path / "OUTRO.md").write_text(
        "<!-- drift-check: path nao_existe.py exists -->\n", encoding="utf-8")
    assert _roda(tmp_path) == []


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
