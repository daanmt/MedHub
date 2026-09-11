"""Regressao F80b (hotfix 2026-09-10, s176): o relogio unico `db.agora()` vale tambem do lado
do LEITOR. Irmao de `test_fuso_unico.py`, que cobre os WRITERS (F80).

Caso real: os writers gravam `fsrs_cards.due` e `sessoes_bulk.data_sessao` em hora LOCAL naive
(contrato F80), mas tres SELECTs de producao comparavam essas colunas contra o `'now'` do
SQLite, que responde em UTC. Medido em 2026-09-10 20:50 local: `datetime('now')` = 23:50 UTC,
`db.agora()` = 20:50 -- delta +3h. Efeito: a janela de erro fresco de 48h operava como 45h, e a
janela de volume do `get_ritmo_real` deslizava um DIA inteiro entre 21h e a meia-noite locais.

🔴 A assimetria que escondia o defeito: dentro da MESMA `get_cards_by_bucket`, os buckets
`atrasados`/`hoje` ja usavam relogio local (o F80 os consertou) e a banda `erros_frescos`, escrita
depois, nao. Duas bandas da mesma fila, dois relogios.

O QUE ESTES TESTES MEDEM -- e o que NAO medem. Eles nao verificam um offset de 3h: verificam
**obediencia ao relogio unico**. Com `db.agora()` congelado, o resultado do leitor tem de ser
funcao APENAS do instante congelado. Um teste ancorado em "3 horas" passaria por acidente num CI
rodando em UTC (offset 0), que e exatamente onde o defeito seria invisivel.

Fixtures: schema canonico via `init_db` em tmp_path; `db.agora` monkeypatchado. Zero contato com
o `ipub.db` real.
"""
import contextlib
import io
import re
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from app.utils import db  # noqa: E402
import init_db  # noqa: E402

# 21:30 local = 00:30 UTC do dia seguinte (BRT) -- o mesmo instante do teste irmao dos writers,
# escolhido porque cai na faixa em que o dia UTC e o dia local ja divergem.
CONGELADO = datetime(2026, 9, 7, 21, 30, 0)


def _carimbo(dt):
    return dt.strftime(db.FORMATO_CARIMBO)


@pytest.fixture
def banco(tmp_path, monkeypatch):
    caminho = str(tmp_path / "ipub.db")
    monkeypatch.setattr(init_db, "DB_PATH", caminho)
    with contextlib.redirect_stdout(io.StringIO()):
        init_db.init_db()
    monkeypatch.setattr(db, "DB_PATH", caminho)
    monkeypatch.setattr(db, "agora", lambda: CONGELADO)
    con = sqlite3.connect(caminho)
    con.execute("INSERT INTO taxonomia_cronograma (id, area, tema) VALUES (1, 'Cirurgia', 'Apendicite Aguda')")
    con.commit()
    con.close()
    return caminho


def _card_de_erro(caminho, card_id, due, questao_id=1):
    """Card state=0 nascido de erro. Para state 0 o contrato e `due == criacao`."""
    con = sqlite3.connect(caminho)
    con.execute("INSERT INTO flashcards (id, tema_id, tipo, questao_id, frente_pergunta, "
                "verso_resposta, quality_source) VALUES (?, 1, 'conteudo', ?, 'P?', 'R.', 'qualitative')",
                (card_id, questao_id))
    con.execute("INSERT INTO fsrs_cards (card_id, state, due) VALUES (?, 0, ?)",
                (card_id, _carimbo(due)))
    con.commit()
    con.close()


# --------------------------------------------------------------------------
# 1. get_fresh_error_cards -- a janela de 48h conta a partir do relogio unico
# --------------------------------------------------------------------------
def test_janela_de_erro_fresco_conta_do_relogio_unico(banco):
    _card_de_erro(banco, 1, CONGELADO - timedelta(hours=1, minutes=30))   # dentro, folgado
    _card_de_erro(banco, 2, CONGELADO - timedelta(hours=47, minutes=30))  # dentro, na borda
    _card_de_erro(banco, 3, CONGELADO - timedelta(hours=57, minutes=30))  # fora

    ids = sorted(c["id"] for c in db.get_fresh_error_cards(janela_horas=48))

    # Sob o defeito o corte vem da hora REAL da maquina (dias a frente do instante
    # congelado) e a lista volta vazia -- o leitor ignora `db.agora()`.
    assert ids == [1, 2], (
        "a janela de erro fresco nao esta ancorada em db.agora(): esperado [1, 2], veio %r" % ids)


def test_borda_da_janela_de_erro_fresco_e_exatamente_a_janela(banco):
    _card_de_erro(banco, 1, CONGELADO - timedelta(hours=48) + timedelta(minutes=1))  # dentro
    _card_de_erro(banco, 2, CONGELADO - timedelta(hours=48) - timedelta(minutes=1))  # fora

    ids = sorted(c["id"] for c in db.get_fresh_error_cards(janela_horas=48))
    assert ids == [1], "a borda de 48h deslizou (offset de zona vazando para o corte): %r" % ids


# --------------------------------------------------------------------------
# 2. get_cards_by_bucket -- a fila inteira responde a UM relogio
# --------------------------------------------------------------------------
def test_banda_de_erro_fresco_da_fila_usa_o_mesmo_relogio_dos_outros_buckets(banco):
    _card_de_erro(banco, 1, CONGELADO - timedelta(hours=2))
    _card_de_erro(banco, 2, CONGELADO - timedelta(hours=60))  # fora da janela

    buckets = db.get_cards_by_bucket()
    frescos = sorted(c["card_id"] for c in buckets["erros_frescos"])

    assert frescos == [1], (
        "a banda erros_frescos nao obedece a db.agora() enquanto atrasados/hoje obedecem "
        "-- duas bandas da mesma fila em dois relogios: %r" % frescos)


def test_card_de_hoje_a_noite_nao_vira_atrasado(banco):
    """O caso que o F80 fixou do lado dos buckets datados -- guarda contra regressao."""
    con = sqlite3.connect(banco)
    con.execute("INSERT INTO flashcards (id, tema_id, tipo, frente_pergunta, verso_resposta, "
                "quality_source) VALUES (9, 1, 'conteudo', 'P?', 'R.', 'qualitative')")
    con.execute("INSERT INTO fsrs_cards (card_id, state, due) VALUES (9, 2, ?)",
                (_carimbo(CONGELADO.replace(hour=23, minute=0)),))
    con.commit()
    con.close()

    buckets = db.get_cards_by_bucket()
    assert 9 not in [c["card_id"] for c in buckets["atrasados"]], \
        "card due as 23h local apareceu como VENCIDO as 21:30 -- o relogio voltou a ser UTC"
    assert 9 in [c["card_id"] for c in buckets["hoje"]]


# --------------------------------------------------------------------------
# 3. get_ritmo_real -- a janela de volume nao desliza um dia
# --------------------------------------------------------------------------
def test_janela_de_volume_conta_dias_do_relogio_unico(banco):
    con = sqlite3.connect(banco)
    for n, (dia, feitas) in enumerate([(CONGELADO.date(), 30),
                                       (CONGELADO.date() - timedelta(days=6), 30),
                                       (CONGELADO.date() - timedelta(days=8), 999)], start=1):
        con.execute("INSERT INTO sessoes_bulk (sessao_num, area, questoes_feitas, "
                    "questoes_acertadas, data_sessao) VALUES (?, 'Cirurgia', ?, 0, ?)",
                    (n, feitas, dia.isoformat()))
    con.commit()
    con.close()

    # Janela de 7 dias: entram os dois primeiros (60 q), o de 8 dias atras fica fora.
    assert db.get_ritmo_real(janela_dias=7) == round(60 / 7, 1), (
        "a janela de volume nao esta ancorada em db.agora() -- entre 21h e a meia-noite locais "
        "o date('now') do SQLite ja e o dia seguinte e a janela inteira desliza")


# --------------------------------------------------------------------------
# 4. Estrutural: nenhum SELECT de producao em app/ pergunta as horas ao SQLite
# --------------------------------------------------------------------------
# 🔴 ESCOPO DECLARADO, NAO ESQUECIDO. Esta varredura cobre `app/`. Os sitios do MESMO defeito em
# `tools/` (`audit_fsrs.py:38,39,44`, `variancia.py:194`) estao DEFERIDOS para uma chamada propria
# de hotfix -- corrigi-los aqui estouraria o teto de 2 arquivos de codigo, e o teto existe para
# impedir que hotfix vire refatoracao. Sensor que nao cobre por desenho e DECLARADO, nunca verde
# por omissao (AGENTE.md §10.8, verification-stack; licao do D11). Quando a chamada deferida
# entrar, `RAIZES` cresce para ("app", "tools") e esta nota vira lapide.
RAIZES = ("app",)
_RELOGIO_CRU = re.compile(r"(?:datetime|date)\s*\(\s*'now'(?!\s*,\s*'localtime')", re.I)


def _fontes_de_producao():
    for base in RAIZES:
        for f in (ROOT / base).rglob("*.py"):
            rel = f.relative_to(ROOT).as_posix()
            if "_archive" in rel or "__pycache__" in rel or f.name.startswith("test_"):
                continue
            yield rel, f.read_text(encoding="utf-8-sig", errors="replace")


def test_nenhum_select_de_producao_le_o_relogio_do_sqlite():
    achados = []
    for rel, texto in _fontes_de_producao():
        for i, linha in enumerate(texto.splitlines(), 1):
            # Comentario que NARRA o defeito nao e o defeito -- mesma distincao
            # que o CONTRATO_REVOGADO faz entre lapide e prescricao ativa.
            codigo = linha.split("#", 1)[0]
            if _RELOGIO_CRU.search(codigo):
                achados.append(f"{rel}:{i}")
    assert not achados, (
        "SELECT de producao lendo o relogio do SQLite (UTC) contra coluna gravada em LOCAL. "
        "Use o corte derivado de `db.agora()`, ou `datetime('now','localtime')` se tiver de ser "
        "SQL puro. Sitios: " + ", ".join(achados))
