Spark Dataframe introduction

convert notebook to python

```
jupyter nbconvert --to script   --output-dir ./scripts  movies_to_parquet.ipynb
```

run python on spark submit

syntax

```
spark-submit [Spark options] application.py [application arguments]
```

```
spark-submit movies_to_parquet.py \
  --input-path "s3://gksdatalake/bronze/movielens/movies/" \
  --output-path "s3://gksdatalake/silver/movielens/movies/"
```

```
spark-submit \
  --master yarn \
  --deploy-mode client \
  movies_to_parquet.py \
  --input-path "s3://gksdatalake/bronze/movielens/movies/" \
  --output-path "s3://gksdatalake/silver/movielens/movies/"
```

```
spark-submit \
  --master yarn \
  --deploy-mode cluster \
  movies_to_parquet.py \
  --input-path "s3://gksdatalake/bronze/movielens/movies/" \
  --output-path "s3://gksdatalake/silver/movielens/movies/"
```
