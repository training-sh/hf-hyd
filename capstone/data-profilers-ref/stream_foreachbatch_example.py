"""Run the DataFrame profilers in foreachBatch; verify checkpoint resumption.

This creates isolated teaching inputs/results. It never reads or changes the
original landing zone. Run from the configured Spark/Iceberg environment:
    python stream_foreachbatch_example.py
"""

import json
import os
from pathlib import Path
import uuid

os.environ.setdefault(
    "PYSPARK_SUBMIT_ARGS", "--driver-memory 512m --jars /opt/iceberg.jar pyspark-shell"
)
from pyspark.sql import SparkSession, functions as F, types as T
from data_profilers.schema_drift import profile_corrupt_records
from data_profilers.exploration import explore_data, write_exploration_to_iceberg


def make_rules():
    import great_expectations as gx

    return [
        gx.expectations.ExpectColumnValuesToNotBeNull(column="order_id"),
        gx.expectations.ExpectColumnValuesToBeBetween(column="quantity", min_value=1),
        gx.expectations.ExpectColumnValuesToBeBetween(column="amount", min_value=0),
    ]


def main():
    root = (
        Path(os.environ.get("STREAM_EXAMPLE_ROOT", "/results/stream-profiler-example"))
        / uuid.uuid4().hex
    )
    landing = root / "landing"
    landing.mkdir(parents=True)
    schema = T.StructType(
        [
            T.StructField("order_id", T.LongType()),
            T.StructField("quantity", T.IntegerType()),
            T.StructField("amount", T.DoubleType()),
            T.StructField("_corrupt_record", T.StringType()),
        ]
    )
    # Good record, business-rule failures, then malformed JSON.
    (landing / "batch01.jsonl").write_text(
        '{"order_id":101,"quantity":2,"amount":20.0}\n'
        '{"order_id":null,"quantity":-2,"amount":-5.0}\n'
        "{broken\n"
    )
    spark = (
        SparkSession.builder.master("local[2]")
        .appName("stream-profiler-example")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.catalog.datalake", "org.apache.iceberg.spark.SparkCatalog")
        .config("spark.sql.catalog.datalake.type", "hadoop")
        .config("spark.sql.catalog.datalake.warehouse", (root / "warehouse").as_uri())
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    enable_corrupt, enable_exploration, enable_gx = True, True, True
    rules = make_rules() if enable_gx else []
    processed = []

    def profile_batch(batch_df, batch_id):
        # A static DataFrame is supplied here; no source file rereading is needed.
        batch_df.cache()
        try:
            rows = batch_df.count()
            if rows == 0:
                return
            batch_spark = batch_df.sparkSession
            run_id = "orders-stream-" + str(batch_id)
            if enable_corrupt:
                profile_corrupt_records(
                    batch_df, dataset_name="orders_stream", run_id=run_id
                )
            if enable_exploration:
                measures = explore_data(
                    batch_spark,
                    batch_df,
                    dataset_name="orders_stream",
                    run_id=run_id,
                    batch_id=str(batch_id),
                    columns=["order_id", "quantity", "amount"],
                    required_columns=["order_id"],
                )
                write_exploration_to_iceberg(batch_spark, measures)
            if enable_gx:
                from data_profilers.great_expectations import profile_expectations

                profile_expectations(
                    batch_df, rules, dataset_name="orders_stream", run_id=run_id
                )
            assert batch_df.is_cached  # Profilers must preserve callback-owned cache.
            processed.append(
                {"batch_id": int(batch_id), "rows": rows, "run_id": run_id}
            )
        finally:
            batch_df.unpersist()

    def process_once():
        stream = (
            spark.readStream.schema(schema)
            .option("mode", "PERMISSIVE")
            .json(landing.as_uri())
            .withColumn("_source_file", F.input_file_name())
        )
        query = (
            stream.writeStream.foreachBatch(profile_batch)
            .option("checkpointLocation", (root / "checkpoint").as_uri())
            .trigger(once=True)
            .start()
        )
        query.awaitTermination()
        # The reader session may cache snapshots written by callback sessions.
        for table in ("corrupt_records", "explorations", "expectation_profiles"):
            spark.catalog.refreshTable("datalake.operations." + table)

    try:
        process_once()
        assert len(processed) == 1 and processed[0]["rows"] == 3
        summary = (
            spark.table("datalake.operations.corrupt_records")
            .where("status = 'SUMMARY'")
            .first()
        )
        assert json.loads(summary.details_json)["corrupt_count"] == 1
        assert (
            spark.table("datalake.operations.corrupt_records")
            .where("status = 'PARSER_REJECTED_RECORD'")
            .count()
            == 1
        )
        assert (
            spark.table("datalake.operations.expectation_profiles")
            .where("status = 'FAILED'")
            .count()
            == 1
        )
        assert (
            spark.table("datalake.operations.expectation_profiles")
            .where("status = 'RULE_FAILED'")
            .count()
            == 3
        )
        assert spark.table("datalake.operations.explorations").count() > 0

        # Same checkpoint + no new files: callback must not process the old file again.
        before = len(processed)
        process_once()
        assert len(processed) == before

        # Same checkpoint + one new file: only this new record is processed.
        (landing / "batch02.jsonl").write_text(
            '{"order_id":102,"quantity":1,"amount":10.0}\n'
        )
        process_once()
        assert len(processed) == 2 and processed[1]["rows"] == 1
        assert (
            spark.table("datalake.operations.expectation_profiles")
            .where("status = 'PASSED'")
            .count()
            == 1
        )
        report = {
            "passed": True,
            "processed_batches": processed,
            "restart_without_new_files_processed_batches": 0,
            "first_batch_corrupt_records": 1,
            "first_batch_failed_gx_rules": 3,
            "new_batch_gx_passed": True,
        }
        (root / "verification.json").write_text(json.dumps(report, indent=2))
        print("PASS STREAM PROFILERS " + json.dumps(report), flush=True)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
