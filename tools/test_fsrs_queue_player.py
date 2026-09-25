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
from datetime import datetime, timedelta, timezone

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
    anexar_agenda,
    aplicar_notas,
    aviso_hub,
    injetar_lote,
    ler_notas,
    montar_lote,
    teto_do_dia,
    triar_notas,
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
    """F64: `vencidos = atrasados + hoje`. s196: teto 90 com CAP 1.0 -- regime de
    divida nao passa de 90. O fallback (60) NAO passaria aqui."""
    fila = ([{"bucket": "atrasados"}] * 50) + ([{"bucket": "hoje"}] * 50)
    assert teto_do_dia(fila) == 90
    assert teto_do_dia([{"bucket": "novos"}] * 5) == 90


def test_teto_do_dia_desconta_o_que_ja_foi_revisado_hoje():
    """s194: o teto e do DIA, nao do lote. Com o /hub-backend publicando um lote novo
    a cada lote drenado, sem o desconto cada lote traria o teto inteiro (a s194 tinha
    159 revisoes gravadas e o export ainda montava 90). Saldo nunca fica negativo."""
    fila = ([{"bucket": "atrasados"}] * 50) + ([{"bucket": "hoje"}] * 20)
    assert teto_do_dia(fila, consumo_hoje=30) == 60
    assert teto_do_dia(fila, consumo_hoje=159) == 0
    assert teto_do_dia([{"bucket": "novos"}] * 5, consumo_hoje=None) == 90


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

# s193 (medhub-hub-v0-part-2): toda nota da pagina tem `ts` (ISO UTC); sem ele a nota
# e REJEITADA. As fixtures antigas ganharam ts no passado; os asserts ficaram intocados.
_TS = "2026-09-16T10:00:00.144Z"
_TS_DEPOIS = "2026-09-16T10:05:00.500Z"


def test_nota_fora_do_lote_e_erro():
    regs, erros, _ = ler_notas({"notas": [{"card_id": 99, "rating_primeira": 3,
                                           "ts": _TS}]}, _CARDS)
    assert regs == [] and any("fora do lote" in e for e in erros)


def test_rating_fora_de_1_a_4_e_erro():
    regs, erros, _ = ler_notas({"notas": [{"card_id": 1, "rating_primeira": 7,
                                           "ts": _TS}]}, _CARDS)
    assert regs == [] and any("rating invalido" in e for e in erros)


def test_duplicata_conta_uma_vez_com_aviso():
    regs, erros, avisos = ler_notas({"notas": [
        {"card_id": 1, "rating_primeira": 2, "ts": _TS},
        {"card_id": 1, "rating_primeira": 4, "ts": _TS_DEPOIS},
    ]}, _CARDS)
    assert erros == []
    assert len(regs) == 1 and regs[0]["rating"] == 2, "a PRIMEIRA nota e a gravavel"
    assert any("repetido" in a for a in avisos)


def test_defeito_sem_motivo_e_erro():
    regs, erros, _ = ler_notas({"notas": [{"card_id": 1, "defeito": True,
                                           "ts": _TS}]}, _CARDS)
    assert regs == [] and any("SEM motivo" in e for e in erros)


def test_selection_reason_vem_do_export_nao_da_pagina():
    regs, erros, _ = ler_notas({"notas": [
        {"card_id": 1, "rating_primeira": 3, "selection_reason": "mentira",
         "ts": _TS}]}, _CARDS)
    assert erros == [] and regs[0]["selection_reason"] == "vencido"


# --------------------------------------------------------------------------
# 4. Gravacao: dry-run, COUNT-ASSERT, duplicata, defeito
# --------------------------------------------------------------------------

def test_dry_run_nao_grava_nada():
    def corpo(tmp):
        regs, _, _ = ler_notas({"notas": [{"card_id": 1, "rating_primeira": 3,
                                           "ts": _TS}]}, _CARDS)
        saida = []
        code, n = aplicar_notas(regs, apply=False, out=saida.append)
        assert code == 0 and n == 1
        assert _conta(tmp, "fsrs_revlog") == 0, "dry-run nao toca o revlog"
        assert any("DRY-RUN" in l for l in saida)
    _com_db(corpo)


def test_expect_errado_recusa_sem_gravar():
    def corpo(tmp):
        regs, _, _ = ler_notas({"notas": [{"card_id": 1, "rating_primeira": 3,
                                           "ts": _TS}]}, _CARDS)
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
            {"card_id": 1, "rating_primeira": 3, "ts": _TS},
            {"card_id": 1, "rating_primeira": 1, "ts": _TS_DEPOIS},
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
            {"card_id": 1, "rating_primeira": 3, "ts": _TS},
            {"card_id": 2, "rating_primeira": 4, "ts": _TS_DEPOIS},
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
            {"card_id": 1, "defeito": True, "motivo": "pergunta composta", "ts": _TS},
            {"card_id": 2, "rating_primeira": 3, "ts": _TS_DEPOIS},
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
             "selection_reason": "vencido", "quando": datetime(2026, 9, 16, 7, 0, 0)}]
    saida = []
    code, n = aplicar_notas(regs, apply=True, expect=1, out=saida.append,
                            record_fn=lambda *a, **k: None,
                            reforja_fn=lambda *a, **k: None,
                            count_fn=lambda: 0,
                            gravado_fn=lambda ids: {})   # s193: sem ler o banco real
    assert code == 2 and n == 1
    assert any("COUNT-ASSERT pos FALHOU" in l for l in saida)


# --------------------------------------------------------------------------
# 4b. s193 (medhub-hub-v0-part-2): relogio da revisao, idempotencia, quarentena
# --------------------------------------------------------------------------

BRT = timezone(timedelta(hours=-3))
_AGORA = datetime(2026, 9, 22, 20, 0, 0)       # relogio do banco CONGELADO (LOCAL naive)


@contextlib.contextmanager
def _relogio(instante=_AGORA):
    """`db.agora` congelado: a recusa de futuro do writer e o `ler_notas` usam o mesmo."""
    orig = db.agora
    db.agora = lambda: instante
    try:
        yield
    finally:
        db.agora = orig


def _gravar(notas, expect, cards=_CARDS):
    """ler -> aplicar com --apply, fuso injetado (-03:00). Devolve (code, n, saida)."""
    regs, rejeitadas, _ = ler_notas({"notas": notas}, cards, fuso=BRT)
    assert rejeitadas == [], rejeitadas
    saida = []
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        code, n = aplicar_notas(regs, apply=True, expect=expect, out=saida.append)
    return code, n, saida


def _review_times(tmp, card_id=1):
    con = sqlite3.connect(tmp)
    linhas = [r[0] for r in con.execute(
        "SELECT review_time FROM fsrs_revlog WHERE card_id = ? ORDER BY id", (card_id,))]
    con.close()
    return linhas


def test_releitura_da_mesma_sessao_grava_zero_com_expect_0():
    """DoD 2 do PRD: ler e gravar a MESMA sessao duas vezes grava ZERO na segunda."""
    notas = [{"card_id": 1, "rating_primeira": 3, "ts": _TS},
             {"card_id": 2, "rating_primeira": 1, "ts": _TS_DEPOIS}]

    def corpo(tmp):
        with _relogio():
            code, n, _ = _gravar(notas, expect=2)
            assert code == 0 and n == 2 and _conta(tmp, "fsrs_revlog") == 2
            code, n, saida = _gravar(notas, expect=0)
        assert code == 0 and n == 0, "a releitura mede N=0 e o --expect 0 passa"
        assert _conta(tmp, "fsrs_revlog") == 2, "nada regravado"
        assert any("JA GRAVADAS" in l and "1, 2" in l for l in saida), saida
    _com_db(corpo)


def test_duas_notas_do_mesmo_card_em_duas_sessoes_gravam_nos_seus_ts():
    """PROPRIEDADE (`/ai-eng`, 22/09): ts1 < ts2 em sessoes diferentes, gravadas em
    ordem -> 2 linhas com review_time = ts1, ts2. Com o relogio da gravacao, a 2a
    sumiria (`review_time >= ts`) ou o intervalo contaria da hora errada."""
    def corpo(tmp):
        with _relogio():
            assert _gravar([{"card_id": 1, "rating_primeira": 3,
                             "ts": "2026-09-20T10:00:00.500Z"}], expect=1)[0] == 0
            assert _gravar([{"card_id": 1, "rating_primeira": 2,
                             "ts": "2026-09-21T13:30:00.900Z"}], expect=1)[0] == 0
        assert _review_times(tmp) == ["2026-09-20 07:00:00", "2026-09-21 10:30:00"]
    _com_db(corpo)


def test_ordem_inversa_sai_fora_de_ordem_reportada_e_nao_grava():
    """A mesma propriedade ao contrario: a nota de ts1 chega DEPOIS da de ts2 -> FORA DE
    ORDEM, reportada com o motivo, nunca gravada por cima (o card so anda para a frente)."""
    def corpo(tmp):
        with _relogio():
            assert _gravar([{"card_id": 1, "rating_primeira": 2,
                             "ts": "2026-09-21T13:30:00.900Z"}], expect=1)[0] == 0
            code, n, saida = _gravar([{"card_id": 1, "rating_primeira": 3,
                                       "ts": "2026-09-20T10:00:00.500Z"}], expect=0)
        assert code == 0 and n == 0
        assert _review_times(tmp) == ["2026-09-21 10:30:00"], "1 linha so"
        fora = [l for l in saida if "FORA DE ORDEM" in l]
        assert len(fora) == 1 and "2026-09-20 07:00:00" in fora[0] and (
            "2026-09-21 10:30:00" in fora[0]), saida
    _com_db(corpo)


def test_nota_utc_entra_no_revlog_em_hora_local():
    """Conversao UTC -> local com fuso INJETADO: a nota real do #92 (10:17:50.144Z)
    grava review_time 07:17:50 -- o momento em que ele respondeu no celular."""
    def corpo(tmp):
        with _relogio():
            assert _gravar([{"card_id": 1, "rating_primeira": 1,
                             "ts": "2026-09-22T10:17:50.144Z"}], expect=1)[0] == 0
        assert _review_times(tmp) == ["2026-09-22 07:17:50"]
    _com_db(corpo)


def test_defeito_relido_nao_remarca():
    notas = [{"card_id": 1, "defeito": True, "motivo": "pergunta composta", "ts": _TS},
             {"card_id": 2, "rating_primeira": 3, "ts": _TS_DEPOIS}]

    def corpo(tmp):
        with _relogio():
            assert _gravar(notas, expect=1)[0] == 0
            code, n, saida = _gravar(notas, expect=0)
        assert code == 0 and n == 0
        assert _conta(tmp, "reforja_marks") == 1, "a releitura nao abre 2a marca"
        assert any("DEFEITO JA MARCADO" in l for l in saida), saida
    _com_db(corpo)


def test_quarentena_grava_os_validos_e_reporta_cada_doc_estranho():
    """Quarentena no writer: 1 doc estranho de cada tipo + 2 validos -> grava 2, cada
    estranho sai com o seu motivo, e nada dele e gravado."""
    estranhos = [
        ({"card_id": 99, "rating_primeira": 3, "ts": _TS}, "fora do lote"),
        ({"card_id": 1, "rating_primeira": 9, "ts": _TS}, "rating invalido"),
        ({"card_id": 1, "rating_primeira": 3}, "ts ausente"),
        ({"card_id": 1, "rating_primeira": 3, "ts": "amanha"}, "ts ilegivel"),
        ({"card_id": 1, "rating_primeira": 3, "ts": "2026-09-30T10:00:00Z"}, "ts no futuro"),
        ({"card_id": 2, "defeito": True, "ts": _TS}, "SEM motivo"),
        ({"card_id": 2, "ts": _TS}, "sem rating e sem defeito"),
    ]
    validos = [{"card_id": 1, "rating_primeira": 3, "ts": _TS},
               {"card_id": 2, "rating_primeira": 4, "ts": _TS_DEPOIS}]

    def corpo(tmp):
        with _relogio():
            regs, rejeitadas, _ = ler_notas(
                {"notas": [n for n, _ in estranhos] + validos}, _CARDS, fuso=BRT)
            assert len(rejeitadas) == len(estranhos), rejeitadas
            for (_, motivo), linha in zip(estranhos, rejeitadas):
                assert motivo in linha, (motivo, linha)
            with contextlib.redirect_stderr(io.StringIO()):
                code, n = aplicar_notas(regs, apply=True, expect=2, out=lambda *_: None)
        assert code == 0 and n == 2
        assert _conta(tmp, "fsrs_revlog") == 2 and _conta(tmp, "reforja_marks") == 0
    _com_db(corpo)


def test_rejeitada_e_fora_de_ordem_vao_inteiras_para_a_quarentena_no_apply():
    """Decisao 4 do `/ai-eng` (s193): nada sai do `db` da pagina sem copia no SSOT. No
    `--apply`, doc rejeitado e nota FORA DE ORDEM sao arquivados INTEIROS, com o motivo;
    reler e regravar nao duplica; dry-run nao escreve."""
    def corpo(tmp):
        with tempfile.TemporaryDirectory() as pasta, _relogio():
            q = os.path.join(pasta, "q.json")
            assert _gravar([{"card_id": 1, "rating_primeira": 2,
                             "ts": "2026-09-21T13:30:00Z"}], expect=1)[0] == 0
            notas = {"notas": [{"card_id": 99, "rating_primeira": 3, "ts": _TS},
                               {"card_id": 1, "rating_primeira": 3, "ts": "2026-09-20T10:00:00Z"},
                               {"card_id": 2, "rating_primeira": 4, "ts": _TS_DEPOIS}]}
            regs, rejeitadas, _ = triar_notas(notas, _CARDS, fuso=BRT)
            aplicar_notas(regs, apply=False, rejeitadas=rejeitadas, quarentena=q, sessao="t",
                          out=lambda *_: None)
            assert not os.path.exists(q), "dry-run nao arquiva"
            for esperado in (1, 0):                              # 2a vez = releitura
                with contextlib.redirect_stderr(io.StringIO()):
                    code, n = aplicar_notas(regs, apply=True, expect=esperado,
                                            rejeitadas=rejeitadas, quarentena=q, sessao="t",
                                            out=lambda *_: None)
                assert code == 0 and n == esperado
            arq = json.load(open(q, encoding="utf-8"))
        tipos = sorted((it["tipo"], it["doc"]["card_id"]) for it in arq["itens"])
        assert tipos == [("fora_de_ordem", 1), ("rejeitada", 99)], "sem duplicata na releitura"
        assert all(it["motivo"] and it["arquivado_em"] for it in arq["itens"])
        assert arq["sessao"] == "t"
    _com_db(corpo)


def test_recusa_do_expect_nao_arquiva_nem_marca_o_hub():
    def corpo(tmp):
        with tempfile.TemporaryDirectory() as pasta, _relogio():
            q, m = os.path.join(pasta, "q.json"), os.path.join(pasta, "m.json")
            regs, rejeitadas, _ = triar_notas({"notas": [
                {"card_id": 99, "rating_primeira": 3, "ts": _TS},
                {"card_id": 1, "rating_primeira": 3, "ts": _TS}]}, _CARDS, fuso=BRT)
            code, _ = aplicar_notas(regs, apply=True, expect=7, rejeitadas=rejeitadas,
                                    quarentena=q, marcador=m, sessao="t", out=lambda *_: None)
            assert code == 2 and not os.path.exists(q) and not os.path.exists(m)
            with contextlib.redirect_stderr(io.StringIO()):
                code, _ = aplicar_notas(regs, apply=True, expect=1, rejeitadas=rejeitadas,
                                        quarentena=q, marcador=m, sessao="t", out=lambda *_: None)
            marca = json.load(open(m, encoding="utf-8"))
        assert code == 0 and marca["sessao"] == "t" and marca["novas"] == 1
        assert marca["arquivadas"] == 1 and marca["gravado_em"].startswith("2026-09-22T20:00")
    _com_db(corpo)


def test_fila_do_chat_avisa_quando_o_hub_nao_foi_gravado():
    """Decisao 5 do `/ai-eng` (s193): o `/revisar` no chat ABRE gravando o hub. A fila
    (`--next`/`--list`/`--export-player`) avisa em stderr quando a ultima gravacao do hub
    passou da janela -- e o portador mais perto do ato (licao do F97)."""
    agora = datetime(2026, 9, 23, 9, 0, 0)
    assert aviso_hub({"gravado_em": "2026-09-23T08:30:00"}, agora) is None
    assert aviso_hub({"gravado_em": "2026-09-23T03:00:00"}, agora) is None, "6h cravadas"
    velho = aviso_hub({"gravado_em": "2026-09-22T20:00:00"}, agora)
    assert velho and "22/09 20:00" in velho and "--record-lote" in velho
    assert "nunca" in aviso_hub(None, agora)
    assert "nunca" in aviso_hub({"gravado_em": "lixo"}, agora)


def _rodar_cli(argv):
    """`main()` em processo, com stdout/stderr capturados. Devolve o exit code."""
    from tools import fsrs_queue
    antigo = sys.argv
    sys.argv = ["fsrs_queue.py"] + argv
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            fsrs_queue.main()
        return 0
    except SystemExit as e:
        return int(e.code or 0)
    finally:
        sys.argv = antigo


def test_cli_com_rejeitada_nao_sai_2_e_grava_os_validos():
    from tools import fsrs_queue

    def corpo(tmp):
        with tempfile.TemporaryDirectory() as pasta:
            # o --apply da CLI arquiva e marca: nunca no history/ nem no tmp/ reais
            orig = fsrs_queue.PASTA_QUARENTENA, fsrs_queue.MARCADOR_HUB
            fsrs_queue.PASTA_QUARENTENA = os.path.join(pasta, "quarentena")
            fsrs_queue.MARCADOR_HUB = os.path.join(pasta, "marca.json")
            try:
                lote = os.path.join(pasta, "lote.json")
                notas = os.path.join(pasta, "notas.json")
                with open(lote, "w", encoding="utf-8") as f:
                    json.dump({"sessao": "t", "cards": _CARDS}, f)
                with open(notas, "w", encoding="utf-8") as f:
                    json.dump({"notas": [{"card_id": 99, "rating_primeira": 3, "ts": _TS},
                                         {"card_id": 1, "rating_primeira": 3, "ts": _TS},
                                         {"card_id": 2, "rating_primeira": 2,
                                          "ts": _TS_DEPOIS}]}, f)
                with _relogio():
                    code = _rodar_cli(["--record-lote", notas, "--lote", lote,
                                       "--apply", "--expect", "2"])
                assert code == 0, "doc rejeitado nao derruba o lote"
                assert _conta(tmp, "fsrs_revlog") == 2
                arquivado = json.load(open(os.path.join(pasta, "quarentena", "t.json"),
                                           encoding="utf-8"))
                assert [it["doc"]["card_id"] for it in arquivado["itens"]] == [99], (
                    "a CLI arquiva o rejeitado em history/quarentena/<sessao>.json")
                assert json.load(open(os.path.join(pasta, "marca.json"),
                                      encoding="utf-8"))["novas"] == 2
                with open(notas, "w", encoding="utf-8") as f:
                    json.dump({"nada": []}, f)
                assert _rodar_cli(["--record-lote", notas, "--lote", lote]) == 2, (
                    "arquivo sem a lista `notas` e erro do ARQUIVO, nao de doc: sai 2")
            finally:
                fsrs_queue.PASTA_QUARENTENA, fsrs_queue.MARCADOR_HUB = orig
    _com_db(corpo)


# --------------------------------------------------------------------------
# 6. Agenda embutida no lote (s194, item 5 do feedback do hub)
# --------------------------------------------------------------------------

HOJE = datetime(2026, 9, 23, 9, 0, 0)


def _agendar(tmp, linhas):
    """linhas = [(card_id, state, due)] de cards FORA do lote, com o FSRS ja rodando."""
    con = sqlite3.connect(tmp)
    for cid, state, due in linhas:
        con.execute("INSERT INTO flashcards (id, tipo, frente_pergunta, verso_resposta, "
                    "quality_source) VALUES (?, 'conteudo', 'P?', 'R.', 'qualitative')", (cid,))
        con.execute("INSERT INTO fsrs_cards (card_id, state, due, stability, difficulty, reps) "
                    "VALUES (?, ?, ?, 5.0, 5.0, 3)", (cid, state, due))
    con.commit()
    con.close()


def test_export_embute_previsao_por_nota_e_agenda_base(monkeypatch):
    monkeypatch.setattr(db, "agora", lambda: HOJE)

    def corpo(tmp):
        _agendar(tmp, [
            (10, 2, "2026-09-24 08:00:00"),          # amanha
            (11, 2, "2026-09-24 22:30:00.123456"),   # amanha, com microssegundo
            (12, 2, "2026-09-30 10:00:00"),          # dia 7 da janela
            (13, 2, "2026-10-01 10:00:00"),          # fora da janela
            (14, 2, "2026-09-20 10:00:00"),          # vencido e fora do lote
            (15, 0, "2026-09-25 10:00:00"),          # novo: nao e agenda de revisao
        ])
        con = sqlite3.connect(tmp)                   # card 2 (NO lote) tambem vence na janela
        con.execute("UPDATE fsrs_cards SET state = 2, due = '2026-09-26 10:00:00' "
                    "WHERE card_id = 2")
        con.commit()
        con.close()
        lote = montar_lote([{"card_id": 1, "bucket": "novos"}, {"card_id": 2, "bucket": "hoje"}],
                           sessao="t")
        return anexar_agenda(lote)

    lote = _com_db(corpo)
    ab = lote["agenda_base"]
    assert [d["data"] for d in ab["dias"]] == ["2026-09-%02d" % d for d in range(24, 31)]
    assert [d["n"] for d in ab["dias"]] == [2, 0, 0, 0, 0, 0, 1], \
        "card 2 (no lote) nao entra; o novo (state 0) tambem nao"
    assert ab["vencidos_fora_do_lote"] == 1
    for card in lote["cards"]:
        prev = card["previsao"]
        assert sorted(prev) == ["1", "2", "3", "4"]
        assert all(len(v) == 10 and v[4] == "-" for v in prev.values()), prev
        assert prev["1"] <= prev["3"] <= prev["4"]


def test_export_para_amanha_usa_o_relogio_de_amanha(monkeypatch):
    """F131 (s195): export de VESPERA. Sem `--para`, o card que vence amanha e futuro e fica
    fora; com `--para amanha`, o relogio anda para as 06:00 de amanha: ele entra, `gerado_em`
    e o `sessao` carregam o dia, e a agenda comeca depois de amanha. Dia passado = exit 2."""
    monkeypatch.setattr(db, "agora", lambda: HOJE)          # hoje = 23/09 09:00

    def corpo(tmp):
        _agendar(tmp, [(10, 2, "2026-09-24 08:00:00"),      # vence amanha
                       (11, 2, "2026-09-20 10:00:00")])     # vencido
        con = sqlite3.connect(tmp)                           # a fila faz LEFT JOIN na taxonomia
        con.execute("CREATE TABLE taxonomia_cronograma (id INTEGER PRIMARY KEY, area TEXT, tema TEXT)")
        con.commit()
        con.close()
        with tempfile.TemporaryDirectory() as pasta:
            hoje_json = os.path.join(pasta, "hoje.json")
            assert _rodar_cli(["--export-player", "--sessao", "h", "--out", hoje_json]) == 0
            hoje_ids = [c["card_id"] for c in json.load(open(hoje_json, encoding="utf-8"))["cards"]]
            assert 11 in hoje_ids and 10 not in hoje_ids, "sem --para, amanha e futuro"

            para_json = os.path.join(pasta, "para.json")
            assert _rodar_cli(["--export-player", "--para", "2026-09-24", "--out", para_json]) == 0
            lote = json.load(open(para_json, encoding="utf-8"))
            ids = [c["card_id"] for c in lote["cards"]]
            assert 10 in ids and 11 in ids
            assert lote["sessao"] == "2026-09-24" and lote["gerado_em"] == "2026-09-24T06:00:00"
            assert lote["agenda_base"]["dias"][0]["data"] == "2026-09-25"
            card11 = next(c for c in lote["cards"] if c["card_id"] == 11)
            assert card11["previsao"]["1"] >= "2026-09-24", "previsao calculada em amanha"

            assert _rodar_cli(["--export-player", "--para", "2026-09-23",
                               "--out", os.path.join(pasta, "x.json")]) == 2, "hoje ou passado: recusa"
    _com_db(corpo)


def test_previsao_que_falha_so_tira_o_campo_do_card(monkeypatch):
    monkeypatch.setattr(db, "agora", lambda: HOJE)

    def explode(cid):
        raise RuntimeError("fsrs quebrado")

    def corpo(tmp):
        monkeypatch.setattr(db, "preview_ratings", explode)
        return anexar_agenda(montar_lote([{"card_id": 1}], sessao="t"))

    lote = _com_db(corpo)
    assert "previsao" not in lote["cards"][0]
    assert "agenda_base" in lote


def test_lote_com_campos_novos_segue_valido_no_record_lote():
    cards = [dict(c, previsao={"1": "2026-09-23", "2": "2026-09-24", "3": "2026-09-26",
                               "4": "2026-10-01"}) for c in _CARDS]
    notas = {"notas": [{"card_id": 1, "rating_primeira": 3, "ts": _TS}]}
    registros, rejeitadas, _ = triar_notas(notas, cards)
    assert len(registros) == 1 and not rejeitadas


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
