"""Record whether Delta's storage layer supports this HDFS URI."""
import json
import duckdb
from config import ROOT, HDFS_BASE, hdfs_uri

report = {}
with duckdb.connect() as con:
    con.execute("LOAD delta")
    try:
        report["delta_hdfs"] = {"status": "passed", "rows": con.execute("SELECT count(*) FROM delta_scan(?)", [hdfs_uri(HDFS_BASE + '/sales_delta')]).fetchone()[0]}
    except Exception as exc:
        report["delta_hdfs"] = {"status": "failed", "error": str(exc)}
(ROOT / "storage-probe.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
