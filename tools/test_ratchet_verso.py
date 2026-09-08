"""test_ratchet_verso.py — s170: a reforja nao pode engordar o verso.

Achado 2/3-B da auditoria: cards em `card_version=4` acusam 46,8% de defeito,
20/47 por verso estourado. Cada rodada de reescrita adiciona frase ao verso --
a reforja mira a frente (memoria `feedback_reforja_mira_frente`) e engorda o
verso sem ninguem medir.

O gate que faltava NAO e "verso longo" (esse ja existe, absoluto, em
`audit_card_atomicity.checar_verso`): e **crescimento**. Um verso que vai de 100
para 219 chars passa limpo pelo check absoluto e mesmo assim inchou 2x.

Ratchet (fonte unica do limite: `audit_card_atomicity.LIMITE_CHARS`):
    len(depois)     <= max(LIMITE_CHARS, len(antes))
    n_frases(depois) <= n_frases(antes)

Trava tambem a telemetria: o mesmo caminho que mede para bloquear grava os 4
numeros no evento `reforja`, para o claim causal [MEDIUM] virar medicao.

Tudo em db/log temp -- `ipub.db` real NUNCA e tocado. Asserts nativos.
"""
import json
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import pytest  # noqa: E402

import audit_card_atomicity as aca  # noqa: E402
import event_log  # noqa: E402
import recurate_cards  # noqa: E402

_DDL = """
CREATE TABLE flashcards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    questao_id INTEGER, tema_id INTEGER, tipo TEXT,
    frente_contexto TEXT, frente_pergunta TEXT, verso_resposta TEXT,
    verso_regra_mestre TEXT, verso_armadilha TEXT,
    quality_source TEXT DEFAULT 'legacy', card_version INTEGER DEFAULT 1,
    needs_qualitative INTEGER DEFAULT 0);
"""

_VERSO_CURTO = "Internacao com antibiotico endovenoso."
# 3 frases e ~240 chars: ja estoura o limite ABSOLUTO por si so.
_VERSO_INCHADO = (
    "Internacao hospitalar com antibiotico endovenoso de amplo espectro. "
    "A drenagem percutanea fica reservada para abscesso maior que quatro "
    "centimetros ou falha do tratamento clinico apos setenta e duas horas. "
    "A colectomia eletiva e discutida caso a caso apos o episodio agudo."
)


def _conn(tmp_path, verso=_VERSO_CURTO, versao=3):
    con = sqlite3.connect(str(tmp_path / "t.db"))
    con.executescript(_DDL)
    con.execute(
        "INSERT INTO flashcards (id, tipo, frente_pergunta, verso_resposta, "
        "quality_source, card_version) VALUES (1, 'conteudo', ?, ?, 'qualitative', ?)",
        ("Qual a conduta inicial?", verso, versao))
    con.commit()
    return con


def _erros(con, novo_verso):
    erros, _avisos, _plano = recurate_cards.validar(
        [{"card_id": 1, "verso_resposta": novo_verso}], con)
    return [e for e in erros if "ratchet" in e or "crescimento" in e]


# --- o ratchet puro --------------------------------------------------------

def test_medir_verso_devolve_len_e_frases():
    assert aca.medir_verso("Uma frase.") == (10, 1)
    assert aca.medir_verso("Uma. Duas. Tres.") == (16, 3)
    assert aca.medir_verso(None) == (0, 0)


def test_ratchet_bloqueia_verso_que_cresce_alem_do_limite():
    assert aca.checar_ratchet_verso(_VERSO_CURTO, _VERSO_INCHADO) is not None


def test_ratchet_permite_verso_que_encolhe():
    assert aca.checar_ratchet_verso(_VERSO_INCHADO, _VERSO_CURTO) is None


def test_ratchet_permite_verso_ja_longo_que_nao_cresce():
    # Card que JA nascia acima do limite: reescrever mantendo o tamanho e
    # legitimo -- o teto e max(LIMITE_CHARS, len(antes)), nao LIMITE_CHARS.
    antes = "x" * (aca.LIMITE_CHARS + 60) + "."
    depois = "y" * (aca.LIMITE_CHARS + 40) + "."
    assert aca.checar_ratchet_verso(antes, depois) is None


def test_ratchet_bloqueia_frase_a_mais_ainda_que_curto():
    # Sob o limite absoluto nos dois lados: o check ABSOLUTO nao ve nada.
    antes, depois = "Fato unico.", "Fato unico. Fato extra."
    assert aca.checar_verso(depois) is None, "pre-condicao: absoluto nao acusa"
    assert aca.checar_ratchet_verso(antes, depois) is not None


# --- o ratchet no caminho do recurate: BLOQUEIA (erro, nao aviso) -----------

def test_validar_bloqueia_crescimento_como_ERRO(tmp_path):
    con = _conn(tmp_path)
    try:
        assert _erros(con, _VERSO_INCHADO), "crescimento tem que entrar em `erros`"
    finally:
        con.close()


def test_validar_nao_bloqueia_reforja_que_encolhe(tmp_path):
    con = _conn(tmp_path, verso=_VERSO_INCHADO)
    try:
        assert _erros(con, _VERSO_CURTO) == []
    finally:
        con.close()


def test_validar_ignora_edicao_que_nao_toca_o_verso(tmp_path):
    con = _conn(tmp_path)
    try:
        erros, _a, _p = recurate_cards.validar(
            [{"card_id": 1, "frente_pergunta": "Qual o proximo passo?"}], con)
        assert [e for e in erros if "ratchet" in e or "crescimento" in e] == []
    finally:
        con.close()


# --- telemetria no evento --------------------------------------------------

def test_evento_carrega_os_4_numeros_do_verso(tmp_path, monkeypatch):
    log_path = str(tmp_path / "log.jsonl")
    monkeypatch.setattr(event_log, "LOG_PATH", log_path)
    con = _conn(tmp_path, verso=_VERSO_INCHADO)
    try:
        plano = [("refazer", 1, {"verso_resposta": _VERSO_CURTO}, 3, "Qual a conduta inicial?")]
        recurate_cards.aplicar(plano, con)
    finally:
        con.close()

    evs = [json.loads(l) for l in open(log_path, encoding="utf-8") if l.strip()]
    ev = [e for e in evs if e.get("tipo") == "reforja"][0]
    assert ev["len_verso_antes"] == len(_VERSO_INCHADO)
    assert ev["len_verso_depois"] == len(_VERSO_CURTO)
    assert ev["n_frases_antes"] == 3
    assert ev["n_frases_depois"] == 1
    # contrato do event_log: numeros e tags, nunca o texto.
    assert _VERSO_CURTO not in json.dumps(ev, ensure_ascii=False)



# --- o SEGUNDO writer tambem tem a guarda (senao ela e contornavel) ---------

def test_update_flashcard_fields_bloqueia_crescimento(tmp_path, monkeypatch):
    from app.utils import db
    con = _conn(tmp_path)
    con.close()
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "t.db"))
    with pytest.raises(ValueError, match="ratchet"):
        db.update_flashcard_fields(1, {"verso_resposta": _VERSO_INCHADO})
    # bloqueado antes do commit: versao intacta.
    con = sqlite3.connect(str(tmp_path / "t.db"))
    try:
        assert con.execute("SELECT card_version FROM flashcards WHERE id=1").fetchone()[0] == 3
    finally:
        con.close()


def test_update_flashcard_fields_grava_telemetria(tmp_path, monkeypatch):
    from app.utils import db
    log_path = str(tmp_path / "log2.jsonl")
    con = _conn(tmp_path, verso=_VERSO_INCHADO)
    con.close()
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "t.db"))
    monkeypatch.setattr(event_log, "LOG_PATH", log_path)
    assert db.update_flashcard_fields(1, {"verso_resposta": _VERSO_CURTO}) is True

    ev = [json.loads(l) for l in open(log_path, encoding="utf-8") if l.strip()][0]
    assert ev["len_verso_antes"] == len(_VERSO_INCHADO)
    assert ev["len_verso_depois"] == len(_VERSO_CURTO)
    assert ev["n_frases_antes"] == 3 and ev["n_frases_depois"] == 1
if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))


# --- guarda indisponivel => escrita RECUSADA (fail-loud, nao fail-open) -----

def test_ratchet_indisponivel_recusa_a_escrita_do_verso(tmp_path, monkeypatch):
    """Se o gate nao pode rodar, a escrita nao acontece.

    Degradar para WARN aqui seria escrever sem guarda dentro do proprio fix que
    existe para impedir isso -- achado do audit do /ai-eng sobre d2026a1.
    """
    from app.utils import db
    con = _conn(tmp_path)
    con.close()
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "t.db"))
    monkeypatch.setitem(sys.modules, "audit_card_atomicity", None)  # -> ImportError
    with pytest.raises(RuntimeError, match="RECUSADA"):
        db.update_flashcard_fields(1, {"verso_resposta": _VERSO_CURTO})
    con = sqlite3.connect(str(tmp_path / "t.db"))
    try:
        assert con.execute("SELECT card_version FROM flashcards WHERE id=1").fetchone()[0] == 3
    finally:
        con.close()


def test_ratchet_indisponivel_nao_bloqueia_edicao_que_nao_toca_o_verso(tmp_path, monkeypatch):
    # Recusar edicao de FRENTE por causa do ratchet do VERSO seria gratuito.
    from app.utils import db
    con = _conn(tmp_path)
    con.close()
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "t.db"))
    monkeypatch.setitem(sys.modules, "audit_card_atomicity", None)
    assert db.update_flashcard_fields(1, {"frente_pergunta": "Qual o proximo passo?"}) is True


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
