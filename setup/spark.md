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
