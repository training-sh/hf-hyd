- Redshift basics
- Weekly exercises


```
aws configure --profile training
```

```
source awsrefresh
```


```
S3_BUCKET_NAME="gksdatalake"
aws s3 sync "$HOME/datalake/" "s3://$S3_BUCKET_NAME/" \
  --region us-east-1 \
  --profile training
```
