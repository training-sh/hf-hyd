import json
import duckdb
from config import ROOT, HDFS_FILE, hdfs_uri

report = {"duckdb": duckdb.__version__, "extensions": {}}
with duckdb.connect() as con:
    for name in ["hdfs", "delta", "iceberg"]:
        try:
            con.execute(f"INSTALL {name}" + (" FROM community" if name == "hdfs" else ""))
            con.execute(f"LOAD {name}")
            report["extensions"][name] = {"status": "loaded"}
        except Exception as exc:
            report["extensions"][name] = {"status": "failed", "error": str(exc)}
    if report["extensions"]["hdfs"]["status"] == "loaded":
        try:
            report["hdfs_csv_rows"] = con.execute("SELECT count(*) FROM read_csv(?)", [hdfs_uri(HDFS_FILE)]).fetchone()[0]
        except Exception as exc:
            report["hdfs_csv_error"] = str(exc)
(ROOT / "extension-probe.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
