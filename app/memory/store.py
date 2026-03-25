"""
SQLiteMemoryStore — LangGraph BaseStore implementation over SQLite.

Implements the BaseStore interface required by LangMem tools.
Uses a single table: memory_store(namespace, key, value, updated_at).
Search in v1 is substring-based; v2 will add sqlite-vec embeddings.

Connections are opened and explicitly closed per operation to avoid
Windows file-locking issues (SQLite __exit__ commits but does NOT close).
"""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Iterator, Optional

from langgraph.store.base import BaseStore, Item, SearchItem


class SQLiteMemoryStore(BaseStore):
    """Persistent key-value store backed by SQLite.

    Compatible with LangMem's create_manage_memory_tool and
    create_search_memory_tool. Thread-safe via per-call connections.
    """

    def __init__(self, db_path: str = "medhub_memory.db"):
        self.db_path = db_path
        self.setup()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @contextmanager
    def _cursor(self):
        """Open, yield (conn, cursor), commit, and always close."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            cur = conn.cursor()
            yield conn, cur
            conn.commit()
        finally:
            conn.close()

    def setup(self) -> None:
        """Create table if it does not exist."""
        with self._cursor() as (conn, cur):
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_store (
                    namespace  TEXT NOT NULL,
                    key        TEXT NOT NULL,
                    value      TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (namespace, key)
                )
                """
            )

    @staticmethod
    def _namespace_str(namespace: tuple) -> str:
        return "/".join(namespace)

    @staticmethod
    def _namespace_tuple(ns_str: str) -> tuple:
        return tuple(ns_str.split("/"))

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    # ------------------------------------------------------------------
    # BaseStore interface
    # ------------------------------------------------------------------

    def put(
        self,
        namespace: tuple[str, ...],
        key: str,
        value: dict[str, Any],
    ) -> None:
        ns = self._namespace_str(namespace)
        with self._cursor() as (conn, cur):
            cur.execute(
                """
                INSERT INTO memory_store (namespace, key, value, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(namespace, key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = excluded.updated_at
                """,
                (ns, key, json.dumps(value), self._now()),
            )

    def get(self, namespace: tuple[str, ...], key: str) -> Optional[Item]:
        ns = self._namespace_str(namespace)
        with self._cursor() as (conn, cur):
            row = cur.execute(
                "SELECT namespace, key, value, updated_at FROM memory_store WHERE namespace=? AND key=?",
                (ns, key),
            ).fetchone()
        if row is None:
            return None
        return Item(
            namespace=self._namespace_tuple(row["namespace"]),
            key=row["key"],
            value=json.loads(row["value"]),
            updated_at=row["updated_at"],
            created_at=row["updated_at"],
        )

    def delete(self, namespace: tuple[str, ...], key: str) -> None:
        ns = self._namespace_str(namespace)
        with self._cursor() as (conn, cur):
            cur.execute(
                "DELETE FROM memory_store WHERE namespace=? AND key=?",
                (ns, key),
            )

    def search(
        self,
        namespace_prefix: tuple[str, ...],
        *,
        query: Optional[str] = None,
        filter: Optional[dict] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[SearchItem]:
        prefix = self._namespace_str(namespace_prefix)
        with self._cursor() as (conn, cur):
            rows = cur.execute(
                """
                SELECT namespace, key, value, updated_at
                FROM memory_store
                WHERE namespace = ? OR namespace LIKE ?
                ORDER BY updated_at DESC
                """,
                (prefix, prefix + "/%"),
            ).fetchall()

        items = []
        for row in rows:
            value = json.loads(row["value"])
            # Substring search across serialized value when query is given
            if query:
                haystack = json.dumps(value).lower()
                if query.lower() not in haystack:
                    continue
            items.append(
                SearchItem(
                    namespace=self._namespace_tuple(row["namespace"]),
                    key=row["key"],
                    value=value,
                    updated_at=row["updated_at"],
                    created_at=row["updated_at"],
                    score=1.0,
                )
            )

        return items[offset : offset + limit]

    def list_namespaces(
        self,
        *,
        prefix: Optional[tuple[str, ...]] = None,
        suffix: Optional[tuple[str, ...]] = None,
        max_depth: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[tuple[str, ...]]:
        with self._cursor() as (conn, cur):
            rows = cur.execute(
                "SELECT DISTINCT namespace FROM memory_store ORDER BY namespace"
            ).fetchall()

        namespaces = [self._namespace_tuple(r["namespace"]) for r in rows]

        if prefix:
            namespaces = [ns for ns in namespaces if ns[: len(prefix)] == prefix]
        if suffix:
            namespaces = [ns for ns in namespaces if ns[-len(suffix) :] == suffix]
        if max_depth is not None:
            namespaces = [ns for ns in namespaces if len(ns) <= max_depth]

        return namespaces[offset : offset + limit]

    # ------------------------------------------------------------------
    # Async stubs (required by BaseStore ABC; not used in MedHub v1)
    # ------------------------------------------------------------------

    async def aput(self, namespace, key, value):
        self.put(namespace, key, value)

    async def aget(self, namespace, key):
        return self.get(namespace, key)

    async def adelete(self, namespace, key):
        self.delete(namespace, key)

    async def asearch(self, namespace_prefix, *, query=None, filter=None, limit=10, offset=0):
        return self.search(namespace_prefix, query=query, filter=filter, limit=limit, offset=offset)

    async def alist_namespaces(self, **kwargs):
        return self.list_namespaces(**kwargs)

    def abatch(self, ops):
        raise NotImplementedError

    def batch(self, ops):
        raise NotImplementedError
