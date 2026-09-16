"""test_fsrs_queue_player.py -- o player de cards como superficie de ENTRADA e o
CLI como unico writer (spec .vibeflow/specs/plano-ssot-e-cards-v2-part-9.md).

O que esta suite trava, em ordem de risco:

1. **O export nao vaza campo que a pagina nao mostra.** `needs_qualitative` e
   `due` sao estado do FSRS; a tela nao os usa e o `--record-lote` nao precisa
   deles. Campo a mais num artefato publicado e superficie a mais.
2. **Card com `</script>` nao quebra a pagina.** O lote entra num
   `<script type="application/json">`; `<`, `>` e `&` viajam escapados em
   `\\uXXXX` -- JSON equivalente, `</script>` impossivel de fechar por dentro.
3. **A pagina e input NAO confiavel.** `card_id` fora do lote e rating fora de
   1..4 sao ERRO; `card_id` repetido conta UMA vez (a primeira nota) com AVISO
   -- o relearning da pagina nunca gera segunda nota gravavel.
4. **COUNT-ASSERT.** `--apply` sem `--expect` igual ao N medido nao grava nada,
   e depois de gravar o `fsrs_revlog` tem de ter crescido EXATAMENTE N.
5. **`record_review` continua sendo o unico caminho de escrita.** O
   `fsrs_queue.py` nao ganha tabela nova (varredura da allowlist F49).

Db sintetico em arquivo temporario -- o `ipub.db` real NUNCA e tocado.
Pytest-nativo + standalone (`python tools/test_fsrs_queue_player.py`).
"""
import contextlib
import io
import json
import os
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from app.utils import db  # noqa: E402
from tools.fsrs_queue import (  # noqa: E402
    CAMPOS_PLAYER,
    MARCA_ABRE,
    MARCA_FECHA,
    aplicar_notas,
    injetar_lote,
    ler_notas,
    montar_lote,
    teto_do_dia,
)
from tools.test_writer_allowlist import ALLOWLIST, ROOT, tabelas_escritas  # noqa: E402

_DDL = """
CREATE TABLE flashcards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    questao_id INTEGER, tema_id INTEGER, tipo TEXT,
    frente_contexto TEXT, frente_pergunta TEXT, verso_resposta TEXT,
    verso_regra_mestre TEXT, verso_armadilha TEXT,
    quality_source TEXT DEFAULT 'legacy', card_version INTEGER DEFAULT 1,
    needs_qualitative INTEGER DEFAULT 0);
CREATE TABLE fsrs_cards (
    card_id INTEGER PRIMARY KEY, state INTEGER DEFAULT 0, due DATETIME,
    stability REAL DEFAULT 0.0, difficulty REAL DEFAULT 0.0,
    elapsed_days INTEGER DEFAULT 0, scheduled_days INTEGER DEFAULT 0,
    reps INTEGER DEFAULT 0, lapses INTEGER DEFAULT 0, last_review DATETIME,
    FOREIGN KEY (card_id) REFERENCES flashcards(id));
CREATE TABLE fsrs_revlog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER, rating INTEGER, state INTEGER, due DATETIME,
    stability REAL, difficulty REAL, elapsed_days INTEGER,
    last_elapsed_days INTEGER, scheduled_days INTEGER,
    review_time DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE reforja_marks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL,
    evento TEXT NOT NULL CHECK (evento IN ('marcada','fechada','descartada')),
    motivo TEXT NOT NULL, evidencia TEXT, origem TEXT, criado_em DATETIME,
    FOREIGN KEY (card_id) REFERENCES flashcards(id));
"""


def _db_temp(ids=(1, 2)):
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    con = sqlite3.connect(path)
    con.executescript(_DDL)
    for i in ids:
        con.execute("INSERT INTO flashcards (id, tipo, frente_pergunta, verso_resposta, "
                    "quality_source) VALUES (?, 'conteudo', 'P?', 'R.', 'qualitative')", (i,))
        con.execute("INSERT INTO fsrs_cards (card_id, state, due) "
                    "VALUES (?, 0, datetime('now'))", (i,))
    con.commit()
    con.close()
    return path


def _com_db(fn, ids=(1, 2)):
    tmp = _db_temp(ids)
    orig = db.DB_PATH
    db.DB_PATH = tmp
    try:
        return fn(tmp)
    finally:
        db.DB_PATH = orig
        os.remove(tmp)


def _conta(tmp, tabela):
    con = sqlite3.connect(tmp)
    n = con.execute("SELECT COUNT(*) FROM %s" % tabela).fetchone()[0]
    con.close()
    return int(n)


def _fila_crua():
    """Duas linhas no formato que `get_cards_by_bucket` devolve -- com os campos
    que o player NAO deve receber (`needs_qualitative`, `due`)."""
    return [
        {"card_id": 7, "frente_contexto": "Homem, 62a", "frente_pergunta": "Conduta?",
         "verso_resposta": "R1", "verso_regra_mestre": "RM1", "verso_armadilha": "A1",
         "needs_qualitative": 0, "due": "2026-09-16 08:00:00", "area": "Clinica",
         "tema": "IC", "selection_reason": "vencido", "bucket": "atrasados"},
        {"card_id": 9, "frente_contexto": None, "frente_pergunta": "Qual o alvo?",
         "verso_resposta": "R2", "verso_regra_mestre": None, "verso_armadilha": None,
         "needs_qualitative": 1, "due": "2026-09-16 09:00:00", "area": "Pediatria",
         "tema": "Asma", "selection_reason": "novo", "bucket": "novos"},
    ]


# --------------------------------------------------------------------------
# 1. Export: so o que vai para a tela
# --------------------------------------------------------------------------

def test_export_carrega_so_os_campos_da_tela():
    lote = montar_lote(_fila_crua(), sessao="2026-09-16", gerado_em="2026-09-16T10:00:00")
    assert lote["sessao"] == "2026-09-16" and lote["total"] == 2
    for card in lote["cards"]:
        assert set(card) == set(CAMPOS_PLAYER), (
            "campo fora do contrato de tela: %s" % sorted(set(card) ^ set(CAMPOS_PLAYER)))
        assert "needs_qualitative" not in card and "due" not in card
    assert [c["card_id"] for c in lote["cards"]] == [7, 9], "ordem do --list preservada"
    assert lote["cards"][0]["selection_reason"] == "vencido"


def test_export_corta_no_limite_preservando_a_ordem():
    lote = montar_lote(_fila_crua(), limit=1, sessao="s")
    assert lote["total"] == 1 and lote["cards"][0]["card_id"] == 7


def test_teto_do_dia_vem_do_day_plan_em_regime_de_divida():
    """F64: `vencidos = atrasados + hoje`. 70 vencidos disparam o regime e o teto
    sobe para min(60+70, 1.5*60) = 90. O fallback (60) NAO passaria aqui."""
    fila = ([{"bucket": "atrasados"}] * 50) + ([{"bucket": "hoje"}] * 20)
    assert teto_do_dia(fila) == 90
    assert teto_do_dia([{"bucket": "novos"}] * 5) == 60


# --------------------------------------------------------------------------
# 2. Build: injecao + escape de </script>
# --------------------------------------------------------------------------

_TEMPLATE = ('<html><body><script id="lote" type="application/json">'
             '{"sessao":"x","cards":[]}</script>\n<script>var a=1;</script></body></html>')


def _lote_do_html(html):
    ini = html.find(MARCA_ABRE) + len(MARCA_ABRE)
    fim = html.find(MARCA_FECHA, ini)
    return json.loads(html[ini:fim])


def test_build_injeta_o_lote_e_escapa_fechamento_de_script():
    hostil = {"card_id": 1, "frente_contexto": 'aspas "duplas" e <b>tag</b>',
              "frente_pergunta": "</script><script>alert(1)</script> & mais?",
              "verso_resposta": "a < b > c", "verso_regra_mestre": None,
              "verso_armadilha": None, "area": "A", "tema": "T",
              "selection_reason": "novo", "bucket": "novos"}
    lote = {"sessao": "2026-09-16", "gerado_em": "t", "total": 1, "cards": [hostil]}
    html = injetar_lote(_TEMPLATE, lote)
    ini = html.find(MARCA_ABRE) + len(MARCA_ABRE)
    fim = html.find(MARCA_FECHA, ini)
    payload = html[ini:fim]
    assert "<" not in payload and ">" not in payload and "&" not in payload, (
        "o payload injetado nao pode conter < > & crus")
    assert "\\u003c" in payload, "escape \\uXXXX presente"
    assert _lote_do_html(html) == lote, "JSON.parse reconstroi o lote identico"
    assert html.count("<script") == 2, "nenhum <script> novo nasceu da injecao"


def test_build_recusa_template_sem_marcador():
    try:
        injetar_lote("<html></html>", {"cards": []})
        raise AssertionError("template sem marcador deveria falhar alto")
    except ValueError:
        pass


def test_build_recusa_marcador_AMBIGUO():
    """Bug real medido na 1a execucao: um comentario do template citava a propria
    tag; o `find` casou com a MENCAO e a injecao comeu 4 KB da pagina (o <style>
    inteiro) ate o proximo </script>. Marcador duplicado agora falha alto."""
    duplicado = "<!-- veja " + MARCA_ABRE + " -->" + _TEMPLATE
    try:
        injetar_lote(duplicado, {"cards": []})
        raise AssertionError("marcador ambiguo deveria falhar alto")
    except ValueError as e:
        assert "exatamente 1" in str(e)


def test_template_real_e_injetavel_e_tem_wrap_unico():
    from tools.fsrs_queue import TEMPLATE_PLAYER
    txt = TEMPLATE_PLAYER.read_text(encoding="utf-8")
    assert txt.count("max-width") <= 2, "um .wrap unico constrange a pagina (memoria s151)"
    assert 'prefers-color-scheme: dark' in txt and ':root[data-theme="dark"]' in txt
    assert ':root:not([data-theme="light"])' in txt
    assert "prefers-reduced-motion" in txt and "focus-visible" in txt
    assert 'claude.use("db")' in txt and "sessoes/" in txt
    # A unica persistencia da pagina e a capability db: nenhuma tabela do FSRS
    # aparece ali, nem sob outro nome (a fronteira e declarada no cabecalho).
    assert "fsrs_revlog" not in txt and "fsrs_cards" not in txt
    assert "aposentar" not in txt.lower(), "sem botao aposentar (decisao do usuario)"
    html = injetar_lote(txt, {"sessao": "t", "gerado_em": "t", "total": 0, "cards": []})
    assert _lote_do_html(html)["sessao"] == "t"


# --------------------------------------------------------------------------
# 3. Notas: input nao confiavel
# --------------------------------------------------------------------------

_CARDS = [{"card_id": 1, "selection_reason": "vencido"},
          {"card_id": 2, "selection_reason": "novo"}]


def test_nota_fora_do_lote_e_erro():
    regs, erros, _ = ler_notas({"notas": [{"card_id": 99, "rating_primeira": 3}]}, _CARDS)
    assert regs == [] and any("fora do lote" in e for e in erros)


def test_rating_fora_de_1_a_4_e_erro():
    regs, erros, _ = ler_notas({"notas": [{"card_id": 1, "rating_primeira": 7}]}, _CARDS)
    assert regs == [] and any("rating invalido" in e for e in erros)


def test_duplicata_conta_uma_vez_com_aviso():
    regs, erros, avisos = ler_notas({"notas": [
        {"card_id": 1, "rating_primeira": 2},
        {"card_id": 1, "rating_primeira": 4},
    ]}, _CARDS)
    assert erros == []
    assert len(regs) == 1 and regs[0]["rating"] == 2, "a PRIMEIRA nota e a gravavel"
    assert any("repetido" in a for a in avisos)


def test_defeito_sem_motivo_e_erro():
    regs, erros, _ = ler_notas({"notas": [{"card_id": 1, "defeito": True}]}, _CARDS)
    assert regs == [] and any("SEM motivo" in e for e in erros)


def test_selection_reason_vem_do_export_nao_da_pagina():
    regs, erros, _ = ler_notas({"notas": [
        {"card_id": 1, "rating_primeira": 3, "selection_reason": "mentira"}]}, _CARDS)
    assert erros == [] and regs[0]["selection_reason"] == "vencido"


# --------------------------------------------------------------------------
# 4. Gravacao: dry-run, COUNT-ASSERT, duplicata, defeito
# --------------------------------------------------------------------------

def test_dry_run_nao_grava_nada():
    def corpo(tmp):
        regs, _, _ = ler_notas({"notas": [{"card_id": 1, "rating_primeira": 3}]}, _CARDS)
        saida = []
        code, n = aplicar_notas(regs, apply=False, out=saida.append)
        assert code == 0 and n == 1
        assert _conta(tmp, "fsrs_revlog") == 0, "dry-run nao toca o revlog"
        assert any("DRY-RUN" in l for l in saida)
    _com_db(corpo)


def test_expect_errado_recusa_sem_gravar():
    def corpo(tmp):
        regs, _, _ = ler_notas({"notas": [{"card_id": 1, "rating_primeira": 3}]}, _CARDS)
        saida = []
        code, n = aplicar_notas(regs, apply=True, expect=99, out=saida.append)
        assert code == 2 and n == 1
        assert _conta(tmp, "fsrs_revlog") == 0, "recusa por --expect NAO grava"
        assert any("RECUSADO" in l for l in saida)
        # sem --expect tambem recusa
        code2, _ = aplicar_notas(regs, apply=True, expect=None, out=saida.append)
        assert code2 == 2 and _conta(tmp, "fsrs_revlog") == 0
    _com_db(corpo)


def test_duplicata_gera_uma_unica_revisao():
    def corpo(tmp):
        regs, _, avisos = ler_notas({"notas": [
            {"card_id": 1, "rating_primeira": 3},
            {"card_id": 1, "rating_primeira": 1},
        ]}, _CARDS)
        assert avisos, "duplicata avisa (WARN-first), nao bloqueia"
        with contextlib.redirect_stdout(io.StringIO()):
            code, n = aplicar_notas(regs, apply=True, expect=1, out=lambda *_: None)
        assert code == 0 and n == 1
        assert _conta(tmp, "fsrs_revlog") == 1, "1 card = 1 linha de revlog"
    _com_db(corpo)


def test_lote_grava_n_revisoes_e_bate_o_count_assert():
    def corpo(tmp):
        regs, erros, _ = ler_notas({"notas": [
            {"card_id": 1, "rating_primeira": 3},
            {"card_id": 2, "rating_primeira": 4},
        ]}, _CARDS)
        assert erros == []
        saida = []
        with contextlib.redirect_stdout(io.StringIO()):
            code, n = aplicar_notas(regs, apply=True, expect=2, out=saida.append)
        assert code == 0 and n == 2
        assert _conta(tmp, "fsrs_revlog") == 2
        assert any("COUNT-ASSERT pos batido" in l for l in saida)
        con = sqlite3.connect(tmp)
        reasons = [r[0] for r in con.execute(
            "SELECT selection_reason FROM fsrs_revlog ORDER BY card_id")]
        con.close()
        assert reasons == ["vencido", "novo"], "proveniencia do export chega no revlog"
    _com_db(corpo)


def test_defeito_vira_marca_de_reforja_e_nao_conta_revisao():
    def corpo(tmp):
        regs, erros, _ = ler_notas({"notas": [
            {"card_id": 1, "defeito": True, "motivo": "pergunta composta"},
            {"card_id": 2, "rating_primeira": 3},
        ]}, _CARDS)
        assert erros == []
        with contextlib.redirect_stdout(io.StringIO()):
            code, n = aplicar_notas(regs, apply=True, expect=1, out=lambda *_: None)
        assert code == 0 and n == 1, "defeito nao entra no N de revisoes"
        assert _conta(tmp, "fsrs_revlog") == 1
        con = sqlite3.connect(tmp)
        linha = con.execute("SELECT card_id, evento, motivo, origem FROM reforja_marks").fetchall()
        con.close()
        assert linha == [(1, "marcada", "pergunta composta", "player")]
    _com_db(corpo)


def test_count_assert_pos_pega_revisao_que_nao_gravou():
    """Se um record falhar no meio do lote, o crescimento do revlog nao bate o N
    e o CLI sai 2 -- fail-loud, nunca 'gravei quase tudo' em silencio."""
    regs = [{"card_id": 1, "rating": 3, "defeito": False, "motivo": "",
             "selection_reason": "vencido"}]
    saida = []
    code, n = aplicar_notas(regs, apply=True, expect=1, out=saida.append,
                            record_fn=lambda *a, **k: None,
                            reforja_fn=lambda *a, **k: None,
                            count_fn=lambda: 0)
    assert code == 2 and n == 1
    assert any("COUNT-ASSERT pos FALHOU" in l for l in saida)


# --------------------------------------------------------------------------
# 5. O caminho de escrita nao mudou
# --------------------------------------------------------------------------

def test_fsrs_queue_nao_ganhou_tabela_nova():
    """Invariante C/F49: o player nao abre um segundo caminho de escrita. O
    `fsrs_queue.py` continua sem nenhum INSERT/UPDATE/DELETE proprio -- tudo
    passa por `app/utils/db.py` (record_review, marcar_reforja)."""
    fonte = (ROOT / "tools" / "fsrs_queue.py").read_text(encoding="utf-8-sig")
    assert tabelas_escritas(fonte) == set(), (
        "fsrs_queue.py passou a escrever direto: %s" % sorted(tabelas_escritas(fonte)))
    assert "tools/fsrs_queue.py" not in ALLOWLIST, (
        "fsrs_queue.py nao pode virar writer na allowlist -- ele e camada fina")
    assert "import sqlite3" not in fonte, "a camada fina nao abre sqlite3 proprio"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))
