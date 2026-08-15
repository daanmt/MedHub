"""
Smoke tests for MedHub Memory v1.

Run from repo root:
    python tools/test_memory.py

Tests:
  1. Persistence  — put → reinitialize store → get (must recover)
  2. Cross-thread — store is global; write under session_001, read from session_002
  3. Search       — put 3 entries → search by query → must return relevant
  4. Consolidation — mock session log → consolidate_session → error_count sincronizado
                     e nenhum namespace write-only criado (consolidacao-part-3)
  5. Context unwrap — envelope LangMem renderizado por load_context

Namespace único vivo: medhub/weak_areas. Textos abaixo são dummy.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).parent.parent))
# F15: saída segura sob pipe cp1252 (decisão 2026-04-23 — CLIs com não-ASCII reconfiguram)
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from app.memory.store import SQLiteMemoryStore

_PASS = "\033[92mPASS\033[0m"
_FAIL = "\033[91mFAIL\033[0m"


def _make_store(db_path: str) -> SQLiteMemoryStore:
    return SQLiteMemoryStore(db_path)


# ---------------------------------------------------------------------------
# Test 1 — Persistence
# ---------------------------------------------------------------------------
def test_persistence() -> bool:
    print("\n[1] Persistência: put -> reinicializar -> get")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db = f.name

    try:
        store = _make_store(db)
        store.put(("medhub", "weak_areas"), "test_persist", {"area": "AreaAlfa", "especialidade": "TemaUm"})
        del store  # destruir instância

        store2 = _make_store(db)  # nova instância, mesmo arquivo
        item = store2.get(("medhub", "weak_areas"), "test_persist")

        if item is None:
            print(f"  {_FAIL} — item não encontrado após reinicialização")
            return False
        if item.value.get("area") != "AreaAlfa":
            print(f"  {_FAIL} — valor incorreto: {item.value}")
            return False
        print(f"  {_PASS} — recuperado: {item.value}")
        return True
    finally:
        os.unlink(db)


# ---------------------------------------------------------------------------
# Test 2 — Cross-thread (store is global)
# ---------------------------------------------------------------------------
def test_cross_thread() -> bool:
    print("\n[2] Cross-thread: escreve em session_001, lê em session_002")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db = f.name

    try:
        store = _make_store(db)
        # Simula agente na session_001 escrevendo uma fraqueza
        store.put(
            ("medhub", "weak_areas"),
            "cardiologia_001",
            {
                "area": "Clínica Médica",
                "especialidade": "Cardiologia",
                "pattern": "Confunde IC sistólica vs diastólica",
                "error_count": 3,
                "last_updated": "2026-03-25",
            },
        )

        # Simula agente na session_002 lendo (store é global, sem thread isolation)
        items = store.search(("medhub", "weak_areas"), limit=10)
        found = [i for i in items if i.key == "cardiologia_001"]

        if not found:
            print(f"  {_FAIL} — item não visível de outra thread")
            return False
        print(f"  {_PASS} — item visível cross-thread: {found[0].value['pattern']}")
        return True
    finally:
        os.unlink(db)


# ---------------------------------------------------------------------------
# Test 3 — Search
# ---------------------------------------------------------------------------
def test_search() -> bool:
    print("\n[3] Search: 3 entradas -> busca por query -> retorna relevante")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db = f.name

    try:
        store = _make_store(db)
        ns = ("medhub", "weak_areas")
        store.put(ns, "s001", {"area": "AreaAlfa", "especialidade": "TemaUm", "pattern": "padrao dummy alfa"})
        store.put(ns, "s002", {"area": "AreaBeta", "especialidade": "TemaDois", "pattern": "padrao dummy beta"})
        store.put(ns, "s003", {"area": "AreaGama", "especialidade": "TemaTres", "pattern": "padrao dummy gama"})

        results = store.search(ns, query="AreaAlfa", limit=10)
        if not results:
            print(f"  {_FAIL} — busca por 'AreaAlfa' não retornou nada")
            return False
        if results[0].key != "s001":
            print(f"  {_FAIL} — resultado inesperado: {results[0].key}")
            return False

        # Negative: busca por algo inexistente
        empty = store.search(ns, query="area_inexistente_xyz", limit=10)
        if empty:
            print(f"  {_FAIL} — busca negativa retornou resultados: {[i.key for i in empty]}")
            return False

        print(f"  {_PASS} — busca 'AreaAlfa' retornou '{results[0].value['area']}'; negativo correto")
        return True
    finally:
        os.unlink(db)


# ---------------------------------------------------------------------------
# Test 4 — Consolidation
# ---------------------------------------------------------------------------
def test_consolidation() -> bool:
    print("\n[4] Consolidação: mock session log -> consolidate_session -> error_count sincronizado")
    import sqlite3

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db = f.name

    # Create a mock session log + ipub sintético em diretório temporário
    with tempfile.TemporaryDirectory() as tmpdir:
        history_dir = Path(tmpdir) / "history"
        history_dir.mkdir()
        mock_log = history_dir / "session_999.md"
        mock_log.write_text(
            "# Session 999 — log dummy\n\nTexto dummy de sessão para o smoke.\n",
            encoding="utf-8",
        )

        fake_ipub = Path(tmpdir) / "ipub_fake.db"
        conn = sqlite3.connect(fake_ipub)
        conn.execute(
            """CREATE TABLE taxonomia_cronograma (
                   id INTEGER PRIMARY KEY AUTOINCREMENT, area TEXT NOT NULL, tema TEXT NOT NULL,
                   questoes_realizadas INTEGER DEFAULT 0, questoes_acertadas INTEGER DEFAULT 0)"""
        )
        conn.execute(
            "INSERT INTO taxonomia_cronograma (area, tema, questoes_realizadas, questoes_acertadas) VALUES ('AreaAlfa','TemaUm',100,40)"
        )
        conn.commit()
        conn.close()

        # Patch history dir + ipub path for the test
        import app.memory.manager as mgr_mod
        original_dir, original_ipub = mgr_mod._HISTORY_DIR, mgr_mod._IPUB_PATH
        mgr_mod._HISTORY_DIR, mgr_mod._IPUB_PATH = history_dir, fake_ipub

        try:
            store = _make_store(db)
            store.put(
                ("medhub", "weak_areas"),
                "wa_dummy",
                {"kind": "WeakArea", "content": {"area": "AreaAlfa", "especialidade": "TemaUm", "error_count": 0}},
            )
            # Sem API key → só o sync de contadores roda
            os.environ.pop("ANTHROPIC_API_KEY", None)
            from app.memory.manager import consolidate_session
            consolidate_session(999, store=store, db_path=db)

            item = store.get(("medhub", "weak_areas"), "wa_dummy")
            if item is None or item.value["content"]["error_count"] != 60:
                print(f"  {_FAIL} — error_count não sincronizado: {item.value if item else None}")
                return False

            # Nenhuma memória write-only pode ter sido criada
            namespaces = store.list_namespaces(prefix=("medhub",), limit=50)
            if any("session_insights" in "/".join(ns) for ns in namespaces):
                print(f"  {_FAIL} — namespace write-only recriado: {namespaces}")
                return False

            print(f"  {_PASS} — error_count=60 por match exato (area, tema); namespaces: {['/'.join(n) for n in namespaces]}")
            return True
        finally:
            mgr_mod._HISTORY_DIR, mgr_mod._IPUB_PATH = original_dir, original_ipub
            os.unlink(db)


# ---------------------------------------------------------------------------
# Test 5 — Context unwrap (envelope LangMem)
# ---------------------------------------------------------------------------
def test_context_unwrap() -> bool:
    print("\n[5] Unwrap: registro-envelope -> load_context renderiza valores reais")
    import io
    import contextlib
    from app.memory.inspect import load_context

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db = f.name

    try:
        store = _make_store(db)
        # Formato canônico do LangMem: envelope {"kind", "content"}
        store.put(
            ("medhub", "weak_areas"),
            "uuid-envelope-1",
            {
                "kind": "WeakArea",
                "content": {
                    "area": "GO",
                    "especialidade": "Obstetrícia",
                    "pattern": "Confunde conduta em DPP vs placenta prévia",
                    "error_count": 3,
                    "last_updated": "2026-07-01",
                },
            },
        )

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            load_context(db)
        out = buf.getvalue()

        if "[? / ?]" in out:
            print(f"  {_FAIL} — placeholder [? / ?] ainda presente no contexto")
            return False
        if "[GO / Obstetrícia]" not in out:
            print(f"  {_FAIL} — fraqueza não renderizada com valores reais:\n{out}")
            return False
        print(f"  {_PASS} — envelope desembrulhado: [GO / Obstetrícia] renderizado, zero [? / ?]")
        return True
    finally:
        os.unlink(db)


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
def main() -> None:
    print("=" * 60)
    print("MedHub Memory v1 — Smoke Tests")
    print("=" * 60)

    results = [
        test_persistence(),
        test_cross_thread(),
        test_search(),
        test_consolidation(),
        test_context_unwrap(),
    ]

    passed = sum(results)
    total = len(results)
    print(f"\n{'='*60}")
    print(f"Resultado: {passed}/{total} testes passaram")
    if passed < total:
        sys.exit(1)
    else:
        print("Todos os testes passaram. Memory v1 operacional.")


if __name__ == "__main__":
    main()
