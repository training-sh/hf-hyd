- Glue Intro
- Classifier
- Crawlers

Inline policy
```
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Effect": "Allow",
			"Action": "iam:PassRole",
			"Resource": "arn:aws:iam::253862056991:role/*"
		}
	]
}
```

```



create a csv file without header

invoice0.csv

inv101,1000.34
inv102,1003.55

add csv classifier
invoice_no,amount
then create crawler with csv classifier

```

```
pyspark \
  --master yarn \
  --deploy-mode client \
  --driver-memory 1g \
  --executor-memory 2g \
  --executor-cores 1 \
  --num-executors 1 \
  --conf spark.executor.memoryOverhead=512m \
  --conf spark.driver.memoryOverhead=512m \
  --conf spark.dynamicAllocation.enabled=false
```

---

Documentation

https://docs.aws.amazon.com/glue/latest/webapi/API_GrokClassifier.html


