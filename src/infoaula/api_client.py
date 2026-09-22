"""Cliente HTTP da API remota — com fallback offline gracioso."""

from __future__ import annotations

import os
from datetime import datetime, timezone

import httpx

from .models import SyncPayload

DEFAULT_API_URL = "http://localhost:8000"


def get_api_url(explicit: str | None = None) -> str:
    return (explicit or os.environ.get("INFOAULA_API_URL") or DEFAULT_API_URL).rstrip("/")


def check_online(api_url: str | None = None, timeout: float = 2.5) -> bool:
    url = get_api_url(api_url)
    try:
        r = httpx.get(f"{url}/health", timeout=timeout)
        return r.status_code == 200
    except Exception:  # noqa: BLE001 — offline é estado normal, qualquer erro = offline
        return False


def fetch_sync(api_url: str | None = None, timeout: float = 10.0) -> SyncPayload:
    """Baixa conteúdo remoto. Levanta exceção se offline — o CLI trata e usa cache."""
    url = get_api_url(api_url)
    r = httpx.get(f"{url}/sync", timeout=timeout)
    r.raise_for_status()
    payload = SyncPayload.model_validate(r.json())
    if payload.updated_at is None:
        payload.updated_at = datetime.now(timezone.utc)
    return payload
