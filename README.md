# InfoAula CLI

Auxiliar didático de informática para o terminal. Funciona **offline**, é **multiplataforma** (Windows + PowerShell, Linux + Bash) e pode **sincronizar** com uma API remota quando há internet.

```
infoaula              → menu interativo
infoaula comandos linux
infoaula atalhos
infoaula buscar "copiar arquivo"
infoaula dica
infoaula exercicio --nivel iniciante
infoaula status
infoaula sync
```

## Instalação (sala de aula)

Requer Python 3.10+ (recomendado 3.13).

**Linux:**
```bash
pip install -e .
infoaula status
```

**Windows (PowerShell):**
```powershell
pip install -e .
infoaula status
```

Para a API (opcional):
```bash
pip install -e ".[api]"
uvicorn infoaula_api.main:app --reload
```

## Como funciona (offline-first)

```
Aluno → InfoAula CLI → SQLite local → (internet?) → API FastAPI → PostgreSQL
                          ↓ não                        ↓ sim
                   conteúdo local                  atualiza cache
```

- Sem internet: tudo funciona com o cache/SQLite local + `content/seed.json`.
- Com internet: `infoaula sync` baixa novidades sem reinstalar o CLI.
- Conteúdo separado da lógica: edite `content/seed.json`, rode `sync` ou reinstale.

## Conteúdo

Categorias em `content/seed.json`: windows, powershell, linux, atalhos-windows, atalhos-linux, conceitos, redes, arquivos, segurança, produtividade, dicas, exercícios.

Cada item:
```json
{
  "title": "Listar arquivos",
  "category": "linux",
  "command": "ls",
  "description": "Lista arquivos e diretórios.",
  "example": "ls -la",
  "difficulty": "iniciante",
  "tags": ["arquivos", "terminal", "linux"]
}
```

## API

| Método | Rota | Uso |
|---|---|---|
| GET | `/health` | checagem online |
| GET | `/sync` | CLI baixa tudo |
| GET | `/items?category=linux&q=arquivo` | consulta filtrada |
| GET | `/categories` | agrupado |

Somente leitura no MVP (sem auth) de propósito — evita overengineering.

## Docker

```bash
docker compose up --build
# API via Nginx em http://localhost:8080/health
```

## Testes

```bash
pip install -e ".[dev]"
pytest -q
```

## Estrutura

```
content/seed.json       conteúdo didático (editável)
src/infoaula/           CLI: models, store(SQLite), api_client, cli(Typer+Rich), ui
src/infoaula_api/       API FastAPI mínima
tests/                  pytest
docker/ nginx/          infra
```

## Variáveis de ambiente

| Var | Padrão | Uso |
|---|---|---|
| `INFOAULA_API_URL` | `http://localhost:8000` | URL da API |
| `INFOAULA_DB` | `~/.local/share/infoaula/infoaula.db` | banco local (útil em prova/aula) |
| `INFOAULA_DATA_DIR` | idem | pasta de dados |
| `DATABASE_URL` | — | PostgreSQL da API |
