"""Testes de tools/plano.py + app/utils/db.py::plano_* (spec plano-ssot-e-cards-v2-part-2).

Banco sintetico em `tmp_path` (padrao do `test_cards_prune.py`): `db.DB_PATH` e
monkeypatchado, o `ipub.db` real NUNCA e tocado. As fontes tambem sao sinteticas --
tres JSONs em memoria com a FORMA dos reais --, exceto os dois testes de regressao
viva, que leem os arquivos versionados de `core/cronograma/` e travam os numeros que
o orquestrador mediu em 16/09 (139 pendentes da Reta Final, 425 tarefas S21-S48).

O que estes testes protegem, em ordem de dano:
  1. **status inicial nunca inferido** -- variante de nome ou tipo diferente nascem
     `pendente`, nao `feita`. Marcar como feito o que nao foi e a unica falha desta
     parte que some do plano um tema que o usuario ainda precisa estudar.
  2. **idempotencia** -- re-semear insere 0 e nao pisa em progresso (`status`,
     `data_conclusao`, `origem_conclusao` ficam fora do UPDATE).
  3. **area fantasma recusada na porta** (F89).
  4. **`--expect` errado nao grava** (COUNT-ASSERT, AGENTE.md secao 10.7).
"""
import json
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from app.utils import db  # noqa: E402
from app.utils.areas import AreaInvalida  # noqa: E402
import plano  # noqa: E402


# ------------------------------------------------------------------- fixtures

def _usar_db(tmp_path, monkeypatch):
    """Aponta o modulo de acesso para um banco novo em tmp (restaurado no teardown
    pelo `monkeypatch`: nenhum teste pode deixar o `DB_PATH` apontando para o tmp)."""
    caminho = str(tmp_path / "plano.db")
    monkeypatch.setattr(db, "DB_PATH", caminho)
    return caminho


def _extensivo():
    """Duas semanas sinteticas com a forma do grade_extensivo.json."""
    def t(n, disc, area, assunto, tipo, tipo_norm, nq=None, subtemas=None):
        return {"tarefa": n, "disciplina": disc, "area_norm": area, "assunto": assunto,
                "subtemas": subtemas or [assunto], "tipo": tipo, "tipo_norm": tipo_norm,
                "paginas_livro": [], "n_paginas": 0, "n_questoes": nq,
                "n_links_questoes": 0, "url_lista": None}
    return {"_meta": {"n_semanas": 2, "n_tasks": 6}, "semanas": [
        {"semana": 21, "tasks": [
            t(1, "Pediatria", "Pediatria", "Imunizações", "Teoria I", "teoria", 23),
            t(2, "Pediatria", "Pediatria", "Diarreia Aguda", "Teoria I", "teoria"),
            t(3, "Cirurgia", "Cirurgia", "Cirurgia Vascular", "Revisão", "revisao"),
            t(4, "Medicina Preventiva", "Preventiva", "Saúde do Idoso", "Revisão", "revisao"),
        ]},
        {"semana": 22, "tasks": [
            t(1, "Radiologia", "Multi", "Radiografia do Tórax", "Teoria", "teoria"),
            t(2, "Pediatria", "Pediatria", "Imunizações", "Revisão", "revisao"),
        ]},
    ]}


def _dashboard():
    """Snapshot sintetico. Cobre os 3 casos do DoD 3:
      - `Imunizações / Teoria I` casa exato e esta realizada -> feita;
      - `Diarreia` (o extensivo diz `Diarreia Aguda`) e variante de nome -> sem match;
      - `Cirurgia Vascular / Teoria I` existe realizada, mas o extensivo pede
        `Revisão` -> tipo diferente, sem match.
    """
    def d(area, n, assunto, tipo, realizada):
        return {"area": area, "tarefa": n, "assunto": assunto, "tipo": tipo,
                "realizada": realizada, "q": 0, "acertos": 0}
    return {"_doc": "sintetico", "lido_em": "2026-09-16", "n_tarefas": 5,
            "n_realizadas": 3, "tarefas": [
                d("Pediatria", 1, "Imunizações", "Teoria I", True),
                d("Pediatria", 2, "Diarreia", "Teoria I", True),
                d("Cirurgia", 3, "Cirurgia Vascular", "Teoria I", True),
                d("Preventiva", 4, "Saúde do Idoso", "Revisão", False),
                d("Pediatria", 5, "Imunizações", "Revisão", False),
            ]}


def _grade_rf():
    """Reta Final sintetica: S17 com 3 tarefas -- uma feita (casa `Teoria*` do mesmo
    assunto), uma pendente e uma da cauda de baixo peso."""
    def t(n, area, tema, tipo, tipo_norm, q, fonte_q="link_no_bloco"):
        return {"tarefa": n, "area_pdf": area, "area_norm": area, "multi_area": False,
                "tema": tema, "tipo": tipo, "tipo_norm": tipo_norm,
                "material_indicado": "resumo", "questoes": q, "questoes_fonte": fonte_q}
    return {"_meta": {"n_semanas": 1}, "semanas": [
        {"semana": 17, "inicio": "2026-07-20", "fim": "2026-07-26", "n_tasks": 4,
         "tasks": [
             t(1, "Pediatria", "Imunizações", "Teoria + Exercícios", "teoria", 22),
             t(2, "Cirurgia", "Cirurgia Vascular", "Revisão", "revisao", 43),
             t(3, "Oftalmo", "Glaucoma", "Revisão", "revisao", 30),
             t(4, "Nefrologia", "Distúrbios Ácido- Base; Distúrbios do Potássio",
               "Revisão", "revisao", 40, "rateio_igual"),
         ]},
    ]}


def _custom(area="Preventiva"):
    return {"_doc": "sintetico", "atualizado_em": "2026-09-16", "tarefas": [
        {"tarefa_fonte": 1, "semana_plano": 1, "ordem": 1, "area": area,
         "tema": "Prevencao Quaternaria", "tipo": "resumo", "tipo_norm": "teoria",
         "url_lista": None, "q_previstas": 0, "nota": "MFC-UERJ"},
    ]}


def _fontes(**troca):
    base = {"extensivo": _extensivo(), "dashboard": _dashboard(),
            "grade_rf": _grade_rf(), "custom": _custom()}
    base.update(troca)
    return base


def _linhas_por_chave(linhas):
    return {(l["fonte"], l["ref_semana_fonte"], l["tarefa_fonte"]): l for l in linhas}


# --------------------------------------------------------------- DDL idempotente

def test_ensure_plano_table_idempotente(tmp_path, monkeypatch):
    caminho = _usar_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(caminho)
    try:
        db._ensure_plano_table(conn)
        db._ensure_plano_table(conn)          # 2a vez nao pode levantar
        cols = {r[1] for r in conn.execute("PRAGMA table_info(plano_tarefas)")}
    finally:
        conn.close()
    esperadas = {"id", "fonte", "ref_semana_fonte", "tarefa_fonte", "semana_plano",
                 "ordem", "area", "tema", "tipo", "tipo_norm", "url_lista",
                 "q_previstas", "status", "data_conclusao", "sessao_bulk_id",
                 "origem_conclusao", "nota", "criado_em", "atualizado_em"}
    assert esperadas <= cols, f"colunas faltando: {esperadas - cols}"


def test_check_de_fonte_e_status_existe_no_schema(tmp_path, monkeypatch):
    caminho = _usar_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(caminho)
    try:
        db._ensure_plano_table(conn)
        for sql, params in (
                ("INSERT INTO plano_tarefas (fonte, status) VALUES (?, 'pendente')",
                 ("inventada",)),
                ("INSERT INTO plano_tarefas (fonte, status) VALUES ('rf', ?)",
                 ("quase_feita",))):
            try:
                conn.execute(sql, params)
                assert False, f"CHECK nao barrou: {params}"
            except sqlite3.IntegrityError:
                pass
    finally:
        conn.close()


# ---------------------------------------------------- status inicial (DoD 3)

def test_status_inicial_cobre_os_tres_casos(tmp_path, monkeypatch):
    _usar_db(tmp_path, monkeypatch)
    linhas, rel = plano.montar_linhas(**_fontes())
    por_chave = _linhas_por_chave(linhas)

    exato = por_chave[("extensivo", 21, 1)]        # Imunizações / Teoria I
    assert exato["status"] == "feita"
    assert exato["origem_conclusao"] == "dashboard_2026-09-10"

    variante = por_chave[("extensivo", 21, 2)]     # Diarreia Aguda x Diarreia
    assert variante["status"] == "pendente"
    assert variante["origem_conclusao"] is None

    outro_tipo = por_chave[("extensivo", 21, 3)]   # Revisão x Teoria I no Dashboard
    assert outro_tipo["status"] == "pendente"
    assert outro_tipo["origem_conclusao"] is None

    assert rel["extensivo_sem_match"] == 3, "variante, tipo diferente e Radiologia"
    assert not any(l["status"] == "feita" and l["origem_conclusao"] is None
                   for l in linhas), "nenhuma linha nasce feita sem origem declarada"


def test_normalizacao_casa_hifen_e_pipe():
    assert plano.normalizar("Distúrbios Ácido- Base") == "disturbios acido base"
    assert plano.normalizar("A | B") == "a b"
    assert plano.normalizar("  Saúde   do Idoso ") == "saude do idoso"


def test_rf_bundlada_so_e_feita_com_todas_as_partes():
    idx = plano.indexar_dashboard([
        {"area": "Nefrologia", "tarefa": 1, "assunto": "Distúrbios Ácido-Base",
         "tipo": "Revisão", "realizada": True, "q": 0, "acertos": 0},
        {"area": "Nefrologia", "tarefa": 2, "assunto": "Distúrbios do Potássio",
         "tipo": "Revisão", "realizada": False, "q": 0, "acertos": 0},
    ])
    assert plano.status_rf(idx, "Nefrologia", "Distúrbios Ácido- Base", "revisao") is True
    assert plano.status_rf(
        idx, "Nefrologia", "Distúrbios Ácido- Base; Distúrbios do Potássio",
        "revisao") is False
    assert plano.status_rf(idx, "Nefrologia", "Tema Que Nao Existe", "revisao") is False


# ------------------------------------------------- regras de fase (puras)

def test_ordenar_fase1_mapeia_semana_rf_para_o_plano():
    assert [plano.semana_fase1_pri1(s) for s in range(17, 29)] == \
        [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6]
    assert min(plano.semana_fase1_cm(s) for s in range(17, 29)) == 3
    assert max(plano.semana_fase1_cm(s) for s in range(17, 29)) == 7


def test_ordenar_fase1_classifica_por_bloco():
    linhas = [
        {"fonte": "rf", "ref_semana_fonte": 19, "tarefa_fonte": 2, "area": "Pediatria",
         "tema": "Diarreia", "tipo_norm": "teoria"},
        {"fonte": "rf", "ref_semana_fonte": 19, "tarefa_fonte": 3, "area": "Oftalmo",
         "tema": "Glaucoma", "tipo_norm": "revisao"},
        {"fonte": "rf", "ref_semana_fonte": 19, "tarefa_fonte": 4, "area": "Nefrologia",
         "tema": "Distúrbios do Potássio", "tipo_norm": "revisao"},
        {"fonte": "rf", "ref_semana_fonte": 19, "tarefa_fonte": 5, "area": "Neurologia",
         "tema": "Cefaleias", "tipo_norm": "revisao"},
        {"fonte": "rf", "ref_semana_fonte": 19, "tarefa_fonte": 6, "area": "Preventiva",
         "tema": "Estatística Médica", "tipo_norm": "revisao"},
    ]
    por_tarefa = {d["tarefa_fonte"]: d for d in plano.ordenar_fase1(linhas)}
    assert por_tarefa[2]["status"] == "pendente" and por_tarefa[2]["semana_plano"] == 2
    assert por_tarefa[3]["status"] == "cortada" and por_tarefa[3]["nota"] == plano.NOTA_CAUDA
    assert por_tarefa[4]["status"] == "pendente" and 3 <= por_tarefa[4]["semana_plano"] <= 7
    assert por_tarefa[5]["status"] == "cortada"
    assert por_tarefa[5]["nota"] == plano.NOTA_CM_EXTENSIVO
    assert por_tarefa[6]["status"] == "cortada", "Estatística Médica e cauda mesmo em Preventiva"


def test_ordenar_fase1_puxa_extensivo_para_semanas_1_e_2():
    linhas = [{"fonte": "extensivo", "ref_semana_fonte": s, "tarefa_fonte": 1,
               "area": "Preventiva", "tema": "X", "tipo_norm": "teoria"}
              for s in (17, 18, 21, 22)]
    saida = plano.ordenar_fase1(linhas)
    assert sorted(d["semana_plano"] for d in saida) == [1, 1, 2, 2]
    assert {d["ordem"] for d in saida} == {1}
    assert all(d["status"] == "pendente" for d in saida)


def test_ordenar_fase2_cobre_as_quatro_faixas():
    base = {"fonte": "extensivo", "tarefa_fonte": 3, "area": "Cardiologia",
            "tema": "Arritmias", "tipo_norm": "teoria", "feita": False}
    linhas = [
        {**base, "ref_semana_fonte": 10},                       # reserva
        {**base, "ref_semana_fonte": 30},                       # fase 2 normal
        {**base, "ref_semana_fonte": 50},                       # cortada
        {**base, "ref_semana_fonte": 30, "feita": True},        # feita
        {**base, "ref_semana_fonte": 24, "area": "Preventiva"},  # Preventiva puxada
        {**base, "ref_semana_fonte": 44, "tema": "IAMCSSST (Infarto Agudo do Miocardio)"},
    ]
    r = plano.ordenar_fase2(linhas)
    assert r[0]["status"] == "pendente" and r[0]["semana_plano"] is None
    assert r[0]["nota"] == plano.NOTA_RESERVA
    assert r[1]["semana_plano"] == 17          # 8 + (30 - 21)
    assert r[2]["status"] == "cortada" and r[2]["nota"] == plano.NOTA_FINAL_FSRS
    assert r[3]["status"] == "feita" and r[3]["origem_conclusao"] == plano.ORIGEM_DASHBOARD
    assert r[3]["semana_plano"] is None
    assert r[4]["semana_plano"] == 9           # Preventiva S24 -> semanas 8-9
    assert r[5]["semana_plano"] == 12          # IAM da S44 puxado


def test_q_prevista_marca_o_derivado():
    assert plano.q_prevista(23, "teoria") == (23.0, False)
    assert plano.q_prevista(None, "revisao") == (43.0, True)
    assert plano.q_prevista(None, "revisao_questoes") == (43.0, True)
    assert plano.q_prevista(None, "teoria") == (0.0, True)


def test_nota_carrega_q_estimada(tmp_path, monkeypatch):
    _usar_db(tmp_path, monkeypatch)
    linhas, _ = plano.montar_linhas(**_fontes())
    por_chave = _linhas_por_chave(linhas)
    sem_declarado = por_chave[("extensivo", 21, 3)]   # Cirurgia Vascular / Revisão
    assert sem_declarado["q_previstas"] == 43.0
    assert "q_estimada" in sem_declarado["nota"]
    declarado = por_chave[("extensivo", 21, 1)]       # Imunizações / Teoria I, 23q
    assert declarado["q_previstas"] == 23.0
    assert not (declarado["nota"] or "")


# -------------------------------------------------------- area fantasma (F89)

def test_area_fantasma_e_recusada(tmp_path, monkeypatch):
    _usar_db(tmp_path, monkeypatch)
    linha = {"fonte": "custom", "ref_semana_fonte": 0, "tarefa_fonte": 1,
             "area": "Clinica Medica", "tema": "X", "status": "pendente"}
    try:
        db.plano_upsert_tarefas([linha])
        assert False, "area fantasma passou pela porta"
    except AreaInvalida as e:
        assert "Clinica Medica" in str(e)
    conn = sqlite3.connect(db.DB_PATH) if os.path.exists(db.DB_PATH) else None
    if conn:
        try:
            db._ensure_plano_table(conn)
            assert conn.execute("SELECT COUNT(*) FROM plano_tarefas").fetchone()[0] == 0
        finally:
            conn.close()


def test_area_ausente_vira_null_com_nota(tmp_path, monkeypatch):
    """`Multi` (Radiologia / 'Todas as Disciplinas') nao e area do vocabulario: a linha
    nasce com `area=NULL` e a nota DIZENDO qual rotulo a fonte trazia -- divida
    declarada, nunca chute."""
    _usar_db(tmp_path, monkeypatch)
    linhas, rel = plano.montar_linhas(**_fontes())
    radiologia = _linhas_por_chave(linhas)[("extensivo", 22, 1)]
    assert radiologia["area"] is None
    assert "area_fonte=Radiologia" in radiologia["nota"]
    assert rel["extensivo_sem_area"] == 1
    db.plano_upsert_tarefas(linhas)          # nao levanta: area ausente != area fantasma


# ------------------------------------------------------ semeadura e COUNT-ASSERT

def test_semear_dry_run_nao_escreve(tmp_path, monkeypatch):
    _usar_db(tmp_path, monkeypatch)
    code, linhas, _ = plano.semear(apply=False, out=lambda *_: None, **_fontes())
    assert code == 0 and len(linhas) == 10      # 6 extensivo + 3 rf pendentes + 1 custom
    # "nao grava" inclui DDL: o dry-run nao pode nem CRIAR a tabela no banco real.
    conn = sqlite3.connect(db.DB_PATH)
    try:
        tabelas = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'")}
    finally:
        conn.close()
    assert "plano_tarefas" not in tabelas, "dry-run criou a tabela no banco"
    assert db.plano_listar() == [], "leitura sem plano semeado devolve vazio, nao erro"


def test_expect_errado_recusa_sem_gravar(tmp_path, monkeypatch):
    _usar_db(tmp_path, monkeypatch)
    code, _, _ = plano.semear(apply=True, expect=999, out=lambda *_: None, **_fontes())
    assert code == 2
    assert db.plano_listar() == [], "recusa por --expect nao pode gravar nada"


def test_semear_e_idempotente(tmp_path, monkeypatch):
    _usar_db(tmp_path, monkeypatch)
    fontes = _fontes()
    code, linhas, _ = plano.semear(apply=True, expect=10, out=lambda *_: None, **fontes)
    assert code == 0
    total = len(db.plano_listar())
    assert total == 10
    # a 2a execucao nao insere nada
    medida = db.plano_upsert_tarefas(linhas, aplicar=False)
    assert medida["novas"] == 0 and medida["existentes"] == 10
    code, _, _ = plano.semear(apply=True, expect=0, out=lambda *_: None, **fontes)
    assert code == 0
    assert len(db.plano_listar()) == 10


def test_reseed_nao_pisa_em_progresso(tmp_path, monkeypatch):
    """`status`/`data_conclusao`/`origem_conclusao` sao progresso (part-3) e ficam
    FORA do UPDATE: re-semear atualiza so os campos semeados."""
    _usar_db(tmp_path, monkeypatch)
    fontes = _fontes()
    plano.semear(apply=True, expect=10, out=lambda *_: None, **fontes)
    conn = sqlite3.connect(db.DB_PATH)
    try:
        conn.execute("UPDATE plano_tarefas SET status = 'feita', "
                     "data_conclusao = '2026-09-16 10:00:00', "
                     "origem_conclusao = 'operador' WHERE fonte = 'rf'")
        conn.commit()
    finally:
        conn.close()
    plano.semear(apply=True, expect=0, out=lambda *_: None, **fontes)
    rf = db.plano_listar(fonte="rf")
    assert rf and all(l["status"] == "feita" for l in rf)
    assert all(l["origem_conclusao"] == "operador" for l in rf)


def test_bloco_derivado_da_area():
    assert db.bloco_de("Preventiva") == "MFC"
    assert db.bloco_de("Pediatria") == "PED"
    assert db.bloco_de("Cirurgia") == "CIR"
    assert db.bloco_de("Ginecologia") == db.bloco_de("Obstetrícia") == "GO"
    assert db.bloco_de("Cardiologia") == "CM"
    assert db.bloco_de(None) == "CM"


def test_listar_filtra_por_semana_bloco_status_e_fonte(tmp_path, monkeypatch):
    _usar_db(tmp_path, monkeypatch)
    plano.semear(apply=True, expect=10, out=lambda *_: None, **_fontes())
    assert {l["fonte"] for l in db.plano_listar(fonte="custom")} == {"custom"}
    assert {l["status"] for l in db.plano_listar(status="feita")} == {"feita"}
    assert {l["bloco"] for l in db.plano_listar(bloco="MFC")} == {"MFC"}
    semana1 = db.plano_listar(semana=1)
    assert semana1 and {l["semana_plano"] for l in semana1} == {1}
    combinado = db.plano_listar(bloco="MFC", status="pendente", fonte="custom")
    assert len(combinado) == 1 and combinado[0]["tema"] == "Prevencao Quaternaria"
    assert db.plano_listar(semana=99) == []


def test_listar_json_serializa(tmp_path, monkeypatch):
    _usar_db(tmp_path, monkeypatch)
    plano.semear(apply=True, expect=10, out=lambda *_: None, **_fontes())
    saida = []
    code, linhas = plano.listar(fonte="custom", como_json=True, out=saida.append)
    assert code == 0
    dados = json.loads("\n".join(saida))
    assert len(dados) == 1 and dados[0]["bloco"] == "MFC"


def test_cli_semear_dry_run_pelo_main(tmp_path, monkeypatch, capsys):
    """O caminho de verdade: `main()` com argv, sem tocar o ipub.db real."""
    _usar_db(tmp_path, monkeypatch)
    code = plano.main(["--semear", "--dry-run"])
    assert code == 0
    texto = capsys.readouterr().out
    assert "COUNT-ASSERT por fonte" in texto
    assert len(db.plano_listar()) == 0, "dry-run nao grava"


def test_cli_apply_sem_expect_e_erro(tmp_path, monkeypatch):
    _usar_db(tmp_path, monkeypatch)
    try:
        plano.main(["--semear", "--apply"])
        assert False, "--apply sem --expect deveria abortar"
    except SystemExit as e:
        assert e.code == 2


# --------------------------------------------------- regressao viva (fontes reais)

def test_fontes_reais_reproduzem_os_numeros_medidos():
    """Trava os numeros que o orquestrador mediu em 16/09/2026 a partir dos arquivos
    versionados. Divergencia aqui e sinal de que a fonte mudou -- investigar, nunca
    ajustar a constante. Le so JSON: nenhum banco e aberto."""
    linhas, rel = plano.montar_linhas()
    assert rel["extensivo_total"] == 735
    assert rel["extensivo_s21_s48"] == 425
    assert rel["rf_total_s17_s28"] == 149
    assert rel["rf_pendentes"] == 139, (
        "139 pendentes da Reta Final S17-S28 -- referencia da s183")
    assert len(linhas) == 735 + 139 + rel["custom"]
    q_rf = sum(l["q_previstas"] for l in linhas if l["fonte"] == "rf")
    assert round(q_rf, 1) == 4035.5, "as ~4.036q pendentes da Reta Final"


def test_fontes_reais_nao_inventam_area():
    """Toda area gravada tem que estar no vocabulario (ou ser NULL declarado)."""
    from app.utils.areas import AREAS_VALIDAS
    linhas, rel = plano.montar_linhas()
    fora = {l["area"] for l in linhas if l["area"] and l["area"] not in AREAS_VALIDAS}
    assert not fora, f"areas fora de core/areas.json: {sorted(fora)}"
    assert rel["extensivo_sem_area"] == 26, (
        "6 tarefas de Radiologia (S41-S47) + 20 de 'Todas as Disciplinas' (S50-S52)")


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))
