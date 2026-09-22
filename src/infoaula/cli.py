"""InfoAula CLI — ponto de entrada Typer + Rich.

Uso em sala de aula:
    infoaula              → menu interativo
    infoaula comandos     → categorias de comandos
    infoaula comandos linux
    infoaula atalhos
    infoaula buscar "copiar arquivo"
    infoaula dica
    infoaula exercicio --nivel iniciante
    infoaula status
    infoaula sync
"""

from __future__ import annotations

import sqlite3
from typing import Annotated

import typer
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from . import __version__, api_client, store
from .ui import console, item_panel, items_table

app = typer.Typer(
    name="infoaula",
    help="Auxiliar didático de informática para o terminal (offline-first).",
    add_completion=False,
    no_args_is_help=False,
)


def _db() -> sqlite3.Connection:
    conn = store.connect()
    store.seed_if_empty(conn)
    return conn


# ---------------------------------------------------------------- menu interativo

MENU = [
    ("1", "Ver comandos", "comandos"),
    ("2", "Ver atalhos", "atalhos"),
    ("3", "Buscar conteúdo", "buscar"),
    ("4", "Dica rápida", "dica"),
    ("5", "Exercício", "exercicio"),
    ("6", "Status", "status"),
    ("7", "Sincronizar", "sync"),
    ("0", "Sair", None),
]


def _menu() -> None:
    console.print(Panel.fit(
        "[bold cyan]InfoAula[/bold cyan] — auxiliar de informática\n"
        "[dim]Digite o número da opção. Funciona offline.[/dim]",
        title=f"v{__version__}",
    ))
    table = Table(show_header=False, box=None)
    table.add_column("op", style="bold green")
    table.add_column("desc")
    for key, label, _ in MENU:
        table.add_row(key, label)
    console.print(table)
    while True:
        try:
            choice = Prompt.ask("Escolha", default="0").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Até logo![/dim]")
            return
        if choice == "0":
            console.print("[dim]Até logo![/dim]")
            return
        elif choice == "1":
            _cmd_comandos(None)
        elif choice == "2":
            _cmd_atalhos(None)
        elif choice == "3":
            term = Prompt.ask("Buscar por").strip()
            if term:
                _cmd_buscar(term)
        elif choice == "4":
            _cmd_dica()
        elif choice == "5":
            _cmd_exercicio("iniciante")
        elif choice == "6":
            _cmd_status()
        elif choice == "7":
            _cmd_sync(None)
        else:
            console.print("[yellow]Opção inválida. Tente 0-7.[/yellow]")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Menu principal. Sem argumentos, abre o menu interativo."""
    if ctx.invoked_subcommand is None:
        _menu()


# ---------------------------------------------------------------- helpers internos

def _cmd_comandos(sistema: str | None) -> None:
    conn = _db()
    filtro = (sistema or "all").lower()
    if filtro in ("win", "windows"):
        filtro = "windows"
    items = store.list_items(conn, category=None if filtro == "all" else filtro)
    # 'comandos' mostra kind=comando + conceitos de terminal; se vazio, mostra tudo do filtro
    cmds = [i for i in items if i.kind == "comando"]
    show = cmds or items
    if not show:
        console.print(f"[yellow]Nada encontrado para '{sistema}'. Tente: windows, linux, powershell.[/yellow]")
        _cmd_categorias(conn)
        conn.close()
        return
    console.print(items_table(show, title=f"Comandos{f' — {sistema}' if sistema else ''}"))
    conn.close()


def _cmd_atalhos(sistema: str | None) -> None:
    conn = _db()
    filtro = (sistema or "all").lower()
    if filtro in ("win",):
        filtro = "windows"
    if filtro == "all":
        items = store.list_items(conn, kind="atalho")
    else:
        items = [i for i in store.list_items(conn, category=filtro) if i.kind in ("atalho",)]
        if not items:  # fallback: qualquer atalho do SO
            items = [i for i in store.list_items(conn, kind="atalho") if filtro in (i.os or "") or filtro in i.category]
    if not items:
        console.print(f"[yellow]Nenhum atalho para '{sistema}'.[/yellow]")
        conn.close()
        return
    console.print(items_table(items, title=f"Atalhos{f' — {sistema}' if sistema else ''}"))
    conn.close()


def _cmd_buscar(termo: str) -> None:
    conn = _db()
    items = store.search(conn, termo)
    conn.close()
    if not items:
        console.print(f"[yellow]Nada encontrado para '{termo}'. Tente 'arquivo', 'rede', 'atalho'...[/yellow]")
        return
    console.print(items_table(items, title=f"Busca: {termo}"))


def _cmd_dica() -> None:
    conn = _db()
    item = store.get_random(conn, kind="dica") or store.get_random(conn)
    conn.close()
    if not item:
        console.print("[yellow]Sem conteúdo local. Rode 'infoaula sync' com internet.[/yellow]")
        return
    console.print(item_panel(item, title="💡 Dica rápida"))


def _cmd_exercicio(nivel: str) -> None:
    conn = _db()
    nivel_norm = nivel.lower()
    item = store.get_random(conn, kind="exercicio", difficulty=nivel_norm)
    if not item and nivel_norm != "all":
        item = store.get_random(conn, kind="exercicio")  # fallback qualquer nível
    conn.close()
    if not item:
        console.print("[yellow]Sem exercícios locais.[/yellow]")
        return
    console.print(item_panel(item, title=f"📝 Exercício ({item.difficulty})"))


def _cmd_status() -> None:
    conn = _db()
    total = store.count_items(conn)
    cats = store.list_categories(conn)
    last = store.get_last_sync(conn)
    conn.close()
    api_url = api_client.get_api_url()
    online = api_client.check_online(api_url)
    mode = "[green]online[/green]" if online else "[yellow]offline[/yellow] (usando cache local)"
    console.print(Panel.fit(
        f"[bold]InfoAula v{__version__}[/bold]\n"
        f"Modo: {mode}\n"
        f"API: {api_url}\n"
        f"Itens locais: [bold]{total}[/bold]\n"
        f"Última sync: {last.isoformat() if last else 'nunca'}\n"
        f"Banco: {store.db_path()}",
        title="Status",
    ))
    if cats:
        t = Table(title="Por categoria", show_header=True, header_style="bold cyan")
        t.add_column("Categoria")
        t.add_column("Qtd", justify="right")
        for c, n in cats:
            t.add_row(c, str(n))
        console.print(t)


def _cmd_sync(api_url: str | None) -> None:
    url = api_client.get_api_url(api_url)
    console.print(f"[dim]Sincronizando com {url}...[/dim]")
    if not api_client.check_online(url):
        console.print("[yellow]Sem internet ou API indisponível. Mantendo conteúdo local.[/yellow]")
        return
    try:
        payload = api_client.fetch_sync(url)
    except Exception as e:  # noqa: BLE001 — sync nunca pode quebrar o uso offline
        console.print(f"[red]Falha na sync: {e}. Conteúdo local preservado.[/red]")
        return
    conn = _db()
    n = store.upsert_items(conn, payload.items)
    store.set_last_sync(conn, payload.updated_at)
    conn.close()
    console.print(f"[green]OK![/green] {n} itens atualizados.")


def _cmd_categorias(conn: sqlite3.Connection | None = None) -> None:
    own = conn is None
    conn = conn or _db()
    cats = store.list_categories(conn)
    if own:
        conn.close()
    if not cats:
        console.print("[yellow]Sem conteúdo local.[/yellow]")
        return
    t = Table(title="Categorias", show_header=True, header_style="bold cyan")
    t.add_column("Categoria", style="magenta")
    t.add_column("Itens", justify="right")
    for c, n in cats:
        t.add_row(c, str(n))
    console.print(t)


# ---------------------------------------------------------------- comandos Typer

@app.command("comandos")
def comandos(
    sistema: Annotated[str | None, typer.Argument(help="Filtro: windows, linux, powershell (vazio = todos)")] = None,
) -> None:
    """Listar categorias/comandos. Ex: infoaula comandos linux"""
    _cmd_comandos(sistema)


@app.command("atalhos")
def atalhos(
    sistema: Annotated[str | None, typer.Argument(help="Filtro: windows, linux (vazio = todos)")] = None,
) -> None:
    """Mostrar atalhos de teclado."""
    _cmd_atalhos(sistema)


@app.command("buscar")
def buscar(termo: Annotated[str, typer.Argument(help="Texto a pesquisar")]) -> None:
    """Pesquisar conteúdo. Ex: infoaula buscar "copiar arquivo\""""
    _cmd_buscar(termo)


@app.command("dica")
def dica() -> None:
    """Mostrar uma dica aleatória."""
    _cmd_dica()


@app.command("exercicio")
def exercicio(
    nivel: Annotated[str, typer.Option("--nivel", "-n", help="iniciante|intermediario|avancado")] = "iniciante",
) -> None:
    """Mostrar um exercício. Ex: infoaula exercicio --nivel iniciante"""
    _cmd_exercicio(nivel)


@app.command("status")
def status() -> None:
    """Versão, modo online/offline, última sync, qtd local."""
    _cmd_status()


@app.command("sync")
def sync(
    api_url: Annotated[str | None, typer.Option("--api-url", help="URL base da API")] = None,
) -> None:
    """Sincronizar conteúdo com a API (se houver internet)."""
    _cmd_sync(api_url)


@app.command("categorias")
def categorias() -> None:
    """Listar categorias disponíveis localmente."""
    _cmd_categorias()


if __name__ == "__main__":
    app()
