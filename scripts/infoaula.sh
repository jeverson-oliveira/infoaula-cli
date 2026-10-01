#!/usr/bin/env bash
# InfoAula via shell — sem instalar Python/venv, só curl + python3.
#
# Uso com VPS (troque pelo IP/domínio da sua VPS):
#   export INFOAULA_URL=http://SEU-VPS:8080
#   ./scripts/infoaula.sh status
#   ./scripts/infoaula.sh comandos linux
#   ./scripts/infoaula.sh atalhos windows
#   ./scripts/infoaula.sh buscar "copiar arquivo"
#   ./scripts/infoaula.sh dica
#   ./scripts/infoaula.sh exercicio --nivel iniciante
#
# Sem instalar nada (zero-install, ideal p/ aluno):
#   curl -sSL $INFOAULA_URL/infoaula.sh | bash -s
#     → sem argumentos abre o MENU interativo (ideal p/ crianca)
#   curl -sSL $INFOAULA_URL/infoaula.sh | bash -s dica
#   curl -sSL $INFOAULA_URL/infoaula.sh | bash -s buscar "rede"
#
set -u
API="${INFOAULA_URL:-http://localhost:8000}"
API="${API%/}"

# Repo público p/ escolas: curl|bash via HTTP permite MITM injetar shell.
# Em produção use https:// (Caddy/Traefik/Cloudflare). Aviso abaixo não bloqueia
# o uso em laboratório (http://192.168.x.x), mas deixa o risco explícito.
case "$API" in
  http://localhost*|http://127.0.0.1*|https://*) ;;
  http://*) echo "AVISO: $API usa HTTP sem TLS — um atacante na rede pode alterar o script e o conteúdo. Prefira https:// na VPS." >&2 ;;
esac

need() { command -v "$1" >/dev/null 2>&1 || { echo "Falta '$1'. No Linux: sudo apt install $1 | No Git-Bash: já vem com curl." >&2; exit 1; }; }
need curl
need python3

CURL="curl -sSf --connect-timeout 5 --max-time 15"

ajuda() {
  cat <<EOF
InfoAula via API ($API)

Uso (sem argumentos = menu interativo):
  $(basename "$0")                         → abre o menu (oque crianca quer)
  $(basename "$0") status                  → API online? quantos itens?
  $(basename "$0") comandos [linux|windows|powershell]
  $(basename "$0") atalhos [windows|linux]
  $(basename "$0") buscar "copiar arquivo"
  $(basename "$0") dica
  $(basename "$0") exercicio [--nivel iniciante|intermediario|avancado]
  $(basename "$0") categorias

Sem instalar nada:
  curl -sSL \$INFOAULA_URL/infoaula.sh | bash -s        → menu
  curl -sSL \$INFOAULA_URL/infoaula.sh | bash -s dica   → direto

Variável: INFOAULA_URL (padrão http://localhost:8000)
EOF
}

# Menu interativo p/ crianca. Usa /dev/tty p/ ler o teclado mesmo quando o
# script veio por pipe (curl | bash) — stdin é o próprio script, não o teclado.
menu() {
  if [ ! -r /dev/tty ]; then ajuda; return; fi
  term() { # lê uma linha do terminal real em $1 (prompt: $2)
    printf "%s" "$2" > /dev/tty || return 1
    read -r "$1" < /dev/tty || return 1
  }
  while true; do
    {
      printf "\n============ InfoAula ============\n"
      printf "  1) Ver comandos (Linux/Windows)\n"
      printf "  2) Ver atalhos de teclado\n"
      printf "  3) Buscar qualquer coisa\n"
      printf "  4) Dica rapida\n"
      printf "  5) Exercicio (iniciante)\n"
      printf "  6) Status do servidor\n"
      printf "  7) Categorias\n"
      printf "  0) Sair\n"
      printf "  Escolha: "
    } > /dev/tty
    local escolha=""
    read -r escolha < /dev/tty || { printf "\nAte logo!\n" > /dev/tty; return; }
    case "$escolha" in
      0) printf "Ate logo!\n" > /dev/tty; return ;;
      1) $CURL "$API/comandos" | fmt_lista ;;
      2) $CURL "$API/atalhos" | fmt_lista ;;
      3)
        term _q "  Buscar por: " || return
        if [ -n "$_q" ]; then $CURL -G "$API/items" --data-urlencode "q=$_q" | fmt_lista; fi
        ;;
      4) $CURL "$API/dica" | fmt_um ;;
      5) $CURL -G "$API/exercicio" --data-urlencode "nivel=iniciante" | fmt_um ;;
      6) cmd_status ;;
      7) cmd_categorias ;;
      *) printf "  Opcao invalida. Tente 0 a 7.\n" > /dev/tty ;;
    esac
  done
}

# Formata lista JSON [{title,category,command,description,example}] em texto legível
fmt_lista() {
  python3 -c '
import json,sys
try:
    data = json.load(sys.stdin)
except Exception as e:
    print(f"Resposta inválida da API: {e}"); sys.exit(1)
if not data:
    print("Nada encontrado. Tente outra palavra (ex: arquivo, rede, atalho)."); sys.exit(0)
for it in data:
    t = it.get("title","(sem título)")
    c = it.get("category","")
    cmd = it.get("command") or "—"
    d = it.get("description","")
    ex = it.get("example")
    print(f"• {t} [{c}]")
    print(f"  $ {cmd}")
    if d: print(f"  {d}")
    if ex: print(f"  Ex: {ex}")
    print()
'
}

fmt_um() {
  python3 -c '
import json,sys
try:
    it = json.load(sys.stdin)
except Exception as e:
    print("Resposta invalida da API: " + str(e)); sys.exit(1)
if isinstance(it, dict) and it.get("detail"):
    print("Nada encontrado (" + str(it.get("detail")) + ")."); sys.exit(0)
print("=== " + str(it.get("title", "InfoAula")) + " ===")
print("Categoria: " + str(it.get("category", "")) + " - Nivel: " + str(it.get("difficulty", "")))
if it.get("command"): print("$ " + str(it.get("command")))
print(str(it.get("description", "")))
if it.get("example"): print("Ex: " + str(it.get("example")))
'
}

cmd_status() {
  health_json=$($CURL "$API/health" 2>&1) || { echo "Offline: nao alcancei $API. Confira INFOAULA_URL e se o container esta rodando na VPS."; echo "$health_json"; exit 1; }
  echo "$health_json" | python3 -c '
import json,sys
h = json.load(sys.stdin)
print("API: OK (versao " + str(h.get("version", "?")) + ")")
'
  echo "URL: $API"
  $CURL "$API/categories" 2>/dev/null | python3 -c '
import json,sys
try:
    cats = json.load(sys.stdin)
    total = sum(c.get("count",0) for c in cats)
    print(f"Itens: {total}")
    for c in cats:
        print("- " + str(c.get("category")) + ": " + str(c.get("count")))
except Exception:
    print("Nao deu para listar categorias.")
'
}

cmd_categorias() {
  $CURL "$API/categories" | python3 -c '
import json,sys
for c in json.load(sys.stdin):
    print(str(c.get("category")) + ": " + str(c.get("count")))
' || { echo "Falha ao falar com $API"; exit 1; }
}

case "${1:-}" in
  "") menu ;;
  ajuda|help|--help|-h) ajuda ;;
  status) cmd_status ;;
  comandos)
    if [ $# -ge 2 ]; then $CURL -G "$API/comandos" --data-urlencode "sistema=$2" | fmt_lista
    else $CURL "$API/comandos" | fmt_lista; fi
    ;;
  atalhos)
    if [ $# -ge 2 ]; then $CURL -G "$API/atalhos" --data-urlencode "sistema=$2" | fmt_lista
    else $CURL "$API/atalhos" | fmt_lista; fi
    ;;
  buscar|search|busca)
    [ $# -lt 2 ] && { echo "Uso: $0 buscar \"copiar arquivo\""; exit 1; }
    $CURL -G "$API/items" --data-urlencode "q=$2" | fmt_lista
    ;;
  dica) $CURL "$API/dica" | fmt_um ;;
  exercicio)
    nivel="iniciante"
    if [ "${2:-}" = "--nivel" ] && [ $# -ge 3 ]; then nivel="$3"
    elif [ "${2:-}" != "" ]; then
      case "$2" in --nivel=*) nivel="${2#--nivel=}" ;; *) nivel="$2" ;; esac
    fi
    $CURL -G "$API/exercicio" --data-urlencode "nivel=$nivel" | fmt_um
    ;;
  categorias) cmd_categorias ;;
  *) echo "Comando desconhecido: $1"; echo; ajuda; exit 1 ;;
esac
