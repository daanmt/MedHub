"""conftest raiz (F12, engenharia-ledger part-4).

Garante que `import app.utils...` e `import tools...` resolvam a partir da
raiz do repo quando o pytest roda de qualquer cwd. Os suites script-style
continuam executaveis standalone (python tools/test_X.py) -- este arquivo
nao os altera.

Globais isolados em tmp_path, em TODO teste, pelo autouse `_event_log_isolado`
(escrita nova em caminho global entra aqui, com o incidente que a motivou):
  - `event_log.LOG_PATH`                      -> history/generation_log.jsonl
  - `ledger_self.ROOT_DIR` e `tools.ledger_self.ROOT_DIR`
                                              -> history/ledger_self{.jsonl,_state.json}
  - `tools.utils.state_utils.WATERMARK_PATH`  -> history/card_watermark.json
  - `MEDHUB_EVIDENCIAS_DB` (env)              -> evidencias.db pareado ao ipub.db (s236)

A Fase 0 Lote 0 part-2a (10/10/2026) acrescentou também:
  - o fixture `db_sintetico` (schema canônico do `tools/init_db.py` em tmp_path, com
    `db.DB_PATH` e `init_db.DB_PATH` apontados para ele);
  - o marcador `vivo` (teste que lê o ipub.db real; sem o banco, pula com motivo `VIVO:`).
    A lane hermética é `python -m pytest tools/ -q -m "not vivo"`.

A part-3h (M-123, 10/10/2026) acrescentou o autouse de SESSÃO `_git_hermetico`: tira do
`os.environ` o ambiente git que o hook herda do commit em curso (`GIT_AMBIENTE_DO_HOOK`) e o
devolve no teardown.
"""
import contextlib
import importlib
import io
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest  # noqa: E402


def pytest_configure(config):
    # Registrado aqui e não no pytest.ini (part-2a, decisão técnica 2): cabe no budget e
    # evita PytestUnknownMarkWarning sem tocar a allowlist de python_files.
    config.addinivalue_line(
        "markers",
        "vivo: lê o ipub.db real da máquina do operador; sem o banco pula com motivo "
        "'VIVO: ...' (lane hermética: -m \"not vivo\")")


# Fase 0 Lote 0 part-3h (M-123): a suíte roda DENTRO do pre-commit (check 2d), e o git exporta
# para o hook o ambiente do commit em curso. Em `git commit -a` ou `git commit <caminhos>`, o
# `GIT_INDEX_FILE` é absoluto e aponta para o índice temporário do repo REAL; herdado, um
# `git -C <repo sintético> add` escreve nele (reproduzido no DoD 4(i) da part-3h: o `add` vai
# para o índice apontado, e o do repo sintético nem nasce). Fora do hook a suíte não tem
# nenhuma destas chaves, então tirá-las deixa a suíte no hook igual à suíte avulsa.
# `monkeypatch` é de função e não serve para o escopo de sessão: a limpeza é feita à mão, e
# o teardown restaura.
# Limite: código de teste que rode git na COLETA (nível de módulo) roda antes de qualquer
# fixture; hoje não há nenhum.
GIT_AMBIENTE_DO_HOOK = ("GIT_INDEX_FILE", "GIT_DIR", "GIT_WORK_TREE", "GIT_PREFIX",
                        "GIT_OBJECT_DIRECTORY")


def limpar_git_env(environ=None):
    """Tira de `environ` (padrão: `os.environ`) as chaves de `GIT_AMBIENTE_DO_HOOK` e devolve
    `{chave: valor}` do que tirou, para `restaurar_git_env`."""
    environ = os.environ if environ is None else environ
    return {k: environ.pop(k) for k in GIT_AMBIENTE_DO_HOOK if k in environ}


def restaurar_git_env(removidas, environ=None):
    """Devolve a `environ` (padrão: `os.environ`) o que `limpar_git_env` tirou."""
    environ = os.environ if environ is None else environ
    environ.update(removidas)


@pytest.fixture(autouse=True, scope="session")
def _git_hermetico():
    removidas = limpar_git_env()
    try:
        yield removidas
    finally:
        restaurar_git_env(removidas)


@pytest.fixture(autouse=True)
def _event_log_isolado(tmp_path, monkeypatch):
    """Consolidacao part-1 (audit-fix do P3): NENHUM teste escreve no
    history/generation_log.jsonl real — testes que exercitam insert_questao
    disparavam _flush_eventos contra o log de producao. Redireciona o global
    para tmp em todo teste; quem passa log_path explicito nao e afetado."""
    try:
        tools_dir = os.path.join(ROOT, "tools")
        if tools_dir not in sys.path:
            sys.path.insert(0, tools_dir)
        import event_log
        monkeypatch.setattr(event_log, "LOG_PATH",
                            str(tmp_path / "generation_log.jsonl"))
    except Exception:
        pass  # sem event_log (arvore parcial) -> nada a isolar
    # ⚰️ 11/10/2026 (part 3.0a2): o isolamento de `app.memory.manager` (`_HISTORY_DIR`, F66;
    # `_ERROR_LOG`, F96) saiu com o módulo -- ninguém mais escreve nesses sinks.
    # Fase 0 Lote 0 part-2a (10/10/2026): o runtime do HARNESS. Teste que exercita
    # `auto_check`/`ledger_self.record` sem `root=` gravava no history/ledger_self.jsonl e no
    # history/card_watermark.json reais (fora do git desde a part-1, mas ainda o runtime do
    # operador). `ledger_self` tem DOIS nomes de módulo (`state_utils` faz
    # `sys.path.insert(tools)` + `from ledger_self import record`; os testes importam
    # `tools.ledger_self`) e cada nome é um objeto com o seu `ROOT_DIR`: os dois são
    # patchados. Importados aqui, e não só "se já estiverem em sys.modules", porque um teste
    # que importasse um deles DEPOIS deste autouse pegaria o módulo sem patch.
    for nome in ("ledger_self", "tools.ledger_self"):
        try:
            monkeypatch.setattr(importlib.import_module(nome), "ROOT_DIR", tmp_path)
        except Exception:
            pass
    # Watermark: o nome canônico é `tools.utils.state_utils` (importado aqui pelo mesmo
    # motivo); `utils.state_utils` (com tools/ no sys.path) seria um 2º objeto -- ninguém o
    # importa hoje, mas se aparecer em sys.modules ele também é isolado.
    try:
        importlib.import_module("tools.utils.state_utils")
    except Exception:
        pass
    for nome in ("tools.utils.state_utils", "utils.state_utils"):
        mod = sys.modules.get(nome)
        if mod is not None and hasattr(mod, "WATERMARK_PATH"):
            monkeypatch.setattr(mod, "WATERMARK_PATH", tmp_path / "card_watermark.json")
    # s236 (evidence-bank): o `evidencias.db` ao lado do ipub.db real é global do mesmo jeito --
    # pareado, ele põe a conjunção de quarentena (e a tabela `card_evidencia`) no
    # `db.ativo_where` de fixtures que não a têm. Todo teste começa SEM banco pareado, também
    # nos CLIs que ele roda em subprocesso (herdam o ambiente); quem exercita a quarentena
    # aponta `MEDHUB_EVIDENCIAS_DB` para o seu (`tools/test_evidencias_quarentena.py`).
    monkeypatch.setenv("MEDHUB_EVIDENCIAS_DB", str(tmp_path / "evidencias_ausente.db"))


@pytest.fixture
def db_sintetico(tmp_path, monkeypatch):
    """Banco sintético com o schema CANÔNICO (part-2a): chama `init_db.init_db()` em
    tmp_path -- não copia DDL, então acompanha o schema quando ele muda -- e aponta
    `db.DB_PATH` e `init_db.DB_PATH` para ele. Seed mínimo: 1 linha em
    `taxonomia_cronograma` (id 1), alvo da FK `flashcards.tema_id`. Devolve o caminho (str).

    Padrão de origem: `tools/test_fuso_unico_leitores.py::banco`. Os 42 arquivos que já
    patcham `db.DB_PATH` por conta própria ficam como estão (anti-scope da part-2a)."""
    tools_dir = os.path.join(ROOT, "tools")
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
    import init_db
    from app.utils import db

    caminho = str(tmp_path / "ipub.db")
    monkeypatch.setattr(init_db, "DB_PATH", caminho)
    with contextlib.redirect_stdout(io.StringIO()):
        init_db.init_db()
    monkeypatch.setattr(db, "DB_PATH", caminho)
    conn = db.get_connection()
    try:
        conn.execute("INSERT INTO taxonomia_cronograma (id, area, tema) "
                     "VALUES (1, 'Cirurgia', 'Apendicite Aguda')")
        conn.commit()
    finally:
        conn.close()
    return caminho
