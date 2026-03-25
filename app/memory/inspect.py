"""
CLI de observabilidade para MedHub Memory v1.

Uso:
    python app/memory/inspect.py --namespace medhub/weak_areas
    python app/memory/inspect.py --threads
    python app/memory/inspect.py --dump
    python app/memory/inspect.py --stats
"""

from __future__ import annotations

import argparse
import json

from app.memory.store import SQLiteMemoryStore
from app.memory.checkpointer import get_checkpointer, get_session_history


_DEFAULT_DB = "medhub_memory.db"
_COL_W = {"namespace": 30, "key": 20, "updated": 20}


def _truncate(s: str, n: int) -> str:
    s = str(s)
    return s if len(s) <= n else s[: n - 1] + "…"


def _print_table(rows: list[dict]) -> None:
    if not rows:
        print("  (vazio)")
        return
    headers = list(rows[0].keys())
    col_widths = {h: max(len(h), max(len(str(r.get(h, ""))) for r in rows)) for h in headers}
    col_widths = {h: min(w, 60) for h, w in col_widths.items()}

    header_row = "  " + "  ".join(h.ljust(col_widths[h]) for h in headers)
    sep = "  " + "  ".join("-" * col_widths[h] for h in headers)
    print(header_row)
    print(sep)
    for row in rows:
        print("  " + "  ".join(_truncate(str(row.get(h, "")), col_widths[h]).ljust(col_widths[h]) for h in headers))


def cmd_namespace(ns_arg: str, db_path: str) -> None:
    """Show all entries in a namespace."""
    # Accept both "medhub/weak_areas" and "medhub weak_areas" forms
    parts = tuple(ns_arg.replace("/", " ").split())
    store = SQLiteMemoryStore(db_path)
    items = store.search(parts, limit=200)

    print(f"\n[namespace: {'/'.join(parts)}]  {len(items)} entradas\n")
    rows = []
    for item in items:
        rows.append(
            {
                "key": item.key,
                "value": json.dumps(item.value, ensure_ascii=False),
                "updated_at": item.updated_at[:19] if item.updated_at else "",
            }
        )
    _print_table(rows)
    print()


def cmd_threads(db_path: str) -> None:
    """List all session threads in the checkpointer."""
    print("\n[threads — SqliteSaver]\n")
    try:
        with get_checkpointer(db_path) as cp:
            # SqliteSaver doesn't expose a direct list-all-threads API;
            # query the underlying SQLite directly as a fallback.
            import sqlite3
            conn = sqlite3.connect(db_path)
            try:
                rows = conn.execute(
                    "SELECT DISTINCT thread_id FROM checkpoints ORDER BY thread_id"
                ).fetchall()
                if not rows:
                    print("  (nenhuma thread registrada)")
                else:
                    for row in rows:
                        history = get_session_history(cp, row[0])
                        steps = len(history)
                        print(f"  {row[0]}  ({steps} checkpoints)")
            except Exception as e:
                print(f"  Erro ao listar threads: {e}")
            finally:
                conn.close()
    except Exception as e:
        print(f"  Checkpointer indisponível: {e}")
    print()


def cmd_dump(db_path: str) -> None:
    """Dump all long-term memory entries across all namespaces."""
    store = SQLiteMemoryStore(db_path)
    namespaces = store.list_namespaces(prefix=("medhub",), limit=50)

    if not namespaces:
        print("\n  (memória longa-duração vazia)\n")
        return

    for ns in namespaces:
        items = store.search(ns, limit=200)
        print(f"\n[{'/'.join(ns)}]  {len(items)} entradas")
        rows = [
            {
                "key": item.key,
                "value": json.dumps(item.value, ensure_ascii=False),
                "updated_at": item.updated_at[:19] if item.updated_at else "",
            }
            for item in items
        ]
        _print_table(rows)
    print()


def cmd_stats(db_path: str) -> None:
    """Show summary statistics."""
    store = SQLiteMemoryStore(db_path)
    namespaces = store.list_namespaces(prefix=("medhub",), limit=50)

    total = 0
    rows = []
    for ns in namespaces:
        items = store.search(ns, limit=1000)
        total += len(items)
        rows.append({"namespace": "/".join(ns), "entries": len(items)})

    print(f"\n[stats — medhub memory]  {total} entradas totais\n")
    _print_table(rows)
    print()


def load_context(db_path: str = _DEFAULT_DB) -> None:
    """Print a concise memory context suitable for agent boot."""
    store = SQLiteMemoryStore(db_path)

    profile_items = store.search(("medhub", "profile"), limit=10)
    prefs_items = store.search(("medhub", "study_preferences"), limit=10)
    weak_items = store.search(("medhub", "weak_areas"), limit=20)
    rules_items = store.search(("medhub", "workflow_rules"), limit=10)

    print("\n=== MedHub Memory Context ===\n")

    if profile_items:
        print("## Perfil do usuário")
        for item in profile_items:
            print(f"  {json.dumps(item.value, ensure_ascii=False)}")

    if prefs_items:
        print("\n## Preferências de estudo")
        for item in prefs_items:
            print(f"  {json.dumps(item.value, ensure_ascii=False)}")

    if weak_items:
        print("\n## Áreas de fraqueza persistentes")
        for item in weak_items:
            v = item.value
            print(f"  [{v.get('area','?')} / {v.get('especialidade','?')}] {v.get('pattern','')}")

    if rules_items:
        print("\n## Regras de workflow aprendidas")
        for item in rules_items:
            v = item.value
            print(f"  [{v.get('learned_in','?')}] {v.get('rule','')} — {v.get('context','')}")

    if not any([profile_items, prefs_items, weak_items, rules_items]):
        print("  (memória vazia — primeira sessão)")

    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MedHub Memory Inspector")
    parser.add_argument("--namespace", "-n", metavar="NS", help="Show entries for namespace (e.g. medhub/profile)")
    parser.add_argument("--threads", "-t", action="store_true", help="List all session threads")
    parser.add_argument("--dump", "-d", action="store_true", help="Dump all long-term memory")
    parser.add_argument("--stats", "-s", action="store_true", help="Summary statistics")
    parser.add_argument("--context", "-c", action="store_true", help="Print agent boot context")
    parser.add_argument("--db", default=_DEFAULT_DB, help=f"Path to memory DB (default: {_DEFAULT_DB})")
    args = parser.parse_args()

    if args.namespace:
        cmd_namespace(args.namespace, args.db)
    elif args.threads:
        cmd_threads(args.db)
    elif args.dump:
        cmd_dump(args.db)
    elif args.stats:
        cmd_stats(args.db)
    elif args.context:
        load_context(args.db)
    else:
        parser.print_help()
