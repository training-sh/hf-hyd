# TODO: DIY

pass paths from command line arguments

Convention

1. use --bronze-movies-path hdfspath
2. use --bronze-rating-path hdfspath
3. use --silver-movies-path  hdfspath
4. use --silver-rating-path hdfspath
5. use --gold-popular-movies-path hdfspath


Spark Dataframe introduction


```
wget -O mysql-connector-j-8.4.0.jar \
  https://repo.maven.apache.org/maven2/com/mysql/mysql-connector-j/8.4.0/mysql-connector-j-8.4.0.jar --no-check-certificate
```


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
