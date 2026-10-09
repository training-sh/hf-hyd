"""Profile parser failures and physical schema drift independently.

These functions return None and write audit findings. They do not repair,
reject, route or write business records. Audit sink failures are raised.
"""

import uuid
from pyspark import StorageLevel
from pyspark.sql import functions as F, types as T
from ._audit import write_audit


def list_source_files(spark, input_path, source_format):
    """Use Hadoop filesystem APIs for local, HDFS and configured S3A paths."""
    suffixes = {
        "csv": (".csv",),
        "jsonl": (".jsonl", ".json"),
        "json": (".json", ".jsonl"),
        "parquet": (".parquet",),
    }[source_format]
    path = spark._jvm.org.apache.hadoop.fs.Path(str(input_path))
    filesystem = path.getFileSystem(spark._jsc.hadoopConfiguration())
    if not filesystem.exists(path):
        raise FileNotFoundError(str(input_path))
    iterator = filesystem.listFiles(path, True)
    paths = []
    while iterator.hasNext():
        item = iterator.next().getPath()
        if item.getName().lower().endswith(suffixes) and not item.getName().startswith(
            ("_", ".")
        ):
            paths.append(item.toString())
    return sorted(paths)


def _field_differences(actual, expected, prefix=""):
    differences = []
    actual_fields = {
        field.name: field for field in actual if field.name != "_corrupt_record"
    }
    expected_fields = {field.name: field for field in expected}
    for name in sorted(actual_fields.keys() | expected_fields.keys()):
        location = prefix + name
        left, right = actual_fields.get(name), expected_fields.get(name)
        if left is None:
            differences.append({"field": location, "change": "MISSING_FIELD"})
        elif right is None:
            differences.append(
                {
                    "field": location,
                    "change": "ADDED_FIELD",
                    "actual": left.dataType.simpleString(),
                }
            )
        elif isinstance(left.dataType, T.StructType) and isinstance(
            right.dataType, T.StructType
        ):
            differences.extend(
                _field_differences(left.dataType, right.dataType, location + ".")
            )
        elif left.dataType.simpleString() != right.dataType.simpleString():
            differences.append(
                {
                    "field": location,
                    "change": "TYPE_DIFFERENCE",
                    "actual": left.dataType.simpleString(),
                    "expected": right.dataType.simpleString(),
                }
            )
    return differences


def profile_corrupt_records(
    df,
    *,
    corrupt_column="_corrupt_record",
    source_file_column="_source_file",
    reason_column=None,
    filter_condition=None,
    dataset_name=None,
    run_id=None,
    audit_table="datalake.operations.corrupt_records"
):
    """Log raw parser failures and a summary. An optional filter scopes profiling.

    Spark supplies raw text, not the precise parser reason. A caller-provided
    reason column is optional. Missing corrupt columns are logged as unavailable.
    Caller-owned caches remain cached; only caches created here are released.
    """
    if df.isStreaming:
        raise ValueError(
            "Call this function on the static DataFrame inside foreachBatch."
        )
    run_id = run_id or str(uuid.uuid4())
    selected = df.filter(filter_condition) if filter_condition is not None else df
    owns_cache = selected.storageLevel == StorageLevel.NONE
    if owns_cache:
        selected.persist(StorageLevel.MEMORY_AND_DISK)
    try:
        count = (
            selected.count()
        )  # Materialize all columns before querying only corrupt text.
        base = {
            "run_id": run_id,
            "dataset_name": dataset_name,
            "profile_kind": "CORRUPT_RECORDS",
        }
        if corrupt_column not in selected.columns:
            write_audit(
                df.sparkSession,
                [
                    dict(
                        base,
                        status="CAPTURE_UNAVAILABLE",
                        details={
                            "row_count": count,
                            "corrupt_count": None,
                            "corrupt_column": corrupt_column,
                        },
                    )
                ],
                audit_table,
            )
            return None
        if reason_column is not None and reason_column not in selected.columns:
            raise ValueError("reason_column does not exist: " + reason_column)
        bad = selected.filter(F.col(corrupt_column).isNotNull())
        bad_count = bad.count()
        write_audit(
            df.sparkSession,
            [
                dict(
                    base,
                    status="SUMMARY",
                    details={"row_count": count, "corrupt_count": bad_count},
                )
            ],
            audit_table,
        )
        # Stream rows in bounded audit batches. Avoid collecting all
        # malformed records in driver memory.
        pending = []
        columns = [corrupt_column]
        for column in (source_file_column, reason_column):
            if column and column in selected.columns and column not in columns:
                columns.append(column)
        for row in bad.select(*columns).toLocalIterator():
            values = row.asDict()
            pending.append(
                dict(
                    base,
                    source_file=values.get(source_file_column),
                    status="PARSER_REJECTED_RECORD",
                    details={
                        "raw_record": values[corrupt_column],
                        "reason": (
                            values.get(reason_column)
                            if reason_column
                            else (
                                "Spark parser rejected this record; "
                                "exact reason unavailable"
                            )
                        ),
                    },
                )
            )
            if len(pending) >= 500:
                write_audit(df.sparkSession, pending, audit_table)
                pending = []
        if pending:
            write_audit(df.sparkSession, pending, audit_table)
    finally:
        if owns_cache:
            selected.unpersist()
    return None


def _inspect_file(spark, path, source_format, expected_schema, reader_options):
    reader = spark.read.options(**reader_options).option("mode", "PERMISSIVE")
    if source_format == "csv":
        reader = (
            reader.option("header", True)
            .option("inferSchema", True)
            .option("escape", '"')
            .option("multiLine", True)
        )
        inferred = reader.csv(path)
        capture_schema = T.StructType(
            list(inferred.schema.fields)
            + [T.StructField("_corrupt_record", T.StringType())]
        )
        frame = reader.schema(capture_schema).csv(path)
    elif source_format in ("json", "jsonl"):
        frame = reader.json(path)
    else:
        frame = reader.parquet(path)
    owns_cache = frame.storageLevel == StorageLevel.NONE
    if owns_cache:
        frame.persist(StorageLevel.MEMORY_AND_DISK)
    try:
        count = frame.count()
        hadoop_path = spark._jvm.org.apache.hadoop.fs.Path(path)
        status = hadoop_path.getFileSystem(
            spark._jsc.hadoopConfiguration()
        ).getFileStatus(hadoop_path)
        corrupt_count = (
            frame.filter(F.col("_corrupt_record").isNotNull()).count()
            if "_corrupt_record" in frame.columns
            else None
        )
        return {
            "row_count": count,
            "corrupt_count": corrupt_count,
            "source_size_bytes": status.getLen(),
            "source_modified_epoch_ms": status.getModificationTime(),
            "corrupt_capture": (
                "AVAILABLE"
                if "_corrupt_record" in frame.columns
                else "NOT_EXPOSED_BY_READER"
            ),
            "actual_schema": frame.schema.jsonValue(),
            "expected_schema": expected_schema.jsonValue(),
            "differences": _field_differences(frame.schema, expected_schema),
        }
    finally:
        if owns_cache:
            frame.unpersist()


def profile_schema_drift(
    spark,
    input_path,
    expected_schema,
    *,
    source_format="jsonl",
    reader_options=None,
    dataset_name=None,
    run_id=None,
    audit_table="datalake.operations.schema_drift_profiles"
):
    """Infer each source file before applying the target schema; log findings.

    Physical encoding differences (Odoo arrays versus desired structs, CSV types)
    are findings, not rejected records. Inference cannot prove semantic correctness
    or required-field constraints. Per-file inspection errors are audited; sink
    errors propagate. Empty arrays and all-null fields provide weak type evidence.
    """
    if source_format not in ("json", "jsonl", "csv", "parquet"):
        raise ValueError("Unsupported source_format: " + source_format)
    if not isinstance(expected_schema, T.StructType):
        raise TypeError("expected_schema must be a Spark StructType")
    base = {
        "run_id": run_id or str(uuid.uuid4()),
        "dataset_name": dataset_name,
        "profile_kind": "SCHEMA_DRIFT",
    }
    try:
        paths = list_source_files(spark, input_path, source_format)
    except Exception as error:
        write_audit(
            spark,
            [
                dict(
                    base,
                    source_file=str(input_path),
                    status="INSPECTION_FAILED",
                    details={"error": str(error)},
                )
            ],
            audit_table,
        )
        return None
    if not paths:
        write_audit(
            spark,
            [
                dict(
                    base,
                    source_file=str(input_path),
                    status="NO_MATCHING_FILES",
                    details={},
                )
            ],
            audit_table,
        )
    for path in paths:
        try:
            details = _inspect_file(
                spark, path, source_format, expected_schema, reader_options or {}
            )
            status = "DRIFT_FOUND" if details["differences"] else "SCHEMA_MATCH"
        except Exception as error:
            details, status = {"error": str(error)}, "INSPECTION_FAILED"
        write_audit(
            spark,
            [dict(base, source_file=path, status=status, details=details)],
            audit_table,
        )
    return None
