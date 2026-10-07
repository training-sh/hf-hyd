"""DuckDB scans files; only query results become DataFrames."""
import json
import os
from contextlib import contextmanager
import duckdb
import fsspec
from config import ROOT, HDFS_USER, HDFS_BASE, WEBHDFS_HOST, WEBHDFS_PORT, hdfs_uri

SOURCES = ["Linux Parquet", "Linux partitioned Parquet", "Linux Delta", "Linux Iceberg", "HDFS Parquet (WebHDFS adapter)"]

def literal(value):
    return "'" + str(value).replace("'", "''") + "'"

@contextmanager
def connect_source(source):
    con = duckdb.connect()
    try:
        data = ROOT / "data"
        if source == "Linux Parquet":
            scan = f"read_parquet({literal(data / 'sales.parquet')})"
        elif source == "Linux partitioned Parquet":
            scan = f"read_parquet({literal(data / 'sales_partitioned/**/*.parquet')}, hive_partitioning=true)"
        elif source == "Linux Delta":
            con.execute("LOAD delta")
            scan = f"delta_scan({literal(data / 'sales_delta')})"
        elif source == "Linux Iceberg":
            con.execute("LOAD iceberg")
            metadata = json.loads((data / "iceberg_metadata.json").read_text())["metadata_location"]
            scan = f"iceberg_scan({literal(metadata)})"
        elif source == "HDFS Parquet (WebHDFS adapter)":
            filesystem = fsspec.filesystem("webhdfs", host=WEBHDFS_HOST, port=WEBHDFS_PORT, user=HDFS_USER)
            con.register_filesystem(filesystem)
            scan = f"read_parquet({literal('webhdfs://' + HDFS_BASE + '/sales_partitioned/**/*.parquet')}, hive_partitioning=true)"
        elif source == "HDFS Parquet (native extension)":
            con.execute("LOAD hdfs")
            scan = f"read_parquet({literal(hdfs_uri(HDFS_BASE + '/sales_partitioned/**/*.parquet'))}, hive_partitioning=true)"
        elif source == "HDFS Iceberg (WebHDFS adapter)":
            from iceberg_hdfs_io import hdfs_filesystem
            con.execute("LOAD iceberg")
            con.register_filesystem(hdfs_filesystem())
            metadata = json.loads((data / "iceberg_hdfs_metadata.json").read_text())["metadata_location"]
            scan = f"iceberg_scan({literal(metadata)})"
        else:
            raise ValueError(f"Unknown source: {source}")
        con.execute(f"CREATE VIEW sales AS SELECT * FROM {scan}")
        yield con
    finally:
        con.close()

def available_sources():
    sources = SOURCES.copy()
    probe = ROOT / "extension-probe.json"
    if probe.exists() and json.loads(probe.read_text()).get("hdfs_csv_rows") == 5000:
        sources.append("HDFS Parquet (native extension)")
    iceberg_probe = ROOT / "iceberg-hdfs-results.json"
    if iceberg_probe.exists() and json.loads(iceberg_probe.read_text()).get("status") == "passed":
        sources.append("HDFS Iceberg (WebHDFS adapter)")
    return sources

def conditions(regions, categories, dates, months=None):
    def membership(column, values):
        return f"{column} IN ({','.join('?' for _ in values)})" if values else "FALSE"
    clauses = [membership("region", regions), membership("category", categories), "order_date BETWEEN ? AND ?"]
    params = [*regions, *categories, dates[0], dates[1]]
    if months is not None:
        clauses.append("year = 2026 AND " + membership("month", months))
        params.extend(months)
    return " AND ".join(clauses), params
