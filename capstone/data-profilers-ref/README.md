# Student data profiler bundle

Extract this ZIP, then start Jupyter from the extracted folder. Keep data_profilers
and datasets alongside the notebooks so imports and sample paths resolve.

Read [the complete profiler guide](data_profilers/README.md) for all audit tables,
function examples, Great Expectations rules, foreachBatch streaming and audit SQL.
Full signatures are in data_profilers/API.md.

## Included notebooks

- schema_drifting_csv_orders.ipynb
- schema_drifting_jsonl_order_lines.ipynb
- schema_drifting_parquet_purchases.ipynb

Each notebook contains ordinary Spark reading and independently optional corrupt
record, schema drift, exploration and Great Expectations cells. The included
complex Olist/Odoo sample datasets contain original and deliberately altered
teaching copies. Their source IDs and hashes are in datasets/olist-samples.json.

## Environment

Requires configured Spark, Java and a compatible Iceberg runtime JAR. Tested:
Spark/PySpark 3.5.7, Java 17, Iceberg 1.9.2 and Great Expectations 1.24.0.
GX is optional when its notebook flag is disabled. It is not required by the
other profiler modules. Set ICEBERG_SPARK_RUNTIME_JAR to your Spark 3.5/Scala 2.12
compatible Iceberg runtime JAR before opening Jupyter.

Example in a Linux Spark teaching environment:

```bash
export ICEBERG_SPARK_RUNTIME_JAR=/path/to/iceberg-spark-runtime-3.5_2.12-1.9.2.jar
jupyter lab
```

Use the three notebooks in a configured PySpark kernel. Profilers write only
Iceberg audit/measure tables; they do not automatically repair or quarantine
business records. Existing examples configure datalake as a local Hadoop catalog.
Remote source URIs require the appropriate Hadoop connectors and credentials.

## Streaming example

stream_foreachbatch_example.py is a runnable example using parser profiling,
exploration and actual GX inside foreachBatch. It creates isolated synthetic
inputs and validates checkpoint resumption and audit outputs. In the configured
Linux Spark/Iceberg environment:

```bash
export PYSPARK_SUBMIT_ARGS="--driver-memory 512m --jars $ICEBERG_SPARK_RUNTIME_JAR pyspark-shell"
STREAM_EXAMPLE_ROOT=./student-output/stream-example python stream_foreachbatch_example.py
```

The function receives the static microbatch DataFrame; file-based schema
inspection remains a separate step. The README shows independent switches and
explains append-only audit behavior on callback retries.

## Verification

The three notebooks passed 10 configurations on aadhi. Additional API tests and
the real streaming example passed. The exploration notebook also passed after
the streaming catalog-refresh fix. Small verification summaries are included in
validation/. These are evidence from the tested environment, not a guarantee
that Spark/Iceberg is already configured on the recipient's machine.

This bundle contains samples and current teaching code; no production database,
full landing zone, credentials, runtime outputs or old conversion pipeline.
