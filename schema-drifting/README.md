# Schema drift and reconciliation notebooks

This project is an example of detecting schema drift while loading CSV, JSONL and Parquet data into Bronze Iceberg tables, and recording file-level schema drift and reconciliation results in the `datalake.operations.schema_drift` Iceberg table.

Each notebook processes one dataset with a format-specific entry point. All share `schema_drift.py`.

| Notebook | Dataset / format | Main lesson | Files | Correct | Bad |
| --- | --- | --- | ---: | ---: | ---: |
| schema_drifting_csv_orders.ipynb | orders / CSV | Added columns and header-only file | 3 | 4 | 1 |
| schema_drifting_jsonl_order_lines.ipynb | order_lines / JSONL | Type changes and malformed JSON | 2 | 3 | 2 |
| schema_drifting_parquet_purchases.ipynb | purchases / Parquet | Missing nullable column and required null | 2 | 3 | 1 |

Start Jupyter in this directory with the existing Linux Spark/Hadoop environment and a PySpark kernel. A compatible Iceberg runtime must be on the Spark classpath or supplied through `ICEBERG_SPARK_RUNTIME_JAR`. Configuration uses environment variables and project-relative paths.

| Environment variable | Default |
| --- | --- |
| SCHEMA_DRIFT_WAREHOUSE | Project warehouse directory as a file URI |
| SCHEMA_DRIFT_DATA_ROOT | Project datasets directory as a file URI |
| SPARK_MASTER | local[2] |
| ICEBERG_SPARK_RUNTIME_JAR | Existing Spark classpath |

For distributed execution, use shared warehouse, landing and quarantine locations accessible to executors. Runtime user, host and timestamps are captured as audit metadata rather than hard-coded configuration.

## One audit row per file

`datalake.operations.schema_drift` stores schema findings and reconciliation together. A batch of 100 visible data files creates 100 audit rows with a shared `batch_id`. Full `source_file_path` is the file key within a batch; basenames alone are not unique. The inventory includes empty and unreadable files and excludes Hadoop/Spark hidden metadata files beginning with `.` or `_`. The source location should contain only intended incoming data files. Globs are accepted.

Each row includes:

- Run/batch/dataset IDs, source path/name, file size and modification time.
- Expected/actual business schema JSON and drift arrays.
- Source, correct and bad record counts.
- Verified `bronze_written_count` and `quarantine_written_count` read from persisted destinations.
- `reconciliation_status`, `reconciliation_error`, `reconciled_at` and `processing_error`.
- Quarantine location, action/status and runtime execution metadata.

`file_count` is always 1 in a file row and `file_names` contains that one full path. These fields retain compatibility with the earlier audit schema; batch file count comes from the summary query. Unknown counts remain null, including unreadable files. `drift_detected = false` with `actual_schema = null` does not mean a schema was checked: inspect `processing_error` and `status`.

## Good/bad split and verification

`process_csv_batch`, `process_jsonl_batch` and `process_parquet_batch` return `summary`, `file_audits`, `correct_records` and `bad_records`. Input and correct/bad split DataFrames use MEMORY_AND_DISK caching by default. Set `cache_enabled=False` in any processor or notebook configuration to disable it. Each file releases its caches in a finally block, including processing failures. Returned split DataFrames are uncached; later actions on them can recompute the source. Read persisted Bronze/quarantine for subsequent inspection. Good records are aligned to the Bronze contract. Bad records retain original parsed values as `source_record_json` and contain `error_columns` and `error_reasons`; malformed JSONL also retains the original raw line. Notebook displays are limited to 20 sample records plus grouped error totals.

Both destinations carry `_batch_id`, `_run_id` and `_source_file`. Bronze remains Iceberg; quarantine is separate Parquet, stored under a batch hash and full-source-path hash. `reconcile_file()` reads each destination back with those identifiers and checks:

```text
source count = correct count + bad count
persisted Bronze count = correct count
persisted quarantine count = bad count
```

`RECONCILED` means all three checks succeeded. It can include bad records successfully quarantined. `FAILED` means a write/check failed or counts mismatched. `NOT_VERIFIABLE` means source/split counts are unknown while destination counts could be read. File `status` remains FAILED for unverified ingestion. Reconciliation is a count check, not a content checksum or atomic transaction guarantee.

`write_audit_to_iceberg()` writes one file dictionary automatically after reconciliation. Do not call it again for the same result. Existing audit tables gain missing columns; historical batch audit rows are preserved with null file paths and excluded from the new summary. Old multi-file rows cannot be reconstructed into file audits without reprocessing their inputs. Bronze metadata columns are added to existing tables; old rows have null metadata and are excluded from new batch-scoped checks.

## Batch summary

`create_batch_summary_view()` registers the session view `schema_drift_batch_summary`. It aggregates file audits by run/batch/dataset/target and propagates unknown counts instead of silently treating them as zero. Query it to count batches, rather than counting file audit rows.

The example uses the Hadoop Iceberg catalog. The summary is a temporary Spark view, not a second Iceberg table. `batch_summary_query()` supplies the same SQL for a persistent `operations.schema_drift_batch_summary` view in a catalog that supports view creation. The view can be re-created in a new session from the persisted Iceberg audit table.

## Policies and boundaries

Schemas are inspected per file before any merging. Added columns are audited/dropped; missing nullable columns are null-filled; missing/null required fields are quarantined; failed scalar casts are quarantined. Nested type mismatches are reported at the top-level field and reject records. Spark scalar casts can round/truncate numeric values: add business validation when lossless conversion is required.

JSONL is parsed line by line with malformed records preserved. CSV uses PERMISSIVE parsing and retains parser-detected malformed records. Spark CSV does not label every token-count mismatch as corrupt: missing values may be null-filled and surplus tokens can be discarded. Strict CSV shape validation is a separate enhancement. These parser semantics are described in the [Spark CSV documentation](https://spark.apache.org/docs/3.5.7/sql-data-sources-csv.html) and [Spark JSON documentation](https://spark.apache.org/docs/3.5.7/sql-data-sources-json.html).

Landing files must remain immutable during the batch: inference, cache eviction or disabling caching can require source rereads. Reconciliation still reads persisted destinations independently of source caches. File size/modification changes during processing are reported as failures; this is not a cryptographic content check. Per-file execution creates Spark actions and commits for each file. A production optimization can group compatible files while retaining file-level metadata and counts.

Unreadable file failures are audited and later files continue. Inventory, target-contract/setup and audit-table setup failures abort before file ingestion. Audit-write failure stops processing. A successful Bronze write followed by audit failure requires manual reconciliation/recovery: three destinations cannot be committed atomically by this example. Explicitly reusing an audited dataset/batch ID is rejected, but fresh IDs do not deduplicate replayed source files. Concurrent writers require external coordination; the duplicate-ID check is not a lock. This detects schema drift, not statistical distribution drift.

## Execution

The package contains three executable notebooks, the reusable schema_drift.py module and sample datasets. Run notebook cells in order using the configured Spark/Iceberg environment. Each notebook includes record-split checks, persisted-count reconciliation and file/batch audit queries.

Returned DataFrames describe the input split; consult verified written counts to determine what reached each destination. To reproduce the notebook checks, choose a fresh dedicated warehouse and run all three notebooks.
