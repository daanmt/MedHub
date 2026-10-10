"""test_revisao_calibrada.py — testes da feature Revisão Calibrada.

Parte 1 (fundação de dados): schema, helpers roundtrip, seed, _find_resumo,
craftsmanship. Partes 2/3 estendem este arquivo.

HERMÉTICO x VIVO (Fase 0 Lote 0 part-2c, 10/10/2026):
  - Hermético: TODAS as funções que tocam banco leem o banco sintético que
    `_banco_sintetico()` cria antes da 1ª chamada (schema do `init_db` em diretório
    temporário + o SEED + 1 card revisado). `db.DB_PATH`, o `DB_PATH` deste script e o
    `review_radar.DB_PATH` apontam para ele, e `test_banco_sintetico` confere isso.
  - Vivo: NENHUMA função. Um sentinela em `sqlite3.connect` recusa e registra toda
    conexão ao ipub.db real; `test_nenhuma_conexao_no_real` exige 0 no fim.
  - Fora do banco, a suíte lê arquivos VERSIONADOS do repo (resumos/, contrato,
    .claude/commands/, AGENTE.md, app/**/*.py) -- documental, não dado do operador.
Script-style (fora do `python_files`): roda só pelo `test_pytest_bridge.py`, por exit
code; marcador de pytest não vale aqui, por isso o banco é próprio e não `-m vivo`.

Uso: python tools/test_revisao_calibrada.py
"""
import os
import re
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# O banco do operador. Esta suíte NÃO o lê (Lote 0 part-2c): só existe aqui para o
# sentinela abaixo reconhecê-lo e recusar a conexão.
REAL_DB = os.path.join(ROOT, "ipub.db")


def _mesmo_arquivo(a, b):
    return os.path.normcase(os.path.abspath(os.fspath(a))) == os.path.normcase(os.path.abspath(os.fspath(b)))


# Sentinela (Lote 0 part-2c): toda conexão SQLite do processo passa por aqui. Conexão ao
# ipub.db real é registrada e RECUSADA -- nada lê nem grava o banco do operador, nem um
# módulo com `DB_PATH` próprio que tenha escapado do redirecionamento. Instalado ANTES de
# importar app.utils.db/day_plan, para valer também para o que rodar na importação.
_conexoes_no_real = []
_connect_original = sqlite3.connect


def _connect_vigiado(database, *args, **kwargs):
    alvo = database
    if isinstance(alvo, str) and alvo.startswith("file:"):
        alvo = alvo[len("file:"):].split("?", 1)[0]
    if isinstance(alvo, (str, os.PathLike)) and _mesmo_arquivo(alvo, REAL_DB):
        _conexoes_no_real.append(os.fspath(database))
        raise RuntimeError(f"VIVO proibido nesta suíte: conexão ao ipub.db real ({database})")
    return _connect_original(database, *args, **kwargs)


sqlite3.connect = _connect_vigiado

import importlib  # noqa: E402

try:
    import app.utils.db as db  # noqa: E402
except ModuleNotFoundError as e:
    # O ponto de falha é app.utils.db -> py-fsrs, instalado só no python global
    # (não no .venv). Mensagem clara em vez de ImportError cru; re-levanta o resto.
    if e.name == "fsrs":
        print("ERRO: py-fsrs ausente. Rode com o python global que tem py-fsrs; "
              "o .venv não tem. (ex.: `python tools/test_revisao_calibrada.py`)")
        sys.exit(2)
    raise
# app.engine.__init__ re-exporta a função get_topic_context, sombreando o
# submódulo homônimo no namespace do pacote — pegar o módulo real via importlib.
gtc = importlib.import_module("app.engine.get_topic_context")  # noqa: E402
import day_plan as dp  # noqa: E402  (tools/ está no sys.path quando rodado como script)

# O banco que TODAS as funções desta suíte leem: o sintético de `_banco_sintetico()`,
# apontado antes da 1ª chamada (o `__main__` o cria primeiro). Nunca o ipub.db real.
DB_PATH = None

SEED = [
    ("Hepato", "Hepatites Virais", 8),
    ("Pediatria", "Doenças Exantemáticas", 6),
    ("Cirurgia", "Cirurgia Infantil", 8),
    ("Obstetrícia", "Síndromes Hipertensivas da Gestação", 6),
    ("Infecto", "Sepse", 6),
]
# Vulvovaginites saiu do SEED em s110p2: dificuldade 7/usuario -> 6/aula via
# registro pos-analise legitimo (HANDOFF s110p1, fluxo normal do /revisar).
# Medicina de Familia e Comunidade saiu do SEED em s114: dificuldade 3/usuario ->
# 5/usuario via input explicito do usuario ("D5") na aula-base Vigilancia+SI+MFC
# (Clausula 2 do contrato -- input explicito e soberano e pode recalibrar a qualquer momento).
# Imunizacoes saiu do SEED na mesma sessao: 9/usuario -> 7/agente_inferida
# (2 rounds de questoes analisados, ~83% estavel, gaps estreitos e remediados).
# Lote 0 part-2c (10/10/2026): o encolhimento acabou. O SEED (valores intactos) agora é
# GRAVADO no banco sintético por `_banco_sintetico()` em SQL cru, e o `test_seed` lê de
# volta com `db.get_dificuldade` -- prova a regra de leitura (nota e fonte gravadas voltam
# iguais), não o estado do operador, que evolui pelo fluxo real de uso e não é invariante
# de código.
SEED_AT = "2026-01-01 00:00:00"   # carimbo fixo do seed sintético; nenhum check o lê
# subconjunto do seed que possui resumo .md homônimo (stem == tema)
COM_RESUMO = ["Hepatites Virais", "Doenças Exantemáticas", "Cirurgia Infantil",
              "Síndromes Hipertensivas da Gestação"]

falhas = []


def check(cond, msg):
    print(("  OK  " if cond else "  XX  ") + msg)
    if not cond:
        falhas.append(msg)


DB_SINTETICO = None


def _banco_sintetico():
    """Cria o banco da suíte (Lote 0 part-2c) e aponta para ele tudo o que a suíte lê.

    Schema CANÔNICO do `tools/init_db.py` num diretório temporário (não copia DDL: acompanha
    o schema quando ele muda; padrão de `tools/test_fuso_unico_leitores.py::banco`) + o SEED
    inserido em SQL cru. Repontados: `db.DB_PATH`, o `DB_PATH` deste script (lido por
    test_schema/test_readonly_inferencia e pelas cópias de roundtrip/barreiras/aula) e o
    `review_radar.DB_PATH` (módulo com caminho próprio, alcançado por
    `day_plan.montar_sinais`). O diretório é apagado na saída do processo."""
    global DB_PATH, DB_SINTETICO
    import atexit
    import contextlib
    import io
    import shutil
    import tempfile

    import init_db
    import review_radar

    pasta = tempfile.mkdtemp(prefix="revcal_")
    atexit.register(shutil.rmtree, pasta, ignore_errors=True)
    caminho = os.path.join(pasta, "ipub.db")
    init_db.DB_PATH = caminho
    with contextlib.redirect_stdout(io.StringIO()):
        init_db.init_db()
    con = sqlite3.connect(caminho)
    try:
        con.executemany(
            "INSERT INTO taxonomia_cronograma (area, tema, dificuldade, dificuldade_fonte, "
            "dificuldade_at) VALUES (?, ?, ?, 'usuario', ?)",
            [(area, tema, nota, SEED_AT) for area, tema, nota in SEED])
        # 1 card revisado em Hepatites Virais (+ a revisão no revlog): sem ele as barreiras A
        # do test_barreiras_preparar contariam 0 -> 0 e não morderiam um UPDATE em fsrs_cards.
        con.execute(
            "INSERT INTO flashcards (id, tema_id, tipo, frente_pergunta, verso_resposta, "
            "quality_source) SELECT 1, id, 'conteudo', 'P?', 'R.', 'qualitative' "
            "FROM taxonomia_cronograma WHERE area = 'Hepato' AND tema = 'Hepatites Virais'")
        con.execute("INSERT INTO fsrs_cards (card_id, state, due, stability, reps, last_review) "
                    "VALUES (1, 2, '2026-01-10 00:00:00', 5.0, 1, '2026-01-05 00:00:00')")
        con.execute("INSERT INTO fsrs_revlog (card_id, rating, state, due, review_time) "
                    "VALUES (1, 3, 2, '2026-01-10 00:00:00', '2026-01-05 00:00:00')")
        con.commit()
    finally:
        con.close()
    DB_SINTETICO = DB_PATH = caminho
    db.DB_PATH = caminho
    review_radar.DB_PATH = caminho
    return caminho


def test_banco_sintetico():
    print("[Lote0-2c] banco sintético: nenhuma função lê o ipub.db real")
    check(DB_SINTETICO is not None and db.DB_PATH == DB_SINTETICO,
          f"db.DB_PATH aponta para o banco sintético (got {db.DB_PATH})")
    check(not _mesmo_arquivo(db.DB_PATH, REAL_DB), "db.DB_PATH não é o ipub.db real")
    check(DB_SINTETICO is not None and DB_PATH == DB_SINTETICO,
          f"DB_PATH do script = sintético (got {DB_PATH})")
    import review_radar
    check(DB_SINTETICO is not None and review_radar.DB_PATH == DB_SINTETICO,
          f"review_radar.DB_PATH (lido por montar_sinais) = sintético (got {review_radar.DB_PATH})")


def test_nenhuma_conexao_no_real():
    print("[Lote0-2c] sentinela: nenhuma conexão ao ipub.db real durante a suíte")
    check(not _conexoes_no_real, f"0 conexões ao ipub.db real (got {len(_conexoes_no_real)})")


def test_schema():
    print("[DoD-1a] schema")
    con = sqlite3.connect(DB_PATH)
    cols = {r[1] for r in con.execute("PRAGMA table_info(taxonomia_cronograma)")}
    con.close()
    for c in ("dificuldade", "dificuldade_fonte", "dificuldade_at"):
        check(c in cols, f"coluna {c} existe")


def test_seed():
    print("[DoD-2] seed (notas do SEED, fonte=usuario, lidas do banco sintético)")
    for area, tema, nota in SEED:
        d = db.get_dificuldade(area, tema)
        check(d is not None and d["nota"] == nota and d["fonte"] == "usuario",
              f"{tema} = {nota}/usuario (got {d})")


def test_roundtrip():
    print("[DoD-1b] helpers roundtrip")
    # Isolado numa cópia temp do banco sintético (padrão de test_barreiras_preparar):
    # os writes de teste não sujam o banco da suíte, mesmo se um crash cair no meio.
    import shutil
    import tempfile

    tmp = os.path.join(tempfile.gettempdir(), "ipub_test_roundtrip.db")
    shutil.copy(DB_PATH, tmp)
    orig_path = db.DB_PATH
    db.DB_PATH = tmp
    try:
        check(db.set_dificuldade("XAREA", "XTEMA inexistente", 5, "usuario") is False,
              "set tema inexistente -> False")
        check(db.get_dificuldade("XAREA", "XTEMA inexistente") is None,
              "get tema inexistente -> None")
        # clamp + restauração (na cópia temp; o banco da suíte permanece byte-idêntico)
        orig = db.get_dificuldade("Hepato", "Hepatites Virais")["nota"]
        db.set_dificuldade("Hepato", "Hepatites Virais", 99, "usuario")
        got = db.get_dificuldade("Hepato", "Hepatites Virais")["nota"]
        check(got == 10, f"clamp 99 -> 10 (got {got})")
        db.set_dificuldade("Hepato", "Hepatites Virais", orig, "usuario")
        check(db.get_dificuldade("Hepato", "Hepatites Virais")["nota"] == orig,
              "restaurou valor original")
    finally:
        db.DB_PATH = orig_path
        try:
            os.remove(tmp)
        except OSError:
            pass


def test_find_resumo():
    print("[DoD-4] _find_resumo por stem")
    gtc._resumo_index = None  # força reconstrução fresca do índice em-processo
    for tema in COM_RESUMO:
        p = gtc._find_resumo(tema)
        ok = p is not None and p.stem.lower() == tema.lower()
        check(ok, f"'{tema}' -> {p.name if p else None} (stem exato)")


def test_craftsmanship_sqlite():
    print("[DoD-5] import sqlite3 só em app/utils/db.py (+ exceções pré-existentes)")
    # Exceções PRÉ-EXISTENTES (NÃO introduzidas pela Revisão Calibrada):
    #  - app/memory/*           -> backend SEPARADO medhub_memory.db (AGENTE §8)
    #  - app/pages/1_dashboard  -> acesso legacy "last resort" (conventions.md)
    # O gate falha se aparecer uma violação NOVA fora desta allowlist.
    allow = {
        os.path.join("app", "utils", "db.py"),
        os.path.join("app", "memory", "inspect.py"),
        os.path.join("app", "memory", "manager.py"),
        os.path.join("app", "memory", "store.py"),
        os.path.join("app", "pages", "1_dashboard.py"),
    }
    import glob
    bad = []
    for f in glob.glob(os.path.join(ROOT, "app", "**", "*.py"), recursive=True):
        rel = os.path.relpath(f, ROOT)
        if rel in allow:
            continue
        txt = open(f, encoding="utf-8").read()
        if re.search(r"^\s*import sqlite3", txt, re.M):
            bad.append(rel)
    check(not bad, f"nenhum import sqlite3 NOVO fora de db.py (viol: {bad})")


# ----- Parte 2: inferência -------------------------------------------------

def test_infer_nota_fixtures():
    print("[DoD-5b] infer_nota (fixtures determinísticas)")
    check(dp.infer_nota({"acerto_hist": 48, "leu_tema": True, "score_dorm": 10}) >= 7,
          "acerto 48% ⇒ nota ≥7")
    n = dp.infer_nota({"acerto_hist": 85, "leu_tema": True, "score_dorm": 3,
                       "prevalencia": "media"})
    check(n <= 3, f"acerto 85% + quente ⇒ nota ≤3 (got {n})")
    check(dp.infer_nota({"acerto_hist": None, "leu_tema": False}) >= 9,
          "estreia pura (sem sinal de dormência) ⇒ nota ≥9")
    check(dp.infer_nota({"acerto_hist": None, "leu_tema": False, "score_dorm": 50}) == 10,
          "clamp superior = 10")
    check(dp.infer_nota({"acerto_hist": 90, "leu_tema": True, "score_dorm": 3,
                         "prevalencia": "alta"}) >= 4, "prevalência alta ⇒ piso 4")


def test_divergencia():
    print("[DoD-6] divergência")
    check(dp._divergencia(3, 6) is not None, "|3-6|=3 ⇒ divergência não-nula")
    check(dp._divergencia(7, 8) is None, "|7-8|=1 ⇒ None")
    check(dp._divergencia(None, 5) is None, "sem nota do usuário ⇒ None")


def test_difficulty_report_estrutura():
    print("[DoD-5a] difficulty_report estrutura")
    r = dp.difficulty_report("Hepato", "Hepatites Virais")
    for k in ("nota_inferida", "nota_usuario", "degrau", "proposito", "divergencia"):
        check(k in r, f"chave '{k}' presente")
    check(isinstance(r["nota_inferida"], int) and 1 <= r["nota_inferida"] <= 10,
          f"nota_inferida int 1-10 (got {r['nota_inferida']})")
    check(r["degrau"] in ("D2", "D5", "D8", "D10"), f"degrau válido (got {r['degrau']})")
    check(r["proposito"] in ("exercicios", "flashcards"),
          f"proposito válido (got {r['proposito']})")


def test_readonly_inferencia():
    print("[craftsmanship-P2] difficulty_report é read-only")
    con = sqlite3.connect(DB_PATH)

    def snap():
        rl = con.execute("SELECT COUNT(*) FROM review_log").fetchone()[0]
        rv = con.execute("SELECT COUNT(*) FROM fsrs_revlog").fetchone()[0]
        nt = con.execute("SELECT dificuldade FROM taxonomia_cronograma "
                         "WHERE area='Hepato' AND tema='Hepatites Virais'").fetchone()[0]
        return (rl, rv, nt)

    antes = snap()
    dp.difficulty_report("Hepato", "Hepatites Virais")
    dp.montar_sinais("Hepato", "Hepatites Virais")
    depois = snap()
    con.close()
    check(antes == depois, f"db inalterado (antes={antes} depois={depois})")


# ----- Parte 3: barreiras de integridade (Invariantes A e B) ---------------

def test_barreiras_preparar():
    print("[DoD-8/9] barreiras A (FSRS intocado) + B (review_log alimentado)")
    import shutil
    import tempfile
    import dormant_refresh as drf

    tmp = os.path.join(tempfile.gettempdir(), "ipub_test_barreiras.db")
    shutil.copy(DB_PATH, tmp)                 # cópia do banco sintético: o da suíte fica limpo
    orig_path = db.DB_PATH
    db.DB_PATH = tmp
    try:
        con = sqlite3.connect(tmp)
        rv0 = con.execute("SELECT COUNT(*) FROM fsrs_revlog").fetchone()[0]
        fc0 = con.execute("SELECT COUNT(*), COALESCE(MAX(due), '') FROM fsrs_cards").fetchone()
        con.close()
        tid = db.resolve_tema_id("Hepato", "Hepatites Virais")
        con = sqlite3.connect(tmp)
        rl0 = con.execute("SELECT COUNT(*) FROM review_log WHERE tema_id=? AND "
                          "kind='directed_review'", (tid,)).fetchone()[0]
        con.close()

        res = drf.stamp(tid, kind="directed_review", note="teste barreira")
        check(res.get("kind") == "directed_review", "stamp aceita kind=directed_review")

        con = sqlite3.connect(tmp)
        rv1 = con.execute("SELECT COUNT(*) FROM fsrs_revlog").fetchone()[0]
        fc1 = con.execute("SELECT COUNT(*), COALESCE(MAX(due), '') FROM fsrs_cards").fetchone()
        rl1 = con.execute("SELECT COUNT(*) FROM review_log WHERE tema_id=? AND "
                          "kind='directed_review'", (tid,)).fetchone()[0]
        con.close()

        check(rl1 - rl0 == 1, f"[B] review_log +1 directed_review (got +{rl1 - rl0})")
        check(rv1 == rv0, f"[A] fsrs_revlog inalterado ({rv0}->{rv1})")
        check(fc1 == fc0, f"[A] fsrs_cards inalterado ({fc0}->{fc1})")

        try:
            drf.stamp(tid, kind="xxx")
            check(False, "kind inválido deveria lançar ValueError")
        except ValueError:
            check(True, "kind inválido -> ValueError")
    finally:
        db.DB_PATH = orig_path
        try:
            os.remove(tmp)
        except OSError:
            pass


def test_barreira_estatica():
    print("[DoD-8b] gate estático: dormant_refresh não toca o FSRS")
    src = open(os.path.join(ROOT, "tools", "dormant_refresh.py"), encoding="utf-8").read()
    for bad in ("record_review", "fsrs_revlog", "fsrs_cards", "UPDATE fsrs"):
        check(bad not in src, f"dormant_refresh.py não menciona '{bad}'")


# ----- Parte 4: contrato, skills, AGENTE (documental) ----------------------

def _read(rel):
    return open(os.path.join(ROOT, rel), encoding="utf-8").read()


def test_contrato():
    print("[DoD-3] contrato revisao-calibrada")
    p = "core/contracts/revisao-calibrada-contract.md"
    check(os.path.exists(os.path.join(ROOT, p)), "contrato existe")
    src = _read(p)
    check("type: contract" in src and "layer: core" in src, "frontmatter type/layer")
    for deg in ("D10", "D8", "D5", "D2"):
        check(deg in src, f"degrau {deg} presente")
    check("7-9" in src and "5-6" in src and "3-4" in src, "faixas de parágrafos")
    check("Invariante A" in src and "Invariante B" in src, "Invariantes A e B nomeadas")
    check("def infer_nota" in src, "pseudocódigo infer_nota presente")


def test_skill_revisar():
    print("[DoD-4] skill revisar fundida + refrescar deprecado")
    src = _read(".claude/commands/revisar.md")
    check("PREPARAR" in src and "DRENAR" in src, "sub-modos PREPARAR/DRENAR")
    check("record_review" in src and "review_log" in src, "barreiras textuais citadas")
    check("NUNCA" in src and "fsrs_cards" in src, "PREPARAR não escreve fsrs_cards (textual)")
    ref = _read(".claude/commands/refrescar.md")
    check("DEPRECAD" in ref.upper(), "refrescar deprecado")


def test_degrau_mecanico():
    print("[DoD-7] degrau mecânico (switches auditáveis)")
    src = _read("core/contracts/revisao-calibrada-contract.md")
    check("Parágrafos" in src, "faixas de parágrafos por degrau")
    check("1ª ocorrência" in src, "regra 'sigla por extenso na 1ª ocorrência'")


def test_agente():
    print("[DoD-10] AGENTE §1.2 atualizado")
    src = _read("AGENTE.md")
    check("Calibração pendente" not in src, "string 'Calibração pendente' removida")
    check("revisao-calibrada-contract.md" in src, "AGENTE aponta o contrato")


# ----- part-3: sinal da aula (F18c + F21) ---------------------------------

def test_f21_f18c_contrato():
    print("[part-3] F21/F18c: Cláusula 10 + Invariante E no contrato + revisar")
    src = _read("core/contracts/revisao-calibrada-contract.md")
    check("Cláusula 10" in src, "Cláusula 10 presente")
    check("Invariante E" in src, "Invariante E nomeada")
    check("piso fixo" in src.lower(), "cobertura = piso fixo (F21)")
    check("sumário da fonte" in src, "piso derivado do sumário da fonte")
    check("fonte='aula'" in src, "registro fonte='aula' (F18c) no contrato")
    check("'usuario'|'agente_inferida'|'aula'" in src, "enum dificuldade_fonte admite 'aula'")
    rev = _read(".claude/commands/revisar.md")
    check("fonte='aula'" in rev, "revisar.md tem o passo de registro fonte='aula'")
    check("piso fixo" in rev.lower(), "revisar.md tem a regra cobertura-piso")


def test_f18c_registro_aula():
    print("[part-3] F18c: set_dificuldade fonte='aula' roundtrip (db temp)")
    import shutil
    import tempfile
    tmp = os.path.join(tempfile.gettempdir(), "ipub_test_aula.db")
    shutil.copy(DB_PATH, tmp)
    orig_path = db.DB_PATH
    db.DB_PATH = tmp
    try:
        ok = db.set_dificuldade("Hepato", "Hepatites Virais", 7, "aula")
        check(ok is True, "set_dificuldade fonte='aula' -> True")
        d = db.get_dificuldade("Hepato", "Hepatites Virais")
        check(d is not None and d["nota"] == 7 and d["fonte"] == "aula",
              f"roundtrip fonte='aula' (got {d})")
    finally:
        db.DB_PATH = orig_path
        try:
            os.remove(tmp)
        except OSError:
            pass


if __name__ == "__main__":
    _banco_sintetico()          # antes da 1ª chamada: tudo abaixo lê o banco sintético
    test_banco_sintetico()
    # Parte 1
    test_schema()
    test_seed()
    test_roundtrip()
    test_find_resumo()
    test_craftsmanship_sqlite()
    # Parte 2
    test_infer_nota_fixtures()
    test_divergencia()
    test_difficulty_report_estrutura()
    test_readonly_inferencia()
    # Parte 3
    test_barreiras_preparar()
    test_barreira_estatica()
    # Parte 4
    test_contrato()
    test_skill_revisar()
    test_degrau_mecanico()
    test_agente()
    # Parte 3 (sinal da aula: F18c + F21)
    test_f21_f18c_contrato()
    test_f18c_registro_aula()
    test_nenhuma_conexao_no_real()
    print()
    if falhas:
        print(f"FALHOU: {len(falhas)} check(s)")
        sys.exit(1)
    print("TODOS OS CHECKS PASSARAM (Partes 1-4)")
