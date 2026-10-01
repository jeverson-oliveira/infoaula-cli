"""InfoAula API — FastAPI mínima, somente leitura (MVP).

Fontes de conteúdo (ordem):
  1. PostgreSQL via DATABASE_URL (tabela `items`, JSON compatível com ContentItem)
  2. Arquivo seed INFOAULA_SEED ou content/seed.json

Endpoints:
  GET /health
  GET /sync        → SyncPayload completo (o CLI consome aqui)
  GET /items       → filtros ?category ?kind ?q ?difficulty ?limit
  GET /categories  → agrupado
  GET /dica        → 1 dica aleatória (atalho p/ shell)
  GET /exercicio   → 1 exercício (?nivel=iniciante)
  GET /random      → 1 item aleatório com filtros
  GET /comandos    → atalho p/ shell (?sistema=linux)
  GET /atalhos     → atalho p/ shell (?sistema=windows)
  GET /infoaula.sh → cliente shell (curl|bash sem instalar nada)
"""

from __future__ import annotations

import json
import logging
import os
import random
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

try:
    from infoaula.models import ContentItem, SyncPayload
except ImportError:  # quando rodado como pacote isolado
    from src.infoaula.models import ContentItem, SyncPayload  # type: ignore

VERSION = "0.1.0"

log = logging.getLogger("infoaula_api")

app = FastAPI(title="InfoAula API", version=VERSION, description="Conteúdo didático para o InfoAula CLI (somente leitura no MVP).")
# API pública somente-leitura: libera GET de qualquer origem (sem cookies/auth),
# então CORS aberto aqui não expõe credencial. Se um dia houver login, restringir.
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


@lru_cache(maxsize=1)
def _cached_seed() -> tuple[ContentItem, ...]:
    """Cache em memória — evita reler seed.json a cada request na VPS."""
    return tuple(_load_seed())


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
    except Exception as e:  # fallback para seed se o PG falhar (com log, sem vazar URL)
        log.warning("PostgreSQL indisponível, usando seed local: %s", type(e).__name__)
        return None


def get_all() -> list[ContentItem]:
    pg = _load_pg()
    if pg is not None:
        return pg
    return list(_cached_seed())


def _filter(
    items: list[ContentItem],
    category: str | None = None,
    kind: str | None = None,
    difficulty: str | None = None,
    q: str | None = None,
) -> list[ContentItem]:
    out = items
    if category:
        out = [i for i in out if category.lower() in i.category.lower()]
    if kind:
        out = [i for i in out if i.kind.lower() == kind.lower()]
    if difficulty:
        norm = {"beginner": "iniciante", "beginners": "iniciante"}.get(
            difficulty.lower(), difficulty.lower()
        )
        out = [i for i in out if i.difficulty.lower() == norm]
    if q:
        ql = q.lower()
        out = [i for i in out if ql in i.searchable_text()]
    return out


def _pick_one(items: list[ContentItem]) -> ContentItem:
    if not items:
        raise HTTPException(status_code=404, detail="Nenhum conteúdo encontrado")
    return random.choice(items)


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
    category: str | None = Query(default=None, max_length=60),
    kind: str | None = Query(default=None, max_length=30),
    difficulty: str | None = Query(default=None, max_length=30),
    q: str | None = Query(default=None, max_length=100),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[ContentItem]:
    return _filter(get_all(), category, kind, difficulty, q)[:limit]


@app.get("/dica", response_model=ContentItem, summary="Dica aleatória (atalho p/ shell)")
def dica() -> ContentItem:
    """GET /dica → 1 dica aleatória. Ideal p/ `curl $API/dica`."""
    return _pick_one([i for i in get_all() if i.kind.lower() == "dica"])


@app.get("/exercicio", response_model=ContentItem, summary="Exercício aleatório")
def exercicio(
    nivel: str | None = Query(default=None, description="iniciante|intermediario|avancado"),
    difficulty: str | None = Query(default=None),
) -> ContentItem:
    """GET /exercicio?nivel=iniciante → 1 exercício (com fallback p/ qualquer nível)."""
    want = (nivel or difficulty or "all").lower()
    pool = [i for i in get_all() if i.kind.lower() == "exercicio"]
    if want != "all":
        norm = {"beginner": "iniciante"}.get(want, want)
        filtered = [i for i in pool if i.difficulty.lower() == norm]
        if filtered:
            pool = filtered
    return _pick_one(pool)


@app.get("/random", response_model=ContentItem, summary="Item aleatório com filtros")
def random_item(
    category: str | None = Query(default=None, max_length=60),
    kind: str | None = Query(default=None, max_length=30),
    difficulty: str | None = Query(default=None, max_length=30),
    q: str | None = Query(default=None, max_length=100),
) -> ContentItem:
    """GET /random?kind=atalho&category=windows → 1 item aleatório filtrado."""
    return _pick_one(_filter(get_all(), category, kind, difficulty, q))


@app.get("/comandos", response_model=list[ContentItem], summary="Atalho p/ shell")
def comandos(
    sistema: str | None = Query(default=None, max_length=30, description="windows|linux|powershell"),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[ContentItem]:
    """GET /comandos?sistema=linux → igual a /items?kind=comando&category=linux."""
    out = [i for i in get_all() if i.kind.lower() == "comando"]
    if sistema:
        s = sistema.lower()
        out = [i for i in out if s in i.category.lower() or s in (i.os or "").lower()]
    return out[:limit]


@app.get("/atalhos", response_model=list[ContentItem], summary="Atalho p/ shell")
def atalhos(
    sistema: str | None = Query(default=None, max_length=30, description="windows|linux"),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[ContentItem]:
    """GET /atalhos?sistema=windows → igual a /items?kind=atalho filtrado."""
    out = [i for i in get_all() if i.kind.lower() == "atalho"]
    if sistema:
        s = sistema.lower()
        filtered = [i for i in out if s in i.category.lower() or s in (i.os or "").lower()]
        if filtered:
            out = filtered
    return out[:limit]


@app.get("/infoaula.sh", response_class=PlainTextResponse, summary="Cliente shell (curl|bash)")
def serve_shell_client() -> PlainTextResponse:
    """Serve o cliente shell p/ uso sem instalação: curl -sSL $API/infoaula.sh | bash -s dica."""
    here = Path(__file__).resolve()
    candidates = [
        here.parent.parent.parent / "scripts" / "infoaula.sh",
        Path.cwd() / "scripts" / "infoaula.sh",
        Path("/app/scripts/infoaula.sh"),
    ]
    for c in candidates:
        if c.exists():
            return PlainTextResponse(c.read_text(encoding="utf-8"), media_type="text/x-shellscript")
    raise HTTPException(status_code=404, detail="scripts/infoaula.sh não encontrado na imagem")
