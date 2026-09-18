"""test_card_por_id.py -- F99 (s187): existe porta para ler UM card por id.

O defeito: **nenhuma superficie servia um card arbitrario com as frentes.**
`fsrs_queue --next/--list` servem so o VENCIDO; `--preview CARD_ID` aceita id arbitrario
mas devolve so o calendario das 4 notas; `reforja`/`cards_regen_queue`/
`audit_flashcard_quality` operam por predicado ou fila.

Consequencia medida (s178): o re-drill inter-sessao que o `revisar.md` prescreve -- e que
a primeira linha do `HANDOFF.md` mandava fazer -- **so funcionava por acaso**. Dos 12
cards, 6 estavam na fila do dia por coincidencia (relearning) e **3 ficaram inalcancaveis**
(#311, #453, #1539); as frentes foram reconstruidas de `history/session_175.md`, que NAO e
a fonte -- o card pode ter sido reforjado desde entao.

🔴 Classe: Reachability-Debt, forma *sem consulta* -- o dado existe, esta correto, e nao ha
porta. Agravante: **a instrucao que exige a porta e lida no boot de toda sessao**. Regra
certa que nao alcanca, um nivel acima do F90.

Invariante que estes testes protegem: o leitor e **READ-ONLY**. Um leitor que mexesse no
`due` ao servir transformaria "eu olhei o card" em "eu revisei o card" -- o mesmo modo de
falha do Invariante A (`test_invariante_a`), com outra porta.
"""
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _db_sintetico(tmp_path):
    """Banco minimo: 1 card ativo vencido, 1 ativo com due no futuro, 1 APOSENTADO."""
    p = tmp_path / "t.db"
    con = sqlite3.connect(p)
    con.executescript("""
        CREATE TABLE taxonomia_cronograma (id INTEGER PRIMARY KEY, area TEXT, tema TEXT);
        CREATE TABLE flashcards (id INTEGER PRIMARY KEY, questao_id INTEGER, tema_id INTEGER,
            tipo TEXT, frente_contexto TEXT, frente_pergunta TEXT, verso_resposta TEXT,
            verso_regra_mestre TEXT, verso_armadilha TEXT, quality_source TEXT,
            card_version INTEGER DEFAULT 1, needs_qualitative INTEGER DEFAULT 0);
        CREATE TABLE fsrs_cards (card_id INTEGER PRIMARY KEY, state INTEGER, due DATETIME,
            stability REAL, difficulty REAL, elapsed_days INTEGER, scheduled_days INTEGER,
            reps INTEGER, lapses INTEGER, last_review DATETIME);
        INSERT INTO taxonomia_cronograma VALUES (1, 'Pediatria', 'Cardiopatias');
        INSERT INTO flashcards (id, questao_id, tema_id, frente_contexto, frente_pergunta,
            verso_resposta, needs_qualitative)
          VALUES (10, 7, 1, 'RN de 4 dias.', 'Por que a cianose e diferencial?', 'Canal.', 0),
                 (11, NULL, 1, 'Contexto B.', 'Pergunta B?', 'Resposta B.', 0),
                 (12, NULL, 1, 'Contexto C.', 'Pergunta C?', 'Resposta C.', 2);
        INSERT INTO fsrs_cards VALUES (10, 2, '2020-01-01 00:00:00', 1.0, 5.0, 0, 0, 3, 1, NULL),
                                      (11, 2, '2099-01-01 00:00:00', 9.0, 5.0, 0, 0, 1, 0, NULL),
                                      (12, 2, '2099-01-01 00:00:00', 9.0, 5.0, 0, 0, 1, 0, NULL);
    """)
    con.commit(); con.close()
    return str(p)


def _db(tmp_path, monkeypatch):
    from app.utils import db
    monkeypatch.setattr(db, "DB_PATH", _db_sintetico(tmp_path))
    return db


# --- a porta existe e serve o que a fila nao serve ------------------------------------

def test_serve_card_FORA_da_fila(tmp_path, monkeypatch):
    """O card #11 tem `due` em 2099 -- nenhuma fila o entregaria. E o caso dos 3
    inalcancaveis da s178."""
    db = _db(tmp_path, monkeypatch)
    c = db.card_por_id(11)
    assert c is not None and c["card_id"] == 11
    assert c["frente_pergunta"] == "Pergunta B?" and c["verso_resposta"] == "Resposta B."
    assert c["ativo"] is True


def test_serve_APOSENTADO_com_ativo_false_em_vez_de_sumir(tmp_path, monkeypatch):
    """Quem depura um card defeituoso precisa exatamente do que foi aposentado.
    Silencio aqui seria a negativa ambigua que o F91 matou."""
    db = _db(tmp_path, monkeypatch)
    c = db.card_por_id(12)
    assert c is not None and c["ativo"] is False
    assert c["frente_pergunta"] == "Pergunta C?"


def test_id_inexistente_devolve_None_e_nao_levanta(tmp_path, monkeypatch):
    db = _db(tmp_path, monkeypatch)
    assert db.card_por_id(99999) is None


def test_traz_area_tema_e_estado_fsrs(tmp_path, monkeypatch):
    db = _db(tmp_path, monkeypatch)
    c = db.card_por_id(10)
    assert c["area"] == "Pediatria" and c["tema"] == "Cardiopatias"
    assert c["state"] == 2 and c["reps"] == 3 and c["lapses"] == 1
    assert c["questao_id"] == 7


def test_selection_reason_nao_mente_a_origem(tmp_path, monkeypatch):
    """O objeto tem a forma da fila, mas NAO veio da fila. Se carregasse
    `vencido`/`novo`, um consumidor (ou o revlog) registraria origem falsa -- e a
    classe F76, que existe para o `reason_servido` nao mentir."""
    db = _db(tmp_path, monkeypatch)
    assert db.card_por_id(10)["selection_reason"] == "por_id"


# --- READ-ONLY: o invariante que protege o FSRS ----------------------------------------

def test_ler_um_card_NAO_altera_nada(tmp_path, monkeypatch):
    """Um leitor que mexesse no `due` transformaria 'eu olhei' em 'eu revisei'."""
    db = _db(tmp_path, monkeypatch)
    con = sqlite3.connect(db.DB_PATH)
    antes = con.execute("SELECT card_id, state, due, stability, difficulty, reps, lapses "
                        "FROM fsrs_cards ORDER BY card_id").fetchall()
    con.close()
    for cid in (10, 11, 12, 99999):
        db.card_por_id(cid)
    con = sqlite3.connect(db.DB_PATH)
    depois = con.execute("SELECT card_id, state, due, stability, difficulty, reps, lapses "
                         "FROM fsrs_cards ORDER BY card_id").fetchall()
    n_rev = con.execute("SELECT COUNT(*) FROM sqlite_master WHERE name='fsrs_revlog'").fetchone()[0]
    con.close()
    assert antes == depois, "servir um card por id mexeu no FSRS"
    assert n_rev == 0, "nenhuma tabela de revlog deveria ter sido criada por uma LEITURA"


def test_leitor_nao_esta_na_allowlist_de_writers():
    """F49: quem so le nao pode aparecer como writer. Guarda contra alguem 'melhorar'
    o leitor carimbando last_review ao servir."""
    import test_writer_allowlist as wa
    fonte = open(os.path.join(ROOT, "app", "utils", "db.py"), encoding="utf-8").read()
    ini = fonte.index("def card_por_id(")
    fim = fonte.index("def preview_ratings(", ini)
    corpo = fonte[ini:fim]
    assert wa.tabelas_escritas(corpo) == set(), \
        "card_por_id escreve em alguma tabela -- tem que ser READ-ONLY"


# --- a flag chega ao CLI ---------------------------------------------------------------

def test_a_flag_card_existe_no_fsrs_queue():
    """Sem a flag o leitor seria 'construido-e-nunca-conectado' (D4) -- que e a mesma
    familia do proprio F99."""
    import ast
    fonte = open(os.path.join(ROOT, "tools", "fsrs_queue.py"), encoding="utf-8").read()
    arvore = ast.parse(fonte)
    flags = set()
    for n in ast.walk(arvore):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == "add_argument" and n.args
                and isinstance(n.args[0], ast.Constant)):
            flags.add(n.args[0].value)
    assert "--card" in flags
    assert "db.card_por_id" in fonte, "a flag tem que chamar o leitor, nao reimplementar"
