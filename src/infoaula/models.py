"""Modelos Pydantic — contrato compartilhado entre CLI, API e conteúdo seed.

Mantido propositalmente pequeno para o MVP. Todo item de conteúdo segue
o mesmo esquema, seja dica, comando, atalho, conceito ou exercício.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

Difficulty = str
ItemKind = str


class ContentItem(BaseModel):
    """Um item didático. Campos opcionais permitem representar comandos e teoria."""

    id: str = Field(description="Slug único, ex: 'linux-ls'")
    title: str = Field(description="Título curto, ex: 'Listar arquivos'")
    category: str = Field(description="Categoria livre, ex: 'linux', 'windows', 'atalhos-windows'")
    kind: ItemKind = Field(default="comando", description="Tipo do item")
    command: str | None = Field(default=None, description="Comando literal, se aplicável")
    description: str = Field(description="Explicação curta para sala de aula")
    example: str | None = Field(default=None, description="Exemplo prático")
    difficulty: str = Field(default="iniciante", description="iniciante|intermediario|avancado")
    tags: list[str] = Field(default_factory=list)
    os: str | None = Field(default=None, description="windows|linux|any")
    updated_at: datetime | None = None

    def searchable_text(self) -> str:
        parts = [self.title, self.category, self.description, self.command or "", self.example or ""]
        parts.extend(self.tags)
        return " ".join(parts).lower()


class SyncPayload(BaseModel):
    """Payload que a API remota entrega no /sync."""

    version: int = 1
    updated_at: datetime | None = None
    items: list[ContentItem]


class LocalStats(BaseModel):
    total: int = 0
    by_category: dict[str, int] = Field(default_factory=dict)
    last_sync: datetime | None = None
    api_url: str | None = None
