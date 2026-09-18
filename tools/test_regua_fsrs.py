"""Regua de notas do FSRS versionada (R2/F112, s186) -- spec `regua-nativa-fsrs-r2`.

O que se prova aqui NAO e o algoritmo do FSRS (isso e do py-fsrs). E a nossa
camada: que a regua tem UM portador, que cada revisao carrega sob QUAL regua foi
dada, que o historico velho e traduzido por LINHA na entrada do Optimizer -- e,
sobretudo, o **gate de paridade**: sobre um revlog 100% v1 (o estado de hoje) o
caminho novo por linha tem que reproduzir exatamente o que o R1 produzia com o
remap global. Refactor que muda numero que ninguem pediu para mudar e regressao.

Os quatro ramos do carregador de parametros tambem vivem aqui: o default do
py-fsrs e a saida CORRETA em tres deles, e a unica forma de provar isso e
disparar cada recusa nominalmente. Parametro adotado sob regua diferente da
regua de escrita e o defeito que o F114 nomeia -- o gate existe para ele.

Banco sintetico em tmp_path; o `ipub.db` de producao nunca e tocado (F49).
"""
import json
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from app.utils import regua as R  # noqa: E402


# ------------------------------------------------------------ o portador unico

def test_regua_atual_e_a_nativa_do_fsrs():
    """v2 = `1 falhou / 2 lembrou com esforco / 3 lembrou / 4 sem esforco`."""
    assert R.REGUA_ATUAL == 2
    rotulos = R.rotulos(2)
    assert set(rotulos) == {1, 2, 3, 4}
    # o degrau 2 e ACERTO com esforco -- e o giro semantico inteiro do F112
    assert "esforco" in rotulos[2].lower()
    assert "sem esforco" in rotulos[4].lower()
    # e o 4 nao pode repetir a definicao do 2
    assert rotulos[2] != rotulos[4]


def test_mapa_v1_e_o_do_r1_verbatim():
    """O mapa do R2 e o MESMO que o R1 mediu -- se divergir, o numero do R1 morre."""
    assert R.MAPA_V1_PARA_NATIVO == {1: 1, 2: 1, 3: 2, 4: 3}
    # nada mapeia para 4: a regua v1 nao tinha degrau de "sem esforco"
    assert 4 not in set(R.MAPA_V1_PARA_NATIVO.values())


def test_fsrs_optimize_nao_redefine_o_mapa():
    """Portador unico (DoD 1): o CLI LE a regua, nao a reescreve."""
    import fsrs_optimize
    assert fsrs_optimize.REMAP_F112 is R.MAPA_V1_PARA_NATIVO


# --------------------------------------------------- a regua de cada linha

@pytest.mark.parametrize("gravado,esperado", [
    (None, 1),   # historico anterior ao R2 -- NULL significa v1 por declaracao
    (0, 1),      # coluna zerada por escrita velha
    (1, 1),
    (2, 2),
])
def test_regua_da_linha(gravado, esperado):
    assert R.regua_da_linha(gravado) == esperado


def test_regua_desconhecida_falha_alto():
    """Regua que ninguem declarou nao vira v1 silenciosamente (licao do F91)."""
    with pytest.raises(ValueError):
        R.regua_da_linha(7)


def test_nota_nativa_traduz_v1_e_preserva_v2():
    # linha v1: o 2 era "sem o alvo" -> falha de recuperacao
    assert R.nota_nativa(2, regua=1) == 1
    assert R.nota_nativa(4, regua=1) == 3
    # linha v2: a nota JA esta na semantica do motor
    assert R.nota_nativa(2, regua=2) == 2
    assert R.nota_nativa(4, regua=2) == 4
    # o 1 e o unico degrau que as duas reguas partilham
    assert R.nota_nativa(1, regua=1) == R.nota_nativa(1, regua=2) == 1


def test_visao_crua_nunca_traduz():
    """A visao `cru` responde 'o que o motor VIU', e isso independe da regua."""
    for regua in (1, 2):
        for nota in (1, 2, 3, 4):
            assert R.nota_efetiva(nota, regua, visao="cru") == nota


def test_visao_nativa_traduz_por_linha():
    assert R.nota_efetiva(2, 1, visao="nativo") == 1
    assert R.nota_efetiva(2, 2, visao="nativo") == 2


def test_visao_invalida_falha_alto():
    with pytest.raises(ValueError):
        R.nota_efetiva(3, 1, visao="meia-boca")


# ------------------------------------------------------ 🔒 GATE DE PARIDADE

def test_paridade_com_o_r1_sobre_revlog_todo_v1():
    """🔒 DoD 4. Hoje o revlog e 100% v1; o caminho por linha TEM que empatar
    com o remap global do R1. Se este teste cair, o refactor mexeu em numero."""
    import fsrs_optimize
    linhas_r1 = [(1, 1), (1, 2), (2, 3), (2, 4), (3, 2), (3, 4)]
    # caminho velho: mapa global aplicado a todas as linhas
    velho = [fsrs_optimize.aplicar_remap(n, R.MAPA_V1_PARA_NATIVO)
             for _cid, n in linhas_r1]
    # caminho novo: regua por linha, todas NULL (= v1)
    novo = [R.nota_efetiva(n, R.regua_da_linha(None), visao="nativo")
            for _cid, n in linhas_r1]
    assert novo == velho


def test_paridade_da_distribuicao_sobre_revlog_todo_v1():
    """Mesma paridade, agora no agregado que vai para o JSON versionado."""
    import fsrs_optimize
    linhas = [(1, 1, "t", None), (1, 2, "t", None), (2, 2, "t", None),
              (2, 3, "t", None), (3, 4, "t", None), (3, 4, "t", None)]
    nova = fsrs_optimize.distribuicao(linhas, visao="nativo")
    antiga = {"1": 3, "2": 1, "3": 2}   # 1,2,2 -> Again ; 3 -> Hard ; 4,4 -> Good
    assert nova == antiga


def test_revlog_misto_traduz_cada_metade_com_a_sua_regua():
    """Depois do R2 o revlog tem as duas safras. A mesma nota 2 significa
    coisas OPOSTAS nas duas, e a traducao tem que respeitar isso."""
    import fsrs_optimize
    linhas = [(1, 2, "t", None),   # v1: "sem o alvo"       -> Again
              (1, 2, "t", 2)]      # v2: "lembrou com esforco" -> Hard
    assert fsrs_optimize.distribuicao(linhas, visao="nativo") == {"1": 1, "2": 1}
    # e na visao crua as duas continuam sendo 2
    assert fsrs_optimize.distribuicao(linhas, visao="cru") == {"2": 2}


# --------------------------------------------- a versao gravada em cada linha

SCHEMA_MINIMO = """
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
  review_time DATETIME DEFAULT CURRENT_TIMESTAMP);
"""


@pytest.fixture
def db_sintetico(tmp_path, monkeypatch):
    """Banco com o schema ANTERIOR ao R2 (sem nenhuma das colunas novas) --
    e o estado real de qualquer maquina que ainda nao rodou esta versao."""
    caminho = tmp_path / "ipub.db"
    conn = sqlite3.connect(caminho)
    conn.executescript(SCHEMA_MINIMO)
    conn.execute("INSERT INTO flashcards (id, tipo, frente_pergunta, verso_resposta) "
                 "VALUES (1, 'conteudo', 'p', 'v')")
    conn.commit()
    conn.close()
    from app.utils import db as dbmod
    monkeypatch.setattr(dbmod, "DB_PATH", str(caminho))
    return caminho


def test_alter_de_regua_versao_e_idempotente(db_sintetico):
    """Mesmo padrao de `_ensure_revlog_columns`: rodar 2x nao quebra."""
    from app.utils import db as dbmod
    conn = sqlite3.connect(db_sintetico)
    dbmod._ensure_revlog_columns(conn)
    dbmod._ensure_revlog_columns(conn)
    cols = {r[1] for r in conn.execute("PRAGMA table_info(fsrs_revlog)")}
    assert "regua_versao" in cols
    conn.close()


def test_record_review_carimba_a_regua_atual(db_sintetico):
    from app.utils import db as dbmod
    dbmod.record_review(1, 3)
    conn = sqlite3.connect(db_sintetico)
    regua = conn.execute("SELECT regua_versao FROM fsrs_revlog").fetchone()[0]
    conn.close()
    assert regua == R.REGUA_ATUAL == 2


def test_historico_antigo_nao_e_backfillado(db_sintetico):
    """Anti-escopo declarado: linha velha fica NULL. NULL JA diz v1 -- reescrever
    3.067 linhas para repetir o que a ausencia afirma e escrita sem ganho."""
    from app.utils import db as dbmod
    conn = sqlite3.connect(db_sintetico)
    conn.execute("INSERT INTO fsrs_revlog (card_id, rating, review_time) "
                 "VALUES (1, 4, '2026-05-01 09:00:00')")
    conn.commit()
    conn.close()
    dbmod.record_review(1, 3)                     # dispara o ALTER
    conn = sqlite3.connect(db_sintetico)
    linhas = conn.execute("SELECT rating, regua_versao FROM fsrs_revlog "
                          "ORDER BY id").fetchall()
    conn.close()
    assert linhas[0] == (4, None)                 # a velha, intacta
    assert linhas[1][1] == 2                      # a nova, carimbada
    assert R.regua_da_linha(linhas[0][1]) == 1    # e lida como v1


# ------------------------------------- os 4 ramos do carregador de parametros

def _params_validos():
    from fsrs.scheduler import DEFAULT_PARAMETERS
    return [p * 1.01 for p in DEFAULT_PARAMETERS]


def test_sem_arquivo_cai_no_default(tmp_path):
    params, motivo = R.carregar_parametros(tmp_path / "nao-existe.json")
    assert params is None
    assert "sem" in motivo.lower()


def test_reportado_mas_nao_adotado_cai_no_default(tmp_path):
    p = tmp_path / "fsrs_params.json"
    p.write_text(json.dumps({"adotado": False, "regua_do_fit": 2,
                             "parametros": _params_validos()}), encoding="utf-8")
    params, motivo = R.carregar_parametros(p)
    assert params is None
    assert "adotado" in motivo.lower()


def test_regua_do_fit_divergente_e_RECUSADA(tmp_path):
    """🔴 O gate do F114. Parametro ajustado sob outra regua agenda um rotulo
    que ele nunca viu -- recusa nominal, nunca uso silencioso."""
    p = tmp_path / "fsrs_params.json"
    p.write_text(json.dumps({"adotado": True, "regua_do_fit": 1,
                             "parametros": _params_validos()}), encoding="utf-8")
    params, motivo = R.carregar_parametros(p, regua=2)
    assert params is None
    assert "regua" in motivo.lower() and "1" in motivo and "2" in motivo


def test_regua_do_fit_ausente_e_RECUSADA(tmp_path):
    """Ausencia nao vira permissao: sem declarar sob que regua foi ajustado,
    o conjunto e inutilizavel (o `core/fsrs_params.json` do R1 esta assim)."""
    p = tmp_path / "fsrs_params.json"
    p.write_text(json.dumps({"adotado": True, "parametros": _params_validos()}),
                 encoding="utf-8")
    params, motivo = R.carregar_parametros(p, regua=2)
    assert params is None
    assert "regua" in motivo.lower()


def test_adotado_e_casando_a_regua_carrega(tmp_path):
    esperado = _params_validos()
    p = tmp_path / "fsrs_params.json"
    p.write_text(json.dumps({"adotado": True, "regua_do_fit": 2,
                             "parametros": esperado}), encoding="utf-8")
    params, motivo = R.carregar_parametros(p, regua=2)
    assert params == esperado
    assert "adotad" in motivo.lower()


def test_params_com_tamanho_errado_sao_RECUSADOS(tmp_path):
    p = tmp_path / "fsrs_params.json"
    p.write_text(json.dumps({"adotado": True, "regua_do_fit": 2,
                             "parametros": [0.1, 0.2]}), encoding="utf-8")
    params, motivo = R.carregar_parametros(p, regua=2)
    assert params is None
    assert "21" in motivo


def test_o_arquivo_real_do_R1_nao_e_adotado():
    """Estado declarado do repo HOJE (Fork B = nao adotar nesta onda). Se alguem
    virar `adotado` sem por `regua_do_fit`, este teste e quem avisa."""
    params, motivo = R.carregar_parametros(ROOT / "core" / "fsrs_params.json")
    assert params is None, (
        "core/fsrs_params.json passou a ser adotado -- se foi de proposito, "
        "atualize este teste E cheque que `regua_do_fit` bate com REGUA_ATUAL. "
        "Motivo devolvido: %s" % motivo)


def test_adaptador_usa_o_carregador_e_mantem_retencao_em_090():
    """O rider declarado: a meta fica 0,90 enquanto nao houver duracao real."""
    from app.utils import fsrs as fsrs_mod
    assert fsrs_mod.REQUEST_RETENTION == 0.9
    assert fsrs_mod.MOTIVO_PARAMETROS                       # sempre diz por que
    assert fsrs_mod._SCHEDULER.desired_retention == 0.9


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
