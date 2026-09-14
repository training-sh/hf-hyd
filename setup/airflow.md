## NOT TESTED BEFORE ON LINUX

gpt notes only here

```
wsl
```

```
sudo apt update
sudo apt install -y  python3-dev build-essential \
    default-libmysqlclient-dev pkg-config
```

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
pip install mysqlclient aiomysql pymysql
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



