# Bootstrap only (design §31): verify uv exists, then hand off to the
# Python CLI, which contains ALL project-generation logic.
$ErrorActionPreference = "Stop"

Set-Location (Join-Path $PSScriptRoot "..")

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: uv is not installed."
    Write-Host ""
    Write-Host "Install uv first:"
    Write-Host ""
    Write-Host '  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"'
    Write-Host ""
    Write-Host "After installation, rerun this script."
    exit 1
}

uv run python-proj-init @args
exit $LASTEXITCODE
