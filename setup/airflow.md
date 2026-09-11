## NOT TESTED BEFORE ON LINUX

gpt notes only here

```
wsl
```

```
sudo apt update
sudo apt install -y python3-venv python3-dev build-essential \
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


