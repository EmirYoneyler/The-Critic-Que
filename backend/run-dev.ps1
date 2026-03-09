$rootScript = Join-Path (Split-Path -Parent $PSScriptRoot) "run-dev.ps1"

if (-not (Test-Path $rootScript)) {
  Write-Error "Cannot find root run script at $rootScript"
  exit 1
}

& $rootScript
