# Apache Spark Setup

```

cd /tmp

wget -O spark-3.5.9-bin-hadoop3.tgz \
  https://archive.apache.org/dist/spark/spark-3.5.9/spark-3.5.9-bin-hadoop3.tgz \
  --no-check-certificate
```

```
sudo tar -xzf /tmp/spark-3.5.9-bin-hadoop3.tgz -C /opt

sudo mv /opt/spark-3.5.9-bin-hadoop3 /opt/spark

sudo chown -R "$USER:$(id -gn)" /opt/spark
```

Check all fine

Environment variable for Spark 

```
ls -ld /opt/spark
ls /opt/spark/bin
```

```
tee -a "$HOME/.bashrc" >/dev/null <<'EOF'

# --- Spark configuration ---
export SPARK_HOME=/opt/spark
export PATH="$SPARK_HOME/bin:$SPARK_HOME/sbin:$PATH"

# Use the existing Python virtual environment
export PYSPARK_PYTHON="$HOME/dataengenv/bin/python"
export PYSPARK_DRIVER_PYTHON="$HOME/dataengenv/bin/python"

# Spark's included Python and Py4J libraries
export PYTHONPATH="$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.9.7-src.zip${PYTHONPATH:+:$PYTHONPATH}"
# --- end Spark configuration ---
EOF
```

### Delta Lake 3.3.2

```

curl -k --fail --location --retry 5 --continue-at - \
  --output "$SPARK_HOME/jars/delta-spark_2.12-3.3.2.jar" \
  https://repo.maven.apache.org/maven2/io/delta/delta-spark_2.12/3.3.2/delta-spark_2.12-3.3.2.jar
```
```
curl -k --fail --location --retry 5 --continue-at - \
  --output "$SPARK_HOME/jars/delta-storage-3.3.2.jar" \
  https://repo.maven.apache.org/maven2/io/delta/delta-storage/3.3.2/delta-storage-3.3.2.jar


```

# Apache Iceberg 1.10.0

# Spark 3.5 / Scala 2.12 / Java 11 compatible choice

```

curl -k --fail --location --retry 5 --continue-at - \
  --output "$SPARK_HOME/jars/iceberg-spark-runtime-3.5_2.12-1.10.0.jar" \
  https://repo.maven.apache.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/1.10.0/iceberg-spark-runtime-3.5_2.12-1.10.0.jar
```

# Kafka Connectors

For spark kafka connectors

```
curl -k --fail --location --retry 5 --continue-at - \
  --output "$SPARK_HOME/jars/spark-sql-kafka-0-10_2.12-3.5.9.jar" \
  https://repo.maven.apache.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.5.9/spark-sql-kafka-0-10_2.12-3.5.9.jar
```

```
curl -k --fail --location --retry 5 --continue-at - \
  --output "$SPARK_HOME/jars/kafka-clients-3.4.1.jar" \
  https://repo.maven.apache.org/maven2/org/apache/kafka/kafka-clients/3.4.1/kafka-clients-3.4.1.jar
```

used for consumer poll by spark


```
curl -k --fail --location --retry 5 --continue-at - \
  --output "$SPARK_HOME/jars/commons-pool2-2.11.1.jar" \
  https://repo.maven.apache.org/maven2/org/apache/commons/commons-pool2/2.11.1/commons-pool2-2.11.1.jar
```

if avro used..

```
curl -k --fail --location --retry 5 --continue-at - \
  --output "$SPARK_HOME/jars/spark-avro_2.12-3.5.9.jar" \
  https://repo.maven.apache.org/maven2/org/apache/spark/spark-avro_2.12/3.5.9/spark-avro_2.12-3.5.9.jar
```

optional for local developemnt, only for kafka in secured mode, like aws/azure managed kafka, auth/sasl/ configuration

```
curl -k --fail --location --retry 5 --continue-at - \
  --output "$SPARK_HOME/jars/spark-token-provider-kafka-0-10_2.12-3.5.9.jar" \
  https://repo.maven.apache.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.5.9/spark-token-provider-kafka-0-10_2.12-3.5.9.jar
```


## MySQL

```
curl -k --fail --location --retry 5 --continue-at - \
  --output "$SPARK_HOME/jars/mysql-connector-j-8.4.0.jar" \
  https://repo.maven.apache.org/maven2/com/mysql/mysql-connector-j/8.4.0/mysql-connector-j-8.4.0.jar
```

## PostgreSQL

```
curl -k --fail --location --retry 5 --continue-at - \
  --output "$SPARK_HOME/jars/postgresql-42.7.8.jar" \
  https://repo.maven.apache.org/maven2/org/postgresql/postgresql/42.7.8/postgresql-42.7.8.jar
```


## For Polaris REST catalog, S3 not for intern batch

```
curl -k --fail --location --retry 5 --continue-at - \
  --output "$SPARK_HOME/jars/iceberg-aws-bundle-1.10.0.jar" \
  https://repo.maven.apache.org/maven2/org/apache/iceberg/iceberg-aws-bundle/1.10.0/iceberg-aws-bundle-1.10.0.jar
```


# Hadoop S3A connector

```
curl -k --fail --location --retry 5 --continue-at - \
  --output "$SPARK_HOME/jars/hadoop-aws-3.3.4.jar" \
  https://repo.maven.apache.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar
```

```
curl -k --fail --location --retry 5 --continue-at - \
  --output "$SPARK_HOME/jars/aws-java-sdk-bundle-1.12.262.jar" \
  https://repo.maven.apache.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar
```

 
 
```
source "$HOME/.bashrc"
```

```
echo "$SPARK_HOME"
which pyspark
which spark-submit
echo "$PYSPARK_PYTHON"

spark-submit --version
```

local spark server, embedded mode

```
pyspark --master local[*]
```

Some python code to test spark hello world

```
spark.range(1, 11).show()
```

Another way to run spark

```
python - <<'PY'
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("SparkTest")
    .master("local[*]")
    .getOrCreate()
)

print("Spark version:", spark.version)
spark.range(1, 11).show()

spark.stop()
PY
```


spark master

```
/opt/spark/sbin/start-master.sh
```

```
jps
```

check in local browser

http://localhost:8080

spark worker

```
/opt/spark/sbin/start-worker.sh "spark://$(hostname):7077"
```

```
jps
```

and Check the spark master ui

http://localhost:8080

spark submit

```
spark-submit \
  --master "spark://$(hostname):7077" \
  /opt/spark/examples/src/main/python/pi.py 10
```

# now run spark over yarn, check README.md for starting hdfs, yarn

```
pyspark \
  --master yarn \
  --deploy-mode client
```



```
spark.range(1, 11).show()

print("Spark version:", spark.version)
print("Spark master:", spark.sparkContext.master)
print("Application ID:", spark.sparkContext.applicationId)
```

```
spark.stop()
exit()
```


# submit using yarn, client mode, discussed later

```
spark-submit \
  --master yarn \
  --deploy-mode client \
  /opt/spark/examples/src/main/python/pi.py 10
```

# submit using yarn, cluster mode, discussed later

```
spark-submit \
  --master yarn \
  --deploy-mode cluster \
  /opt/spark/examples/src/main/python/pi.py 10
```

  


## SPARK CONF, DO NOT ATTEMPT NOW, explained later

```
cd /opt/spark/conf

cp -n spark-env.sh.template spark-env.sh
cp -n spark-defaults.conf.template spark-defaults.conf
cp -n log4j2.properties.template log4j2.properties
``
