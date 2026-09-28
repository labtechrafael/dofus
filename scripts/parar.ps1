$panel = "http://127.0.0.1:8080"
try {
    Write-Host "Salvando e desligando o servidor (pode levar ate 1 minuto)..."
    Invoke-RestMethod -Method Post "$panel/api/server/all/stop" -TimeoutSec 120 | Format-List
} catch { Write-Host "Painel nao respondeu: $($_.Exception.Message)" }
Get-CimInstance Win32_Process -Filter "Name='node.exe'" | Where-Object { $_.CommandLine -like '*server.js*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
Write-Host "Tudo desligado."
Start-Sleep -Seconds 3
