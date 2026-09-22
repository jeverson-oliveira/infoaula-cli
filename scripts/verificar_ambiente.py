#!/usr/bin/env python3
"""InfoAula — verificação do ambiente (script didático).

Como usar (não precisa instalar nada antes):

    python scripts/verificar_ambiente.py
    python3 scripts/verificar_ambiente.py   # no Linux, se `python` não existir

O script verifica se sua máquina está pronta para rodar o InfoAula CLI e,
se algo estiver faltando, explica em linguagem simples como resolver.

Saída: 0 = pronto para instalar | 1 = precisa ajustar algo.
"""

from __future__ import annotations

import platform
import sys

MIN_PYTHON = (3, 10)
RECOMENDADO = (3, 13)


def check_python() -> tuple[str, str]:
    """Retorna (status, mensagem). status: OK | AVISO | ERRO."""
    atual = sys.version_info[:3]
    versao = f"{atual[0]}.{atual[1]}.{atual[2]}"
    if atual >= RECOMENDADO:
        return "OK", f"Python {versao} (versão recomendada ou superior)."
    if atual >= MIN_PYTHON:
        return "AVISO", (
            f"Python {versao} funciona, mas o recomendado é 3.13+. "
            "Considere atualizar quando puder."
        )
    return "ERRO", (
        f"Python {versao} é antigo demais (mínimo: 3.10). "
        "Instale uma versão nova antes de continuar."
    )


def check_pip() -> tuple[str, str]:
    try:
        import pip  # noqa: F401
        return "OK", "pip disponível (instalador de pacotes do Python)."
    except ImportError:
        return "ERRO", (
            "pip não encontrado. No Linux: `sudo apt install python3-pip`. "
            "No Windows: reinstale o Python marcando a opção 'pip'."
        )


def check_venv() -> tuple[str, str]:
    em_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    if em_venv:
        return "OK", "Ambiente virtual (venv) ativo. Bom — é o recomendado!"
    return "AVISO", (
        "Nenhum venv ativo. Recomendado criar um para não misturar pacotes:\n"
        "      python -m venv .venv  →  .venv\\Scripts\\Activate.ps1 (Windows)\n"
        "      python3 -m venv .venv  →  source .venv/bin/activate (Linux)"
    )


def como_instalar_python() -> str:
    sistema = platform.system()
    if sistema == "Windows":
        return (
            "Windows: baixe em https://www.python.org/downloads/ "
            "(marque 'Add python.exe to PATH') ou rode `winget install Python.Python.3.13`."
        )
    if sistema == "Linux":
        distro = platform.freedesktop_os_release().get("PRETTY_NAME", "Linux") if hasattr(platform, "freedesktop_os_release") else "Linux"
        return (
            f"{distro}: `sudo apt update && sudo apt install python3 python3-pip python3-venv` "
            "(Debian/Ubuntu/Mint)."
        )
    return "Baixe em https://www.python.org/downloads/."


def main() -> int:
    print("== InfoAula · Verificação do ambiente ==\n")
    print(f"Sistema: {platform.system()} {platform.release()} ({platform.machine()})")

    resultados = [
        ("Python", *check_python()),
        ("pip", *check_pip()),
        ("venv", *check_venv()),
    ]
    for nome, status, msg in resultados:
        simbolo = {"OK": "[OK]", "AVISO": "[!]", "ERRO": "[X]"}[status]
        print(f"{simbolo} {nome}: {msg}")

    erros = [r for r in resultados if r[1] == "ERRO"]
    print("\n-- Recomendação --")
    if erros:
        print(como_instalar_python())
        print("Depois rode este script de novo para confirmar.")
        return 1
    print("Tudo certo! Próximo passo:")
    print("  pip install -e .  →  infoaula status")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
