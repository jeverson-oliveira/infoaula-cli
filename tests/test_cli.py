
import pytest
from typer.testing import CliRunner

runner = CliRunner()


@pytest.fixture()
def isolated_db(monkeypatch, tmp_path):
    db = tmp_path / "test.db"
    monkeypatch.setenv("INFOAULA_DB", str(db))
    # garante offline nos testes de status/sync
    monkeypatch.setenv("INFOAULA_API_URL", "http://127.0.0.1:9")
    return db


def test_cli_help(isolated_db):
    from infoaula.cli import app
    r = runner.invoke(app, ["--help"])
    assert r.exit_code == 0
    assert "infoaula" in r.output.lower() or "Usage" in r.output


def test_cli_comandos_buscar_dica_status(isolated_db):
    from infoaula.cli import app
    for args in (
        ["comandos"],
        ["comandos", "linux"],
        ["atalhos"],
        ["buscar", "arquivo"],
        ["dica"],
        ["exercicio"],
        ["exercicio", "--nivel", "iniciante"],
        ["categorias"],
        ["status"],
    ):
        r = runner.invoke(app, args)
        assert r.exit_code == 0, f"{args} falhou: {r.output}"


def test_cli_sync_offline_graceful(isolated_db):
    from infoaula.cli import app
    r = runner.invoke(app, ["sync"])
    assert r.exit_code == 0
    assert "local" in r.output.lower() or "offline" in r.output.lower() or "internet" in r.output.lower()
