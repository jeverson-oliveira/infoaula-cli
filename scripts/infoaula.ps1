# InfoAula no Windows - sem instalar nada (o PowerShell ja vem no Windows).
#
# Como usar (cole no PowerShell):
#   iex (irm http://SERVIDOR-DA-ESCOLA:8080/infoaula.ps1)
#   -> abre o menu interativo. Digite o numero e Enter. 0 = sair.
#
# Salvo como arquivo tambem funciona:
#   .\infoaula.ps1 status
#   .\infoaula.ps1 dica
#   .\infoaula.ps1 buscar "copiar arquivo"
#   .\infoaula.ps1 comandos linux
#   .\infoaula.ps1 exercicio --nivel iniciante

# PS 5.1 (Windows 10) precisa disso para HTTPS moderno
try {
  [Net.ServicePointManager]::SecurityProtocol = `
    [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
} catch {}

$API = 'http://localhost:8000'
if ($env:INFOAULA_URL) { $API = $env:INFOAULA_URL.TrimEnd('/') }

# curl|bash/irm|iex via HTTP permite MITM na rede: avisa fora de localhost.
if ($API -like 'http://*' -and $API -notlike 'http://localhost*' -and $API -notlike 'http://127.0.0.1*') {
  Write-Warning "AVISO: $API usa HTTP sem TLS - prefira https:// em producao."
}

function Get-InfoAula([string]$PathAndQuery) {
  try {
    return Invoke-RestMethod -Uri ($API + $PathAndQuery) -TimeoutSec 15 -ErrorAction Stop
  } catch {
    $msg = $_.Exception.Message
    if ($_.ErrorDetails -and $_.ErrorDetails.Message) { $msg = $_.ErrorDetails.Message }
    Write-Host ("  (sem resposta da API: " + $msg + ")") -ForegroundColor Yellow
    return $null
  }
}

function Show-List($items) {
  $list = @($items)
  if ($list.Count -eq 0 -or $null -eq $list[0]) {
    Write-Host "Nada encontrado. Tente outra palavra (ex: arquivo, rede, atalho)." -ForegroundColor Yellow
    return
  }
  foreach ($it in $list) {
    Write-Host ("  " + $it.title + "  [" + $it.category + "]") -ForegroundColor Cyan
    $cmd = '-'
    if ($it.command) { $cmd = $it.command }
    Write-Host ("    $ " + $cmd) -ForegroundColor Green
    if ($it.description) { Write-Host ("    " + $it.description) }
    if ($it.example) { Write-Host ("    Ex: " + $it.example) -ForegroundColor DarkYellow }
    Write-Host ""
  }
}

function Show-One($it) {
  if ($null -eq $it) { return }
  if ($it.PSObject.Properties['detail']) {
    Write-Host ("Nada encontrado (" + $it.detail + ").") -ForegroundColor Yellow
    return
  }
  Write-Host ("=== " + $it.title + " ===") -ForegroundColor Cyan
  Write-Host ("Categoria: " + $it.category + " - Nivel: " + $it.difficulty)
  if ($it.command) { Write-Host ("$ " + $it.command) -ForegroundColor Green }
  if ($it.description) { Write-Host $it.description }
  if ($it.example) { Write-Host ("Ex: " + $it.example) -ForegroundColor DarkYellow }
}

function Show-Comandos([string]$sistema) {
  if ($sistema) { Show-List (Get-InfoAula ("/comandos?sistema=" + $sistema)) }
  else { Show-List (Get-InfoAula '/comandos') }
}

function Show-Atalhos([string]$sistema) {
  if ($sistema) { Show-List (Get-InfoAula ("/atalhos?sistema=" + $sistema)) }
  else { Show-List (Get-InfoAula '/atalhos') }
}

function Show-Buscar([string]$termo) {
  $q = [uri]::EscapeDataString($termo)
  Show-List (Get-InfoAula ("/items?q=" + $q))
}

function Show-Dica { Show-One (Get-InfoAula '/dica') }

function Show-Exercicio([string]$nivel) {
  $n = [uri]::EscapeDataString($nivel)
  Show-One (Get-InfoAula ("/exercicio?nivel=" + $n))
}

function Show-Status {
  $h = Get-InfoAula '/health'
  if ($null -eq $h) {
    Write-Host ("Offline: nao alcancei " + $API + ". Confira a URL do servidor da escola.") -ForegroundColor Red
    return
  }
  Write-Host ("API: OK (versao " + $h.version + ")") -ForegroundColor Green
  Write-Host ("URL: " + $API)
  $cats = Get-InfoAula '/categories'
  if ($cats) {
    $total = ($cats | Measure-Object -Property count -Sum).Sum
    Write-Host ("Itens: " + $total)
    foreach ($c in $cats) { Write-Host ("  - " + $c.category + ": " + $c.count) }
  }
}

function Show-Categorias {
  $cats = Get-InfoAula '/categories'
  if ($null -eq $cats) { Write-Host "Falha ao falar com o servidor." -ForegroundColor Red; return }
  foreach ($c in $cats) { Write-Host ($c.category + ": " + $c.count) }
}

function Show-Menu {
  while ($true) {
    Write-Host ""
    Write-Host "==============================" -ForegroundColor Cyan
    Write-Host "  InfoAula - menu interativo" -ForegroundColor Cyan
    Write-Host "==============================" -ForegroundColor Cyan
    Write-Host "  1) Ver comandos (Linux/Windows)"
    Write-Host "  2) Ver atalhos de teclado"
    Write-Host "  3) Buscar qualquer coisa"
    Write-Host "  4) Dica rapida"
    Write-Host "  5) Exercicio (iniciante)"
    Write-Host "  6) Status do servidor"
    Write-Host "  7) Categorias"
    Write-Host "  0) Sair"
    $c = Read-Host "  Escolha"
    switch ("$c".Trim()) {
      '0' { Write-Host "Ate logo!" -ForegroundColor DarkGray; return }
      '1' { Show-Comandos $null }
      '2' { Show-Atalhos $null }
      '3' {
        $termo = Read-Host "  Buscar por"
        if ("$termo".Trim()) { Show-Buscar $termo.Trim() }
      }
      '4' { Show-Dica }
      '5' { Show-Exercicio 'iniciante' }
      '6' { Show-Status }
      '7' { Show-Categorias }
      default { Write-Host "  Opcao invalida. Tente 0 a 7." -ForegroundColor Yellow }
    }
  }
}

# ---------------- dispatch ----------------
$comando = ''
if ($args -and $args.Count -gt 0) { $comando = "$($args[0])".ToLower() }

if (-not $comando) {
  Show-Menu
} else {
  $resto = @()
  if ($args.Count -gt 1) { $resto = $args[1..($args.Count - 1)] }
  switch ($comando) {
    { $_ -in 'ajuda', 'help', '--help', '-h' } {
      Write-Host "Uso: infoaula.ps1 [status|comandos [so]|atalhos [so]|buscar <texto>|dica|exercicio [--nivel N]|categorias]"
      Write-Host "Sem argumentos abre o menu. Defina INFOAULA_URL para mudar o servidor."
    }
    'status' { Show-Status }
    'comandos' { if ($resto.Count -ge 1) { Show-Comandos $resto[0] } else { Show-Comandos $null } }
    'atalhos' { if ($resto.Count -ge 1) { Show-Atalhos $resto[0] } else { Show-Atalhos $null } }
    { $_ -in 'buscar', 'busca', 'search' } {
      if ($resto.Count -ge 1) { Show-Buscar ($resto -join ' ') }
      else { Write-Host 'Uso: infoaula.ps1 buscar "copiar arquivo"' -ForegroundColor Yellow }
    }
    'dica' { Show-Dica }
    'exercicio' {
      $nivel = 'iniciante'
      if ($resto.Count -ge 2 -and $resto[0] -eq '--nivel') { $nivel = $resto[1] }
      elseif ($resto.Count -ge 1 -and $resto[0] -ne '--nivel') { $nivel = $resto[0] }
      Show-Exercicio $nivel
    }
    'categorias' { Show-Categorias }
    default { Write-Host ("Comando desconhecido: " + $comando + " (tente ajuda)") -ForegroundColor Yellow }
  }
}
