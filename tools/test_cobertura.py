#!/usr/bin/env python3
"""test_cobertura.py -- testes do relatorio de cobertura de SSOT (F16a, part-1).

Cobre: normalizacao tolerante, pareamento (par divergente reconhecido +
nao-par mantido orfao), ordenacao por rendimento, e o read de taxonomia em
db.py contra um db temporario. Asserts nativos (coletavel por pytest).

Uso: python tools/test_cobertura.py  OU  pytest tools/test_cobertura.py
"""

import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import cobertura_conhecimento as cob  # noqa: E402


def test_normaliza_tolerante():
    # prefixo numerico EMED + acento + case + pontuacao colapsam para a mesma chave
    assert cob.normaliza_stem("12 - Apendicite Aguda") == cob.normaliza_stem("Apendicite Aguda")
    # acento proposital (testa remocao de acento). chr(0x00e1)='a' acentuado:
    # mantem o fonte ASCII-limpo (AGENTE 4.5) sem perder o dado da fixture.
    acentuado = "Cirrose Hep" + chr(0x00e1) + "tica"
    assert cob.normaliza_stem("07. Cirrose Hepatica") == cob.normaliza_stem(acentuado)
    assert cob.normaliza_stem("Meckel") != cob.normaliza_stem("Apendicite Aguda")


def test_par_divergente_reconhecido(tmp_path):
    # PDF com prefixo numerico do EMED pareia com .md de nome "limpo" (par verdadeiro).
    base = tmp_path / "resumos" / "Cirurgia"
    base.mkdir(parents=True)
    (base / "12 - Apendicite Aguda.pdf").write_bytes(b"%PDF-1.4 fake")
    (base / "Apendicite Aguda.md").write_text("# Apendicite", encoding="utf-8")

    pdfs, mds = cob.coletar(str(tmp_path / "resumos"))
    pareado = cob.parear(pdfs, mds)
    ap = next(p for p in pareado if "Apendicite" in p["stem"])
    assert ap["coberto"] is True, f"esperava coberto, veio {ap}"


def test_nao_par_mantido_orfao(tmp_path):
    # PDF sem .md correspondente permanece orfao; .md de outro tema nao o cobre.
    base = tmp_path / "resumos" / "Cirurgia"
    base.mkdir(parents=True)
    (base / "Diverticulo de Meckel.pdf").write_bytes(b"%PDF-1.4 fake")
    (base / "Apendicite Aguda.md").write_text("# Apendicite", encoding="utf-8")

    pdfs, mds = cob.coletar(str(tmp_path / "resumos"))
    pareado = cob.parear(pdfs, mds)
    meckel = next(p for p in pareado if "Meckel" in p["stem"])
    assert meckel["coberto"] is False, f"esperava orfao, veio {meckel}"


def test_ordenacao_por_rendimento():
    # 3 orfaos: um na semana corrente, um na grade com volume, um fora da grade.
    orfaos = [
        {"stem": "Fora da Grade", "norm": cob.normaliza_stem("Fora da Grade"),
         "area": "Clinica", "candidato": None, "score": 0.0},
        {"stem": "Na Grade", "norm": cob.normaliza_stem("Na Grade"),
         "area": "Clinica", "candidato": None, "score": 0.0},
        {"stem": "Da Semana", "norm": cob.normaliza_stem("Da Semana"),
         "area": "Clinica", "candidato": None, "score": 0.0},
    ]
    semana_norms = {cob.normaliza_stem("Da Semana")}
    grade_norms = {cob.normaliza_stem("Da Semana"), cob.normaliza_stem("Na Grade")}
    taxonomia = {cob.normaliza_stem("Na Grade"): (50, 20, "Clinica")}

    semana, restantes = cob.priorizar(orfaos, semana_norms, grade_norms, taxonomia)

    # semana corrente sai isolada na sua secao
    assert [x["stem"] for x in semana] == ["Da Semana"]
    # restantes: o que esta na grade (com volume) vem antes do que esta fora
    assert [x["stem"] for x in restantes] == ["Na Grade", "Fora da Grade"]
    assert restantes[0]["in_grade"] is True and restantes[0]["volume"] == 50
    assert restantes[1]["in_grade"] is False


def test_db_taxonomia_rendimento(tmp_path):
    # get_taxonomia_rendimento() le volume/erros de um db temporario (read via db.py).
    import app.utils.db as db
    tmp_db = tmp_path / "ipub_test.db"
    con = sqlite3.connect(str(tmp_db))
    con.execute("""
        CREATE TABLE taxonomia_cronograma (
            id INTEGER PRIMARY KEY, area TEXT, tema TEXT,
            questoes_realizadas INTEGER DEFAULT 0,
            questoes_acertadas INTEGER DEFAULT 0
        )""")
    con.execute("INSERT INTO taxonomia_cronograma (area, tema, questoes_realizadas, questoes_acertadas) "
                "VALUES ('Cirurgia', 'Apendicite Aguda', 30, 18)")
    con.commit()
    con.close()

    orig = db.DB_PATH
    db.DB_PATH = str(tmp_db)
    try:
        rows = db.get_taxonomia_rendimento()
    finally:
        db.DB_PATH = orig

    assert len(rows) == 1
    r = rows[0]
    assert r["tema"] == "Apendicite Aguda"
    assert r["volume"] == 30
    assert r["erros"] == 12  # 30 - 18


if __name__ == "__main__":
    import tempfile
    from pathlib import Path

    falhas = []

    def _run(fn, precisa_tmp):
        try:
            if precisa_tmp:
                with tempfile.TemporaryDirectory() as d:
                    fn(Path(d))
            else:
                fn()
            print(f"  OK  {fn.__name__}")
        except AssertionError as e:
            falhas.append(fn.__name__)
            print(f"FALHOU {fn.__name__}: {e}")
        except Exception as e:
            falhas.append(fn.__name__)
            print(f"ERRO  {fn.__name__}: {e}")

    _run(test_normaliza_tolerante, False)
    _run(test_par_divergente_reconhecido, True)
    _run(test_nao_par_mantido_orfao, True)
    _run(test_ordenacao_por_rendimento, False)
    _run(test_db_taxonomia_rendimento, True)

    print()
    if falhas:
        print(f"FALHOU: {len(falhas)} check(s)")
        sys.exit(1)
    print("TODOS OS CHECKS PASSARAM (part-1 cobertura)")
