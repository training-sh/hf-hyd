"""Stage a genuine HDFS Iceberg table; test native URI and adapter reads."""
import json
import traceback

import duckdb
import pandas as pd
import pyarrow.parquet as pq
from pyiceberg.catalog import load_catalog
from pyiceberg.partitioning import PartitionSpec, PartitionField
from pyiceberg.transforms import IdentityTransform
from pyiceberg.schema import Schema
from pyiceberg.types import NestedField, LongType, DateType, StringType, DoubleType

from config import ROOT, HDFS_BASE, hdfs_uri
from iceberg_hdfs_io import hdfs_filesystem


def main():
    report = {"duckdb": duckdb.__version__, "checks": {}}
    report_path = ROOT / "iceberg-hdfs-results.json"
    try:
        warehouse = hdfs_uri(HDFS_BASE + "/iceberg_warehouse")
        catalog = load_catalog("day60_hdfs", type="sql",
                              uri=f"sqlite:///{ROOT / 'data/iceberg_hdfs_catalog.db'}",
                              warehouse=warehouse,
                              **{"py-io-impl": "iceberg_hdfs_io.IcebergHdfsFileIO"})
        catalog.create_namespace_if_not_exists("lab")
        arrow = pq.read_table(ROOT / "data/sales.parquet")
        schema = Schema(*[NestedField(i, name, kind, required=False) for i, (name, kind) in enumerate([
            ("order_id", LongType()), ("order_date", DateType()), ("region", StringType()),
            ("category", StringType()), ("quantity", LongType()), ("revenue", DoubleType()),
            ("profit", DoubleType())], start=1)])
        table = catalog.create_table_if_not_exists(
            "lab.sales", schema=schema,
            partition_spec=PartitionSpec(PartitionField(source_id=schema.find_field("region").field_id, field_id=1000,
                                                        transform=IdentityTransform(), name="region")))
        table.overwrite(arrow)
        # Keep an older snapshot with an extra row, then restore the baseline.
        # This proves iceberg_scan follows snapshots rather than globbing Parquet.
        table.append(arrow.slice(0, 1))
        previous_snapshot_id = table.current_snapshot().snapshot_id
        table.overwrite(arrow)
        metadata = table.metadata_location
        (ROOT / "data/iceberg_hdfs_metadata.json").write_text(json.dumps({"metadata_location": metadata}, indent=2) + "\n")
        report["metadata_location"] = metadata
        report["checks"]["staging"] = "passed"
        with duckdb.connect() as con:
            con.execute("LOAD iceberg")
            try:
                report["checks"]["without_adapter"] = {"rows": con.execute("SELECT count(*) FROM iceberg_scan(?)", [metadata]).fetchone()[0]}
            except Exception as exc:
                report["checks"]["without_adapter"] = {"status": "failed", "error": str(exc)}
        with duckdb.connect() as con:
            con.execute("LOAD iceberg")
            filesystem = hdfs_filesystem()
            accessed = []
            original_open = filesystem._open
            def traced_open(path, *args, **kwargs):
                accessed.append(str(path))
                return original_open(path, *args, **kwargs)
            filesystem._open = traced_open
            con.register_filesystem(filesystem)
            frame = con.execute("SELECT * FROM iceberg_scan(?) ORDER BY order_id", [metadata]).df()
            baseline = pd.read_csv(ROOT / "data/sales.csv", parse_dates=["order_date"])
            pd.testing.assert_frame_equal(baseline, frame[baseline.columns], check_dtype=False)
            totals = con.execute("SELECT count(*), sum(revenue) FROM iceberg_scan(?)", [metadata]).fetchone()
            assert totals[0] == 5000 and abs(totals[1] - baseline.revenue.sum()) < .001
            historical = con.execute("SELECT count(*) FROM iceberg_scan(?, snapshot_from_id=?)", [metadata, previous_snapshot_id]).fetchone()[0]
            assert historical == 5001, historical
            expected = len(baseline[baseline.region == "South"])
            assert con.execute("SELECT count(*) FROM iceberg_scan(?) WHERE region='South'", [metadata]).fetchone()[0] == expected
            accessed_before_filter = list(accessed)
            accessed.clear()
            # Fresh DuckDB instance: avoid reusing data cached by the full scan.
            with duckdb.connect() as filtered_con:
                filtered_con.execute("LOAD iceberg")
                filtered_con.register_filesystem(filesystem)
                plan = filtered_con.execute("EXPLAIN ANALYZE SELECT sum(revenue) FROM iceberg_scan(?) WHERE region='South'", [metadata]).fetchone()[1]
            (ROOT / "plan-iceberg-hdfs.txt").write_text(plan)
            filtered_files = sorted(set(path for path in accessed if path.endswith('.parquet')))
            assert len(filtered_files) == 1 and '/region=South/' in filtered_files[0], filtered_files
            report["checks"]["partition_pruning"] = {"status": "passed", "parquet_files_opened": filtered_files}
            report["checks"]["snapshot_time_travel"] = {"status": "passed", "previous_snapshot_id": previous_snapshot_id, "previous_rows": historical, "current_rows": totals[0]}
            accessed.extend(accessed_before_filter)
            assert accessed and all(path.startswith(HDFS_BASE + '/iceberg_warehouse/') for path in accessed), accessed
            assert any(path.endswith('.metadata.json') for path in accessed), accessed
            assert any(path.endswith('.avro') for path in accessed), accessed
            assert any(path.endswith('.parquet') for path in accessed), accessed
            report["checks"]["adapter_read"] = {"status": "passed", "rows": totals[0], "revenue": round(totals[1], 2), "south_rows": expected}
            report["hdfs_opened_paths"] = sorted(set(accessed))
        report["status"] = "passed"
    except Exception as exc:
        report["status"] = "failed"
        report["error"] = str(exc)
        traceback.print_exc()
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2), flush=True)
    if report["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
