$ErrorActionPreference = "Stop"
$ErrorActionPreference = "Continue"

docker compose exec -T postgres pg_isready -U "$env:POSTGRES_USER" -d "$env:POSTGRES_DB"
if ($LASTEXITCODE -eq 0) {
    Write-Host "PostgreSQL: healthy"
} else {
    Write-Warning "PostgreSQL: unavailable"
}

try {
    Invoke-WebRequest -Uri "http://localhost:8083/" -UseBasicParsing -TimeoutSec 5 | Out-Null
    Write-Host "Kafka Connect: healthy"
} catch {
    Write-Warning "Kafka Connect: unavailable ($($_.Exception.Message))"
}

try {
    Invoke-WebRequest -Uri "http://localhost:8333/" -UseBasicParsing -TimeoutSec 5 | Out-Null
    Write-Host "SeaweedFS S3: healthy"
} catch {
    Write-Warning "SeaweedFS S3: unavailable ($($_.Exception.Message))"
}
