# Instalador do Dofus LabTech: servidor local (StarLoco 1.39.8) + Mundo LabTech + painel.
# Nao baixa nem distribui o jogo: o cliente Dofus Retro 1.39.8 precisa estar em server\client-starloco.
# Pode rodar de novo quantas vezes quiser: cada passo pula o que ja esta pronto.
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$root = Split-Path -Parent $PSScriptRoot
$rt = Join-Path $root 'runtime'
$srv = Join-Path $root 'server'
$client = Join-Path $srv 'client-starloco\resources\app\retroclient'

$STARLOCO = @{
    game  = @{ url = 'https://github.com/StarLoco/StarLoco-Game.git';  commit = '038dd961324d1fc80bb0b4d38b32b9f9da2b38e7' }
    login = @{ url = 'https://github.com/StarLoco/StarLoco-Login.git'; commit = 'b2b72861dbdb6f123d1e1a4b120a8e7a57aab178' }
    web   = @{ url = 'https://github.com/StarLoco/StarLoco-Web.git';   commit = '9a94d3f6f2568d143cbbc827989beb7f7dd04458' }
}
$DOWNLOADS = @(
    @{ nome = 'jdk21';   url = 'https://corretto.aws/downloads/latest/amazon-corretto-21-x64-windows-jdk.zip' },
    @{ nome = 'mariadb'; url = 'https://archive.mariadb.org/mariadb-11.4.3/winx64-packages/mariadb-11.4.3-winx64.zip' },
    @{ nome = 'gradle';  url = 'https://services.gradle.org/distributions/gradle-8.10.2-bin.zip' },
    @{ nome = 'ffdec';   url = 'https://github.com/jindrapetrik/jpexs-decompiler/releases/download/version26.3.0/ffdec_26.3.0.zip' }
)

function Passo($t) { Write-Host "`n== $t" -ForegroundColor Cyan }
function Falha($t) { Write-Host "`nERRO: $t" -ForegroundColor Red; exit 1 }
function Tem($cmd) { [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }

# ------------------------------------------------------------------ 1. programas do sistema
Passo '1/9 Conferindo Git, Python e Node.js'
$falta = @()
if (-not (Tem 'git')) { $falta += 'Git (winget install Git.Git)' }
if (-not (Tem 'python')) { $falta += 'Python 3.10+ (winget install Python.Python.3.12)' }
if (Tem 'node') {
    $v = [version]((node --version).TrimStart('v'))
    if ($v -lt [version]'22.5.0') { $falta += "Node.js 22.5+ (voce tem $v; winget install OpenJS.NodeJS.LTS)" }
} else { $falta += 'Node.js 22.5+ (winget install OpenJS.NodeJS.LTS)' }
if ($falta) { Falha ("instale antes e abra um terminal novo:`n  - " + ($falta -join "`n  - ")) }
python -c "import PIL" 2>$null
if ($LASTEXITCODE -ne 0) { Write-Host '   instalando Pillow (Python)'; python -m pip install --user --quiet pillow }

# ------------------------------------------------------------------ 2. cliente do jogo (fornecido pelo usuario)
Passo '2/9 Conferindo o cliente Dofus Retro 1.39.8'
foreach ($f in 'loader.swf', 'Dofus.exe', 'config.xml', 'clips\sprites\10.swf', 'clips\artworks\breeds\back\1.swf') {
    if (-not (Test-Path (Join-Path $client $f))) {
        Falha "cliente nao encontrado ou incompleto (falta $f).`n  Coloque a pasta do cliente Dofus Retro 1.39.8 em:`n  $srv\client-starloco`n  de modo que exista: $client\loader.swf"
    }
}
$ver = python -c "import zlib,sys; d=open(sys.argv[1],'rb').read(); b=zlib.decompress(d[8:]) if d[:3]==b'CWS' else d; print('ok' if b'31/01/2023 11:30 UTC+1' in b else 'outra')" (Join-Path $client 'loader.swf')
if ($ver -ne 'ok') { Write-Host '   AVISO: o loader.swf nao parece ser o da versao 1.39.8 (31/01/2023). Os patches podem nao encaixar.' -ForegroundColor Yellow }
# o cliente busca os arquivos de dados (lang) no painel local, porta 8080
$cfg = Join-Path $client 'config.xml'
$xml = [IO.File]::ReadAllText($cfg)
$novo = [regex]::Replace($xml, '<connserver name="([^"]*)" ip="[^"]*" port="\d+"', '<connserver name="$1" ip="127.0.0.1" port="450"')
$novo = [regex]::Replace($novo, '<dataserver url="http://[^"]*" priority="3"', '<dataserver url="http://127.0.0.1:8080/" priority="3"')
if ($novo -ne $xml) { [IO.File]::WriteAllText($cfg, $novo); Write-Host '   config.xml apontado para o servidor local' }

# ------------------------------------------------------------------ 3. runtimes portateis
Passo '3/9 Baixando Java 21, MariaDB, Gradle e JPEXS (so na primeira vez)'
New-Item -ItemType Directory -Force (Join-Path $rt 'dl') | Out-Null
foreach ($d in $DOWNLOADS) {
    $dest = Join-Path $rt $d.nome
    if (Test-Path $dest) { continue }
    $zip = Join-Path $rt "dl\$($d.nome).zip"
    if (-not (Test-Path $zip)) { Write-Host "   baixando $($d.url)"; Invoke-WebRequest $d.url -OutFile $zip -UseBasicParsing }
    $tmp = Join-Path $rt 'work'
    if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
    Expand-Archive $zip $tmp
    $itens = @(Get-ChildItem $tmp)
    if ($itens.Count -eq 1 -and $itens[0].PSIsContainer) { Move-Item $itens[0].FullName $dest } else { Move-Item $tmp $dest }
    if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
    Write-Host "   $($d.nome) pronto"
}
$env:JAVA_HOME = Join-Path $rt 'jdk21'
$env:GRADLE_USER_HOME = Join-Path $rt 'gradle-home'
$mysql = Join-Path $rt 'mariadb\bin\mariadb.exe'

# ------------------------------------------------------------------ 4. StarLoco + nossas mudancas
Passo '4/9 Baixando o StarLoco (servidor) e aplicando as mudancas do LabTech'
foreach ($nome in 'game', 'login', 'web') {
    $dir = Join-Path $srv $nome
    if (-not (Test-Path (Join-Path $dir '.git'))) {
        git clone --quiet $STARLOCO[$nome].url $dir
        if ($LASTEXITCODE) { Falha "nao consegui clonar $($STARLOCO[$nome].url)" }
        git -C $dir -c core.autocrlf=false checkout --quiet $STARLOCO[$nome].commit
    }
}
$game = Join-Path $srv 'game'
if (-not (Test-Path (Join-Path $game 'src\org\starloco\locos\panel\PanelBridge.java'))) {
    git -C $game -c core.autocrlf=false apply --whitespace=nowarn (Join-Path $root 'patches\starloco-game.patch')
    if ($LASTEXITCODE) { Falha 'o patch do servidor nao encaixou (versao do StarLoco diferente?)' }
    Write-Host '   patch aplicado'
}
Copy-Item (Join-Path $root 'config\game.config.properties') (Join-Path $game 'game.config.properties') -Force
Copy-Item (Join-Path $root 'config\login.config.properties') (Join-Path $srv 'login\login.config.properties') -Force

# ------------------------------------------------------------------ 5. banco de dados
Passo '5/9 Criando o banco de dados (MariaDB)'
$data = Join-Path $rt 'mariadb-data'
if (-not (Test-Path (Join-Path $data 'mysql'))) {
    & (Join-Path $rt 'mariadb\bin\mariadb-install-db.exe') "--datadir=$data" --port=3306 | Out-Null
}
$ini = @"
[mysqld]
datadir=$($data.Replace('\', '/'))
port=3306
bind-address=127.0.0.1
max_allowed_packet=256M
innodb_buffer_pool_size=512M
character-set-server=utf8mb4
sql_mode=NO_ENGINE_SUBSTITUTION
[client]
port=3306
plugin-dir=$((Join-Path $rt 'mariadb\lib\plugin').Replace('\', '/'))
"@
[IO.File]::WriteAllText((Join-Path $data 'my.ini'), $ini)
function PortaAberta($p) { try { $c = New-Object Net.Sockets.TcpClient; $c.Connect('127.0.0.1', $p); $c.Close(); $true } catch { $false } }
$ligueiBanco = $false
if (-not (PortaAberta 3306)) {
    Start-Process -FilePath (Join-Path $rt 'mariadb\bin\mysqld.exe') -ArgumentList "--defaults-file=`"$(Join-Path $data 'my.ini')`"" -WindowStyle Hidden
    for ($i = 0; $i -lt 60 -and -not (PortaAberta 3306); $i++) { Start-Sleep -Milliseconds 500 }
    if (-not (PortaAberta 3306)) { Falha 'o MariaDB nao ligou' }
    $ligueiBanco = $true
}
$existe = & $mysql -u root -N -B -e "SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name='starloco_game'"
if ($existe -eq '0') {
    foreach ($sql in Get-ChildItem (Join-Path $game 'db-init') -Filter '*.sql' | Sort-Object Name) {
        Write-Host "   importando $($sql.Name)"
        cmd /c "`"$mysql`" -u root --default-character-set=utf8mb4 < `"$($sql.FullName)`""
        if ($LASTEXITCODE) { Falha "erro ao importar $($sql.Name)" }
    }
}

# ------------------------------------------------------------------ 6. compilar o servidor
Passo '6/9 Compilando login e jogo (Gradle; a primeira vez baixa as dependencias)'
$gradle = Join-Path $rt 'gradle\bin\gradle.bat'
foreach ($nome in 'login', 'game') {
    Push-Location (Join-Path $srv $nome)
    & $gradle jar -q
    $ok = $LASTEXITCODE -eq 0
    Pop-Location
    if (-not $ok) { Falha "a compilacao do $nome falhou" }
}

# ------------------------------------------------------------------ 7. painel
Passo '7/9 Instalando o painel (Node.js)'
Push-Location (Join-Path $root 'panel')
npm install --silent --no-audit --no-fund
$ok = $LASTEXITCODE -eq 0
if ($ok) {
    node -e "const g=require('./lib/game'); g.createAccounts('conta', 8, '123').then(c=>{console.log('   contas criadas: '+(c.join(', ')||'nenhuma (ja existiam)')); return g.pool.end();}).catch(e=>{console.error(e.message); process.exit(1);})"
    $ok = $LASTEXITCODE -eq 0
}
Pop-Location
if (-not $ok) { Falha 'nao consegui instalar o painel ou criar as contas' }

# ------------------------------------------------------------------ 8. Mundo LabTech
Passo '8/9 Gerando o Mundo LabTech e a classe 13 no seu cliente (alguns minutos)'
# o build le os textos originais do jogo (classes, itens, mapas, monstros, feiticos) extraidos do cliente
python (Join-Path $root 'panel\tools\extrair_lang.py')
if ($LASTEXITCODE) { Falha 'nao consegui extrair os textos do jogo' }
python (Join-Path $root 'panel\tools\labtech\build.py')
if ($LASTEXITCODE) { Falha 'o build do Mundo LabTech falhou' }
python (Join-Path $root 'panel\tools\labtech\menuadmin_pt.py')
python (Join-Path $root 'panel\tools\extrair_lang.py')
if ($LASTEXITCODE) { Falha 'nao consegui extrair os textos do painel' }

# ------------------------------------------------------------------ 9. fim
Passo '9/9 Pronto'
if ($ligueiBanco) { & (Join-Path $rt 'mariadb\bin\mariadb-admin.exe') -u root shutdown }
Write-Host @"

Tudo instalado. Agora:
  1. De dois cliques em "Iniciar Dofus.bat" (liga banco, login, jogo e abre o painel).
  2. Espere o painel mostrar Banco, Login e Jogo em verde (1 a 2 minutos).
  3. Abra o jogo: $client\Dofus.exe
  4. Entre com conta1 ... conta8, senha 123, servidor Eratz.
"@ -ForegroundColor Green
