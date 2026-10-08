# Landing-to-Bronze schema drift example

This project detects schema drift during landing-to-Bronze file processing. Correct and bad records retain the source file format. Only file-level audit metadata is stored in the `datalake.operations.schema_drift` Iceberg table, using Parquet data files.

| Landing format | Correct records in Bronze | Bad records in quarantine | Audit |
| --- | --- | --- | --- |
| CSV | CSV files | CSV files | Iceberg / Parquet |
| JSONL | JSONL files | JSONL files | Iceberg / Parquet |
| Parquet | Parquet files | Parquet files | Iceberg / Parquet |

Format preservation means the output encoding is the same as the input. It does not mean byte-for-byte copying: correct records are aligned to the configured schema, and metadata/error fields are added. Spark JSON output contains one object per line; its part files use the `.json` extension and are valid JSONL.

Three notebooks share `schema_drift.py`:

| Notebook | Main example | Files | Correct | Bad |
| --- | --- | ---: | ---: | ---: |
| schema_drifting_csv_orders.ipynb | Added columns and header-only CSV | 3 | 4 | 1 |
| schema_drifting_jsonl_order_lines.ipynb | Type changes and malformed JSONL | 2 | 3 | 2 |
| schema_drifting_parquet_purchases.ipynb | Missing nullable column and required null | 2 | 3 | 1 |

## Configuration

Run Jupyter from this directory with the configured Linux Spark/Hadoop environment and a PySpark kernel. The compatible Iceberg runtime must be on the classpath or supplied through `ICEBERG_SPARK_RUNTIME_JAR`.

| Environment variable | Default |
| --- | --- |
| SCHEMA_DRIFT_DATA_ROOT | Project datasets directory |
| SCHEMA_DRIFT_BRONZE_ROOT | Project bronze directory |
| SCHEMA_DRIFT_QUARANTINE_ROOT | Project quarantine directory |
| SCHEMA_DRIFT_WAREHOUSE | Project warehouse directory, used only by the audit catalog |
| SPARK_MASTER | local[2] |
| ICEBERG_SPARK_RUNTIME_JAR | Existing Spark classpath |

Defaults are explicit local file URIs. Distributed execution requires shared locations accessible to executors. Each processor requires an `expected_schema` StructType and separate `bronze_path` and `quarantine_path`. `audit_catalog` defaults to datalake. No Bronze Iceberg table is created or consulted. `reader_options` controls landing parsing; optional `output_options` controls the common Bronze/quarantine output encoding and read-back, such as CSV separators and headers.

`process_csv_batch`, `process_jsonl_batch` and `process_parquet_batch` return `summary`, `file_audits`, `correct_records` and `bad_records`. Caching defaults to `cache_enabled=True` with MEMORY_AND_DISK for the input and split DataFrames. Each file releases caches in a finally block. Set the parameter to False to disable caching. Returned frames are uncached; later inspection should read the persisted output paths.

## File outputs and traceability

For each source file, both output roots use a batch hash and full-source-path hash:

```text
bronze/<dataset>/<batch-hash>/<source-path-hash>/part-*.<source-format>
quarantine/<dataset>/<batch-hash>/<source-path-hash>/part-*.<source-format>
```

The file audit stores `bronze_file_path` and `quarantine_file_path`. These identify directories, not single physical part files. Both destinations carry `_batch_id`, `_run_id` and `_source_file`. Empty splits produce no output directory and have a verified written count of zero.

Correct records use the configured schema, drop extra fields and null-fill missing nullable columns. Bad records preserve original values in `source_record_json`, with `error_columns` and `error_reasons`; malformed JSONL also retains the original line. CSV cannot store native arrays/structs, so complex fields become JSON strings inside CSV cells. `read_output()` decodes those fields using the supplied schema. JSONL and Parquet retain native error arrays. Displays show only a limited sample and grouped reason counts.

## Iceberg file audit and reconciliation

`operations.schema_drift` contains one metadata row per visible source file, including empty or unreadable files. All files in an ingestion share a batch ID. A batch of 100 files creates 100 audit rows, not one million rows for one million source records. Full source paths distinguish identical basenames. Hidden Hadoop/Spark metadata files beginning with `.` or `_` are excluded from the inventory.

The row contains source metadata, expected/actual schema JSON, drift findings, input/split counts, both output directory paths, output format, verified written counts, reconciliation status/error and processing errors. `write_audit_to_iceberg()` writes the file audit automatically after verification, with Iceberg's Parquet write format configured explicitly. Do not call it again for the same result.

`reconcile_file()` reads both output directories back in the original format with explicit schemas and checks:

```text
source count = correct count + bad count
persisted Bronze count = correct count
persisted quarantine count = bad count
```

RECONCILED means the counts agree, including successfully quarantined records. FAILED indicates a write/check failure or mismatch. NOT_VERIFIABLE indicates unknown source/split counts. Unreadable source files retain null counts and a processing error; later files continue. The `schema_drift_batch_summary` session view aggregates persisted file audits and preserves unknown totals. `batch_summary_query()` provides equivalent SQL for a catalog-supported permanent view.

Existing audit tables gain missing columns. Historical records from the earlier Iceberg-Bronze design retain their old metadata but are excluded from the new file-output summary because `output_format` is null. Existing Bronze Iceberg tables are not modified or used by this flow.

## Limits and execution checks

Landing files must remain immutable: inference, eviction or disabled caching can cause rereads. Size/modification checks detect changes during processing but are not content checksums. Scalar casts can round/truncate numeric values; add business rules when lossless conversion is needed. Nested type mismatches are reported at the top-level field and quarantined.

CSV uses permissive parsing and captures parser-detected malformed rows. Spark does not classify every token-count mismatch as corrupt; strict CSV shape validation is an additional policy. Malformed JSONL is retained as an error record rather than silently dropped.

Bronze, quarantine and audit writes remain separate operations. Reconciliation detects mismatches but does not make writes atomic or implement automatic recovery. Reusing an explicitly audited dataset/batch ID is rejected; new IDs do not deduplicate source replays. Concurrent runs require external coordination. Source inventory, schema/setup and audit-table failures abort before ingestion; audit-write failure stops the batch. Per-file processing favors clarity; production can group compatible schemas while retaining file-level metadata.

Run notebook cells in order against a fresh warehouse and output roots. Each notebook checks the file audits and persisted counts, and queries the batch summary. No generation or validation helper scripts are required in this package.
