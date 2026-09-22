"""InfoAula API — FastAPI mínima, somente leitura (MVP).

Fontes de conteúdo (ordem):
  1. PostgreSQL via DATABASE_URL (tabela `items`, JSON compatível com ContentItem)
  2. Arquivo seed INFOAULA_SEED ou content/seed.json

Endpoints:
  GET /health
  GET /sync        → SyncPayload completo (o CLI consome aqui)
  GET /items       → filtros ?category ?kind ?q ?difficulty ?limit
  GET /categories  → agrupado
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

try:
    from infoaula.models import ContentItem, SyncPayload
except ImportError:  # quando rodado como pacote isolado
    from src.infoaula.models import ContentItem, SyncPayload  # type: ignore

VERSION = "0.1.0"

app = FastAPI(title="InfoAula API", version=VERSION, description="Conteúdo didático para o InfoAula CLI (somente leitura no MVP).")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


def _seed_path() -> Path:
    env = os.environ.get("INFOAULA_SEED")
    if env:
        return Path(env)
    here = Path(__file__).resolve()
    candidates = [
        here.parent.parent.parent / "content" / "seed.json",
        Path.cwd() / "content" / "seed.json",
        Path("/app/content/seed.json"),
    ]
    for c in candidates:
        if c.exists():
            return c
    return candidates[0]


def _load_seed() -> list[ContentItem]:
    p = _seed_path()
    if not p.exists():
        return []
    data = json.loads(p.read_text(encoding="utf-8"))
    return [ContentItem.model_validate(o) for o in data]


def _load_pg() -> list[ContentItem] | None:
    """Tenta PostgreSQL se DATABASE_URL definido. Retorna None se indisponível."""
    url = os.environ.get("DATABASE_URL")
    if not url:
        return None
    try:
        from sqlalchemy import create_engine, text
    except ImportError:
        return None
    try:
        eng = create_engine(url, pool_pre_ping=True)
        with eng.connect() as c:
            rows = c.execute(text("SELECT data FROM items")).fetchall()
        items = []
        for (blob,) in rows:
            obj = blob if isinstance(blob, dict) else json.loads(blob)
            items.append(ContentItem.model_validate(obj))
        return items
    except Exception:  # noqa: BLE001 — fallback para seed se o PG falhar
        return None


def get_all() -> list[ContentItem]:
    pg = _load_pg()
    if pg is not None:
        return pg
    return _load_seed()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": VERSION}


@app.get("/sync", response_model=SyncPayload)
def sync() -> SyncPayload:
    items = get_all()
    return SyncPayload(version=1, updated_at=datetime.now(timezone.utc), items=items)


@app.get("/categories")
def categories() -> list[dict]:
    agg: dict[str, int] = {}
    for it in get_all():
        agg[it.category] = agg.get(it.category, 0) + 1
    return [{"category": k, "count": v} for k, v in sorted(agg.items())]


@app.get("/items", response_model=list[ContentItem])
def items(
    category: str | None = Query(default=None),
    kind: str | None = Query(default=None),
    difficulty: str | None = Query(default=None),
    q: str | None = Query(default=None),
    limit: int = Query(default=100, le=500),
) -> list[ContentItem]:
    out = get_all()
    if category:
        out = [i for i in out if category.lower() in i.category.lower()]
    if kind:
        out = [i for i in out if i.kind.lower() == kind.lower()]
    if difficulty:
        out = [i for i in out if i.difficulty.lower() == difficulty.lower()]
    if q:
        ql = q.lower()
        out = [i for i in out if ql in i.searchable_text()]
    return out[:limit]
