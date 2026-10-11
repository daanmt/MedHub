"""test_schema_escrita.py -- toda tabela que as fontes ESCREVEM existe no schema
(Fase 0 Lote 0 part-4a, 10/10/2026).

Origem: `cronograma_progresso` não existe no ipub.db nem no `init_db.py`, e duas fontes
escreviam nela: `app/utils/db.py` (`update_cronograma_status`, sem chamador) e o writer de
questões, este dentro de `try/except Exception: pass  # tabela opcional`. A escrita falhava
calada a cada erro registrado. Nenhum teste via: o defeito não dá erro, só não acontece.

O teste pega a CLASSE, não o caso (decisão técnica 2 da spec): varre por regex os literais
de string (via `ast`) de `tools/*.py` e `app/**/*.py`, sem `test_*` e sem `_archive`, e
exige que todo nome depois de `INSERT [OR ...] INTO`, `UPDATE ... SET` e `DELETE FROM`:
  - exista no schema que o `init_db.init_db()` cria em tmp_path (fixture `db_sintetico`), OU
  - tenha `CREATE TABLE IF NOT EXISTS <nome>` nas mesmas fontes (DDL lazy, ex. `plano_dia`,
    `plano_tarefas`, `emed_*`, `memory_store`), OU
  - esteja em `EXCECOES`, com o motivo (vazia hoje; caso legítimo novo entra ali declarado).

Irmão do `test_writer_allowlist` (perímetro arquivo -> tabela, regex sobre o texto inteiro):
aquele pergunta QUEM pode escrever onde; este pergunta se o ONDE existe.

Limites declarados:
  - SQL montado dinamicamente fica de fora: nome com `{` ou `%` (f-string, `.format`,
    `%s`) não é checado, e a concatenação com `+` parte o literal (o pedaço "UPDATE "
    sozinho não traz nome).
  - `UPDATE` só conta seguido de `<nome> SET`: é o que separa SQL de prosa ("o UPDATE é
    condicionado ..."); o `DO UPDATE SET` do upsert não é tabela. `INSERT INTO` e
    `DELETE FROM` não têm esse filtro, e o casamento ignora caixa: prosa com
    "insert into <palavra>" acusaria (falso positivo VISÍVEL, nunca silencioso; hoje nenhum).
  - A DDL lazy vale em qualquer fonte da varredura, sem conferir a ordem de execução
    (que o CREATE rode antes do INSERT é responsabilidade do writer).
  - Lê o texto, não executa: não sabe a que banco a conexão aponta (`memory_store` mora
    no medhub_memory.db e passa pela DDL lazy do próprio módulo).
"""
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: {tabela: motivo}: escrita legítima em tabela que nem o schema canônico nem a DDL lazy
#: das fontes criam. Nasce vazia (part-4a); entrada nova exige motivo.
EXCECOES = {}

RX_ESCRITA = re.compile(
    r"\b(?:INSERT\s+(?:OR\s+\w+\s+)?INTO\s+(?P<ins>[^\s(,;]+)"
    r"|DELETE\s+FROM\s+(?P<del>[^\s(,;]+)"
    r"|(?<!DO\s)UPDATE\s+(?:OR\s+\w+\s+)?(?P<upd>[^\s(,;]+)\s+SET\b)",
    re.I)
RX_DDL_LAZY = re.compile(r"\bCREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+([^\s(,;]+)", re.I)


def fontes(root=ROOT):
    """Fontes varridas: `tools/*.py` e `app/**/*.py`, sem `test_*`, `_archive` e cache."""
    root = Path(root)
    achadas = sorted((root / "tools").glob("*.py"))
    achadas += [p for p in sorted((root / "app").rglob("*.py"))
                if not {"_archive", "__pycache__"} & set(p.parts)]
    return [p for p in achadas if not p.name.startswith("test_")]


def literais(path):
    """[(linha, texto)] dos literais de string do arquivo. Uma f-string vira UM texto, com
    `{}` no lugar de cada campo (assim o nome dinâmico aparece como dinâmico)."""
    arvore = ast.parse(Path(path).read_text(encoding="utf-8-sig"), filename=str(path))
    out, partes_de_fstring = [], set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.JoinedStr):
            texto = []
            for v in no.values:
                if isinstance(v, ast.Constant) and isinstance(v.value, str):
                    partes_de_fstring.add(id(v))
                    texto.append(v.value)
                else:
                    texto.append("{}")
            out.append((no.lineno, "".join(texto)))
    for no in ast.walk(arvore):
        if (isinstance(no, ast.Constant) and isinstance(no.value, str)
                and id(no) not in partes_de_fstring):
            out.append((no.lineno, no.value))
    return out


def _nome(bruto):
    return bruto.strip('"`[]\'')


def varrer(arquivos, root=ROOT):
    """(escritas, ddl_lazy): escritas = [(rel:linha, tabela)] com nome estático;
    ddl_lazy = {tabela} com `CREATE TABLE IF NOT EXISTS` em algum dos arquivos."""
    escritas, ddl_lazy = [], set()
    for path in arquivos:
        rel = Path(path).resolve().relative_to(Path(root).resolve()).as_posix()
        for linha, texto in literais(path):
            for m in RX_ESCRITA.finditer(texto):
                nome = m.group("ins") or m.group("del") or m.group("upd")
                if "{" in nome or "%" in nome:
                    continue                      # dinâmico: limite declarado
                local = f"{rel}:{linha + texto.count(chr(10), 0, m.start())}"
                escritas.append((local, _nome(nome)))
            ddl_lazy.update(_nome(m.group(1)) for m in RX_DDL_LAZY.finditer(texto))
    return escritas, ddl_lazy


def faltantes(escritas, tabelas, ddl_lazy, excecoes=EXCECOES):
    """[(local, tabela)] das escritas em tabela que nada cria."""
    return [(local, t) for local, t in escritas
            if t not in tabelas and t not in ddl_lazy and t not in excecoes]


def _tabelas_do_schema(caminho):
    from app.utils import db
    assert Path(db.DB_PATH) == Path(caminho), "db.DB_PATH não aponta para o sintético"
    conn = db.get_connection()
    try:
        return {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    finally:
        conn.close()


def test_toda_tabela_escrita_existe_no_schema(db_sintetico):
    tabelas = _tabelas_do_schema(db_sintetico)
    escritas, ddl_lazy = varrer(fontes())
    # anti-vacuidade: a varredura vê os writers canônicos, e o schema veio inteiro
    escritas_em = {t for _, t in escritas}
    assert {"flashcards", "fsrs_cards", "questoes_erros"} <= escritas_em, sorted(escritas_em)
    assert {"flashcards", "fsrs_cards", "taxonomia_cronograma"} <= tabelas, sorted(tabelas)
    falta = faltantes(escritas, tabelas, ddl_lazy)
    assert falta == [], (
        "escrita em tabela que nem o schema do init_db nem uma DDL lazy das fontes cria "
        "(a escrita falha, ou falha calada sob try/except): "
        + "; ".join(f"{local} -> {t}" for local, t in falta))


def test_detector_separa_escrita_real_de_prosa_e_de_sql_dinamico(tmp_path):
    """Prova o detector sobre fontes plantadas: acusa as 3 formas de escrita, aceita a DDL
    lazy e deixa de fora prosa, upsert, nome dinâmico e arquivo de teste."""
    (tmp_path / "tools").mkdir()
    (tmp_path / "app" / "utils").mkdir(parents=True)
    (tmp_path / "tools" / "writer.py").write_text(
        'A = "UPDATE fantasma_upd SET x = 1"\n'
        "B = '''\n    INSERT OR IGNORE INTO \"fantasma_ins\" (a) VALUES (?)\n'''\n"
        'C = "DELETE FROM fantasma_del WHERE id = ?"\n'
        'D = "CREATE TABLE IF NOT EXISTS lazy_t (a)"\n'
        'E = "INSERT INTO lazy_t (a) VALUES (1)"\n'
        'F = "INSERT INTO existe (a) VALUES (1) ON CONFLICT(a) DO UPDATE SET a = excluded.a"\n'
        'def g(t, n):\n'
        '    """O UPDATE e condicionado ao lock (prosa: sem SET depois do nome)."""\n'
        '    return f"UPDATE {t} SET a = 1", "DELETE FROM %s" % n\n',
        encoding="utf-8")
    (tmp_path / "tools" / "test_ignorado.py").write_text(
        'X = "UPDATE fantasma_de_teste SET a = 1"\n', encoding="utf-8")
    (tmp_path / "app" / "utils" / "mod.py").write_text(
        'Y = "UPDATE fantasma_app SET a = 1"\n', encoding="utf-8")

    arquivos = fontes(tmp_path)
    assert [p.name for p in arquivos] == ["writer.py", "mod.py"], "test_* fica fora"
    escritas, ddl_lazy = varrer(arquivos, root=tmp_path)
    assert ddl_lazy == {"lazy_t"}
    falta = faltantes(escritas, {"existe"}, ddl_lazy, excecoes={})
    assert sorted(falta) == [("app/utils/mod.py:1", "fantasma_app"),
                             ("tools/writer.py:1", "fantasma_upd"),
                             ("tools/writer.py:3", "fantasma_ins"),
                             ("tools/writer.py:5", "fantasma_del")], falta
    # a exceção declarada cala o achado, e só ele
    falta = faltantes(escritas, {"existe"}, ddl_lazy, excecoes={"fantasma_app": "motivo"})
    assert ("app/utils/mod.py:1", "fantasma_app") not in falta and len(falta) == 3
