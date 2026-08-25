
# EMR Mapreduce


```
ssh -i ~/.ssh/ec2emrkey.pem hadoop@PRIMARY-DNS
```

```
yarn node -list
```

```
hdfs getconf -confKey fs.defaultFS
hdfs getconf -confKey hadoop.tmp.dir
hdfs getconf -confKey dfs.namenode.name.dir
hdfs getconf -confKey dfs.datanode.data.dir
```

```
hdfs dfsadmin -report
```

```
hdfs dfs -ls /
```

```
yarn application -list -appStates ALL
```

# S3 and HDFS 

below are reference commands for s3/hdfs. You can still use s3 input directly into map reduce instead of using hdfs.

```
aws s3 ls s3://YOUR-BUCKET/
```

```
hadoop fs -ls s3://YOUR-BUCKET/
```
```
hadoop fs -ls s3://YOUR-BUCKET/
```
```
aws s3 ls s3://YOUR-BUCKET/ --recursive
```
```
aws s3 cp \
  s3://YOUR-BUCKET/input/test.txt \
  /tmp/test.txt
```
```
echo "EMR S3 test" >/tmp/emr-test.txt
```
```
aws s3 cp \
  /tmp/emr-test.txt \
  s3://YOUR-BUCKET/emr-test/emr-test.txt
```



to connect to core nodes or task nodes, use jump connection approach, using ssh itself a proxy

```
ssh \
  -i ~/.ssh/ec2emrkey.pem \
  -o ProxyCommand="ssh -i ~/.ssh/ec2emrkey.pem -W %h:%p hadoop@PRIMARY-DNS" \
  hadoop@CORE-TASK-NODE-DNS
```




```
hdfs dfsadmin -report
```

```
hdfs dfsadmin -report | grep -E 'Name:|Hostname:|Decommission Status'
```

to run map reduce 

```
hadoop jar \
  /usr/lib/hadoop-mapreduce/hadoop-mapreduce-examples.jar \
  wordcount \
  "/user/$USER/input" \
  "/user/$USER/output"
```


Fault Tolerance


Check available EMR service names

On a core node:

```
sudo systemctl status hadoop-hdfs-datanode
sudo systemctl status hadoop-yarn-nodemanager
```

Discover them if the names differ:

```
systemctl list-unit-files |
  grep -E 'hadoop.*(datanode|nodemanager)'
```

```
hdfs getconf -confKey dfs.replication
```

test file

```
seq 1 100000 > /tmp/failover-demo.txt

hdfs dfs -mkdir -p /demo/failover
hdfs dfs -put -f /tmp/failover-demo.txt /demo/failover/
```

all the blocks

```
hdfs fsck /demo/failover/failover-demo.txt \
  -files \
  -blocks \
  -locations
```

do this on primary node

```
sudo systemctl status hadoop-hdfs-datanode --no-pager
```

```
hdfs dfs -cat /demo/failover/failover-demo.txt |
  head
```

```
hdfs dfsadmin -report
```

stop datanode, do on datanode vm

```
sudo systemctl stop hadoop-hdfs-datanode
```

```
sudo systemctl status hadoop-hdfs-datanode --no-pager
```

now read on primary node again

```
hdfs dfs -cat /demo/failover/failover-demo.txt |
  head
```


```
hdfs dfsadmin -report
```

```
hdfs fsck /demo/failover/failover-demo.txt \
  -files \
  -blocks \
  -locations
```

restart again..

```
sudo systemctl start hadoop-hdfs-datanode
sudo systemctl status hadoop-hdfs-datanode --no-pager
```

```
hdfs dfsadmin -report
```

----

Task node stop and restart, do this on task node or core node
```
sudo systemctl status hadoop-yarn-nodemanager
```
```
sudo systemctl stop hadoop-yarn-nodemanager
```
```
yarn node -list -all
```
```
yarn application -list
```
```
yarn application -status APPLICATION_ID
```

watch dogs on data node

```
sudo journalctl \
  -u hadoop-hdfs-datanode \
  -f
```

for task or node manager over task or data node

```
sudo journalctl \
  -u hadoop-yarn-nodemanager \
  -f
```



## PluralSight

```
ssh -i ~/.ssh/ec2emrkey.pem \
  hadoop@ec2-100-62-23-158.compute-1.amazonaws.com \
  'hostname -f; sudo ss -lntp | grep -E ":(8088|9870|18080|19888)\b"'
```

```
EMR_PRIMARY=$(ssh -i ~/.ssh/ec2emrkey.pem \
  hadoop@ec2-100-62-23-158.compute-1.amazonaws.com \
  'hostname -f')
```

```
echo "$EMR_PRIMARY"
```

```
ssh -i ~/.ssh/ec2emrkey.pem \
  -N \
  -o ExitOnForwardFailure=yes \
  -L 18088:"$EMR_PRIMARY":8088 \
  -L 19870:"$EMR_PRIMARY":9870 \
  -L 18080:"$EMR_PRIMARY":18080 \
  -L 19888:"$EMR_PRIMARY":19888 \
  hadoop@ec2-100-62-23-158.compute-1.amazonaws.com
```


### Livy EMR


```
ssh -i ~/.ssh/ec2emrkey.pem \
  hadoop@ec2-100-62-23-158.compute-1.amazonaws.com \
  'sudo ss -lntp | grep ":8998" || echo "Livy is not listening on port 8998"'
```

```
ssh -i ~/.ssh/ec2emrkey.pem \
  hadoop@ec2-100-62-23-158.compute-1.amazonaws.com \
  'curl -i "http://$(hostname -f):8998/sessions"'
```

Run Livy ssh proxy

```
EMR_PRIMARY=$(ssh -i ~/.ssh/ec2emrkey.pem \
  hadoop@ec2-100-62-23-158.compute-1.amazonaws.com \
  'hostname -f')

echo "$EMR_PRIMARY"
```

proxy

```
ssh -i ~/.ssh/ec2emrkey.pem \
  -N \
  -o ExitOnForwardFailure=yes \
  -L 18998:"$EMR_PRIMARY":8998 \
  hadoop@ec2-100-62-23-158.compute-1.amazonaws.com
```

check this locally, whether proxy works, able to fetch sessions, empty sessions are fine

```
curl -i http://localhost:18998/sessions
```


# Spark magic


```
mkdir -p "$HOME/.sparkmagic"
```

```
tee "$HOME/.sparkmagic/config.json" >/dev/null <<'EOF'
{
  "kernel_python_credentials": {
    "username": "",
    "password": "",
    "url": "http://127.0.0.1:18998",
    "auth": "None"
  },

  "kernel_scala_credentials": {
    "username": "",
    "password": "",
    "url": "http://127.0.0.1:18998",
    "auth": "None"
  },

  "kernel_r_credentials": {
    "username": "",
    "password": "",
    "url": "http://127.0.0.1:18998",
    "auth": "None"
  },

  "logging_config": {
    "version": 1,
    "formatters": {
      "magicsFormatter": {
        "format": "%(asctime)s\t%(levelname)s\t%(message)s",
        "datefmt": ""
      }
    },
    "handlers": {
      "magicsHandler": {
        "class": "hdijupyterutils.filehandler.MagicsFileHandler",
        "formatter": "magicsFormatter",
        "home_path": "~/.sparkmagic"
      }
    },
    "loggers": {
      "magicsLogger": {
        "handlers": ["magicsHandler"],
        "level": "DEBUG",
        "propagate": 0
      }
    }
  },

  "authenticators": {
    "Kerberos": "sparkmagic.auth.kerberos.Kerberos",
    "None": "sparkmagic.auth.customauth.Authenticator",
    "Basic_Access": "sparkmagic.auth.basic.Basic"
  },

  "wait_for_idle_timeout_seconds": 15,
  "livy_session_startup_timeout_seconds": 60,

  "http_session_config": {
    "adapters": [
      {
        "prefix": "http://",
        "adapter": "requests.adapters.HTTPAdapter"
      }
    ]
  },

  "fatal_error_suggestion": "The code failed because of a fatal error:\n\t{}.\n\nSome things to try:\na) Make sure Spark has enough available resources for Jupyter to create a Spark context.\nb) Contact your Jupyter administrator to make sure the Spark magics library is configured correctly.\nc) Restart the kernel.",

  "ignore_ssl_errors": false,

  "session_configs": {
    "driverMemory": "1000M",
    "executorCores": 2
  },

  "session_configs_defaults": {
    "conf": {
      "spark.sql.catalog.spark_catalog.type": "hive"
    }
  },

  "use_auto_viz": true,
  "coerce_dataframe": true,
  "max_results_sql": 2500,
  "pyspark_dataframe_encoding": "utf-8",

  "heartbeat_refresh_seconds": 30,
  "livy_server_heartbeat_timeout_seconds": 0,
  "heartbeat_retry_seconds": 10,

  "server_extension_default_kernel_name": "pysparkkernel",
  "custom_headers": {},

  "retry_policy": "configurable",
  "retry_seconds_to_sleep_list": [0.2, 0.5, 1, 3, 5],
  "configurable_retry_policy_max_retries": 8
}
EOF
```
