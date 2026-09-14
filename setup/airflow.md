## NOT TESTED BEFORE ON LINUX

gpt notes only here

```
wsl
```

```
sudo apt update
sudo apt install -y  python3-dev build-essential \
    default-libmysqlclient-dev pkg-config graphviz
```

 pip install graphviz

```
mkdir ~/airflow
cd ~/airflow
 

export AIRFLOW_HOME=$HOME/airflow
```

need to download file if proxy blocks

```
AIRFLOW_VERSION=3.3.1

PYTHON_VERSION="$(python -c \
'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"

CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"



wget --no-check-certificate \
  "$CONSTRAINT_URL" \
  -O airflow-constraints.txt

pip install "apache-airflow==${AIRFLOW_VERSION}" \
  --constraint airflow-constraints.txt
 
```

```
pip install "apache-airflow==3.3.1" \
    apache-airflow-providers-mysql 
    
```

```
pip install mysqlclient aiomysql pymysql graphviz
```

```
pip install \
  apache-airflow-providers-apache-spark \
  apache-airflow-providers-apache-hive \
  apache-airflow-providers-apache-hdfs \
  apache-airflow-providers-snowflake
```

For EMR, for livy

```
pip install apache-airflow-providers-apache-livy
```

# MYSQL DB

```
mysql -u root -p 
```

```
CREATE DATABASE airflow_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER 'airflow'@'localhost'
  IDENTIFIED BY 'airflow123';

GRANT ALL PRIVILEGES
ON airflow_db.*
TO 'airflow'@'localhost';

FLUSH PRIVILEGES;

EXIT;
```

# .bashrc 

```
echo 'export AIRFLOW_HOME=$HOME/airflow' >> ~/.bashrc
```

```
echo "export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN='mysql+mysqldb://airflow:airflow123@localhost:3306/airflow_db'" >> ~/.bashrc
```

we configure airflow on port 8090

```
echo "export AIRFLOW__API__PORT=8090" >> ~/.bashrc
```

```
echo "export AIRFLOW__API__HOST='127.0.0.1'" >> ~/.bashrc
```

also bind to loopback/localhost, else it will listen on 0.0.0.0

note, we don't learn user/permission/auth/acl with airflow. this is not guide for complete airflow. we expose airflow with admin, no password at all

```
echo 'export AIRFLOW__CORE__SIMPLE_AUTH_MANAGER_ALL_ADMINS=True' >> ~/.bashrc
```
 

```
source ~/.bashrc
```

double underscore used in Airflow is convention, which has specific meaning.

```
AIRFLOW__CORE__DAGS_FOLDER
AIRFLOW__CORE__EXECUTOR
AIRFLOW__LOGGING__BASE_LOG_FOLDER
AIRFLOW__WEBSERVER__WEB_SERVER_PORT
```


it is equal to a config.ini file, with section.

below is information only, not a command

```
[core]
dags_folder = ...
executor = ...

[logging]
base_log_folder = ...

[webserver]
web_server_port = ...
```

```
echo $AIRFLOW_HOME
echo $AIRFLOW__DATABASE__SQL_ALCHEMY_CONN
```

check this working

```
airflow config get-value database sql_alchemy_conn
```

```
mkdir -p "$AIRFLOW_HOME"/{dags,logs,plugins,scripts}
```

```
airflow db migrate
```

```
airflow db check
```

```
airflow config get-value core dags_folder
```


```
 airflow config get-value api port
 ```

```
airflow standalone
```

it runs on port. we try to use a port other than 8080, which is default.

We have configured airflow for `8090`


### Nginx proxy

if only for plural sight, not needed for localhost/wsl

```
sudo tee /etc/nginx/snippets/airflow.conf > /dev/null <<'EOF'
location = /airflow {
    return 301 /airflow/;
}

location /airflow/ {
    proxy_pass http://127.0.0.1:8090;

    proxy_http_version 1.1;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-Port $server_port;
    proxy_set_header X-Forwarded-Prefix /airflow;

    proxy_redirect off;

    proxy_buffering off;
    proxy_read_timeout 300;
    proxy_send_timeout 300;
}
EOF
```

```
sudo nano /etc/nginx/sites-available/default
```

paste below with other include session

```
    include /etc/nginx/snippets/airflow.conf;
```

```
sudo nginx -t
```

```
sudo systemctl restart nginx
```

access airflow in /airflow path

```
cat >> ~/.bashrc <<'EOF'

# Apache Airflow
export AIRFLOW_HOME="$HOME/airflow"

export AIRFLOW__API__HOST="127.0.0.1"
export AIRFLOW__API__PORT="8090"

export AIRFLOW_FQDN="$(hostname -f)"
export AIRFLOW__API__BASE_URL="https://${AIRFLOW_FQDN}/airflow"
export AIRFLOW__CORE__EXECUTION_API_SERVER_URL="https://${AIRFLOW_FQDN}/airflow/execution/"
EOF
```

```
source ~/.bashrc
```

```
echo "$AIRFLOW_FQDN"
echo "$AIRFLOW__API__BASE_URL"

airflow config get-value api host
airflow config get-value api port
airflow config get-value api base_url
airflow config get-value core execution_api_server_url
```



```
cat > ~/.airflow.env <<'EOF'
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=mysql+mysqldb://airflow:airflow123@localhost:3306/airflow_db
EOF

chmod 600 ~/.airflow.env
```


```
mkdir -p ~/airflow/scripts

cat > ~/airflow/scripts/start-airflow.sh <<'EOF'
#!/bin/bash
set -e

AIRFLOW_FQDN="$(hostname -f)"

export AIRFLOW__API__BASE_URL="https://${AIRFLOW_FQDN}/airflow"
export AIRFLOW__CORE__EXECUTION_API_SERVER_URL="https://${AIRFLOW_FQDN}/airflow/execution/"

exec /home/cloud_user/dataengenv/bin/airflow standalone
EOF

chmod +x ~/airflow/scripts/start-airflow.sh
```

```
sudo tee /etc/systemd/system/airflow.service >/dev/null <<'EOF'
[Unit]
Description=Apache Airflow
Wants=network-online.target
After=network-online.target mysql.service

[Service]
Type=simple

User=cloud_user
Group=cloud_user

WorkingDirectory=/home/cloud_user/airflow

EnvironmentFile=/home/cloud_user/.airflow.env

Environment="HOME=/home/cloud_user"
Environment="AIRFLOW_HOME=/home/cloud_user/airflow"

# ----------------------------------------------------------
# Airflow Web/API
# ----------------------------------------------------------
Environment="AIRFLOW__API__HOST=127.0.0.1"
Environment="AIRFLOW__API__PORT=8090"
Environment="AIRFLOW__CORE__SIMPLE_AUTH_MANAGER_ALL_ADMINS=True"

# ----------------------------------------------------------
# Java
# ----------------------------------------------------------
Environment="JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64"

# ----------------------------------------------------------
# Hadoop / HDFS / YARN
# ----------------------------------------------------------
Environment="HADOOP_HOME=/opt/hadoop"
Environment="HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop"
Environment="YARN_CONF_DIR=/opt/hadoop/etc/hadoop"

# ----------------------------------------------------------
# Apache Hive
# ----------------------------------------------------------
Environment="HIVE_HOME=/opt/hive"
Environment="HIVE_CONF_DIR=/opt/hive/conf"

# ----------------------------------------------------------
# Apache Spark
# ----------------------------------------------------------
Environment="SPARK_HOME=/opt/spark"

Environment="PYSPARK_PYTHON=/home/cloud_user/dataengenv/bin/python"
Environment="PYSPARK_DRIVER_PYTHON=/home/cloud_user/dataengenv/bin/python"

Environment="PYTHONPATH=/opt/spark/python:/opt/spark/python/lib/py4j-0.10.9.7-src.zip"

# ----------------------------------------------------------
# Apache Livy
# ----------------------------------------------------------
Environment="LIVY_HOME=/opt/livy"

# ----------------------------------------------------------
# PATH
# ----------------------------------------------------------
Environment="PATH=/home/cloud_user/dataengenv/bin:/opt/spark/bin:/opt/spark/sbin:/opt/hive/bin:/opt/hadoop/bin:/opt/hadoop/sbin:/opt/livy/bin:/usr/local/bin:/usr/bin:/bin"

ExecStart=/home/cloud_user/airflow/scripts/start-airflow.sh

Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```


```
sudo systemctl daemon-reload
sudo systemctl enable --now airflow
```

```
sudo systemctl status airflow --no-pager
```

```
sudo systemctl status airflow --no-pager
```

```
sudo journalctl -u airflow -f
```

```
sudo ss -ltnp | grep 8090
```

verify runtime that airflow inherits

```
sudo -u cloud_user env \
  JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64 \
  HADOOP_HOME=/opt/hadoop \
  HIVE_HOME=/opt/hive \
  SPARK_HOME=/opt/spark \
  PATH=/home/cloud_user/dataengenv/bin:/opt/spark/bin:/opt/spark/sbin:/opt/hive/bin:/opt/hadoop/bin:/opt/hadoop/sbin:/opt/livy/bin:/usr/local/bin:/usr/bin:/bin \
  bash -c '
    echo "java:         $(command -v java)"
    echo "hdfs:         $(command -v hdfs)"
    echo "yarn:         $(command -v yarn)"
    echo "hive:         $(command -v hive)"
    echo "spark-submit: $(command -v spark-submit)"
    echo "airflow:      $(command -v airflow)"
  '


```
