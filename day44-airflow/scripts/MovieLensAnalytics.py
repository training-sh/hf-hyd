"""Join silver movies and ratings; write popular movies in four gold formats.
Run with spark-submit; see ../MOVIELENS.md. --help lists parameters.
"""
import argparse
from pyspark.sql import SparkSession, functions as F
p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--movies", required=True)
p.add_argument("--ratings", required=True)
p.add_argument("--output", required=True)
p.add_argument("--min-ratings", type=int, default=100)
p.add_argument("--min-average", type=float, default=3.5)
p.add_argument("--partitions", type=int, default=1)
args = p.parse_args()
spark = SparkSession.builder.appName("D44-MovieLens-Gold").getOrCreate()
spark.sparkContext.setLogLevel("WARN")
try:
    movies = spark.read.parquet(args.movies)
    ratings = spark.read.parquet(args.ratings)
    popular = (ratings.groupBy("movieId")
        .agg(F.avg("rating").alias("avg_rating"), F.count("userId").alias("total_ratings"))
        .filter((F.col("total_ratings") >= args.min_ratings) & (F.col("avg_rating") >= args.min_average))
        .join(movies, "movieId")
        .select("movieId", "title", "genres", "avg_rating", "total_ratings")
        .orderBy(F.desc("total_ratings"), F.desc("avg_rating"), "movieId")
        .coalesce(args.partitions).cache())
    count = popular.count()
    if not count:
        raise ValueError("No popular movies: check inputs and thresholds")
    for fmt in ("csv", "parquet", "orc", "json"):
        path = args.output.rstrip("/") + "/" + fmt
        popular.write.mode("overwrite").format(fmt).option("header", True).save(path)
        actual = spark.read.format(fmt).option("header", True).load(path).count()
        assert actual == count, (fmt, actual, count)
    print("GOLD_ROWS", count, "ALL_FOUR_FORMATS_VERIFIED")
    popular.unpersist()
finally:
    spark.stop()
