# InfoAula CLI 📚💻

**Seu auxiliar de informática dentro do terminal.**

O InfoAula ajuda **alunos e monitores** a consultar comandos, atalhos de teclado,
conceitos básicos e exercícios — direto no terminal, **mesmo sem internet**.

```
infoaula              → abre o menu interativo (comece por aqui!)
infoaula comandos linux
infoaula atalhos
infoaula buscar "copiar arquivo"
infoaula dica
infoaula exercicio --nivel iniciante
infoaula status
infoaula sync
```

> **Para professores/monitores:** há um [roteiro de aula](#-roteiro-de-aula-40-min)
> pronto no final deste guia.

---

## 1. O que você precisa (requisitos)

| Item     | Mínimo    | Recomendado | Como conferir              |
|----------|-----------|-------------|----------------------------|
| Python   | 3.10      | 3.13+       | `python --version`         |
| pip      | qualquer  | junto ao Python | `pip --version`        |
| Sistema  | Windows 10+ ou Linux | qualquer um dos dois | —        |
| Internet | **não precisa** | só para `sync` | `infoaula status` |

Não sabe se sua máquina está pronta? O projeto inclui um **script de
verificação** que diz exatamente o que falta — veja o passo 0.

---

## 2. Passo 0 — Verifique seu ambiente (1 minuto)

Abra o terminal na pasta do projeto e rode:

```bash
python scripts/verificar_ambiente.py
```

> No Linux, se `python` não existir, use `python3 scripts/verificar_ambiente.py`.

Saída esperada quando está tudo certo:

```
== InfoAula · Verificação do ambiente ==

Sistema: Linux 6.x (x86_64)
[OK] Python: Python 3.13.x (versão recomendada ou superior).
[OK] pip: pip disponível (instalador de pacotes do Python).
[!] venv: Nenhum venv ativo. Recomendado criar um...

-- Recomendação --
Tudo certo! Próximo passo:
  pip install -e .  →  infoaula status
```

- `[OK]` → pronto.
- `[!]` → funciona, mas tem recomendação de melhoria (leia a dica).
- `[X]` → precisa resolver antes de continuar (o script diz como).

---

## 3. Passo 1 — Instale o Python (só se o script pedir)

**Windows (PowerShell):**

Opção A — site oficial: baixe em <https://www.python.org/downloads/> e, na
primeira tela do instalador, **marque a caixa "Add python.exe to PATH"**.

Opção B — via terminal:

```powershell
winget install Python.Python.3.13
```

Feche e reabra o PowerShell depois de instalar, e confira:

```powershell
python --version
```

**Linux (Debian, Ubuntu, Mint):**

```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv
python3 --version
```

---

## 4. Passo 2 — Instale o InfoAula

Recomendamos um **ambiente virtual** (venv): ele isola os pacotes do projeto e
evita bagunça no Python do sistema.

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
infoaula status
```

**Linux (Bash):**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
infoaula status
```

Se `infoaula status` mostrar a versão e a quantidade de itens locais, deu certo! 🎉

> **Erro `externally-managed-environment`?** É o Linux pedindo para usar venv.
> É só seguir os comandos acima (criar e ativar o `.venv`) que resolve.

---

## 5. Passo 3 — Primeiros comandos

Abra o menu interativo (ideal para quem está começando):

```bash
infoaula
```

| Quero...                  | Comando                              |
|---------------------------|--------------------------------------|
| Ver comandos de Linux     | `infoaula comandos linux`            |
| Ver comandos de Windows   | `infoaula comandos windows`          |
| Ver PowerShell            | `infoaula comandos powershell`       |
| Ver atalhos de teclado    | `infoaula atalhos`                   |
| Pesquisar qualquer coisa  | `infoaula buscar "copiar arquivo"`   |
| Uma dica rápida           | `infoaula dica`                      |
| Um exercício              | `infoaula exercicio --nivel iniciante` |
| Ver se estou online       | `infoaula status`                    |
| Atualizar o conteúdo      | `infoaula sync`                      |
| Ver categorias            | `infoaula categorias`                |

---

## 6. 🍎 Roteiro de aula (40 min)

1. **Ambiente (10 min):** cada aluno roda `scripts/verificar_ambiente.py` e
   segue as recomendações até ver "Tudo certo!".
2. **Navegação (10 min):** `infoaula comandos linux` (ou `windows`) +
   `infoaula exercicio --nivel iniciante` — executar o exercício no terminal.
3. **Atalhos (10 min):** `infoaula atalhos` — cada aluno testa 3 atalhos e
   conta para a turma qual economiza mais tempo.
4. **Desafio (10 min):** `infoaula buscar "rede"` → descobrir o IP da própria
   máquina (`ipconfig` no Windows, `ip a` no Linux) e fazer `ping 8.8.8.8`.

Sem internet no laboratório? Sem problema: tudo acima funciona offline.

---

## 7. Como funciona (offline-first)

```
Aluno → InfoAula CLI → SQLite local → tem internet? ─ SIM → API FastAPI → PostgreSQL
                                              └ NÃO → usa o conteúdo local
```

- **Sem internet:** tudo funciona com o banco local + `content/seed.json`.
- **Com internet:** `infoaula sync` baixa novidades **sem reinstalar o CLI**.
- **Conteúdo separado da lógica:** para adicionar conteúdo, edite
  `content/seed.json` seguindo o modelo abaixo.

Exemplo de item:

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

Categorias disponíveis: `windows`, `powershell`, `linux`, `atalhos-windows`,
`atalhos-linux`, `conceitos`, `redes`, `arquivos`, `seguranca`,
`produtividade`, `dicas`, `exercicios`.

---

## 8. Problemas comuns

| Erro / sintoma | Causa provável | Solução |
|---|---|---|
| `python não é reconhecido` (Windows) | PATH não marcado na instalação | Reinstale marcando "Add python.exe to PATH" |
| `externally-managed-environment` | PEP 668: sistema protege o Python global | Use venv (passo 2) |
| `infoaula: comando não encontrado` | venv desativado ou instalação incompleta | Ative o `.venv` e rode `pip install -e .` de novo |
| `sync` diz "sem internet" | Sem rede ou API fora do ar | Normal! O conteúdo local continua funcionando |
| `pip install` lento no laboratório | Rede da escola limitada | Instale uma vez e distribua a pasta `.venv`, ou use `sync` depois |

---

## 9. Para quem quer ir além (opcional)

**API remota** (serve conteúdo atualizado para os CLIs):

```bash
pip install -e ".[api]"
uvicorn infoaula_api.main:app --reload
```

| Método | Rota | Uso |
|---|---|---|
| GET | `/health` | checagem online |
| GET | `/sync` | o CLI baixa tudo aqui |
| GET | `/items?category=linux&q=arquivo` | consulta filtrada |
| GET | `/categories` | agrupado |

Somente leitura no MVP (sem autenticação) de propósito — evita overengineering.

**Docker:**

```bash
docker compose up --build
# API via Nginx em http://localhost:8080/health
```

**Testes:**

```bash
pip install -e ".[dev]"
pytest -q
```

---

## 10. Estrutura do projeto

```
content/seed.json            conteúdo didático (editável)
scripts/verificar_ambiente.py  script de verificação do ambiente
src/infoaula/                CLI: models, store (SQLite), api_client, cli (Typer+Rich), ui
src/infoaula_api/            API FastAPI mínima
tests/                       pytest
docker/ nginx/               infra
```

**Variáveis de ambiente:**

| Var | Padrão | Uso |
|---|---|---|
| `INFOAULA_API_URL` | `http://localhost:8000` | URL da API |
| `INFOAULA_DB` | `~/.local/share/infoaula/infoaula.db` | banco local (útil em prova/aula) |
| `INFOAULA_DATA_DIR` | idem | pasta de dados |
| `DATABASE_URL` | — | PostgreSQL da API |
