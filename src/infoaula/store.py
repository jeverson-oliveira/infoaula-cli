"""Armazenamento local SQLite — cache offline-first.

Multiplataforma:
  - Windows: %APPDATA%/infoaula/infoaula.db
  - Linux/macOS: ~/.local/share/infoaula/infoaula.db
Override para testes/aula: INFOAULA_DATA_DIR ou INFOAULA_DB
"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .models import ContentItem

SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  category TEXT NOT NULL,
  kind TEXT NOT NULL DEFAULT 'comando',
  command TEXT,
  description TEXT NOT NULL DEFAULT '',
  example TEXT,
  difficulty TEXT NOT NULL DEFAULT 'iniciante',
  tags TEXT NOT NULL DEFAULT '[]',
  os TEXT,
  updated_at TEXT
);
CREATE TABLE IF NOT EXISTS meta (
  key TEXT PRIMARY KEY,
  value TEXT
);
"""


def data_dir() -> Path:
    override = os.environ.get("INFOAULA_DATA_DIR")
    if override:
        p = Path(override).expanduser()
        p.mkdir(parents=True, exist_ok=True)
        return p
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming")))
        p = base / "infoaula"
    else:
        p = Path.home() / ".local" / "share" / "infoaula"
    p.mkdir(parents=True, exist_ok=True)
    return p


def db_path() -> Path:
    override = os.environ.get("INFOAULA_DB")
    if override:
        return Path(override).expanduser()
    return data_dir() / "infoaula.db"


def connect(path: Path | None = None) -> sqlite3.Connection:
    p = path or db_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(p))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def _row_to_item(row: sqlite3.Row) -> ContentItem:
    return ContentItem(
        id=row["id"],
        title=row["title"],
        category=row["category"],
        kind=row["kind"] or "comando",
        command=row["command"],
        description=row["description"] or "",
        example=row["example"],
        difficulty=row["difficulty"] or "iniciante",
        tags=json.loads(row["tags"] or "[]"),
        os=row["os"],
        updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None,
    )


def upsert_items(conn: sqlite3.Connection, items: list[ContentItem]) -> int:
    n = 0
    for it in items:
        conn.execute(
            """INSERT INTO items (id,title,category,kind,command,description,example,difficulty,tags,os,updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)
               ON CONFLICT(id) DO UPDATE SET
                 title=excluded.title, category=excluded.category, kind=excluded.kind,
                 command=excluded.command, description=excluded.description,
                 example=excluded.example, difficulty=excluded.difficulty,
                 tags=excluded.tags, os=excluded.os, updated_at=excluded.updated_at""",
            (
                it.id, it.title, it.category, it.kind, it.command, it.description,
                it.example, it.difficulty, json.dumps(it.tags, ensure_ascii=False),
                it.os, it.updated_at.isoformat() if it.updated_at else None,
            ),
        )
        n += 1
    conn.commit()
    return n


def load_seed_file(seed_path: Path) -> list[ContentItem]:
    data = json.loads(seed_path.read_text(encoding="utf-8"))
    return [ContentItem.model_validate(o) for o in data]


def seed_if_empty(conn: sqlite3.Connection, seed_path: Path | None = None) -> int:
    cur = conn.execute("SELECT COUNT(*) AS c FROM items")
    if cur.fetchone()["c"] > 0:
        return 0
    if seed_path is None:
        # content/seed.json relativo à raiz do projeto
        here = Path(__file__).resolve()
        candidates = [
            here.parent.parent.parent / "content" / "seed.json",  # src/infoaula -> raiz
            Path.cwd() / "content" / "seed.json",
        ]
        seed_path = next((c for c in candidates if c.exists()), None)
    if seed_path is None or not seed_path.exists():
        return 0
    items = load_seed_file(seed_path)
    return upsert_items(conn, items)


def list_categories(conn: sqlite3.Connection) -> list[tuple[str, int]]:
    cur = conn.execute("SELECT category, COUNT(*) AS c FROM items GROUP BY category ORDER BY category")
    return [(r["category"], r["c"]) for r in cur.fetchall()]


def list_items(
    conn: sqlite3.Connection,
    category: str | None = None,
    kind: str | None = None,
    difficulty: str | None = None,
    limit: int = 100,
) -> list[ContentItem]:
    q = "SELECT * FROM items WHERE 1=1"
    params: list = []
    if category and category != "all":
        q += " AND lower(category) LIKE ?"
        params.append(f"%{category.lower()}%")
    if kind and kind != "all":
        q += " AND lower(kind) = ?"
        params.append(kind.lower())
    if difficulty and difficulty != "all":
        # aceita sinônimos beginner/iniciante
        norm = {"beginner": "iniciante", "beginners": "iniciante"}.get(difficulty.lower(), difficulty.lower())
        q += " AND lower(difficulty) = ?"
        params.append(norm)
    q += " ORDER BY category, title LIMIT ?"
    params.append(limit)
    return [_row_to_item(r) for r in conn.execute(q, params).fetchall()]


def search(conn: sqlite3.Connection, term: str, limit: int = 20) -> list[ContentItem]:
    like = f"%{term.lower()}%"
    cur = conn.execute(
        """SELECT * FROM items
           WHERE lower(title) LIKE ? OR lower(description) LIKE ?
              OR lower(command) LIKE ? OR lower(example) LIKE ?
              OR lower(tags) LIKE ? OR lower(category) LIKE ?
           ORDER BY category, title LIMIT ?""",
        (like, like, like, like, like, like, limit),
    )
    return [_row_to_item(r) for r in cur.fetchall()]


def get_random(conn: sqlite3.Connection, kind: str | None = None, difficulty: str | None = None) -> ContentItem | None:
    q = "SELECT * FROM items WHERE 1=1"
    params: list = []
    if kind:
        q += " AND lower(kind) = ?"
        params.append(kind.lower())
    if difficulty:
        q += " AND lower(difficulty) = ?"
        params.append(difficulty.lower())
    q += " ORDER BY RANDOM() LIMIT 1"
    row = conn.execute(q, params).fetchone()
    return _row_to_item(row) if row else None


def count_items(conn: sqlite3.Connection) -> int:
    return conn.execute("SELECT COUNT(*) AS c FROM items").fetchone()["c"]


def get_last_sync(conn: sqlite3.Connection) -> datetime | None:
    row = conn.execute("SELECT value FROM meta WHERE key='last_sync'").fetchone()
    if row and row["value"]:
        try:
            return datetime.fromisoformat(row["value"])
        except ValueError:
            return None
    return None


def set_last_sync(conn: sqlite3.Connection, when: datetime | None = None) -> None:
    when = when or datetime.now(timezone.utc)
    conn.execute(
        "INSERT INTO meta(key,value) VALUES('last_sync',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (when.isoformat(),),
    )
    conn.commit()
