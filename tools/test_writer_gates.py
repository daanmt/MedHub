"""test_writer_gates.py — gate de qualidade nos writers restantes (part-4).

Cobre: insert_card_base e insert_card_extra recusando lote com defeito (zero
linhas) e gravando lote valido; recurate_cards rejeitando item vazio (fim do
no-op disfarcado: card_version NAO incrementa) e item reprovado no gate.
Tudo em db temp. Pytest-nativo + standalone.
"""
import contextlib
import importlib
import io
import json
import os
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

_DDL = """
CREATE TABLE taxonomia_cronograma (id INTEGER PRIMARY KEY AUTOINCREMENT,
    area TEXT, tema TEXT, questoes_realizadas INTEGER DEFAULT 0,
    questoes_acertadas INTEGER DEFAULT 0, percentual_acertos REAL DEFAULT 0,
    ultima_revisao TEXT);
CREATE TABLE questoes_erros (id INTEGER PRIMARY KEY AUTOINCREMENT,
    tema_id INTEGER, titulo TEXT);
CREATE TABLE flashcards (id INTEGER PRIMARY KEY AUTOINCREMENT,
    questao_id INTEGER, tema_id INTEGER, tipo TEXT, frente_contexto TEXT,
    frente_pergunta TEXT, verso_resposta TEXT, verso_regra_mestre TEXT,
    verso_armadilha TEXT, quality_source TEXT DEFAULT 'legacy',
    card_version INTEGER DEFAULT 1, needs_qualitative INTEGER DEFAULT 0);
CREATE TABLE fsrs_cards (card_id INTEGER PRIMARY KEY, state INTEGER, due TIMESTAMP);
"""


def _import_writer(nome):
    """Writers antigos mexem em sys.stdout no import — protege o capture."""
    orig = sys.stdout
    sys.stdout = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
    try:
        return importlib.import_module(nome)
    finally:
        sys.stdout = orig


def _db_temp():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    con = sqlite3.connect(path)
    con.executescript(_DDL)
    con.commit()
    con.close()
    return path


def _json_temp(payload):
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False)
    return path


def _rodar(mod, argv, db_path):
    """Roda mod.main() com argv/db patchados. Retorna (exit_code, stdout).

    Aceita os DOIS estilos de saida: `sys.exit(n)` de dentro do main (writers
    antigos) e `return n` com o `sys.exit(main())` no __main__ (estilo que o
    recurate_cards herdou do apply_reforja na fusao da part-6). Sem isso, um
    main() que RETORNA 1 seria lido como sucesso -- teste verde decorativo.
    """
    orig_argv, orig_db = sys.argv, mod.DB_PATH
    sys.argv, mod.DB_PATH = argv, db_path
    out = io.StringIO()
    code = 0
    try:
        with contextlib.redirect_stdout(out):
            try:
                ret = mod.main()
                if isinstance(ret, int):
                    code = ret
            except SystemExit as e:
                code = int(e.code or 0)
    finally:
        sys.argv, mod.DB_PATH = orig_argv, orig_db
    return code, out.getvalue()


def _count(db, tabela="flashcards"):
    con = sqlite3.connect(db)
    n = con.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
    con.close()
    return n


CARD_OK = {"frente_pergunta": "Qual o criterio diagnostico da sindrome ficticia?",
           "verso_resposta": "Criterio Y maior que limiar Z."}
CARD_TEMPLATE = {"frente_pergunta": "Tema Generico: qual a conduta/criterio correto?",
                 "verso_resposta": "Resposta qualquer."}
CARD_ENCODING = {"frente_pergunta": "Qual a sequencia da via ficticia?",
                 "verso_resposta": "A → B em duas etapas."}


def test_base_gate_reprova_e_nada_grava():
    icb = _import_writer("insert_card_base")
    db, lote = _db_temp(), _json_temp([CARD_OK, CARD_TEMPLATE])
    try:
        code, out = _rodar(icb, ["insert_card_base.py", "--area", "Cirurgia", "--tema", "T",
                                 "--from", lote], db)
        assert code == 1, f"gate reprovado deve sair 1 (got {code})"
        assert _count(db) == 0, "all-or-nothing: NADA gravado"
        assert "template-conduta-criterio" in out
    finally:
        os.remove(db)
        os.remove(lote)


def test_base_grava_lote_valido():
    icb = _import_writer("insert_card_base")
    db, lote = _db_temp(), _json_temp([CARD_OK])
    try:
        code, _ = _rodar(icb, ["insert_card_base.py", "--area", "Cirurgia", "--tema", "T",
                               "--from", lote], db)
        assert code == 0
        assert _count(db) == 1 and _count(db, "fsrs_cards") == 1
    finally:
        os.remove(db)
        os.remove(lote)


def test_extra_gate_reprova_encoding():
    ice = _import_writer("insert_card_extra")
    db = _db_temp()
    lote = _json_temp([dict(CARD_ENCODING, questao_id=1, tema_id=1)])
    try:
        code, out = _rodar(ice, ["insert_card_extra.py", "--from", lote, "--apply"], db)
        assert code == 1 and _count(db) == 0
        assert "seta Unicode" in out
    finally:
        os.remove(db)
        os.remove(lote)


def test_extra_grava_valido():
    ice = _import_writer("insert_card_extra")
    db = _db_temp()
    con = sqlite3.connect(db)
    con.execute("INSERT INTO taxonomia_cronograma (id, area, tema) VALUES (1, 'Cirurgia', 'T')")
    con.execute("INSERT INTO questoes_erros (id, tema_id, titulo) VALUES (1, 1, 'caso')")
    con.commit()
    con.close()
    lote = _json_temp([dict(CARD_OK, questao_id=1, tema_id=1)])
    try:
        code, _ = _rodar(ice, ["insert_card_extra.py", "--from", lote, "--apply"], db)
        assert code == 0 and _count(db) == 1
    finally:
        os.remove(db)
        os.remove(lote)


def _db_com_card():
    db = _db_temp()
    con = sqlite3.connect(db)
    con.execute("INSERT INTO flashcards (id, tipo, frente_pergunta, verso_resposta, "
                "quality_source, card_version) VALUES (1, 'conteudo', 'P?', 'R.', 'heuristic', 1)")
    con.commit()
    con.close()
    return db


def _card1(db):
    con = sqlite3.connect(db)
    row = con.execute("SELECT card_version, quality_source, frente_pergunta "
                      "FROM flashcards WHERE id=1").fetchone()
    con.close()
    return row


def test_recurate_item_vazio_rejeitado_sem_noop():
    rc = _import_writer("recurate_cards")
    db, lote = _db_com_card(), _json_temp([{"card_id": 1}])
    try:
        code, out = _rodar(rc, ["recurate_cards.py", "--from", lote], db)
        assert code == 1, "item vazio -> exit 1"
        assert _card1(db) == (1, "heuristic", "P?"), \
            "no-op NAO incrementa versao nem flipa quality_source"
        assert "nenhum campo valido" in out
    finally:
        os.remove(db)
        os.remove(lote)


def test_recurate_gate_rejeita_template():
    rc = _import_writer("recurate_cards")
    db = _db_com_card()
    lote = _json_temp([{"card_id": 1, "pergunta": "X: qual a conduta/criterio correto?"}])
    try:
        code, out = _rodar(rc, ["recurate_cards.py", "--from", lote], db)
        assert code == 1 and _card1(db)[0] == 1, "reprovado nao aplica"
        assert "template-conduta-criterio" in out
    finally:
        os.remove(db)
        os.remove(lote)


def test_recurate_valido_aplica():
    """part-6 (fusao a): --apply passou a ser OBRIGATORIO para gravar.

    Antes o default do recurate_cards era GRAVAR (--dry-run era opt-in); o
    apply_reforja, que este CLI absorveu, tinha o default inverso (dry-run,
    --apply para gravar). Fundir mantendo o default mais frouxo rebaixaria o
    rigor -- justamente o que a fusao existe para impedir. Por isso o teste
    mudou: a invocacao sem --apply agora e o caso `test_recurate_dry_run_default`.
    """
    rc = _import_writer("recurate_cards")
    db = _db_com_card()
    lote = _json_temp([{"card_id": 1, "pergunta": "Qual o criterio da sindrome ficticia?"}])
    try:
        code, _ = _rodar(rc, ["recurate_cards.py", "--from", lote, "--apply"], db)
        ver, qs, fp = _card1(db)
        assert code == 0 and ver == 2 and qs == "qualitative"
        assert fp == "Qual o criterio da sindrome ficticia?"
    finally:
        os.remove(db)
        os.remove(lote)


def test_recurate_dry_run_default():
    """Sem --apply: gate aprova, exit 0, e NADA e gravado (dry-run default)."""
    rc = _import_writer("recurate_cards")
    db = _db_com_card()
    lote = _json_temp([{"card_id": 1, "pergunta": "Qual o criterio da sindrome ficticia?"}])
    try:
        code, out = _rodar(rc, ["recurate_cards.py", "--from", lote], db)
        assert code == 0, "lote valido em dry-run sai 0"
        assert _card1(db) == (1, "heuristic", "P?"), "dry-run NAO grava"
        assert "dry-run" in out
    finally:
        os.remove(db)
        os.remove(lote)


def test_recurate_absorve_gate_atomicidade():
    """Absorcao do gate 3 do apply_reforja: reforja que continua duplo-ask
    NAO entra -- e o rebaixamento --permitir-atomicidade a deixa passar."""
    rc = _import_writer("recurate_cards")
    db = _db_com_card()
    duplo = "Qual o criterio da sindrome ficticia e qual a dose inicial?"
    lote = _json_temp([{"card_id": 1, "pergunta": duplo}])
    try:
        code, out = _rodar(rc, ["recurate_cards.py", "--from", lote, "--apply"], db)
        assert code == 1, "duplo-ask bloqueia"
        assert _card1(db)[0] == 1, "nada aplicado"
        assert "AVISO-ATOMICIDADE" in out and "duplo-ask" in out
        code2, _ = _rodar(rc, ["recurate_cards.py", "--from", lote, "--apply",
                               "--permitir-atomicidade"], db)
        assert code2 == 0 and _card1(db)[0] == 2, "rebaixamento explicito aplica"
    finally:
        os.remove(db)
        os.remove(lote)


def test_recurate_all_or_nothing():
    """Absorcao do all-or-nothing: um item ruim no lote impede TODO o lote.

    Antes da part-6 o recurate aplicava item a item e commitava os bons --
    lote parcialmente aplicado, o estado que ninguem sabe descrever.
    """
    rc = _import_writer("recurate_cards")
    db = _db_com_card()
    con = sqlite3.connect(db)
    con.execute("INSERT INTO flashcards (id, tipo, frente_pergunta, verso_resposta, "
                "quality_source, card_version) VALUES (2, 'conteudo', 'Q?', 'R.', "
                "'heuristic', 1)")
    con.commit()
    con.close()
    lote = _json_temp([
        {"card_id": 1, "pergunta": "Qual o criterio da sindrome ficticia?"},   # bom
        {"card_id": 2, "pergunta": "X: qual a conduta/criterio correto?"},     # ruim
    ])
    try:
        code, out = _rodar(rc, ["recurate_cards.py", "--from", lote, "--apply"], db)
        assert code == 1
        assert "all-or-nothing" in out
        con = sqlite3.connect(db)
        vers = [r[0] for r in con.execute("SELECT card_version FROM flashcards ORDER BY id")]
        con.close()
        assert vers == [1, 1], f"o item BOM tambem nao pode ter sido aplicado (got {vers})"
    finally:
        os.remove(db)
        os.remove(lote)


def test_recurate_aceita_nomes_v5_do_apply_reforja():
    """Lotes no formato do falecido apply_reforja (nomes de coluna v5) seguem
    valendo -- a fusao nao invalida JSON ja gerado."""
    rc = _import_writer("recurate_cards")
    db = _db_com_card()
    lote = _json_temp([{"card_id": 1,
                        "frente_pergunta": "Qual o criterio da sindrome ficticia?",
                        "verso_resposta": "Criterio Y acima do limiar Z."}])
    try:
        code, _ = _rodar(rc, ["recurate_cards.py", "--from", lote, "--apply"], db)
        assert code == 0
        ver, qs, fp = _card1(db)
        assert ver == 2 and qs == "qualitative"
        assert fp == "Qual o criterio da sindrome ficticia?"
    finally:
        os.remove(db)
        os.remove(lote)


# ---------------------------------------------------------------------------------------
# Fase 0 Lote 1 part-3 (P6): card de consolidacao ancorado na RESPOSTA EMED (emed_card_ancora),
# nunca num erro vizinho. Modelo (decisao do planner, correcao N=3): `flashcards.questao_id` =
# ORIGEM do card (0..1, o erro de onde nasceu; NULL se so consolida); `emed_card_ancora` = as
# ancoras de consolidacao (0..n, N:M com emed_respostas(lista,num)). Invariante: card `conteudo`
# tem AO MENOS UMA ancora (questao_id ou emed). Tudo sobre `db_sintetico` (schema canonico).

def _seed_p6(caminho):
    """Seed comum: tema 2, erros 1 e 2, cards 20/21 ancorados 'por proximidade' no erro 1, e
    respostas: t40_5/t40_8/t40_9 certas sem erro; t40_6 errada; t40_7 certa mas ligada ao erro 1."""
    from app.utils import db
    con = sqlite3.connect(caminho)
    con.execute("PRAGMA foreign_keys = ON")
    db._ensure_emed_tables(con)
    con.execute("INSERT INTO taxonomia_cronograma (id, area, tema) VALUES (2, 'Obstetricia', 'DMG')")
    con.execute("INSERT INTO questoes_erros (id, tema_id) VALUES (1, 1)")
    con.execute("INSERT INTO questoes_erros (id, tema_id) VALUES (2, 2)")
    for cid in (20, 21):
        con.execute("INSERT INTO flashcards (id, questao_id, tema_id, tipo, frente_pergunta, "
                    "verso_resposta) VALUES (?, 1, 1, 'conteudo', ?, 'R.')", (cid, f"P{cid}?"))
    for num, correta, qerr in ((5, 1, None), (6, 0, None), (7, 1, 1), (8, 1, None), (9, 1, None)):
        con.execute("INSERT INTO emed_respostas (lista, num, correta, confianca, questao_erro_id) "
                    "VALUES ('t40', ?, ?, 'duvida', ?)", (num, correta, qerr))
    con.commit()
    con.close()


def _sha(caminho):
    import hashlib
    with open(caminho, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _q(caminho, sql, args=()):
    con = sqlite3.connect(caminho)
    try:
        return con.execute(sql, args).fetchall()
    finally:
        con.close()


def _orfaos(caminho):
    """Card `conteudo` sem NENHUMA ancora: questao_id nulo e zero linhas em emed_card_ancora."""
    return _q(caminho, "SELECT id FROM flashcards f WHERE tipo = 'conteudo' AND questao_id IS NULL "
                       "AND NOT EXISTS (SELECT 1 FROM emed_card_ancora a WHERE a.card_id = f.id)")


# --- DoD 2: tabela + writer unico db.emed_ancorar_card ---------------------------------

def test_ancora_ddl_idempotente_e_duas_fks(db_sintetico):
    from app.utils import db
    con = sqlite3.connect(db_sintetico)
    try:
        db._ensure_emed_tables(con)
        db._ensure_emed_tables(con)  # 2x sem erro
        fks = {(r[2], r[3], r[4]) for r in con.execute("PRAGMA foreign_key_list(emed_card_ancora)")}
    finally:
        con.close()
    assert ("flashcards", "card_id", "id") in fks
    assert ("emed_respostas", "lista", "lista") in fks and ("emed_respostas", "num", "num") in fks


def _ancorar(caminho, lista, num, card_id):
    from app.utils import db
    con = sqlite3.connect(caminho)
    con.execute("PRAGMA foreign_keys = ON")
    try:
        r = db.emed_ancorar_card(con, lista, num, card_id)
        con.commit()
        return r
    finally:
        con.close()


def _recusa(caminho, lista, num, card_id, trecho):
    import pytest
    with pytest.raises(ValueError, match=trecho):
        _ancorar(caminho, lista, num, card_id)
    assert _q(caminho, "SELECT COUNT(*) FROM emed_card_ancora")[0][0] == 0, "recusa = nada gravado"


def test_ancora_recusa_resposta_inexistente(db_sintetico):
    _seed_p6(db_sintetico)
    _recusa(db_sintetico, "t40", 99, 20, "nao existe")


def test_ancora_recusa_resposta_com_erro(db_sintetico):
    _seed_p6(db_sintetico)
    _recusa(db_sintetico, "t40", 7, 20, "ancore no erro #1")


def test_ancora_recusa_resposta_errada(db_sintetico):
    _seed_p6(db_sintetico)
    _recusa(db_sintetico, "t40", 6, 20, "registre o erro antes")


def test_ancora_recusa_card_inexistente(db_sintetico):
    _seed_p6(db_sintetico)
    _recusa(db_sintetico, "t40", 5, 999, "card 999")


def test_ancora_mesmo_par_e_noop(db_sintetico):
    _seed_p6(db_sintetico)
    assert _ancorar(db_sintetico, "t40", 5, 20) is True
    assert _ancorar(db_sintetico, "t40", 5, 20) is False
    assert _q(db_sintetico, "SELECT card_id, lista, num FROM emed_card_ancora") == [(20, "t40", 5)]


# --- DoD 3: insert_card_extra aceita a ancora emed (e recusa card sem ancora) ------------

CARD_EMED = {"frente_pergunta": "Qual o criterio de rastreio da sindrome ficticia?",
             "verso_resposta": "Criterio Y maior que limiar Z.", "tema_id": 2}


def _extra(caminho, cards, *flags):
    ice = _import_writer("insert_card_extra")
    lote = _json_temp(cards)
    try:
        return _rodar(ice, ["insert_card_extra.py", "--from", lote, *flags], caminho)
    finally:
        os.remove(lote)


def test_extra_emed_valido_duas_ancoras(db_sintetico):
    _seed_p6(db_sintetico)
    code, out = _extra(db_sintetico, [dict(CARD_EMED, emed=["t40_5", "t40_8"])], "--apply")
    assert code == 0, out
    novo = _q(db_sintetico, "SELECT id, questao_id, tema_id FROM flashcards WHERE frente_pergunta=?",
              (CARD_EMED["frente_pergunta"],))
    assert len(novo) == 1 and novo[0][1] is None and novo[0][2] == 2
    cid = novo[0][0]
    assert _q(db_sintetico, "SELECT lista, num FROM emed_card_ancora WHERE card_id=? ORDER BY num",
              (cid,)) == [("t40", 5), ("t40", 8)]
    assert _q(db_sintetico, "SELECT COUNT(*) FROM fsrs_cards WHERE card_id=?", (cid,))[0][0] == 1
    # idempotencia: a mesma frente ja ancorada no mesmo (lista, num) vira [SKIP]
    code2, out2 = _extra(db_sintetico, [dict(CARD_EMED, emed=["t40_5", "t40_8"])], "--apply")
    assert code2 == 0 and "[SKIP]" in out2
    assert _q(db_sintetico, "SELECT COUNT(*) FROM flashcards")[0][0] == 3
    assert _orfaos(db_sintetico) == []


def test_extra_origem_e_ancora_juntas(db_sintetico):
    """Um card pode ter ORIGEM (questao_id do erro) E ancoras de consolidacao (o caso do 1947)."""
    _seed_p6(db_sintetico)
    code, out = _extra(db_sintetico, [dict(CARD_EMED, questao_id=2, emed="t40_9")], "--apply")
    assert code == 0, out
    assert _q(db_sintetico, "SELECT f.questao_id, a.lista, a.num FROM flashcards f JOIN "
                            "emed_card_ancora a ON a.card_id = f.id") == [(2, "t40", 9)]


def test_extra_emed_resposta_errada_recusada(db_sintetico):
    _seed_p6(db_sintetico)
    antes = _sha(db_sintetico)
    code, out = _extra(db_sintetico, [dict(CARD_EMED, emed="t40_6")], "--apply")
    assert code == 1 and "NADA gravado" in out and "registre o erro antes" in out
    assert _sha(db_sintetico) == antes


def test_extra_emed_resposta_com_erro_recusada(db_sintetico):
    _seed_p6(db_sintetico)
    antes = _sha(db_sintetico)
    code, out = _extra(db_sintetico, [dict(CARD_EMED, emed=["t40_7"])], "--apply")
    assert code == 1 and "NADA gravado" in out and "ancore no erro #1" in out
    assert _sha(db_sintetico) == antes


def test_extra_sem_ancora_recusado(db_sintetico):
    """Substitui o `[SKIP] sem questao_id` silencioso: o [SKIP] era o que escondia o P6."""
    _seed_p6(db_sintetico)
    antes = _sha(db_sintetico)
    code, out = _extra(db_sintetico, [dict(CARD_EMED)], "--apply")
    assert code == 1 and "NADA gravado" in out and "sem ancora" in out
    assert _sha(db_sintetico) == antes


def test_extra_ancora_invalida_no_lote_nada_gravado(db_sintetico):
    """Validacao de TODAS as ancoras antes da 1a escrita: o card bom tambem nao entra."""
    _seed_p6(db_sintetico)
    bom = dict(CARD_OK, questao_id=2, tema_id=2)
    code, out = _extra(db_sintetico, [bom, dict(CARD_EMED, emed="t40_99")], "--apply")
    assert code == 1 and "NADA gravado" in out
    assert _q(db_sintetico, "SELECT COUNT(*) FROM flashcards")[0][0] == 2


def test_extra_dry_run_nao_toca_o_banco(db_sintetico):
    _seed_p6(db_sintetico)
    con = sqlite3.connect(db_sintetico)
    con.execute("DROP TABLE emed_card_ancora")  # dry-run nao roda DDL
    con.commit()
    con.close()
    antes = _sha(db_sintetico)
    code, out = _extra(db_sintetico, [dict(CARD_EMED, emed=["t40_5", "t40_8"])])
    assert code == 0 and "dry-run" in out, out
    assert _sha(db_sintetico) == antes
    assert _q(db_sintetico, "SELECT name FROM sqlite_master WHERE name='emed_card_ancora'") == []


# --- DoD 4: --reancorar com rito (dry-run default, --expect, fixado, transacao) ---------

REANCORAR = [{"card_id": 20, "emed": ["t40_5", "t40_8"], "tema_id": 2},
             {"card_id": 21, "emed": ["t40_9"], "tema_id": 2, "questao_id": 2}]


def _reancorar(caminho, plano, *flags, monkeypatch=None, fixar=None):
    ice = _import_writer("insert_card_extra")
    if monkeypatch is not None and fixar is not None:
        monkeypatch.setattr(ice, "_fixar_antes", fixar)
    arq = _json_temp(plano)
    try:
        return _rodar(ice, ["insert_card_extra.py", "--reancorar", arq, *flags], caminho)
    finally:
        os.remove(arq)


def test_reancorar_dry_run_mudo(db_sintetico):
    _seed_p6(db_sintetico)
    antes = _sha(db_sintetico)
    code, out = _reancorar(db_sintetico, REANCORAR)
    assert code == 0, out
    assert "questao_id 1 -> NULL" in out and "tema_id 1 -> 2" in out
    assert "questao_id 1 -> 2" in out and "t40_5" in out and "t40_9" in out
    assert "2 card(s) mudam" in out and "3 ancora(s)" in out
    assert _sha(db_sintetico) == antes


def test_reancorar_expect_errado_exit2_nada_gravado(db_sintetico):
    _seed_p6(db_sintetico)
    antes = _sha(db_sintetico)
    code, out = _reancorar(db_sintetico, REANCORAR, "--apply", "--expect", "5")
    assert code == 2 and "--expect 5" in out and "2 card(s) mudam" in out, out
    assert _sha(db_sintetico) == antes
    code, out = _reancorar(db_sintetico, REANCORAR, "--apply")  # sem --expect tambem recusa
    assert code == 2 and "--expect" in out and _sha(db_sintetico) == antes


def test_reancorar_apply_chega_ao_estado_e_reexecucao_da_zero(db_sintetico):
    _seed_p6(db_sintetico)
    code, out = _reancorar(db_sintetico, REANCORAR, "--apply", "--expect", "2")
    assert code == 0, out
    assert "FIXADO" in out
    assert _q(db_sintetico, "SELECT id, questao_id, tema_id FROM flashcards WHERE id IN (20, 21) "
                            "ORDER BY id") == [(20, None, 2), (21, 2, 2)]
    assert _q(db_sintetico, "SELECT card_id, lista, num FROM emed_card_ancora ORDER BY card_id, num") \
        == [(20, "t40", 5), (20, "t40", 8), (21, "t40", 9)]
    assert _orfaos(db_sintetico) == []
    antes = _sha(db_sintetico)
    code, out = _reancorar(db_sintetico, REANCORAR)
    assert code == 0 and "0 card(s) mudam" in out and "2 iguais" in out, out
    code, out = _reancorar(db_sintetico, REANCORAR, "--apply", "--expect", "0")
    assert code == 0 and _sha(db_sintetico) == antes


def test_reancorar_sem_fixado_recusa(db_sintetico, monkeypatch):
    _seed_p6(db_sintetico)
    antes = _sha(db_sintetico)

    def _sem_ponto(ato):
        raise RuntimeError("sem ponto de retorno")
    code, out = _reancorar(db_sintetico, REANCORAR, "--apply", "--expect", "2",
                           monkeypatch=monkeypatch, fixar=_sem_ponto)
    assert code == 1 and "NADA gravado" in out
    assert _sha(db_sintetico) == antes


def test_reancorar_card_inexistente_ou_ancora_invalida_recusa(db_sintetico):
    _seed_p6(db_sintetico)
    antes = _sha(db_sintetico)
    for plano in ([{"card_id": 999, "emed": ["t40_5"], "tema_id": 2}],
                  [{"card_id": 20, "emed": ["t40_6"], "tema_id": 2}],
                  [{"card_id": 20, "emed": [], "tema_id": 2}]):
        code, out = _reancorar(db_sintetico, plano, "--apply", "--expect", "1")
        assert code == 1 and "NADA gravado" in out, out
    assert _sha(db_sintetico) == antes


if __name__ == "__main__":
    import inspect
    # part-3 (P6): os testes da ancora usam a fixture `db_sintetico` -- so rodam no pytest
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and not inspect.signature(v).parameters]
    falhas = 0
    for fn in fns:
        try:
            fn()
            print("  OK  " + fn.__name__)
        except AssertionError as e:
            falhas += 1
            print("  XX  %s: %s" % (fn.__name__, e))
    print()
    if falhas:
        print("FALHOU: %d teste(s)" % falhas)
        sys.exit(1)
    print("TODOS OS TESTES PASSARAM (flashcards-integridade part-4)")
