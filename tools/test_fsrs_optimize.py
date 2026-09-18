"""Testes de tools/fsrs_optimize.py (R1, s184) -- o que se testa e a NOSSA logica.

O Optimizer do py-fsrs e torch e nao entram aqui: ajustar 21 parametros sobre
512+ revisoes leva minutos e o que pode quebrar por nossa causa e outra coisa
-- o remap (F112), a fronteira read-only, o gate <512, a metadata que viaja no
JSON e a contagem x2 de leech. O Optimizer e MOCKADO por monkeypatch nas duas
funcoes de fronteira (`otimizar`, `retencao_otima`).

Banco sintetico em tmp_path com as 3 tabelas reais (colunas minimas do schema
do ipub.db). O `ipub.db` de producao nunca e tocado -- `DB_PATH` e
monkeypatchado, como manda a disciplina de writer-allowlist (F49).

A prova central e a do REMAP + IMUTABILIDADE: a nota 2 vira Again na ENTRADA
do Optimizer e o snapshot do `fsrs_revlog` fica byte-identico depois do passe.
"""
import json
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fsrs_optimize  # noqa: E402

SCHEMA = """
CREATE TABLE flashcards (id INTEGER PRIMARY KEY AUTOINCREMENT, questao_id INTEGER,
  tema_id INTEGER, tipo TEXT, frente_contexto TEXT, frente_pergunta TEXT,
  verso_resposta TEXT, verso_regra_mestre TEXT, verso_armadilha TEXT,
  quality_source TEXT DEFAULT 'legacy', card_version INTEGER DEFAULT 1,
  needs_qualitative INTEGER DEFAULT 0);
CREATE TABLE fsrs_cards (card_id INTEGER PRIMARY KEY, state INTEGER DEFAULT 0,
  due DATETIME, stability REAL DEFAULT 0.0, difficulty REAL DEFAULT 0.0,
  elapsed_days INTEGER DEFAULT 0, scheduled_days INTEGER DEFAULT 0,
  reps INTEGER DEFAULT 0, lapses INTEGER DEFAULT 0, last_review DATETIME);
CREATE TABLE fsrs_revlog (id INTEGER PRIMARY KEY AUTOINCREMENT, card_id INTEGER,
  rating INTEGER, state INTEGER, due DATETIME, stability REAL, difficulty REAL,
  elapsed_days INTEGER, last_elapsed_days INTEGER, scheduled_days INTEGER,
  review_time DATETIME DEFAULT CURRENT_TIMESTAMP, card_version INTEGER,
  selection_reason TEXT, reason_servido TEXT);
"""

#: Parametros de mentira, so para provar que o payload carrega o que o mock deu.
#: Tem de ser VALIDOS (o Scheduler valida limites), entao sao os defaults
#: deslocados 20% e recortados nos bounds -- diferentes do default o bastante
#: para a metrica "otimizado" nao colar na metrica "default".
from fsrs.scheduler import (  # noqa: E402
    DEFAULT_PARAMETERS, LOWER_BOUNDS_PARAMETERS, UPPER_BOUNDS_PARAMETERS,
)

PARAMS_FAKE = [min(max(p * 1.2, lo), hi) for p, lo, hi
               in zip(DEFAULT_PARAMETERS, LOWER_BOUNDS_PARAMETERS,
                      UPPER_BOUNDS_PARAMETERS)]


def _dia(n):
    return "2026-01-%02d 09:00:00" % n


def _montar_db(path, revisoes, cards=None):
    """revisoes = [(card_id, rating, review_time)]; cards = [(id, lapses, difficulty, nq)]."""
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    ids = sorted({c for c, _r, _t in revisoes} | {c[0] for c in (cards or [])})
    por_card = {c[0]: c for c in (cards or [])}
    for cid in ids:
        _i, lapses, dif, nq = por_card.get(cid, (cid, 0, 5.0, 0))
        conn.execute("INSERT INTO flashcards (id, tipo, frente_pergunta, verso_resposta, "
                     "needs_qualitative) VALUES (?, 'conteudo', 'f', 'v', ?)", (cid, nq))
        conn.execute("INSERT INTO fsrs_cards (card_id, state, lapses, difficulty) "
                     "VALUES (?, 2, ?, ?)", (cid, lapses, dif))
    for cid, rating, quando in revisoes:
        conn.execute("INSERT INTO fsrs_revlog (card_id, rating, state, review_time) "
                     "VALUES (?, ?, 2, ?)", (cid, rating, quando))
    conn.commit()
    conn.close()


def _serie(n_por_card, n_cards, ratings):
    """Serie sintetica com 1 revisao por dia por card (dias distintos = pontuam)."""
    fora = []
    for c in range(1, n_cards + 1):
        for i in range(n_por_card):
            fora.append((c, ratings[(c + i) % len(ratings)], _dia(1 + i)))
    return fora


def _snapshot(path):
    conn = sqlite3.connect(path)
    try:
        return conn.execute("SELECT id, card_id, rating, review_time FROM fsrs_revlog "
                            "ORDER BY id").fetchall()
    finally:
        conn.close()


@pytest.fixture
def db_grande(tmp_path, monkeypatch):
    """>= 512 revisoes: 60 cards x 10 revisoes = 600, as 4 notas representadas."""
    p = tmp_path / "ipub.db"
    _montar_db(p, _serie(10, 60, [1, 2, 3, 4]))
    monkeypatch.setattr(fsrs_optimize, "DB_PATH", p)
    monkeypatch.setattr(fsrs_optimize, "OUT_PATH", tmp_path / "core" / "fsrs_params.json")
    return p


@pytest.fixture
def mock_optimizer(monkeypatch):
    """Substitui as 2 fronteiras do py-fsrs e REGISTRA as notas que chegaram."""
    vistos = {"otimizar": [], "retencao": []}

    def _otimizar(review_logs):
        fsrs_optimize.exigir_minimo(len(review_logs))       # o gate continua real
        vistos["otimizar"].append([int(rl.rating) for rl in review_logs])
        return list(PARAMS_FAKE)

    def _retencao(review_logs, parametros):
        fsrs_optimize.exigir_minimo(len(review_logs))
        vistos["retencao"].append(list(parametros))
        return 0.85

    monkeypatch.setattr(fsrs_optimize, "otimizar", _otimizar)
    monkeypatch.setattr(fsrs_optimize, "retencao_otima", _retencao)
    return vistos


# --------------------------------------------------------------- 1. o remap

def test_remap_transforma_as_notas_certas():
    """A tabela do F112, nota a nota: 2 vira Again; 3 vira Hard; 4 vira Good."""
    assert fsrs_optimize.REMAP_F112 == {1: 1, 2: 1, 3: 2, 4: 3}
    for nota, esperado in ((1, 1), (2, 1), (3, 2), (4, 3)):
        assert fsrs_optimize.aplicar_remap(nota, fsrs_optimize.REMAP_F112) == esperado
    # visao crua = identidade
    for nota in (1, 2, 3, 4):
        assert fsrs_optimize.aplicar_remap(nota, None) == nota
    # 4 (Easy) nunca e alvo: a regua do MedHub nao mede "sem esforco"
    assert 4 not in set(fsrs_optimize.REMAP_F112.values())


def test_remap_chega_no_optimizer_como_rating(db_grande):
    """O ReviewLog entregue ao Optimizer ja vem com a nota traduzida.

    R2 (s186): o corpus sintetico deste teste nao tem `regua_versao`, entao todas
    as linhas leem como v1 -- e e exatamente por isso que ele segue sendo a prova
    de PARIDADE com o R1: mesma entrada, mesmos numeros, caminho novo.
    """
    linhas = fsrs_optimize.ler_revlog(db_grande)
    assert {g for _c, _r, _q, g in linhas} == {1}    # 100% v1, como o revlog real
    cru = fsrs_optimize.construir_review_logs(linhas, "cru")
    remap = fsrs_optimize.construir_review_logs(linhas, "nativo")
    n_cru = sorted({int(rl.rating) for rl in cru})
    n_remap = sorted({int(rl.rating) for rl in remap})
    assert n_cru == [1, 2, 3, 4]
    assert n_remap == [1, 2, 3]                     # Easy some, Again engorda
    d_cru = fsrs_optimize.distribuicao(linhas, "cru")
    d_remap = fsrs_optimize.distribuicao(linhas, "nativo")
    assert d_remap["1"] == d_cru["1"] + d_cru["2"]
    assert d_remap["2"] == d_cru["3"]
    assert d_remap["3"] == d_cru["4"]
    assert "4" not in d_remap


def test_remap_nao_toca_o_banco(db_grande, mock_optimizer, capsys):
    """Passe completo (2 visoes) e o revlog fica byte-identico. Fronteira dura."""
    antes = _snapshot(db_grande)
    assert fsrs_optimize.main([]) == 0
    assert _snapshot(db_grande) == antes


def test_conexao_e_read_only(db_grande):
    """A conexao do modulo recusa INSERT -- nao e disciplina, e o modo do sqlite."""
    conn = fsrs_optimize._conectar_ro(db_grande)
    try:
        with pytest.raises(sqlite3.OperationalError):
            conn.execute("INSERT INTO fsrs_revlog (card_id, rating, state) VALUES (1,1,2)")
    finally:
        conn.close()


# ------------------------------------------------- 2. metadata no JSON + IO

def test_json_carrega_a_metadata_do_remap(db_grande, mock_optimizer):
    """Parametro sem a regua que o gerou e numero orfao -- a regua viaja junto."""
    linhas = fsrs_optimize.ler_revlog(db_grande)
    visoes = [fsrs_optimize.analisar_visao(linhas, v, n, 0.2, 16500)
              for n, v in (("cru", "cru"), ("remap", "nativo"))]
    payload = fsrs_optimize.construir_payload(linhas, visoes, 0.2, 16500, "6.3.1")

    meta = payload["metadata_remap"]
    assert meta["mapa"] == {"1": 1, "2": 1, "3": 2, "4": 3}
    assert meta["achado"] == "F112"
    assert meta["fonte_da_regua"] == ".claude/commands/revisar.md, passo 4"
    assert "sem o alvo" in meta["citacao_literal"]
    assert set(meta["justificativa_por_nota"]) == {"1->1", "2->1", "3->2", "4->3"}
    assert "fsrs_revlog imutavel" in meta["escopo"]

    assert payload["py_fsrs_version"] == "6.3.1"
    assert payload["revisoes_usadas"] == len(linhas) == 600
    assert payload["adotado"] is False
    assert "nunca adotado" in payload["aviso_retencao"]
    assert set(payload["visoes"]) == {"cru", "remap"}
    assert payload["visoes"]["cru"]["remap"] is None
    assert payload["visoes"]["remap"]["remap"] == {"1": 1, "2": 1, "3": 2, "4": 3}
    # R2: a regua do fit viaja com o conjunto -- sem ela o adaptador RECUSA adotar
    assert payload["visoes"]["remap"]["regua_do_fit"] == 2
    assert payload["visoes"]["cru"]["regua_do_fit"] == 1
    assert payload["visoes"]["cru"]["reguas_no_corpus"] == [1]
    for v in payload["visoes"].values():
        assert v["parametros"] == [round(x, 6) for x in PARAMS_FAKE]
        assert v["retencao_otima"] == 0.85
        assert v["metrica"]["nome"] == "log_loss"
        assert v["metrica"]["n_pontos"] > 0
        assert v["metrica"]["default"] is not None
        assert v["metrica"]["otimizado"] is not None
    # serializavel de fato (o CLI grava json.dumps deste dict)
    assert json.loads(json.dumps(payload, ensure_ascii=False))["adotado"] is False


def test_dry_run_nao_escreve_arquivo(db_grande, mock_optimizer):
    """Default e dry-run; --dry-run junto de --write tambem NAO grava."""
    assert fsrs_optimize.main([]) == 0
    assert not fsrs_optimize.OUT_PATH.exists()

    assert fsrs_optimize.main(["--dry-run", "--write"]) == 0
    assert not fsrs_optimize.OUT_PATH.exists()

    assert fsrs_optimize.main(["--write"]) == 0
    assert fsrs_optimize.OUT_PATH.exists()
    gravado = json.loads(fsrs_optimize.OUT_PATH.read_text(encoding="utf-8"))
    assert gravado["metadata_remap"]["mapa"]["2"] == 1
    assert gravado["adotado"] is False


def test_metrica_e_a_mesma_nas_duas_visoes_e_usa_a_cauda(db_grande, mock_optimizer):
    """Mesma metrica nos dois lados; a cauda pontua menos que a serie inteira."""
    linhas = fsrs_optimize.ler_revlog(db_grande)
    corte = fsrs_optimize.corte_holdout(linhas, 0.2)
    treino, cauda = fsrs_optimize.particionar(linhas, corte)
    assert treino and cauda and len(treino) + len(cauda) == len(linhas)
    assert all(l[2] < corte for l in treino)
    assert all(l[2] >= corte for l in cauda)

    _, n_tudo = fsrs_optimize.log_loss(linhas, None, None, "cru")
    _, n_cauda = fsrs_optimize.log_loss(linhas, None, corte, "cru")
    assert 0 < n_cauda < n_tudo

    v_cru = fsrs_optimize.analisar_visao(linhas, "cru", "cru", 0.2, 16500)
    v_remap = fsrs_optimize.analisar_visao(linhas, "nativo", "remap", 0.2, 16500)
    assert v_cru["metrica"]["nome"] == v_remap["metrica"]["nome"] == "log_loss"
    assert v_cru["metrica"]["n_pontos"] == v_remap["metrica"]["n_pontos"]
    # rotulos diferentes -> numeros diferentes (por isso nao se comparam entre si)
    assert v_cru["metrica"]["default"] != v_remap["metrica"]["default"]


# ------------------------------------------------------------- 3. gate <512

def test_gate_menos_de_512_revisoes(tmp_path, monkeypatch, capsys):
    """Abaixo de 512 o CLI para com exit 2 -- nao deixa a lib devolver default silencioso."""
    p = tmp_path / "ipub.db"
    _montar_db(p, _serie(10, 20, [1, 2, 3, 4]))          # 200 revisoes
    monkeypatch.setattr(fsrs_optimize, "DB_PATH", p)
    monkeypatch.setattr(fsrs_optimize, "OUT_PATH", tmp_path / "core" / "fsrs_params.json")

    assert fsrs_optimize.MIN_REVLOG == 512
    assert len(fsrs_optimize.ler_revlog(p)) == 200

    with pytest.raises(fsrs_optimize.RevlogInsuficiente):
        fsrs_optimize.exigir_minimo(511)
    assert fsrs_optimize.exigir_minimo(512) == 512

    assert fsrs_optimize.main(["--write"]) == 2
    assert not fsrs_optimize.OUT_PATH.exists()          # bloqueio nao grava nada
    assert "512" in capsys.readouterr().err


def test_gate_nao_bloqueia_o_painel_de_leech(tmp_path, monkeypatch):
    """--leech nao depende do Optimizer, entao o gate <512 nao se aplica a ele."""
    p = tmp_path / "ipub.db"
    _montar_db(p, [(1, 1, _dia(1)), (1, 1, _dia(2)), (1, 1, _dia(3)), (1, 1, _dia(4))],
               cards=[(1, 3, 9.1, 0)])
    monkeypatch.setattr(fsrs_optimize, "DB_PATH", p)
    assert fsrs_optimize.main(["--leech"]) == 0


# ---------------------------------------------------------------- 4. leech x2

def test_leech_conta_x2(tmp_path, monkeypatch):
    """Com o 2 contando como acerto o lapso fica subcontado -- o limiar mente."""
    p = tmp_path / "ipub.db"
    revisoes = []
    # card 1: 1a revisao + 3 notas 1  -> 3 lapsos nas DUAS visoes
    revisoes += [(1, 3, _dia(1)), (1, 1, _dia(2)), (1, 1, _dia(3)), (1, 1, _dia(4))]
    # card 2: 1a revisao + 3 notas 2  -> 0 lapsos na crua, 3 no remap (o achado)
    revisoes += [(2, 3, _dia(1)), (2, 2, _dia(2)), (2, 2, _dia(3)), (2, 2, _dia(4))]
    # card 3: 1a revisao = nota 1 + 2 notas 2 -> 0 crua (a 1a nao e lapso), 2 remap
    revisoes += [(3, 1, _dia(1)), (3, 2, _dia(2)), (3, 2, _dia(3))]
    # card 4: sempre acertou -> 0 nas duas
    revisoes += [(4, 4, _dia(1)), (4, 4, _dia(2)), (4, 4, _dia(3)), (4, 4, _dia(4))]
    # card 5: APOSENTADO (needs_qualitative=2) com 3 lapsos -> fora das duas contagens
    revisoes += [(5, 3, _dia(1)), (5, 1, _dia(2)), (5, 1, _dia(3)), (5, 1, _dia(4))]
    _montar_db(p, revisoes, cards=[(1, 3, 9.0, 0), (2, 0, 8.0, 0), (3, 0, 7.0, 0),
                                   (4, 0, 4.0, 0), (5, 3, 9.9, 2)])
    monkeypatch.setattr(fsrs_optimize, "DB_PATH", p)

    linhas = fsrs_optimize.ler_revlog(p)
    rel = fsrs_optimize.medir_leech(linhas, fsrs_optimize.ler_cards(p), limiar=3)

    assert rel["cards_ativos"] == 4                      # o aposentado nao entra
    assert rel["crua"]["cards"] == 1 and rel["crua"]["ids"] == [1]
    assert rel["crua_reconstruida"]["ids"] == [1]        # reconstrucao bate com o motor
    assert rel["reconstrucao"]["cards_divergentes"] == 0
    assert rel["remap"]["cards"] == 2 and rel["remap"]["ids"] == [1, 2]

    # a difficulty exibida e a ARMAZENADA; muda QUEM cruza o limiar, nao a nota
    assert rel["crua"]["difficulty"]["mediana"] == 9.0
    assert rel["remap"]["difficulty"]["n"] == 2
    assert rel["remap"]["difficulty"]["media"] == 8.5

    # limiar e argumento, nao constante escondida
    rel4 = fsrs_optimize.medir_leech(linhas, fsrs_optimize.ler_cards(p), limiar=4)
    assert rel4["crua"]["cards"] == 0 and rel4["remap"]["cards"] == 0


def test_lapso_nao_conta_a_primeira_revisao(tmp_path):
    """Regra copiada de app/utils/fsrs.py::evaluate -- `if rating == 1 and not is_new`."""
    linhas = [(1, 1, fsrs_optimize._parse_utc(_dia(1)), 1),
              (1, 1, fsrs_optimize._parse_utc(_dia(2)), 1)]
    assert fsrs_optimize.contar_lapsos(linhas, visao="cru") == {1: 1}
    assert fsrs_optimize.contar_lapsos([linhas[0]], visao="cru") == {1: 0}
