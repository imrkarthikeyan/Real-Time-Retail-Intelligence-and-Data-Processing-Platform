# RetailPulse

RetailPulse is a local, production-style retail data engineering platform demonstrating batch ETL, CDC, streaming, a medallion data lake, orchestration, quality checks, and analytics.

## Quick start (Windows PowerShell)

```powershell
Copy-Item .env.example .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
docker compose up -d postgres kafka seaweedfs seaweedfs-init kafka-connect
.\scripts\health-check.ps1
retailpulse-generate --customers 1000 --products 100 --orders 5000
spark-submit jobs/batch/historical_ingestion.py --input data\generated --lake s3a://retailpulse
streamlit run dashboard\app.py
```

The default generator sizes are configurable using `.env`; smaller sizes are recommended for local smoke tests.

## CDC

Register the Debezium connector after Kafka Connect is healthy:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8083/connectors `
  -ContentType "application/json" -InFile kafka\connectors\postgres-source.json
```

CDC events use Debezium's `payload.op` values: `c` create, `u` update, `d` delete, and `r` snapshot read. The streaming job preserves the operation, source table, timestamp, and row payload.

## Data contracts and guarantees

- Bronze preserves source-shaped data.
- Silver contains validated, normalized records.
- Gold contains business aggregates.
- Invalid records are written to `quarantine`.
- Spark checkpoints provide restart progress, but the Parquet sink does not by itself establish an end-to-end exactly-once claim.

## Test and lint

```powershell
pytest
ruff check .
```

## Resource guidance

Run ELK, Airflow, Hive, and Spark containers only when needed. Generated data targets are configurable and are not performance guarantees.

## SeaweedFS S3 data lake

The data lake is stored in the `retailpulse` SeaweedFS bucket.

```powershell
Copy-Item .env.example .env
docker compose up -d seaweedfs seaweedfs-init
docker compose ps seaweedfs seaweedfs-init
.\scripts\test-seaweedfs.ps1
```

- S3 API from Docker containers: `http://seaweedfs:8333`
- S3 API from Windows: `http://localhost:8333`
- Bronze: `s3a://retailpulse/bronze/orders`
- Silver: `s3a://retailpulse/silver/orders`
- Quarantine: `s3a://retailpulse/quarantine/orders`
- Gold: `s3a://retailpulse/gold/daily_sales`

The default environment values are:

```text
SEAWEED_ACCESS_KEY=retailpulse
SEAWEED_SECRET_KEY=retailpulse_secret
SEAWEED_BUCKET=retailpulse
SEAWEED_S3_ENDPOINT=http://localhost:8333
```
