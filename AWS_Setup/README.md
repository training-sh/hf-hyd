AWS Cli, S3 Sync, other Automation scripts due to lab cleanup
 

setup structure to be copied into s3

```

cd ~

mkdir -p datalake

mkdir -p datalake/bronze/movielens
mkdir -p datalake/bronze/olist

mkdir -p datalake/bronze/movielens/movies
mkdir -p datalake/bronze/movielens/ratings


wget https://files.grouplens.org/datasets/movielens/ml-latest-small.zip --no-check-certificate

 unzip ml-latest-small.zip


cp ml-latest-small/movies.csv  ~/datalake/bronze/movielens/movies

cp ml-latest-small/ratings.csv  ~/datalake/bronze/movielens/ratings
```
