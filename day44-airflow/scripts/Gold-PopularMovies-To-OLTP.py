"""Read gold Parquet and replace the selected MySQL table; verify the row count.
Run with spark-submit --jars <connector.jar>; see ../MOVIELENS.md.
The database must already exist (the DAG creates it). Password is read from env.
"""
import argparse
import os
from pyspark.sql import SparkSession
p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--input", required=True)
p.add_argument("--jdbc-url", required=True)
p.add_argument("--table", required=True)
p.add_argument("--user", required=True)
p.add_argument("--password-env", default="MYSQL_PWD")
args = p.parse_args()
password = os.environ[args.password_env]
spark = SparkSession.builder.appName("D44-MovieLens-MySQL").getOrCreate()
spark.sparkContext.setLogLevel("WARN")
try:
    df = spark.read.parquet(args.input)
    expected = df.count()
    if not expected:
        raise ValueError("Gold is empty; refusing to replace the table")
    properties = {"user": args.user, "password": password, "driver": "com.mysql.cj.jdbc.Driver"}
    # One JDBC writer is sufficient for this small result. Reruns replace this table.
    df.coalesce(1).write.mode("overwrite").jdbc(args.jdbc_url, args.table, properties=properties)
    actual = spark.read.jdbc(args.jdbc_url, args.table, properties=properties).count()
    assert actual == expected, (actual, expected)
    print("MYSQL_ROWS", actual, "VERIFIED")
finally:
    spark.stop()
