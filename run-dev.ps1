$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendPath = Join-Path $projectRoot "backend"
$frontendPath = Join-Path $projectRoot "backend\src\Frontend"

Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$backendPath'; python -m src.main"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$frontendPath'; npm install; npm run dev"

Write-Output "Started backend and frontend in separate PowerShell windows."
