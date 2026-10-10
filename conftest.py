"""conftest raiz (F12, engenharia-ledger part-4).

Garante que `import app.utils...` e `import tools...` resolvam a partir da
raiz do repo quando o pytest roda de qualquer cwd. Os suites script-style
continuam executaveis standalone (python tools/test_X.py) -- este arquivo
nao os altera.

Globais isolados em tmp_path, em TODO teste, pelo autouse `_event_log_isolado`
(escrita nova em caminho global entra aqui, com o incidente que a motivou):
  - `event_log.LOG_PATH`                      -> history/generation_log.jsonl
  - `app.memory.manager._HISTORY_DIR`         -> sink de dívida de vocabulário (F66)
  - `app.memory.manager._ERROR_LOG`           -> history/memory_errors.log (F96)
  - `ledger_self.ROOT_DIR` e `tools.ledger_self.ROOT_DIR`
                                              -> history/ledger_self{.jsonl,_state.json}
  - `tools.utils.state_utils.WATERMARK_PATH`  -> history/card_watermark.json

A Fase 0 Lote 0 part-2a (10/10/2026) acrescentou também:
  - o fixture `db_sintetico` (schema canônico do `tools/init_db.py` em tmp_path, com
    `db.DB_PATH` e `init_db.DB_PATH` apontados para ele);
  - o marcador `vivo` (teste que lê o ipub.db real; sem o banco, pula com motivo `VIVO:`).
    A lane hermética é `python -m pytest tools/ -q -m "not vivo"`.
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
    # F66 (s176): MESMA classe, writer novo. `reconciliar_weak_areas` grava o sink de
    # divida de vocabulario; `test_boot_verdadeiro` a chama com store SINTETICO e, sem
    # este isolamento, o sink de PRODUCAO era sobrescrito por dado de fixture (medido:
    # 100 itens reais viraram 1 `wa_dummy`). Isolamos `_HISTORY_DIR` -- a costura que o
    # proprio modulo ja expoe e que `tools/test_memory.py` (script-style, fora do pytest)
    # ja patchava: um seam so, valido nos DOIS harnesses. Escrita nova em caminho global entra aqui.
    try:
        import app.memory.manager as _mgr
        monkeypatch.setattr(_mgr, "_HISTORY_DIR", tmp_path)
        # F96 (s177): `_ERROR_LOG` e um SEGUNDO global derivado de `_ROOT`, fora da
        # costura acima. O caminho de SUCESSO do sink ficou isolado no 1.3 e o de FALHA
        # nao: `log_error` seguia escrevendo no `history/memory_errors.log` real, e o
        # teste que forca a falha de proposito somava 1 linha por rodada (14 medidas
        # entre 10 e 11/09/2026). O painel do `ledger_self` conta as linhas desse
        # arquivo -- a suite inflava o numero que o operador le.
        monkeypatch.setattr(_mgr, "_ERROR_LOG", tmp_path / "memory_errors.log")
    except Exception:
        pass
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
