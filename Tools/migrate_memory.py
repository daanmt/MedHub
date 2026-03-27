"""
Migração one-time: move WeakAreas do namespace errado para o correto.

medhub/session_insights (errado) → medhub/weak_areas (correto)

Uso:
    python Tools/migrate_memory.py --dry-run   # preview
    python Tools/migrate_memory.py             # executa
"""

import argparse
import json
import sqlite3
from datetime import datetime, timezone

DB_PATH = "medhub_memory.db"
SRC_NS = "medhub/session_insights"
DST_NS = "medhub/weak_areas"


def migrate(dry_run: bool = True) -> None:
    conn = sqlite3.connect(DB_PATH)
    now = datetime.now(timezone.utc).isoformat()

    rows = conn.execute(
        "SELECT key, value, updated_at FROM memory_store WHERE namespace = ?",
        (SRC_NS,),
    ).fetchall()

    to_migrate = [(k, v, u) for k, v, u in rows if json.loads(v).get("kind") == "WeakArea"]

    print(f"Encontradas {len(to_migrate)} WeakAreas em '{SRC_NS}'")
    if not to_migrate:
        print("Nada a migrar.")
        conn.close()
        return

    for key, value, updated_at in to_migrate:
        d = json.loads(value)
        area = d.get("content", {}).get("area", "?")
        esp = d.get("content", {}).get("especialidade", "?")
        pattern = str(d.get("content", {}).get("pattern", ""))[:60]
        print(f"  {'[DRY-RUN] ' if dry_run else ''}key={key[:8]} | {area} / {esp} | {pattern}...")

        if not dry_run:
            conn.execute(
                """INSERT INTO memory_store (namespace, key, value, updated_at)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(namespace, key) DO UPDATE SET
                       value = excluded.value,
                       updated_at = excluded.updated_at""",
                (DST_NS, key, value, updated_at),
            )
            conn.execute(
                "DELETE FROM memory_store WHERE namespace = ? AND key = ?",
                (SRC_NS, key),
            )

    if not dry_run:
        conn.commit()
        print(f"\n✓ {len(to_migrate)} WeakAreas migradas: '{SRC_NS}' → '{DST_NS}'")
    else:
        print(f"\n[DRY-RUN] {len(to_migrate)} entradas seriam migradas. Use sem --dry-run para executar.")

    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrar WeakAreas para namespace correto")
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="Apenas mostrar o que seria migrado (default)")
    parser.add_argument("--execute", action="store_true",
                        help="Executar a migração de fato")
    args = parser.parse_args()

    migrate(dry_run=not args.execute)
