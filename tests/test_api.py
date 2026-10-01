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


def test_shell_shortcuts():
    c = TestClient(app)
    assert c.get("/dica").status_code == 200
    assert c.get("/exercicio", params={"nivel": "iniciante"}).status_code == 200
    assert c.get("/random", params={"kind": "atalho"}).status_code == 200
    assert c.get("/comandos", params={"sistema": "linux"}).status_code == 200
    assert c.get("/atalhos", params={"sistema": "windows"}).status_code == 200


def test_shell_clients_and_quickstart():
    c = TestClient(app)
    sh = c.get("/infoaula.sh")
    assert sh.status_code == 200
    assert "INFOAULA_URL" in sh.text
    # a API injeta a propria URL no script (zero-install nao passa env var)
    assert "http://testserver" in sh.text
    assert "http://localhost:8000" not in sh.text
    ps1 = c.get("/infoaula.ps1")
    assert ps1.status_code == 200
    assert "INFOAULA_URL" in ps1.text
    assert "Invoke-RestMethod" in ps1.text
    assert "http://testserver" in ps1.text
    root = c.get("/")
    assert root.status_code == 200
    assert "iex (irm" in root.text and "infoaula.sh | bash" in root.text
