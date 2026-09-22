import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "verificar_ambiente.py"


def test_script_existe():
    assert SCRIPT.exists(), "scripts/verificar_ambiente.py deve existir"


def test_script_aprova_ambiente_valido():
    r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, check=False)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "InfoAula" in r.stdout
    assert "Tudo certo" in r.stdout or "Recomenda" in r.stdout
