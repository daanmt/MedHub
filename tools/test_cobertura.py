#!/usr/bin/env python3
"""test_cobertura.py -- testes do relatorio de cobertura de SSOT (F16a, part-1).

Cobre: normalizacao tolerante, pareamento (par divergente reconhecido +
nao-par mantido orfao), ordenacao por rendimento, e o read de taxonomia em
db.py contra um db temporario. Asserts nativos (coletavel por pytest).

E06 (s216): a semana corrente e a do PLANO pela regua do `plano.panorama` -- fixture
sintetica de `plano_tarefas` + calendario; o `semana_conteudo` antigo (S17) e ignorado.

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
    # F37 (s185): `erros` passou a vir de `questoes_erros`, nao da aritmetica sobre
    # `questoes_realizadas` -- que esta inflado 5,4x e errava por duas ordens de
    # grandeza (`[bulk] Neurologia`: 149 pelo campo, 1 real). A fixture ganha a
    # tabela porque o leitor legitimamente precisa dela; degradar para 0 em silencio
    # seria o honest-negative que o F91 proibe.
    con.execute("CREATE TABLE questoes_erros (id INTEGER PRIMARY KEY AUTOINCREMENT, tema_id INTEGER)")
    con.execute("INSERT INTO taxonomia_cronograma (area, tema, questoes_realizadas, questoes_acertadas) "
                "VALUES ('Cirurgia', 'Apendicite Aguda', 30, 18)")
    for _ in range(12):
        con.execute("INSERT INTO questoes_erros (tema_id) VALUES (1)")
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
    assert r["erros"] == 12  # contagem REAL em questoes_erros (F37), nao 30-18


# --- E06 (s216): semana corrente = semana do PLANO (regua do plano.panorama) ---

from datetime import date  # noqa: E402

import plano  # noqa: E402

_CAL = {3: (date(2026, 9, 28), date(2026, 10, 4)), 4: (date(2026, 10, 5), date(2026, 10, 11)),
        5: (date(2026, 10, 12), date(2026, 10, 18))}


def _tarefa(i, semana, tema, status="pendente"):
    return {"id": i, "semana_plano": semana, "area": "Clinica", "tema": tema,
            "status": status, "fonte": "rf", "q_previstas": 10, "url_lista": None}


_LINHAS = [
    _tarefa(1, 3, "Da Semana Passada", "feita"),
    _tarefa(2, 4, "Sindromes Aorticas Agudas | Cardiomiopatias"),
    _tarefa(3, 4, "Pre-Natal; Vitalidade Fetal", "feita"),
    _tarefa(4, 4, "Tema Cortado", "cortada"),
    _tarefa(5, 5, "Da Proxima Semana"),
]


def test_semana_corrente_e_a_do_plano_pela_regua_do_panorama():
    hoje = date(2026, 10, 5)
    semana, temas = cob.semana_do_plano(_LINHAS, _CAL, hoje)
    # reuso, nao copia: a semana e exatamente a do panorama (calendario da trilha)
    assert semana == 4 == plano.panorama(_LINHAS, _CAL, hoje)["semana"]
    n = cob.normaliza_stem
    # tema bundlado entra inteiro E por parte (`|` e `;`); feita da semana conta
    for t in ("Sindromes Aorticas Agudas", "Cardiomiopatias", "Pre-Natal", "Vitalidade Fetal"):
        assert n(t) in temas, t
    # cortada, semana passada e semana seguinte ficam fora
    for t in ("Tema Cortado", "Da Semana Passada", "Da Proxima Semana"):
        assert n(t) not in temas, t


def test_sem_calendario_cai_na_menor_semana_com_pendencia():
    semana, temas = cob.semana_do_plano(_LINHAS, {}, date(2026, 10, 5))
    assert semana == 4 and cob.normaliza_stem("Cardiomiopatias") in temas


def test_semana_conteudo_antigo_nao_governa_mais(monkeypatch):
    """O defeito do E06: `preparacao_estado.semana_conteudo` = 17 (grade antiga) com o plano
    na S4. O leitor real (`carregar_semana`) sobre plano sintetico tem de dizer 4."""
    import app.utils.db as db
    monkeypatch.setattr(db, "get_semana_conteudo", lambda: 17)
    monkeypatch.setattr(db, "plano_listar", lambda *a, **k: list(_LINHAS))
    monkeypatch.setattr(db, "hoje", lambda: date(2026, 10, 5))
    monkeypatch.setattr(plano, "calendario_trilha", lambda trilha=None: dict(_CAL))
    semana, temas = cob.carregar_semana()
    assert semana == 4
    assert cob.normaliza_stem("Cardiomiopatias") in temas


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
    _run(test_semana_corrente_e_a_do_plano_pela_regua_do_panorama, False)
    _run(test_sem_calendario_cai_na_menor_semana_com_pendencia, False)

    print()
    if falhas:
        print(f"FALHOU: {len(falhas)} check(s)")
        sys.exit(1)
    print("TODOS OS CHECKS PASSARAM (part-1 cobertura)")
