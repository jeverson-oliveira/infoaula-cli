import sqlite3
from pathlib import Path

from infoaula import store
from infoaula.models import ContentItem

SEED = Path(__file__).resolve().parent.parent / "content" / "seed.json"


def _memdb() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(store.SCHEMA)
    return conn


def test_seed_loads():
    items = store.load_seed_file(SEED)
    assert len(items) >= 20
    assert all(isinstance(i, ContentItem) for i in items)


def test_upsert_search_filter():
    conn = _memdb()
    items = store.load_seed_file(SEED)
    n = store.upsert_items(conn, items)
    assert n == len(items)
    assert store.count_items(conn) == len(items)
    assert store.search(conn, "copiar arquivo") or store.search(conn, "arquivo")
    assert store.list_items(conn, category="linux")
    assert store.list_items(conn, kind="atalho")
    assert store.get_random(conn, kind="dica") is not None
    conn.close()


def test_seed_if_empty_idempotent():
    conn = _memdb()
    a = store.seed_if_empty(conn, SEED)
    b = store.seed_if_empty(conn, SEED)
    assert a > 0 and b == 0
    conn.close()
