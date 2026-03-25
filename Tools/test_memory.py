"""
Smoke tests for MedHub Memory v1.

Run from repo root:
    python Tools/test_memory.py

Tests:
  1. Persistence  — put → reinitialize store → get (must recover)
  2. Cross-thread — store is global; write under session_001, read from session_002
  3. Search       — put 3 entries → search by query → must return relevant
  4. Consolidation — write mock session log → run consolidate_session → verify session_insights updated
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.memory.store import SQLiteMemoryStore

_PASS = "\033[92mPASS\033[0m"
_FAIL = "\033[91mFAIL\033[0m"


def _make_store(db_path: str) -> SQLiteMemoryStore:
    return SQLiteMemoryStore(db_path)


# ---------------------------------------------------------------------------
# Test 1 — Persistence
# ---------------------------------------------------------------------------
def test_persistence() -> bool:
    print("\n[1] Persistência: put → reinicializar → get")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db = f.name

    try:
        store = _make_store(db)
        store.put(("medhub", "profile"), "test_user", {"exam_target": "USP", "study_pace": "intensivo"})
        del store  # destruir instância

        store2 = _make_store(db)  # nova instância, mesmo arquivo
        item = store2.get(("medhub", "profile"), "test_user")

        if item is None:
            print(f"  {_FAIL} — item não encontrado após reinicialização")
            return False
        if item.value.get("exam_target") != "USP":
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
    print("\n[3] Search: 3 entradas → busca por query → retorna relevante")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db = f.name

    try:
        store = _make_store(db)
        store.put(("medhub", "session_insights"), "s001", {"session_id": "session_001", "insight": "Dengue grave: plaquetas < 20k + sangramento espontâneo", "area": "Infectologia"})
        store.put(("medhub", "session_insights"), "s002", {"session_id": "session_002", "insight": "Sífilis congênita: qualquer RN de mãe com VDRL reagente sem tratamento adequado deve tratar", "area": "GO"})
        store.put(("medhub", "session_insights"), "s003", {"session_id": "session_003", "insight": "IC com FEr: IECAs + betabloqueador + antagonistas aldosterona reduzem mortalidade", "area": "Cardiologia"})

        results = store.search(("medhub", "session_insights"), query="dengue", limit=10)
        if not results:
            print(f"  {_FAIL} — busca por 'dengue' não retornou nada")
            return False
        if results[0].key != "s001":
            print(f"  {_FAIL} — resultado inesperado: {results[0].key}")
            return False

        # Negative: busca por algo inexistente
        empty = store.search(("medhub", "session_insights"), query="nefrologia_inexistente_xyz", limit=10)
        if empty:
            print(f"  {_FAIL} — busca negativa retornou resultados: {[i.key for i in empty]}")
            return False

        print(f"  {_PASS} — busca 'dengue' retornou '{results[0].value['area']}'; negativo correto")
        return True
    finally:
        os.unlink(db)


# ---------------------------------------------------------------------------
# Test 4 — Consolidation
# ---------------------------------------------------------------------------
def test_consolidation() -> bool:
    print("\n[4] Consolidação: mock session log → consolidate_session → session_insights atualizado")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db = f.name

    # Create a mock session log in a temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        history_dir = Path(tmpdir) / "history"
        history_dir.mkdir()
        mock_log = history_dir / "session_999.md"
        mock_log.write_text(
            "# Session 999 — Cardiologia\n\n"
            "Analisamos questões de Insuficiência Cardíaca e Cardiologia.\n"
            "Erro recorrente em IC com FEr (classificação NYHA).\n",
            encoding="utf-8",
        )

        # Patch history dir for the test
        import app.memory.manager as mgr_mod
        original_dir = mgr_mod._HISTORY_DIR
        mgr_mod._HISTORY_DIR = history_dir

        try:
            store = _make_store(db)
            # Run without API key → fallback path
            os.environ.pop("ANTHROPIC_API_KEY", None)
            from app.memory.manager import consolidate_session
            consolidate_session(999, store=store, db_path=db)

            # Verify session_insights has an entry
            items = store.search(("medhub", "session_insights"), limit=10)
            if not items:
                print(f"  {_FAIL} — nenhuma entrada criada em session_insights")
                return False

            entry = items[0]
            print(f"  {_PASS} — insight criado: '{entry.value.get('insight', '')[:60]}…'")
            return True
        finally:
            mgr_mod._HISTORY_DIR = original_dir
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
