# InfoAula 📚

**Aprenda comandos de informática direto no terminal — sem instalar nada.**

O InfoAula mostra comandos, atalhos, conceitos e exercícios de informática.
Roda no **Windows** e no **Linux**, e funciona mesmo sem internet no laboratório.

---

## 👦👧 Aluno — comece aqui (2 passos)

Você precisa de **duas coisas**:

1. Um **endereço** que o professor escreve no quadro, parecido com
   `http://SERVIDOR-DA-ESCOLA:8080`
2. O **terminal** do seu computador

### 🪟 Windows

1. Tecle **Windows + R**, digite `powershell` e dê **Enter**
2. Cole a linha abaixo e dê **Enter** (troque o endereço pelo do professor):

```powershell
iex (irm http://SERVIDOR-DA-ESCOLA:8080/infoaula.ps1)
```

Pronto! Aparece um **menu**. Digite o **número** da opção e **Enter**.

### 🐧 Linux

Abra o **Terminal** (**Ctrl + Alt + T**) e cole:

```bash
curl -sSL http://SERVIDOR-DA-ESCOLA:8080/infoaula.sh | bash -s
```

Pronto! O mesmo **menu** aparece. Digite o **número** e **Enter**.

> ⚠️ Não funciona? Veja [Problemas comuns](#-problemas-comuns).
> Digitou errado? É só colar de novo — nada quebra.

---

## O que o menu faz

| Número | O que aparece |
|---|---|
| **1** | Comandos de Linux e Windows (ls, dir, cd...) |
| **2** | Atalhos de teclado (Ctrl + C, Win + D...) |
| **3** | Buscar qualquer palavra (ex: `rede`, `arquivo`) |
| **4** | Uma dica rápida 💡 |
| **5** | Um exercício para praticar 📝 |
| **6** | Se o servidor está funcionando |
| **7** | As categorias de conteúdo |
| **0** | Sair |

### Comandos digitados (se preferir digitar em vez do menu)

**Linux** (com o script salvo, veja o resumo abaixo):

```bash
./infoaula.sh comandos linux      # ou: windows, powershell
./infoaula.sh atalhos windows
./infoaula.sh buscar "copiar arquivo"
./infoaula.sh dica
./infoaula.sh exercicio --nivel iniciante
./infoaula.sh status
```

**Windows** (PowerShell, com o script salvo):

```powershell
.\infoaula.ps1 comandos linux
.\infoaula.ps1 buscar "copiar arquivo"
.\infoaula.ps1 dica
.\infoaula.ps1 exercicio --nivel iniciante
```

**No navegador** também funciona (dados em JSON) — abra o endereço do
professor e depois `/dica`: `http://SERVIDOR-DA-ESCOLA:8080/dica`

---

## 🍎 Roteiro de aula (40 min) — para o professor

1. **Entrar (5 min):** cada aluno abre o terminal e cola a linha da aula até
   ver o menu. Quem terminar ajuda o colega.
2. **Comandos (10 min):** opção **1** → ver a lista de comandos (Linux e
   Windows aparecem juntos). Cada aluno executa `ls` (ou `dir`) e `pwd` no
   próprio terminal.
3. **Atalhos (10 min):** opção **2** → cada aluno testa 3 atalhos e conta
   para a turma qual economiza mais tempo.
4. **Desafio (10 min):** opção **3** → busca por `rede`. Descobrir o IP da
   máquina (`ipconfig` no Windows, `ip a` no Linux) e `ping 8.8.8.8`.
5. **Exercício (5 min):** opção **5** → cada um faz o exercício que aparecer.

Sem internet no laboratório? O professor pode rodar o servidor no próprio
computador (veja abaixo) e usar o endereço da rede local (ex:
`http://192.168.1.10:8080`).

---

<details>
<summary><b>🖥️ Professor: colocar o servidor no ar (1 vez, ~5 min)</b></summary>

Precisa de Docker em uma máquina (VPS, notebook do professor ou PC do lab):

```bash
git clone https://github.com/jeverson-oliveira/infoaula-cli.git
cd infoaula-cli
docker compose -f docker-compose.vps.yml up -d --build
```

Confira: `curl http://localhost:8080/health` deve responder `ok`.

* **A URL dos alunos** é `http://SEU-IP-OU-DOMINIO:8080` — escreva no quadro.
* Libere a porta **8080** no firewall/security group da VPS.
* Atualizar conteúdo: edite `content/seed.json` e
  `docker compose -f docker-compose.vps.yml restart api`.
* **Em produção use `https://`** (Caddy, Traefik ou Cloudflare Tunnel) —
  em HTTP puro um atacante na rede pode alterar o conteúdo. Detalhes em
  [SECURITY.md](SECURITY.md).
* Quer banco PostgreSQL completo (opcional): `docker compose up --build`
  (usa `docker-compose.yml` com Postgres + Nginx).

</details>

<details>
<summary><b>🐍 Opcional: instalar o InfoAula com Python (offline total)</b></summary>

Para quem quer o CLI completo **no próprio computador, sem servidor**.
Requer **Python 3.10+** (recomendado 3.13+).

**Verifique o ambiente** (1 min):

```bash
python scripts/verificar_ambiente.py   # ou python3 no Linux
```

`[OK]` = pronto · `[!]` = recomendação · `[X]` = resolver antes.

**Instale** (Linux):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
infoaula status
```

**Instale** (Windows / PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
infoaula status
```

Sem venv, o Linux pode reclamar `externally-managed-environment` — é só
seguir os passos acima. Sem internet para instalar? Peça o pacote pronto
ao professor, ou use o caminho do aluno no topo desta página (só precisa do
servidor da escola).

</details>

<details>
<summary><b>🍎 Baixar o cliente uma vez (opcional, evita colar a linha toda hora)</b></summary>

**Linux** — salve e use quantas vezes quiser:

```bash
curl -sSL http://SERVIDOR-DA-ESCOLA:8080/infoaula.sh -o infoaula.sh
chmod +x infoaula.sh
./infoaula.sh                  # menu
./infoaula.sh buscar "rede"    # direto
```

**Windows** — no PowerShell:

```powershell
irm http://SERVIDOR-DA-ESCOLA:8080/infoaula.ps1 -OutFile infoaula.ps1
.\infoaula.ps1                 # menu
.\infoaula.ps1 dica            # direto
```

Se o Windows reclamar de política de execução, abra o PowerShell assim:
**Windows + X** → *Windows PowerShell* e cole de novo.

</details>

<details>
<summary><b>⚙️ Como funciona (offline-first)</b></summary>

```
Aluno → cliente (shell/PowerShell) → servidor da escola (API) → content/seed.json
                                   └ sem conexão? → mensagem amigável
```

* **Conteúdo separado da lógica:** para adicionar conteúdo, edite
  `content/seed.json` seguindo o modelo abaixo.

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

Categorias: `windows`, `powershell`, `linux`, `atalhos-windows`,
`atalhos-linux`, `conceitos`, `redes`, `arquivos`, `seguranca`,
`produtividade`, `dicas`, `exercicios`.

* **CLI com Python (offline total):** SQLite local + `infoaula sync`
  baixa novidades sem reinstalar.

</details>

<details>
<summary><b>🔌 API e desenvolvimento (para quem vai além)</b></summary>

**API remota** (os clientes consomem ela):

```bash
pip install -e ".[api]"
uvicorn infoaula_api.main:app --reload
```

| Método | Rota | Uso |
|---|---|---|
| GET | `/` | passo a rápido do aluno |
| GET | `/health` | checagem online |
| GET | `/sync` | o CLI Python baixa tudo aqui |
| GET | `/items?category=linux&q=arquivo` | consulta filtrada |
| GET | `/dica` · `/exercicio?nivel=` · `/random` | 1 item (atalho p/ shell) |
| GET | `/comandos?sistema=` · `/atalhos?sistema=` | atalho p/ shell |
| GET | `/infoaula.sh` · `/infoaula.ps1` | clientes zero-install |
| GET | `/categories` | agrupado |

Somente leitura no MVP (sem autenticação) de propósito — evita
overengineering.

**Testes:**

```bash
pip install -e ".[dev,api]"
pytest -q
```

**Estrutura do projeto:**

```
content/seed.json              conteúdo didático (editável)
scripts/infoaula.sh            cliente Linux (zero-install)
scripts/infoaula.ps1           cliente Windows (zero-install)
scripts/verificar_ambiente.py  verificação do ambiente Python
src/infoaula/                  CLI Python (Typer+Rich, SQLite)
src/infoaula_api/              API FastAPI
tests/                         pytest
docker/ nginx/                 infra
```

</details>

---

## 🚨 Problemas comuns

| Erro / sintoma | Causa provável | Solução |
|---|---|---|
| `irm` / `iex` não funciona (Windows) | Linha digitada errada ou sem internet até o servidor | Cole de novo inteira; confira a URL com o professor |
| `curl: command not found` (Linux) | curl não instalado | `sudo apt install curl` — ou use o PC do lab |
| `connection refused` / não abre o menu | Servidor desligado ou URL errada | Confirme o endereço no quadro; avise o professor |
| `Aviso: usa HTTP sem TLS` | Servidor sem HTTPS | Informativo — em sala está ok; o professor cuida disso |
| Windows bloqueia `.\infoaula.ps1` | Política de execução | Use a linha `iex (irm ...)` (ela não é bloqueada) |
| `externally-managed-environment` | Tentou instalar Python sem venv | Só quem instalou o CLI Python — siga o passo no resumo acima |
| `infoaula: comando não encontrado` | CLI Python não instalado | Use a linha do aluno (não precisa de `infoaula`) |

---

## 🔧 Variáveis de ambiente (avançado)

| Var | Padrão | Uso |
|---|---|---|
| `INFOAULA_URL` | `http://localhost:8000` | servidor dos clientes shell/PowerShell |
| `INFOAULA_API_URL` | `http://localhost:8000` | servidor do CLI Python |
| `INFOAULA_DB` | `~/.local/share/infoaula/infoaula.db` | banco local (útil em prova/aula) |
| `INFOAULA_DATA_DIR` | idem | pasta de dados |
| `INFOAULA_SEED` | `content/seed.json` | conteúdo da API |
| `DATABASE_URL` | — | PostgreSQL da API |

## Licença

MIT — veja [SECURITY.md](SECURITY.md) para reportar vulnerabilidades.
