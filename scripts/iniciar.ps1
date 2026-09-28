$root = Split-Path -Parent $PSScriptRoot
$panel = "http://127.0.0.1:8080"

function PanelUp { try { Invoke-RestMethod "$panel/api/status" -TimeoutSec 2 | Out-Null; $true } catch { $false } }

if (-not (PanelUp)) {
    Write-Host "Iniciando o painel..."
    Start-Process -FilePath "node" -ArgumentList "server.js" -WorkingDirectory "$root\panel" -WindowStyle Hidden `
        -RedirectStandardOutput "$root\logs\panel.log" -RedirectStandardError "$root\logs\panel-erros.log"
    for ($i = 0; $i -lt 30 -and -not (PanelUp); $i++) { Start-Sleep -Milliseconds 500 }
}

Write-Host "Ligando banco, login e jogo..."
$r = Invoke-RestMethod -Method Post "$panel/api/server/all/start" -TimeoutSec 120
$r | Format-List
Start-Process $panel
Write-Host "Painel aberto no navegador. O jogo leva 1-2 minutos para carregar."
Start-Sleep -Seconds 3
