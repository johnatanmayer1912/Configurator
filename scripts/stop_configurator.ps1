# Stop NX-OS Configuration Authority (port 9000)
$ErrorActionPreference = "Stop"
$port = 9000

$pids = @()
netstat -ano | ForEach-Object {
    if ($_ -match "LISTENING" -and $_ -match ":$port\s") {
        $parts = $_ -split "\s+" | Where-Object { $_ -ne "" }
        if ($parts.Count -ge 1) {
            $pid = [int]$parts[-1]
            if ($pid -gt 0) { $pids += $pid }
        }
    }
}
$pids = $pids | Select-Object -Unique

if (-not $pids) {
    Write-Host "No process listening on port $port."
    exit 0
}

foreach ($pid in $pids) {
    Write-Host "Stopping PID $pid ..."
    taskkill /PID $pid /T /F | Out-Null
}

$pidFile = Join-Path (Split-Path $PSScriptRoot -Parent) "logs\nxos_configurator.pid"
if (Test-Path $pidFile) { Remove-Item $pidFile -Force }

Write-Host "Stopped NX-OS Configurator on port $port."
