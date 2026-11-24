# RetailPulse Project Audit

Audit date: 2026-11-23

## Scope

This audit covers the repository sources, Docker Compose configuration, database schema,
Kafka and Debezium configuration, Spark jobs, Airflow DAG, Streamlit dashboard, tests,
scripts, generated data, data lake content, and documentation.

## Verified Baseline

The following checks were actually executed:

- `pytest -q`: 4 tests passed.
- `ruff check .`: passed.
- `docker compose config`: configuration parsed successfully.
- Python package installation: `retailpulse` 0.1.0 is installed in the project virtual environment.
- Dataset generation: 1,000 orders and 2,945 order items were generated.
- Dashboard HTTP smoke check: the Streamlit server returned HTTP 200.
- Docker Compose baseline: no project services were running initially.
- Docker Compose infrastructure attempt: registry pull failures prevented starting
  PostgreSQL, Kafka, Kafka Connect, and MinIO.
- Spark batch attempt: execution reached Spark but failed on the Windows Hadoop native
  library path with `UnsatisfiedLinkError`.

These baseline results are evidence, not a claim that the end-to-end project is working.

## Component Classification

| Component | Classification | Evidence |
|---|---|---|
| Python package structure | IMPLEMENTED BUT NOT TESTED | Package builds and imports, but many modules have little or no coverage. |
| Dataset generator | PARTIALLY IMPLEMENTED | Creates CSV/JSON data and is configurable, but cannot load PostgreSQL and does not validate relationships or clean prior output. |
| PostgreSQL schema | IMPLEMENTED BUT NOT TESTED | Tables, foreign keys, indexes and publication exist, but PostgreSQL runtime replication settings are not explicitly configured. |
| PostgreSQL data loader | NOT IMPLEMENTED | No loader or generator database integration exists. |
| Docker Compose core services | PARTIALLY IMPLEMENTED | PostgreSQL, Kafka, Kafka Connect and MinIO are declared, but Kafka listener configuration and health checks are incomplete. |
| Spark | BROKEN | No Compose Spark service and Windows execution is blocked by Hadoop native-library compatibility. |
| Batch ETL | PARTIALLY IMPLEMENTED | Bronze, Silver, Quarantine and Gold transforms exist, but order totals are inflated when joined to order items, output is local-only, and JSON inventory is not ingested. |
| MinIO integration | NOT IMPLEMENTED | MinIO is only declared as a container; application code has no S3 configuration or object verification. |
| Structured streaming | PARTIALLY IMPLEMENTED | Reads Kafka and writes checkpointed Parquet, but lacks Kafka integration packaging, robust envelope handling, deduplication, watermarks, operation semantics, metrics and graceful output options. |
| Debezium connector | IMPLEMENTED BUT NOT TESTED | Connector JSON exists, but registration/status scripts and actual database-change verification do not exist. |
| Kafka topics | NOT IMPLEMENTED | No topic creation or verification automation exists. |
| Airflow | PARTIALLY IMPLEMENTED | One BashOperator DAG exists, but Airflow is absent from Compose and no retries, quality tasks or maintenance/daily analytics DAGs exist. |
| Hive | NOT IMPLEMENTED | No Hive Metastore, Thrift server or analytical table definitions exist. |
| Data quality | PARTIALLY IMPLEMENTED | One order rule exists, but null, duplicate, schema, foreign-key, timestamp, payment and quantity validation are absent. |
| Quarantine storage | PARTIALLY IMPLEMENTED | Batch code writes invalid orders, but reusable quarantine/report storage and validation reports do not exist. |
| ELK | NOT IMPLEMENTED | No Elasticsearch, Logstash, Kibana or structured application log shipping exists. |
| Streamlit dashboard | PARTIALLY IMPLEMENTED | Gold local Parquet files are read dynamically, but there are no pipeline metadata, customer, inventory, quality or monitoring views. |
| Unit tests | PARTIALLY IMPLEMENTED | Only CDC parsing and simple order validation tests exist. |
| Integration tests | NOT IMPLEMENTED | No real PostgreSQL, Kafka, Debezium, MinIO or Spark integration tests exist. |
| End-to-end tests | NOT IMPLEMENTED | There is no real generator-to-analytics test. |
| Failure recovery tests | NOT IMPLEMENTED | Spark restart, checkpoint, Airflow retry and service recovery are not tested. |
| Performance benchmarks | NOT IMPLEMENTED | No benchmark harness or measured thresholds exist. |
| README and scripts | PARTIALLY IMPLEMENTED | Setup commands exist, but health checks, CDC instructions and local-only Spark assumptions are inaccurate or incomplete. |

## Incomplete Functionality

1. PostgreSQL loading from generated files.
2. Configurable PostgreSQL host and S3/MinIO settings.
3. Kafka listener configuration for broker-to-broker and host access.
4. PostgreSQL logical replication configuration.
5. Kafka, Kafka Connect and MinIO health checks.
6. Spark image/job execution and Windows/Linux compatibility.
7. MinIO Bronze/Silver/Gold writes.
8. Inventory JSON ingestion.
9. Schema validation and reusable quarantine/report generation.
10. CDC registration and status automation.
11. Real CDC integration test cases for insert, update and delete.
12. Structured streaming handling for delete operations and duplicate events.
13. Spark event-time processing, watermarks and streaming metrics.
14. Airflow Compose service and production dependencies.
15. Four missing Airflow DAG workflows.
16. Hive Metastore and external analytical tables.
17. ELK Compose services and structured log forwarding.
18. Dashboard customer, inventory, quality and pipeline views.
19. Integration, end-to-end, recovery and performance tests.

## Incorrect or Missing Configurations

### Docker Compose

- Kafka advertises `localhost:9092` although Debezium Connect and Spark run on the Docker
  network. Kafka clients inside Compose should use `kafka:9092`; host clients should use
  `localhost:9092`.
- PostgreSQL does not explicitly set `wal_level=logical`, making Debezium unreliable or
  ineffective depending on the base image.
- Kafka health is not checked before Kafka Connect starts.
- Kafka Connect and MinIO lack health checks.
- Kafka Connect image, Kafka image and Debezium image are unpinned or registry-dependent.
- Resource limits and restart policies are absent.
- No Spark, Airflow, Hive, Elasticsearch, Logstash or Kibana services exist.
- The Compose validation path is Windows-sensitive and image availability is not guaranteed.

### Application Configuration

- `Settings` has PostgreSQL host/port but no explicit S3, Kafka, MinIO, Airflow or lake settings.
- `.env.example` does not define PostgreSQL host or replication settings.
- The health script probes PostgreSQL over HTTP, but PostgreSQL has no HTTP health endpoint.
- The batch DAG writes to local files rather than object storage.
- The README does not document the verified local Windows limitations.

### Data Flow

- The batch job joins orders to order items and sums `total_amount` again for every item,
  which inflates daily revenue.
- Bronze currently preserves source-shaped CSV orders but does not ingest JSON inventory.
- Silver does not use the reusable quality module.
- MinIO is not used by any application workflow.
- Streaming writes all Kafka payload fields as a generic Parquet structure and does not
  apply a clear operation-aware upsert/delete path.
- Generated CSV/JSON files are not loaded into PostgreSQL.

## Reliability and Performance Issues

- Database and data lake files can retain stale records between runs.
- CSV loading has no file-empty guard and `rows[0]` can raise `IndexError`.
- Batch Spark output mode and invalid record handling are not atomic with the data source.
- Streaming duplicate-event handling is absent.
- Streaming has no explicit event-time column/watermark configuration.
- No streaming metrics endpoint or structured log forwarding exists.
- Batch and streaming Spark jobs are not packaged with all required Kafka/S3 dependencies.
- The Airflow DAG has no retries or quality/data-lake verification dependencies.
- Large default generation values are suitable for a demonstration but not a smoke test.

## Test Gaps

There are no real tests for:

- PostgreSQL record counts or foreign-key relationships.
- Database to Debezium to Kafka CDC events.
- Kafka topic consumption.
- Spark batch output or MinIO Bronze/Silver/Gold objects.
- Spark restart and checkpoint recovery.
- Duplicate or malformed CDC events.
- Airflow parse/DAG execution/task retries.
- Hive queries.
- Dashboard values changing with data.
- ELK log delivery.
- Performance thresholds or failure recovery.

## Documentation Inaccuracies

- The quick-start claim is not complete without infrastructure startup and PostgreSQL loading.
- The health-check script incorrectly sends HTTP probes to PostgreSQL.
- The README implies a working local Spark command without addressing Windows Hadoop issues.
- The claim that Bronze and Silver guarantees exist is not fully evidenced by tested output.
- The batch data contract is incomplete without object-storage integration.
- CDC cannot be tested until PostgreSQL logical replication, registration scripts and running
  Kafka infrastructure are available.

## Implementation Milestones

### Milestone 1: Make infrastructure deterministic

- Replace and pin Compose images.
- Configure dual-listener Kafka.
- Enable PostgreSQL logical replication.
- Add health checks, restart policies, volumes and resource limits.
- Add profiles for core, analytics and observability services.

### Milestone 2: Complete ingestion

- Add PostgreSQL loading with foreign-key-safe ordering.
- Add an idempotent generator/load CLI.
- Add reusable lake configuration and MinIO client utilities.
- Improve CSV/JSON validation and stale-output handling.

### Milestone 3: Complete CDC

- Add connector registration, status and event-inspection scripts.
- Add real database-change integration tests.
- Add PostgreSQL, Kafka and connector health automation.

### Milestone 4: Fix and integrate Spark

- Correct batch revenue aggregation.
- Add schemas for every dataset.
- Implement reusable quality/quarantine logic.
- Configure S3A/MinIO for Bronze, Silver and Gold output.
- Add Spark Compose execution support.

### Milestone 5: Complete streaming

- Package Kafka and S3 dependencies.
- Parse CDC envelopes for insert/update/delete.
- Implement deduplication and event-time watermarks.
- Add checkpoint recovery and structured metrics/logging.

### Milestone 6: Add orchestration and analytics

- Add Airflow and four required DAGs.
- Add Hive Metastore and external tables.
- Add analytical SQL validation.

### Milestone 7: Add monitoring and dashboard integration

- Add ELK Compose services.
- Send structured application logs to Elasticsearch.
- Replace dashboard assumptions with live Gold, quality and pipeline metadata.

### Milestone 8: Add comprehensive tests and documentation

- Add real integration and end-to-end tests.
- Add duplicate, invalid, update, delete and restart tests.
- Add recovery and performance checks.
- Generate implementation, testing, architecture and troubleshooting documentation.
