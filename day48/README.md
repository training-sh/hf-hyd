# Day 48 — Practical Spark data quality

for import statement, spark session creation

```python
import sys
import subprocess

import great_expectations as gx
from pyspark.sql import types as T

import pyspark
from pyspark.sql import SparkSession, Window, functions as F

active = SparkSession.getActiveSession()
 
spark = (SparkSession.builder.master("local[2]").appName("GE")
    .getOrCreate())
spark.sparkContext.setLogLevel("ERROR")
 
print("Spark:", spark.version)

```


Twelve instructor-led notebooks covering ingestion, schema contracts, record validation, business rules, quarantine, reconciliation, exception handling, quality gates and monitoring. **S3/EMR is the primary deployment route**, with an HDFS route for `student@spark-host` and an optional AWS Glue notebook. No Hive catalog, crawler or persistent SQL table is required.

## Start here

1. Choose a dedicated storage prefix and configure `DQ_BASE_PATH` in the Spark driver environment, **or edit the configuration cell in each notebook**.
2. Before class, upload the existing `data/raw` folder using [Sample data setup](docs/DATA_SETUP.md). Both clean and invalid examples are already supplied. No generator needs to run during class.
3. Open [00_setup_and_seed.ipynb](notebooks/00_setup_and_seed.ipynb) to check the uploaded files. It only reads the inputs.
4. Work through 01–10. After setup, each notebook is self-contained: it does not rely on Python variables from a previous notebook.
5. Run 11 in a Glue Spark session when demonstrating AWS-native Data Quality.

| Environment | Example `DQ_BASE_PATH` | Requirements |
|---|---|---|
| EMR on S3 | `s3://YOUR-BUCKET/training/order-quality/your-name` | Spark-enabled EMR and an execution role allowed to use the prefix |
| Standard Spark with S3A | `s3a://YOUR-BUCKET/training/order-quality/your-name` | Compatible Hadoop S3A connector, AWS SDK and role/provider chain |
| Spark VM HDFS | `hdfs:///user/student/order-quality` | Hadoop configuration available to Spark |
| Linux local practice | `file:///tmp/order-quality` | Local Spark 3.5 kernel and Java 11/17 |
| AWS Glue | `s3://YOUR-BUCKET/training/order-quality/your-name` | Glue Spark session and an execution role |

`YOUR-BUCKET` is deliberately blocked until replaced. No account names, keys or credentials are embedded. Changing paths does not install S3 connectors or provision AWS infrastructure. Prefer the cloud platform’s supplied connectors and PySpark distribution.

The configuration cell is duplicated intentionally to keep notebooks portable into remote kernels without a project upload. [config/config.py](config/config.py) is a reference for script-based use; notebooks do not automatically import it. Set the same base path in every notebook. `DQ_PROCESSING_DATE` uses a fixed sample date matching the fixtures. Keep it aligned with the input scenarios.

## Lesson sequence

| Notebook | Main demonstration | Suggested minutes |
|---|---|---:|
| [00 Setup](notebooks/00_setup_and_seed.ipynb) | Check prepared sample files; storage choices | 15 |
| [01 Ingestion](notebooks/01_ingestion_quality.ipynb) | PERMISSIVE, DROPMALFORMED, FAILFAST; corrupt CSV/JSON; inference | 30 |
| [02 Schema](notebooks/02_schema_validation.ipynb) | Missing/unexpected columns, types, nested drift, nullable expectations | 25 |
| [03 Record validation](notebooks/03_record_validation.ipynb) | Completeness, casts, ranges, domains, duplicates, formats, dates, foreign keys | 50 |
| [04 Business rules](notebooks/04_business_rules.ipynb) | Shipment/cancellation evidence, item totals, discounts | 25 |
| [05 Reconciliation](notebooks/05_reconciliation.ipynb) | Counts, decimal controls, keys, source identities, group differences, hashes | 35 |
| [06 Exceptions](notebooks/06_exception_handling.ipynb) | Missing/empty input, record/dataset/pipeline scope, write failures | 20 |
| [07 Gates](notebooks/07_quality_gates.ipynb) | Configurable PASS/WARN/FAIL policy and publication stages | 20 |
| [08 Monitoring](notebooks/08_quality_monitoring.ipynb) | Computed metrics, dataset health, 30 synthetic historical runs | 35 |
| [09 Reuse and GX](notebooks/09_reusable_rules_and_gx.ipynb) | Tiny declarative framework, optional GX Core 1.x mapping | 25 |
| [10 Complete pipeline](notebooks/10_end_to_end_pipeline.ipynb) | Dirty batch blocked; clean batch published; audit and artifacts | 45 |
| [11 Glue](notebooks/11_aws_glue_data_quality.ipynb) | DynamicFrames, DQDL, native result audit and explicit gate | 25 |

Allow roughly six hours plus breaks, or split into two sessions. For a short demonstration run 00, 03, 05, 07 and 10.

## Prepared inputs

The ready-to-upload files are in [data/raw](data/raw). Follow [Sample data setup](docs/DATA_SETUP.md) before class. The `orders` folder contains the mixed batch; `clean` contains the valid order and `clean_items` its matching item.

### Optional sample-data maintenance

Only run these commands if you want to change or recreate the supplied files:

```bash
python scripts/generate_data.py
# Optional destination:
python scripts/generate_data.py --output /tmp/order-quality-input
```

[scripts/generate_data.py](scripts/generate_data.py) is the single, readable fixture generator. Generated raw files are included under `data/raw` for inspection. It creates orders, customers, products, order_items, parser edge cases, schema drift and clean controls. Main orders contain **22 physical envelopes**: 21 well-formed JSON lines plus one malformed line. O019 is the valid control within the dirty batch. O001 is duplicated exactly; O002 has a conflicting total. Other rows demonstrate missing/blank values, invalid types/dates, negative/zero quantities, unrealistic volume, unknown references, invalid statuses, late events and business-rule failures.

After changing lesson code, rebuild the notebooks:

```bash
python -m pip install -r requirements-dev.txt
python scripts/build_notebooks.py
```

The builder regenerates all notebooks from visible Markdown and Python source in that script. Edit the builder when you want changes to survive regeneration. Do not rebuild after hand-editing notebooks unless those edits have been copied back.

Upload the prepared files before class, from the lesson directory:

```bash
aws s3 cp data/raw/ s3://YOUR-BUCKET/training/order-quality/your-name/raw/ --recursive
```

Use a fresh input prefix if it already contains Spark part files from an earlier lesson. Mixing those files with the supplied inputs duplicates records.

## Outputs and reruns

All paths derive from the base prefix: `raw`, `bronze`, `silver`, `gold`, `quarantine`, `audit`.

- Notebook 00 reads the prepared inputs without creating or overwriting data.
- Other notebooks write under unique run IDs using `errorifexists`.
- Notebook 10 retains malformed envelopes, original text, filenames, source occurrence IDs and arrays of rule failures.
- Silver in the final exercise is **candidate output**, not consumer-approved data.
- Gold is written only when the gate allows it. A publication manifest under `audit/published/<run_id>` is written last.
- Reconciliation uses one rejected row per source occurrence, never exploded failure counts.
- Audit exists for failed gates too. Native DQ results and simulated history are separate from pipeline run audit.

This small lab is single-writer and batch-oriented. It does not promise an atomic transaction across S3 prefixes. A manifest prevents consumers that honor it from treating unfinished runs as published, but does not create a transaction or deduplicate job retries.

## Environment guides and validation

- [AWS and Spark VM runbook](docs/ENVIRONMENTS.md)
- [Lesson notes, expected results and exercises](docs/LESSON_NOTES.md)
- [Validation record](validation/README.md)

Target: Spark **3.5** with ANSI mode enabled and safe casts. Core code uses DataFrames, Spark SQL and Parquet; it has no Glue dependency. GX is disabled by default and installed separately. The Glue notebook must run inside Glue.

## Source references

Documentation for parser behavior and optional integrations:

- [Spark CSV options](https://spark.apache.org/docs/3.5.7/sql-data-sources-csv.html): parser modes and corrupt-record caveats.
- [Spark JSON options](https://spark.apache.org/docs/3.5.7/sql-data-sources-json.html): schemas and corrupt input.
- [EMR Spark guide](https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-spark.html): platform runtime selection.
- [GX Spark DataFrame connections](https://docs.greatexpectations.io/docs/core/connect_to_data/dataframes/): optional Core 1.x workflow.
- [Glue EvaluateDataQuality](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-api-crawler-pyspark-transforms-EvaluateDataQuality.html) and [DQDL](https://docs.aws.amazon.com/glue/latest/dg/dqdl.html): AWS-native extension.
