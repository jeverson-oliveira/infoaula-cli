"""Helpers visuais Rich — tabelas e painéis padronizados para sala de aula."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .models import ContentItem

console = Console()


def items_table(items: list[ContentItem], title: str = "Conteúdo") -> Table:
    t = Table(title=title, show_lines=False, header_style="bold cyan")
    t.add_column("Título", style="bold", no_wrap=False)
    t.add_column("Categoria", style="magenta")
    t.add_column("Comando", style="green")
    t.add_column("Descrição", no_wrap=False)
    for it in items:
        t.add_row(it.title, it.category, it.command or "—", it.description)
    return t


def item_panel(it: ContentItem, title: str | None = None) -> Panel:
    body = f"[bold]{it.title}[/bold]  [dim]({it.category} · {it.difficulty})[/dim]\n\n{it.description}"
    if it.command:
        body += f"\n\n[bold green]$ {it.command}[/bold green]"
    if it.example:
        body += f"\n[dim]Exemplo:[/dim] [yellow]{it.example}[/yellow]"
    if it.tags:
        body += f"\n[dim]Tags:[/dim] {', '.join(it.tags)}"
    return Panel(body, title=title or "InfoAula", border_style="cyan")


def detail_table(it: ContentItem) -> Table:
    t = Table(show_header=False, box=None)
    t.add_column("k", style="bold cyan")
    t.add_column("v")
    t.add_row("Título", it.title)
    t.add_row("Categoria", it.category)
    t.add_row("Tipo", it.kind)
    if it.command:
        t.add_row("Comando", f"[green]{it.command}[/green]")
    t.add_row("Descrição", it.description)
    if it.example:
        t.add_row("Exemplo", f"[yellow]{it.example}[/yellow]")
    t.add_row("Nível", it.difficulty)
    return t
