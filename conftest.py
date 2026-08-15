"""conftest raiz (F12, engenharia-ledger part-4).

Garante que `import app.utils...` e `import tools...` resolvam a partir da
raiz do repo quando o pytest roda de qualquer cwd. Os suites script-style
continuam executaveis standalone (python tools/test_X.py) -- este arquivo
nao os altera.
"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest  # noqa: E402


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
