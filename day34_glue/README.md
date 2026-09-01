- Glue Intro
- Classifier
- Crawlers


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


