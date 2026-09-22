try:
    from fastapi.testclient import TestClient

    from infoaula_api.main import app
    HAS_API = True
except Exception:  # noqa: BLE001 — permite rodar suite sem deps da API
    HAS_API = False

import pytest

pytestmark = pytest.mark.skipif(not HAS_API, reason="fastapi não instalado")


def test_health():
    c = TestClient(app)
    r = c.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_sync_and_filters():
    c = TestClient(app)
    s = c.get("/sync")
    assert s.status_code == 200
    assert len(s.json()["items"]) >= 20
    items = c.get("/items", params={"category": "linux", "limit": 5})
    assert items.status_code == 200
    cats = c.get("/categories")
    assert cats.status_code == 200
