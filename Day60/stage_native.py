"""Stage partitioned Parquet, Delta and Iceberg without modifying other labs."""
import json
import subprocess

import duckdb
import pyarrow.parquet as pq
from deltalake import write_deltalake
from pyiceberg.catalog import load_catalog

from config import ROOT, HDFS_BIN, HDFS_BASE

data = ROOT / "data"
with duckdb.connect() as con:
    source = str(data / "sales.parquet").replace("'", "''")
    output = str(data / "sales_partitioned").replace("'", "''")
    con.execute(f"COPY (SELECT *, year(order_date) AS year, month(order_date) AS month FROM read_parquet('{source}')) TO '{output}' (FORMAT PARQUET, PARTITION_BY (year, month), OVERWRITE_OR_IGNORE)")
arrow = pq.read_table(data / "sales.parquet")
write_deltalake(str(data / "sales_delta"), arrow, mode="overwrite", partition_by=["region"])
warehouse = data / "iceberg_warehouse"
warehouse.mkdir(exist_ok=True)
catalog = load_catalog("day60", type="sql", uri=f"sqlite:///{warehouse / 'catalog.db'}", warehouse=warehouse.as_uri())
catalog.create_namespace_if_not_exists("lab")
table = catalog.create_table_if_not_exists("lab.sales", schema=arrow.schema)
table.overwrite(arrow)
(data / "iceberg_metadata.json").write_text(json.dumps({"metadata_location": table.metadata_location}, indent=2) + "\n")
subprocess.run([HDFS_BIN, "dfs", "-mkdir", "-p", HDFS_BASE], check=True, timeout=60)
subprocess.run([HDFS_BIN, "dfs", "-put", "-f", str(data / "sales_partitioned"), HDFS_BASE + "/"], check=True, timeout=120)
subprocess.run([HDFS_BIN, "dfs", "-put", "-f", str(data / "sales_delta"), HDFS_BASE + "/"], check=True, timeout=120)
print("Staged Linux partitioned Parquet/Delta/Iceberg and HDFS partitioned Parquet/Delta")
