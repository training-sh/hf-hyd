AWS Cli, S3 Sync, other Automation scripts due to lab cleanup


```
S3_BUCKET_NAME="gksdatalake"


aws s3 sync "$HOME/datalake/" "s3://$S3_BUCKET_NAME/" \
  --region us-east-1 \
  --profile training
```

# Now S3 Bucket to local directory

```
S3_BUCKET_NAME="gksdatalake"
LOCAL_BACKUP="$HOME/datalake_from_s3"
aws s3 sync "s3://$S3_BUCKET_NAME/" "$LOCAL_BACKUP/" \
  --exact-timestamps \
  --region us-east-1 \
  --profile training
```



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
