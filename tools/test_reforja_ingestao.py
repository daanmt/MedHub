"""F39 (s177, item 1.6): a worklist do detector de atomicidade vira ESTADO com lifecycle.

O defeito que isto encerra nao e "o detector nao acha" -- ele acha 270 cards. E que o
numero nao se move ha 47 dias (`ledger_self`: `card_atomicidade :: card#167` com 202
repeticoes), porque **olhar nao tinha onde ser gravado**. Um WARN solto nao distingue
"ainda nao triado" de "triado, e e falso-positivo conhecido" -- e a diferenca entre os
dois e justamente o trabalho. A fila de reforja (B2, item 0.3) ja tinha os tres
desfechos; faltava a porta de entrada mecanica.

🔴 O ponto delicado deste item: o detector tem uma classe de FALSO-POSITIVO declarada na
propria docstring -- o **card discriminador** ("A x B: qual das duas ...?"), que a regra 5
do formato atomico ENDOSSA. Ingerir sem tratar isso encheria de ruido "a unica cifra
citavel do passivo" -- a doenca que a fila cura. O tratamento nao e um regex melhor (o
desempate e contar CRITERIOS DE ACERTO, e nenhum regex faz isso): e o lifecycle. Para o
discriminador o predicado NUNCA para de disparar, entao `--fechar` recusa sempre e o
desfecho correto e `--descartar`, um estado DIFERENTE de "resolvi". Estes testes travam
essa assimetria.

Fixtures hermeticas: schema canonico via `init_db` em tmp_path, cards sinteticos com as
assinaturas reais dos dois anti-padroes.
"""
import argparse
import contextlib
import io
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from app.utils import db  # noqa: E402
import card_checks  # noqa: E402
import init_db  # noqa: E402
import reforja  # noqa: E402

# Verso em paragrafo -> resposta-multifato (acima de 220 chars).
VERSO_PARAGRAFO = (
    "A conduta inicial e estabilizar o paciente com cristaloide aquecido em bolus. "
    "Em seguida, reavaliar a resposta hemodinamica e classificar a hemorragia. "
    "Se a resposta for transitoria, indicar hemocomponentes e acionar o centro cirurgico, "
    "porque a fonte do sangramento nao foi controlada."
)
# Frente de card DISCRIMINADOR, VERBATIM do #857 do corpus real: dispara
# `duplo-ask/conectivo` ("... e qual ...") e e exatamente o caso ambiguo que
# nenhum regex resolve -- um contraste par-a-par (regra 5) escrito como duas
# perguntas. Quem decide se sao 2 CRITERIOS DE ACERTO ou 1 mapeamento e a
# leitura humana; por isso o desfecho vive em `--descartar`, nao em `--fechar`.
FRENTE_DISCRIMINADOR = ("Fluxo inspiratorio em ONDA QUADRADA x fluxo LIVRE/DESACELERADO: "
                        "qual corresponde a VCV e qual a PCV?")


def _args(**kw):
    base = dict(ingerir=None, apply=False, dry_run=False, origem=None, motivo=None,
                todas=False, json=False, limit=25, marcar=None, fechar=None,
                descartar=None, justificativa=None, forcar=False, backfill=False)
    base.update(kw)
    return argparse.Namespace(**base)


def _rodar(fn, args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = fn(args)
    return rc, buf.getvalue()


@pytest.fixture
def banco(tmp_path, monkeypatch):
    caminho = str(tmp_path / "ipub.db")
    monkeypatch.setattr(init_db, "DB_PATH", caminho)
    with contextlib.redirect_stdout(io.StringIO()):
        init_db.init_db()
    monkeypatch.setattr(db, "DB_PATH", caminho)
    conn = db.get_connection()
    conn.execute("INSERT INTO taxonomia_cronograma (id, area, tema) VALUES (1, 'Cirurgia', 'Trauma')")
    conn.execute("INSERT INTO flashcards (id, tema_id, tipo, frente_pergunta, verso_resposta, "
                 "card_version, quality_source) VALUES (1, 1, 'conteudo', ?, ?, 1, 'qualitative')",
                 ("Qual a conduta inicial no choque hemorragico?", VERSO_PARAGRAFO))
    conn.execute("INSERT INTO flashcards (id, tema_id, tipo, frente_pergunta, verso_resposta, "
                 "card_version, quality_source) VALUES (2, 1, 'conteudo', ?, 'Cancro mole.', "
                 "1, 'qualitative')", (FRENTE_DISCRIMINADOR,))
    # card SAO: uma demanda, uma frase -- o controle negativo.
    conn.execute("INSERT INTO flashcards (id, tema_id, tipo, frente_pergunta, verso_resposta, "
                 "card_version, quality_source) VALUES (3, 1, 'conteudo', "
                 "'Qual a triade de Beck?', 'Hipofonese, turgencia jugular e hipotensao.', "
                 "1, 'qualitative')")
    conn.commit()
    conn.close()
    return caminho


# --- P1: o predicado entrou no registro, sem 2a fonte de regex ----------------

def test_predicado_esta_no_registro_e_delega_sem_copiar_regex(monkeypatch):
    assert "nao_atomico" in card_checks.PREDICADOS_VERIFICAVEIS
    import audit_card_atomicity as aca
    # Se `card_checks` tivesse COPIADO a regex, trocar a fonte nao mudaria nada.
    monkeypatch.setattr(aca, "checar_front", lambda t: "sentinela-de-delegacao")
    assert card_checks.checar_nao_atomico({"frente_pergunta": "x", "verso_resposta": "y"}) \
        == "sentinela-de-delegacao", \
        "checar_nao_atomico tem que DELEGAR a audit_card_atomicity, nunca reimplementar"


def test_shape_do_scan_bate_com_o_shape_do_fechamento(banco):
    """Varredura e re-verificacao TEM que ler os mesmos campos -- senao o gate mente."""
    conn = db.get_connection()
    try:
        do_fechamento = set(db._card_para_predicado(conn, 1))
    finally:
        conn.close()
    do_scan = set(db.cards_ativos_para_predicado()[0]) - {"id"}
    assert do_scan == do_fechamento


# --- P2: ingestao ------------------------------------------------------------

def test_ingerir_recusa_motivo_sem_predicado(banco, capsys):
    rc = reforja.cmd_ingerir(_args(ingerir="pacote_de_fatos"))
    assert rc == 1, "motivo sem predicado tem que FALHAR alto, nao criar marca orfa"
    err = capsys.readouterr().err
    assert "PREDICADOS_VERIFICAVEIS" in err and "nao_atomico" in err


def test_dry_run_declara_count_e_nao_escreve(banco):
    rc, out = _rodar(reforja.cmd_ingerir, _args(ingerir="nao_atomico"))
    assert rc == 0
    assert "COUNT-ASSERT declarado ANTES de escrever: 2 linha(s)" in out
    assert "DRY-RUN" in out
    assert db.fila_reforja() == [], "dry-run escreveu -- o COUNT deixou de ser assert"


def test_apply_escreve_exatamente_o_count_declarado(banco):
    rc, out = _rodar(reforja.cmd_ingerir, _args(ingerir="nao_atomico", apply=True))
    assert rc == 0
    assert "[APLICADO] 2 linha(s)" in out
    fila = db.fila_reforja()
    assert sorted(d["card_id"] for d in fila) == [1, 2]
    assert all(d["motivo"] == "nao_atomico" and d["aberta"] for d in fila)


def test_card_sao_nunca_entra_na_fila(banco):
    _rodar(reforja.cmd_ingerir, _args(ingerir="nao_atomico", apply=True))
    assert 3 not in [d["card_id"] for d in db.fila_reforja()], \
        "o controle negativo entrou -- o predicado esta acusando card atomico"


def test_reingerir_e_idempotente_e_nao_infla_n_marcacoes(banco):
    _rodar(reforja.cmd_ingerir, _args(ingerir="nao_atomico", apply=True))
    rc, out = _rodar(reforja.cmd_ingerir, _args(ingerir="nao_atomico", apply=True))
    assert rc == 0
    assert "ja ABERTAS      : 2" in out
    assert "[APLICADO] 0 linha(s)" in out
    assert all(d["n_marcacoes"] == 1 for d in db.fila_reforja()), \
        "re-rodar o detector inflou n_marcacoes -- o numero passa a medir o sensor, nao a divida"


def test_descartada_nao_e_reaberta_pela_varredura(banco):
    """O veredito humano ('olhei, e discriminador legitimo') sobrevive ao detector."""
    _rodar(reforja.cmd_ingerir, _args(ingerir="nao_atomico", apply=True))
    db.descartar_reforja(2, "nao_atomico", "card discriminador: 1 criterio de acerto (regra 5)")
    assert 2 not in [d["card_id"] for d in db.fila_reforja()]
    rc, out = _rodar(reforja.cmd_ingerir, _args(ingerir="nao_atomico", apply=True))
    assert rc == 0
    assert "[APLICADO] 0 linha(s)" in out
    assert 2 not in [d["card_id"] for d in db.fila_reforja()], \
        "a varredura reabriu um descarte -- o trabalho humano seria apagado a cada rodada"


def test_encerrada_que_ainda_acusa_e_REPORTADA_nao_re_marcada(banco):
    """Classe F82: fechar com --forcar e o defeito continuar la tem que ser VISIVEL."""
    _rodar(reforja.cmd_ingerir, _args(ingerir="nao_atomico", apply=True))
    db.fechar_reforja(1, "nao_atomico", forcar=True, justificativa="fechei sem consertar")
    rc, out = _rodar(reforja.cmd_ingerir, _args(ingerir="nao_atomico", apply=True))
    assert "ja encerradas   : 1" in out
    assert "F82" in out and "[1]" in out
    assert "[APLICADO] 0 linha(s)" in out, "re-abriu em silencio -- o fechamento falso ficaria escondido"


# --- P3: a assimetria fechar x descartar no falso-positivo conhecido ---------

def test_discriminador_nao_fecha_por_fechar_e_fecha_por_descartar(banco):
    _rodar(reforja.cmd_ingerir, _args(ingerir="nao_atomico", apply=True))
    with pytest.raises(db.ReforjaAindaDefeituosa):
        db.fechar_reforja(2, "nao_atomico")
    db.descartar_reforja(2, "nao_atomico", "regra 5: contraste com 1 criterio de acerto")
    assert 2 not in [d["card_id"] for d in db.fila_reforja()]


def test_fechar_de_verdade_exige_o_card_consertado(banco):
    with pytest.raises(db.ReforjaAindaDefeituosa):
        db.fechar_reforja(1, "nao_atomico")
    conn = db.get_connection()
    conn.execute("UPDATE flashcards SET verso_resposta = 'Cristaloide aquecido em bolus.' WHERE id = 1")
    conn.commit()
    conn.close()
    db.fechar_reforja(1, "nao_atomico")   # agora o predicado nao acusa mais
    assert 1 not in [d["card_id"] for d in db.fila_reforja()]
