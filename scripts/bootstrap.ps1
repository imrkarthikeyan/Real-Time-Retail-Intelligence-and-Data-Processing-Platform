$ErrorActionPreference = "Stop"
if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env" }
docker compose up -d postgres kafka seaweedfs kafka-connect
Write-Host "Core services started. Run scripts/health-check.ps1 to verify them."
