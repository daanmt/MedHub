"""Spec plano-ssot-e-cards-v2-part-1: segundo derivador do cronograma (Extensivo, 52
semanas). Fixture SINTETICA (2 semanas, forma real do PDF -- cabecalho glued
'ExtensivoSemana NN' + 'Resumo' + 'Tarefa N' + bloco de detalhe 'Passo a Passo');
zero dependencia do '[52 wk] Cronograma Extensivo.pdf' real (IP do EMED, gitignored).

Cobre (DoD 3): parser, normalizacao de disciplina (nome cheio + abreviado + lista
multi-disciplina tipo Semana 52), sha-check, e a asseracao 735/52 sobre o JSON
versionado (`core/cronograma/grade_extensivo.json`).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cronograma as cr  # noqa: E402


def _cabecalho_semana(pagina_n, semana_n, apos="Resumo"):
    return [
        "Estratégia",
        f"MEDCURSO EXTENSIVO{pagina_n}",
        f"Estratégia MED | Residência Médica | Cronograma ExtensivoSemana {semana_n:02d}",
        apos,
    ]


def _texto_fixture():
    """2 semanas sintéticas com a forma real: cabeçalho glued, Resumo (lista curta,
    disciplina+assunto+tipo colados numa linha) e Passo a Passo (Tarefa N isolada +
    detalhe com páginas/questões/URL). Cobre: disciplina de nome cheio (Pediatria),
    abreviada (Preventiva, Hepato) e lista multi-disciplina (Cardio, Psiquiatria e
    Nefro -- forma da Semana 52 real)."""
    paginas = []

    # ---- Semana 01: Resumo (página 1) ----
    p1 = _cabecalho_semana(1, 1) + [
        "Tarefa 1 PediatriaFebre Sem Sinais LocalizatóriosTeoria I",
        "Tarefa 2 PreventivaÉtica MédicaRevisão",
        "Tarefa 3 Cardio, Psiquiatria e NefroQuestões Erradas",
        "",
    ]
    paginas.append("\n".join(p1))

    # ---- Semana 01: Passo a Passo (página 2) ----
    p2 = [
        "Estratégia",
        "MEDCURSO EXTENSIVO2",
        "Estratégia MED | Residência Médica | Cronograma ExtensivoPasso a Passo",
        "Tarefa 1",
        "PediatriaLivro Digital: Febre Sem Sinais Localizatórios (Teoria I)",
        "Leia das páginas 10 a 25 do Livro Digital.",
        "Acesse o material indicado no link abaixo:Link - 12 questões:"
        "https://med.estrategia.com/cadernos-e-simulados/cadernos/"
        "aaaa1111-bbbb-2222-cccc-333344445555/?per_page=20Acesse o material "
        "indicado no link abaixo!Aula de Pediatria - Curso Extensivo:"
        "https://med.estrategia.com/meus-cursos/pediatria-extensivo",
        "Tarefa 2",
        "PreventivaLivro Digital: Ética Médica (Revisão)",
        "Leia das páginas 30 a 40 do Livro Digital.",
        "Tarefa 3",
        "Cardio, Psiquiatria e NefroLink - 20 questões:"
        "https://med.estrategia.com/cadernos-e-simulados/cadernos/"
        "dddd4444-eeee-5555-ffff-666677778888/?per_page=20Acesse o material "
        "indicado no link abaixo!",
        "",
    ]
    paginas.append("\n".join(p2))

    # ---- Semana 02: Resumo (página 3) ----
    p3 = _cabecalho_semana(3, 2) + [
        "Tarefa 1 HepatoCirrose HepáticaTeoria II",
        "Tarefa 2 Todas as DisciplinasDiversos Assuntos",
        "",
    ]
    paginas.append("\n".join(p3))

    # ---- Semana 02: Passo a Passo (página 4) ----
    p4 = [
        "Estratégia",
        "MEDCURSO EXTENSIVO4",
        "Estratégia MED | Residência Médica | Cronograma ExtensivoPasso a Passo",
        "Tarefa 1",
        "HepatoLivro Digital: Cirrose Hepática (Teoria II)",
        "Leia das páginas 5 a 9 do Livro Digital.",
        "Tarefa 2",
        "Todas as DisciplinasQuestões de revisão geral, sem link de lista.",
        "",
    ]
    paginas.append("\n".join(p4))

    return cr._juntar_paginas_extensivo(paginas)


# ---------------------------------------------------------------------------
# Parser -- fixture de 2 semanas sintéticas
# ---------------------------------------------------------------------------
def test_parse_extensivo_text_duas_semanas():
    semanas = cr.parse_extensivo_text(_texto_fixture())
    assert [s["semana"] for s in semanas] == [1, 2]
    assert len(semanas[0]["tasks"]) == 3
    assert len(semanas[1]["tasks"]) == 2


def test_disciplina_nome_cheio_e_tipo_teoria():
    semanas = cr.parse_extensivo_text(_texto_fixture())
    t1 = semanas[0]["tasks"][0]
    assert t1["tarefa"] == 1
    assert t1["disciplina"] == "Pediatria"
    assert t1["area_norm"] == "Pediatria"
    assert t1["assunto"] == "Febre Sem Sinais Localizatórios"
    assert t1["tipo"] == "Teoria I"
    assert t1["tipo_norm"] == "teoria"


def test_disciplina_abreviada_casa_para_forma_canonica():
    """'Preventiva'/'Hepato' (sem o nome cheio) têm que casar -- medido no PDF real
    a partir da S20/S29: o EMED abrevia a partir de certo ponto do Extensivo."""
    semanas = cr.parse_extensivo_text(_texto_fixture())
    t2 = semanas[0]["tasks"][1]
    assert t2["disciplina"] == "Medicina Preventiva"
    assert t2["area_norm"] == "Preventiva"
    assert t2["tipo_norm"] == "revisao"

    hepato = semanas[1]["tasks"][0]
    assert hepato["disciplina"] == "Hepatologia"
    assert hepato["area_norm"] == "Hepato"


def test_lista_multi_disciplina_vira_multi_em_vez_da_primeira_da_lista():
    """'Cardio, Psiquiatria e Nefro' (forma da Semana 52 real) não pode virar
    Cardiologia sozinha -- vira Todas as Disciplinas / area_norm Multi."""
    semanas = cr.parse_extensivo_text(_texto_fixture())
    t3 = semanas[0]["tasks"][2]
    assert t3["disciplina"] == "Todas as Disciplinas"
    assert t3["area_norm"] == "Multi"
    assert t3["assunto"] == "Cardio, Psiquiatria e Nefro"
    assert t3["tipo_norm"] == "revisao_questoes"   # "Questões Erradas"


def test_diversos_assuntos_sem_tipo_explicito():
    semanas = cr.parse_extensivo_text(_texto_fixture())
    diversos = semanas[1]["tasks"][1]
    assert diversos["disciplina"] == "Todas as Disciplinas"
    assert diversos["tipo"] == "Diversos Assuntos"
    assert diversos["tipo_norm"] == "revisao_questoes"


def test_detalhe_paginas_questoes_e_url_mergeados_na_tarefa():
    semanas = cr.parse_extensivo_text(_texto_fixture())
    t1 = semanas[0]["tasks"][0]
    assert t1["paginas_livro"] == [[10, 25]]
    assert t1["n_paginas"] == 16
    assert t1["n_questoes"] == 12
    assert t1["n_links_questoes"] == 1
    assert t1["url_lista"] == (
        "https://med.estrategia.com/cadernos-e-simulados/cadernos/"
        "aaaa1111-bbbb-2222-cccc-333344445555/?per_page=20")


def test_detalhe_sem_link_de_lista_fica_null():
    semanas = cr.parse_extensivo_text(_texto_fixture())
    diversos = semanas[1]["tasks"][1]
    assert diversos["n_questoes"] is None
    assert diversos["url_lista"] is None
    assert diversos["n_links_questoes"] == 0


def test_watermark_da_ultima_tarefa_da_semana_nao_vaza_no_tipo():
    """A marca d'água ('Medicina livre, venda proibida...') cola depois da última
    tarefa do Resumo em toda semana real (ela não tem 'Tarefa N+1' pra bounda-la).
    Sem o filtro, o tipo (ancorado em fim-de-linha) para de casar."""
    linhas_p1 = _cabecalho_semana(1, 9) + [
        "Tarefa 1 CirurgiaApendicite AgudaTeoria I",
        "Medicina livre, venda proibida, twitter @Livremedicina",
        "Medicina livre, venda proibida, twitter @Livremedicina",
        "",
    ]
    texto = cr._juntar_paginas_extensivo(["\n".join(linhas_p1)])
    semanas = cr.parse_extensivo_text(texto)
    assert semanas[0]["tasks"][0]["tipo_norm"] == "teoria"
    assert semanas[0]["tasks"][0]["assunto"] == "Apendicite Aguda"


# ---------------------------------------------------------------------------
# normaliza_area_extensivo -- DoD 3 (area_norm ∈ core/areas.json ∪ {Multi})
# ---------------------------------------------------------------------------
def test_normaliza_area_extensivo_reusa_area_pdf_to_canon():
    assert cr.normaliza_area_extensivo("Pediatria") == "Pediatria"
    assert cr.normaliza_area_extensivo("Obstetrícia") == "Obstetrícia"
    assert cr.normaliza_area_extensivo("Gastroenterologia") == "Gastro"
    assert cr.normaliza_area_extensivo("Otorrinolaringologia") == "Otorrino"


def test_normaliza_area_extensivo_radiologia_e_todas_disciplinas_viram_multi():
    """Decisão documentada (spec DoD 3 / Risk): 'Radiologia' não está em
    core/areas.json -- cai em Multi em vez de inventar 21ª área sem decisão do
    operador (F89). 'Todas as Disciplinas' já é o coringa multi-área."""
    assert cr.normaliza_area_extensivo("Radiologia") == "Multi"
    assert cr.normaliza_area_extensivo("Todas as Disciplinas") == "Multi"


def test_normaliza_area_extensivo_area_norm_sempre_no_vocabulario():
    from app.utils.areas import AREAS_VALIDAS
    for disciplina in cr.EXTENSIVO_DISCIPLINAS:
        area = cr.normaliza_area_extensivo(disciplina)
        assert area == "Multi" or area in AREAS_VALIDAS, (
            f"{disciplina!r} -> {area!r} fora do vocabulario e fora de Multi")


# ---------------------------------------------------------------------------
# resolve_pdf_extensivo / check_extensivo -- sha-check, sem traceback com PDF ausente
# ---------------------------------------------------------------------------
def test_resolve_pdf_extensivo_prefere_raiz_e_cai_para_data(tmp_path):
    nome = cr.PDF_EXTENSIVO_NOME
    raiz = tmp_path / nome
    data = tmp_path / "data" / nome
    data.parent.mkdir()
    data.write_bytes(b"%PDF-fake-data")
    assert cr.resolve_pdf_extensivo(str(tmp_path)) == str(data)
    raiz.write_bytes(b"%PDF-fake-root")
    assert cr.resolve_pdf_extensivo(str(tmp_path)) == str(raiz)


def test_check_extensivo_sem_pdf_degrada_sem_traceback(tmp_path):
    grade = tmp_path / "grade_extensivo.json"
    grade.write_text('{"_meta": {"sha256": "abc"}, "semanas": []}', encoding="utf-8")
    r = cr.check_extensivo(pdf_path=str(tmp_path / "nao_existe.pdf"), grade_path=str(grade))
    assert r["status"] == "missing_pdf"
    assert cr.PDF_EXTENSIVO_NOME in r["msg"]


def test_check_extensivo_fresh_vs_stale(tmp_path):
    pdf = tmp_path / cr.PDF_EXTENSIVO_NOME
    pdf.write_bytes(b"%PDF-conteudo-v1")
    grade = tmp_path / "grade_extensivo.json"
    grade.write_text(json.dumps({"_meta": {"sha256": cr.sha256_file(str(pdf))}, "semanas": []}),
                      encoding="utf-8")
    r = cr.check_extensivo(pdf_path=str(pdf), grade_path=str(grade))
    assert r["status"] == "fresh"

    pdf.write_bytes(b"%PDF-conteudo-v2-mudou")
    r2 = cr.check_extensivo(pdf_path=str(pdf), grade_path=str(grade))
    assert r2["status"] == "stale"


def test_check_extensivo_sem_grade_pede_rebuild(tmp_path):
    r = cr.check_extensivo(pdf_path=str(tmp_path / "x.pdf"),
                            grade_path=str(tmp_path / "nao_existe.json"))
    assert r["status"] == "missing"
    assert "--rebuild-extensivo" in r["msg"]


# ---------------------------------------------------------------------------
# Falha dura de contagem (Technical Decision da spec)
# ---------------------------------------------------------------------------
def test_rebuild_extensivo_falha_duro_quando_contagem_diverge(tmp_path, monkeypatch):
    """A fixture tem 5 tarefas/2 semanas -- bem longe de 735/52. Sem
    --expect-tasks, `rebuild_extensivo` tem que RECUSAR gravar."""
    texto_fixo = _texto_fixture()
    monkeypatch.setattr(cr, "extrai_paginas", lambda pdf_path: [])
    monkeypatch.setattr(cr, "_juntar_paginas_extensivo", lambda paginas: texto_fixo)
    monkeypatch.setattr(cr, "sha256_file", lambda path: "sha-fake")
    grade_path = tmp_path / "grade_extensivo.json"
    import pytest
    with pytest.raises(cr.ExtensivoContagemDivergente):
        cr.rebuild_extensivo(pdf_path=str(tmp_path / "fake.pdf"), grade_path=str(grade_path))
    assert not grade_path.exists()


def test_rebuild_extensivo_expect_tasks_destrava_a_divergencia(tmp_path, monkeypatch):
    texto_fixo = _texto_fixture()
    monkeypatch.setattr(cr, "extrai_paginas", lambda pdf_path: [])
    monkeypatch.setattr(cr, "_juntar_paginas_extensivo", lambda paginas: texto_fixo)
    monkeypatch.setattr(cr, "sha256_file", lambda path: "sha-fake")
    grade_path = tmp_path / "grade_extensivo.json"
    g = cr.rebuild_extensivo(pdf_path=str(tmp_path / "fake.pdf"), grade_path=str(grade_path),
                              expect_tasks=5)
    assert g["_meta"]["n_tasks"] == 5
    assert g["_meta"]["n_semanas"] == 2
    assert grade_path.exists()


# ---------------------------------------------------------------------------
# Asseração 735/52 sobre o JSON VERSIONADO (core/cronograma/grade_extensivo.json)
# ---------------------------------------------------------------------------
def test_grade_extensivo_json_versionado_tem_735_tarefas_52_semanas():
    path = cr.GRADE_EXTENSIVO_PATH
    if not os.path.exists(path):
        import pytest
        pytest.skip("grade_extensivo.json não foi gerado ainda -- rode --rebuild-extensivo")
    g = cr.load_grade(path)
    m = g["_meta"]
    assert m["n_semanas"] == 52
    assert m["n_tasks"] == 735
    assert m["n_teoria"] + m["n_revisao"] + m["n_rpq"] == 735
    assert sum(len(s["tasks"]) for s in g["semanas"]) == 735
    assert len(g["semanas"]) == 52
