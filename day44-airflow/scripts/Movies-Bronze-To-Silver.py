"""Read the specified bronze CSV and overwrite the specified silver Parquet directory.
Run with spark-submit; see ../MOVIELENS.md. --help lists parameters.
"""
import argparse
from pyspark.sql import SparkSession
p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--input", required=True)
p.add_argument("--output", required=True)
p.add_argument("--partitions", type=int, default=2)
args = p.parse_args()
spark = SparkSession.builder.appName("D44-Movies-Silver").getOrCreate()
spark.sparkContext.setLogLevel("WARN")
try:
    # Explicit schema avoids inference; malformed CSV fails the task.
    df = spark.read.option("header", True).option("mode", "FAILFAST").schema("movieId INT, title STRING, genres STRING").csv(args.input)
    df.repartition(args.partitions).write.mode("overwrite").parquet(args.output)
    print("SILVER_ROWS", spark.read.parquet(args.output).count())
finally:
    spark.stop()
