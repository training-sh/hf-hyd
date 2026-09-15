# Apache Airflow 3.3.1 --- Useful Commands Cheat Sheet

This cheat sheet is intended for a Linux/WSL Airflow 3.3.1 training
environment.

> **Training note:** Keep the Airflow API/web server bound to
> `127.0.0.1`. Do not expose an insecure training installation directly
> to an open network.

------------------------------------------------------------------------

## 1. Installation and General Information

``` bash
# Airflow version
airflow version

# Main help
airflow --help

# Help for a command group
airflow dags --help
airflow tasks --help
airflow db --help
airflow config --help
airflow providers --help

# Check Python package dependency consistency
pip check

# Find executables
which python
which pip
which airflow

# Python version
python --version
```

------------------------------------------------------------------------

## 2. Airflow Environment

``` bash
# Airflow home
echo "$AIRFLOW_HOME"

# Database connection environment variable
echo "$AIRFLOW__DATABASE__SQL_ALCHEMY_CONN"

# API host
echo "$AIRFLOW__API__HOST"

# API port
echo "$AIRFLOW__API__PORT"

# Reverse-proxy base URL
echo "$AIRFLOW__API__BASE_URL"

# FQDN used by the training VM
echo "$AIRFLOW_FQDN"
```

------------------------------------------------------------------------

## 3. Airflow Configuration

``` bash
# List configuration
airflow config list

# DAG folder
airflow config get-value core dags_folder

# Executor
airflow config get-value core executor

# Metadata database connection
airflow config get-value database sql_alchemy_conn

# API host
airflow config get-value api host

# API port
airflow config get-value api port

# API base URL
airflow config get-value api base_url

# Airflow 3 execution API URL
airflow config get-value core execution_api_server_url
```

Airflow environment variables follow the convention:

``` text
AIRFLOW__<SECTION>__<KEY>
```

For example:

``` text
AIRFLOW__API__PORT=8090
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=...
```

------------------------------------------------------------------------

## 4. Metadata Database

``` bash
# Check database connectivity
airflow db check

# Create/update the metadata database schema
airflow db migrate

# Database command help
airflow db --help
```

A useful first health check is:

``` bash
airflow db check
```

------------------------------------------------------------------------

## 5. List DAGs

``` bash
# List all discovered DAGs
airflow dags list

# DAG command help
airflow dags --help

# List DAG import errors
airflow dags list-import-errors
```

If a newly created DAG does not appear:

``` bash
airflow dags list
airflow dags list-import-errors
```

------------------------------------------------------------------------

## 6. DAG Details

``` bash
# Show DAG details
airflow dags details <dag_id>

# Example
airflow dags details my_spark_dag
```

------------------------------------------------------------------------

## 7. List Tasks in a DAG

``` bash
# List tasks
airflow tasks list <dag_id>

# Example
airflow tasks list my_spark_dag

# Display task dependency tree
airflow tasks list <dag_id> --tree

# Example
airflow tasks list my_spark_dag --tree
```

------------------------------------------------------------------------

## 8. Trigger a DAG

``` bash
# Trigger a DAG manually
airflow dags trigger <dag_id>

# Example
airflow dags trigger my_spark_dag
```

Trigger with configuration:

``` bash
airflow dags trigger <dag_id> \
    --conf '{"key":"value"}'
```

Example:

``` bash
airflow dags trigger my_etl_dag \
    --conf '{"source":"sales","date":"2026-09-15"}'
```

------------------------------------------------------------------------

## 9. Pause and Unpause DAGs

``` bash
# Pause
airflow dags pause <dag_id>

# Unpause
airflow dags unpause <dag_id>
```

Example:

``` bash
airflow dags pause my_spark_dag

airflow dags unpause my_spark_dag
```

------------------------------------------------------------------------

## 10. List DAG Runs

``` bash
# List DAG runs
airflow dags list-runs

# Runs belonging to one DAG
airflow dags list-runs -d <dag_id>

# Example
airflow dags list-runs -d my_spark_dag
```

------------------------------------------------------------------------

## 11. Test a Complete DAG

Useful during DAG development and classroom demonstrations.

``` bash
airflow dags test <dag_id> <logical_date>
```

Example:

``` bash
airflow dags test my_spark_dag 2026-09-15
```

Conceptually:

``` text
airflow dags trigger
        |
        +--> creates a normal DAG run
        +--> scheduler/executor participates

airflow dags test
        |
        +--> development/debugging
        +--> useful for testing the DAG locally
```

------------------------------------------------------------------------

## 12. Test an Individual Task

``` bash
airflow tasks test <dag_id> <task_id> <logical_date>
```

Example:

``` bash
airflow tasks test \
    my_spark_dag \
    submit_spark_job \
    2026-09-15
```

This is one of the most useful commands when developing a DAG because an
individual task can be debugged without waiting for its normal schedule.

------------------------------------------------------------------------

## 13. Check Task State

``` bash
airflow tasks state \
    <dag_id> \
    <task_id> \
    <logical_date>
```

Example:

``` bash
airflow tasks state \
    my_spark_dag \
    submit_spark_job \
    2026-09-15
```

------------------------------------------------------------------------

## 14. DAG Import Errors

Always check this when a DAG file exists but is missing from Airflow.

``` bash
airflow dags list-import-errors
```

Typical causes include:

``` text
Python syntax error
ImportError
ModuleNotFoundError
Missing provider
Incorrect DAG code
Invalid configuration
Dependency/import problem
```

You can also validate the Python file directly:

``` bash
python ~/airflow/dags/my_dag.py
```

Compile-check it:

``` bash
python -m py_compile ~/airflow/dags/my_dag.py
```

------------------------------------------------------------------------

## 15. Airflow Providers

``` bash
# List installed providers
airflow providers list

# Search the provider list
airflow providers list | grep spark
airflow providers list | grep hive
airflow providers list | grep hdfs
airflow providers list | grep livy
airflow providers list | grep mysql
airflow providers list | grep snowflake
```

For the Big Data training setup:

``` bash
airflow providers list | grep -E \
'apache.spark|apache.hive|apache.hdfs|apache.livy|mysql|snowflake'
```

------------------------------------------------------------------------

## 16. Python Package Checks

``` bash
# Dependency consistency
pip check

# Airflow packages
pip list | grep airflow

# Specific packages
pip show apache-airflow
pip show apache-airflow-providers-apache-spark
pip show apache-airflow-providers-apache-hive
pip show apache-airflow-providers-apache-hdfs
pip show apache-airflow-providers-apache-livy
pip show apache-airflow-providers-mysql
pip show apache-airflow-providers-snowflake
```

Verify Airflow from Python:

``` bash
python -c "import airflow; print(airflow.__version__)"
```

------------------------------------------------------------------------

## 17. Airflow Log Directory

Default training setup:

``` bash
echo "$AIRFLOW_HOME/logs"
```

List logs:

``` bash
ls -lah "$AIRFLOW_HOME/logs"
```

Recursively list log files:

``` bash
find "$AIRFLOW_HOME/logs" -type f
```

Find the most recently modified log files:

``` bash
find "$AIRFLOW_HOME/logs" \
    -type f \
    -printf '%T@ %p\n' \
    | sort -nr \
    | head -20
```

------------------------------------------------------------------------

## 18. Read and Follow Task Logs

Read a log:

``` bash
cat /path/to/task.log
```

Read the last 100 lines:

``` bash
tail -n 100 /path/to/task.log
```

Follow the log continuously:

``` bash
tail -f /path/to/task.log
```

Follow the last 100 lines and continue:

``` bash
tail -n 100 -f /path/to/task.log
```

------------------------------------------------------------------------

## 19. Search Airflow Logs for Errors

``` bash
grep -Rni "ERROR" "$AIRFLOW_HOME/logs"
```

Search for common failure indicators:

``` bash
grep -RniE \
    "ERROR|FAILED|Exception|Traceback" \
    "$AIRFLOW_HOME/logs"
```

Search for a specific task:

``` bash
grep -Rni "submit_spark_job" "$AIRFLOW_HOME/logs"
```

Search for Spark errors:

``` bash
grep -RniE \
    "SparkException|Py4J|AnalysisException|ERROR" \
    "$AIRFLOW_HOME/logs"
```

------------------------------------------------------------------------

## 20. Airflow systemd Service

For the training VM where Airflow runs as `airflow.service`:

``` bash
# Status
sudo systemctl status airflow --no-pager

# Start
sudo systemctl start airflow

# Stop
sudo systemctl stop airflow

# Restart
sudo systemctl restart airflow

# Enable at boot
sudo systemctl enable airflow

# Disable at boot
sudo systemctl disable airflow
```

Check whether it is active:

``` bash
systemctl is-active airflow
```

Check whether it is enabled:

``` bash
systemctl is-enabled airflow
```

------------------------------------------------------------------------

## 21. systemd Airflow Logs

Recent logs:

``` bash
sudo journalctl -u airflow --no-pager -n 100
```

Follow logs:

``` bash
sudo journalctl -u airflow -f
```

Logs from the current boot:

``` bash
sudo journalctl -u airflow -b
```

Logs from the last hour:

``` bash
sudo journalctl -u airflow \
    --since "1 hour ago"
```

Logs since today:

``` bash
sudo journalctl -u airflow \
    --since today
```

Show errors:

``` bash
sudo journalctl -u airflow \
    -p err \
    --no-pager
```

------------------------------------------------------------------------

## 22. After Changing airflow.service

If `/etc/systemd/system/airflow.service` is modified:

``` bash
sudo systemctl daemon-reload

sudo systemctl restart airflow

sudo systemctl status airflow --no-pager
```

Then inspect logs:

``` bash
sudo journalctl -u airflow -n 100 --no-pager
```

Changing only a DAG normally does **not** require restarting the Airflow
service.

------------------------------------------------------------------------

## 23. Check Airflow Processes

``` bash
ps aux | grep '[a]irflow'
```

Alternative:

``` bash
pgrep -af airflow
```

------------------------------------------------------------------------

## 24. Check Airflow Port

This training setup uses port `8090`.

``` bash
sudo ss -ltnp | grep 8090
```

You specifically want Airflow bound to loopback:

``` text
127.0.0.1:8090
```

Do **not** expose the insecure training configuration as:

``` text
0.0.0.0:8090
```

------------------------------------------------------------------------

## 25. Test Airflow Locally

``` bash
curl -I http://127.0.0.1:8090
```

More verbose troubleshooting:

``` bash
curl -v http://127.0.0.1:8090
```

------------------------------------------------------------------------

## 26. Nginx Reverse Proxy Checks

Validate Nginx configuration:

``` bash
sudo nginx -t
```

Status:

``` bash
sudo systemctl status nginx --no-pager
```

Restart:

``` bash
sudo systemctl restart nginx
```

Nginx logs:

``` bash
sudo journalctl -u nginx -n 100 --no-pager
```

Follow Nginx logs:

``` bash
sudo journalctl -u nginx -f
```

Test the Airflow proxy:

``` bash
curl -I "https://$(hostname -f)/airflow/"
```

------------------------------------------------------------------------

## 27. Check Airflow Runtime Environment

``` bash
echo "AIRFLOW_HOME=$AIRFLOW_HOME"
echo "JAVA_HOME=$JAVA_HOME"
echo "HADOOP_HOME=$HADOOP_HOME"
echo "HIVE_HOME=$HIVE_HOME"
echo "SPARK_HOME=$SPARK_HOME"
echo "LIVY_HOME=$LIVY_HOME"
```

Check executables:

``` bash
command -v python
command -v airflow
command -v java
command -v hdfs
command -v yarn
command -v hive
command -v spark-submit
```

------------------------------------------------------------------------

## 28. Check Runtime as the systemd User

For the training VM user `cloud_user`:

``` bash
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

------------------------------------------------------------------------

## 29. Verify External Big Data Tools

Java:

``` bash
java -version
```

Hadoop:

``` bash
hadoop version
hdfs version
```

HDFS:

``` bash
hdfs dfs -ls /
```

YARN:

``` bash
yarn version
yarn node -list
```

Hive:

``` bash
hive --version
```

Spark:

``` bash
spark-submit --version
```

Livy process/port checks can be performed according to the Livy
installation used in the training environment.

------------------------------------------------------------------------

## 30. Useful DAG Development Workflow

After creating or modifying a DAG:

``` bash
# 1. Check Python syntax
python -m py_compile ~/airflow/dags/my_dag.py

# 2. Check whether Airflow imported it
airflow dags list

# 3. Check import failures
airflow dags list-import-errors

# 4. Inspect tasks
airflow tasks list my_dag

# 5. Inspect dependency tree
airflow tasks list my_dag --tree

# 6. Test one task
airflow tasks test my_dag my_task 2026-09-15

# 7. Test complete DAG
airflow dags test my_dag 2026-09-15

# 8. Trigger normal run
airflow dags trigger my_dag

# 9. Inspect DAG runs
airflow dags list-runs -d my_dag

# 10. Inspect logs
grep -RniE \
    "ERROR|FAILED|Exception|Traceback" \
    "$AIRFLOW_HOME/logs"
```

------------------------------------------------------------------------

## 31. Spark DAG Troubleshooting Workflow

When an Airflow Spark task fails:

``` bash
# Airflow sees the DAG?
airflow dags list

# DAG import problem?
airflow dags list-import-errors

# Spark provider installed?
airflow providers list | grep spark

# spark-submit available?
command -v spark-submit

# Spark version?
spark-submit --version

# Java available?
java -version

# Airflow service log
sudo journalctl -u airflow -n 200 --no-pager

# Search task logs
grep -RniE \
    "SparkException|Py4J|AnalysisException|Exception|ERROR" \
    "$AIRFLOW_HOME/logs"
```

------------------------------------------------------------------------

## 32. Hive/HDFS Troubleshooting

``` bash
# Provider checks
airflow providers list | grep hive
airflow providers list | grep hdfs

# Hadoop/HDFS executables
command -v hadoop
command -v hdfs

# Hive executable
command -v hive

# HDFS access
hdfs dfs -ls /

# Hive version
hive --version

# Airflow service logs
sudo journalctl -u airflow -n 200 --no-pager
```

------------------------------------------------------------------------

## 33. Snowflake Provider Check

``` bash
airflow providers list | grep snowflake
```

Python package:

``` bash
pip show apache-airflow-providers-snowflake
```

Check all Airflow-related Snowflake packages:

``` bash
pip list | grep -i snowflake
```

------------------------------------------------------------------------

## 34. MySQL Metadata Database Troubleshooting

Check Airflow database:

``` bash
airflow db check
```

Check configured connection:

``` bash
airflow config get-value database sql_alchemy_conn
```

Check MySQL service:

``` bash
sudo systemctl status mysql --no-pager
```

Connect manually:

``` bash
mysql -u airflow -p airflow_db
```

Inside MySQL:

``` sql
SHOW TABLES;
```

------------------------------------------------------------------------

## 35. File and Directory Checks

``` bash
# Airflow home
ls -lah "$AIRFLOW_HOME"

# DAGs
ls -lah "$AIRFLOW_HOME/dags"

# Logs
ls -lah "$AIRFLOW_HOME/logs"

# Plugins
ls -lah "$AIRFLOW_HOME/plugins"

# Scripts
ls -lah "$AIRFLOW_HOME/scripts"
```

Expected training structure:

``` text
~/airflow/
├── dags/
├── logs/
├── plugins/
└── scripts/
```

------------------------------------------------------------------------

## 36. Quick Health Check

Run these when you first log in:

``` bash
airflow version

airflow db check

airflow dags list

airflow dags list-import-errors

sudo systemctl status airflow --no-pager

sudo ss -ltnp | grep 8090
```

------------------------------------------------------------------------

## 37. Essential Student Command Set

These are the commands worth memorizing first:

``` bash
# Installation
airflow version

# Database
airflow db check

# DAG discovery
airflow dags list
airflow dags list-import-errors

# DAG structure
airflow tasks list <dag_id>
airflow tasks list <dag_id> --tree

# Testing
airflow tasks test <dag_id> <task_id> <logical_date>
airflow dags test <dag_id> <logical_date>

# Run
airflow dags trigger <dag_id>

# Runs
airflow dags list-runs -d <dag_id>

# Service
sudo systemctl status airflow --no-pager

# Live service logs
sudo journalctl -u airflow -f

# Search task logs
grep -RniE \
    "ERROR|FAILED|Exception|Traceback" \
    "$AIRFLOW_HOME/logs"

# Port
sudo ss -ltnp | grep 8090
```

------------------------------------------------------------------------

## 38. Practical Airflow Debugging Order

When something does not work, debug in this order:

``` text
1. Is Airflow installed?
       airflow version

2. Is metadata DB reachable?
       airflow db check

3. Is DAG discovered?
       airflow dags list

4. Is there an import error?
       airflow dags list-import-errors

5. Are expected tasks present?
       airflow tasks list <dag_id> --tree

6. Can the individual task run?
       airflow tasks test ...

7. Can the DAG run in test mode?
       airflow dags test ...

8. Can a normal DAG run be triggered?
       airflow dags trigger ...

9. What happened to the run?
       airflow dags list-runs -d <dag_id>

10. What do the logs say?
       sudo journalctl -u airflow -f
       grep -RniE "ERROR|FAILED|Exception|Traceback" "$AIRFLOW_HOME/logs"

11. Is Airflow listening on the expected interface/port?
       sudo ss -ltnp | grep 8090
```

------------------------------------------------------------------------

# Quick Reference

``` bash
airflow version
airflow db check

airflow dags list
airflow dags list-import-errors
airflow dags details <dag_id>
airflow dags trigger <dag_id>
airflow dags list-runs -d <dag_id>
airflow dags pause <dag_id>
airflow dags unpause <dag_id>
airflow dags test <dag_id> <logical_date>

airflow tasks list <dag_id>
airflow tasks list <dag_id> --tree
airflow tasks test <dag_id> <task_id> <logical_date>
airflow tasks state <dag_id> <task_id> <logical_date>

airflow providers list

airflow config get-value core dags_folder
airflow config get-value core executor
airflow config get-value database sql_alchemy_conn
airflow config get-value api host
airflow config get-value api port

sudo systemctl status airflow --no-pager
sudo systemctl restart airflow
sudo journalctl -u airflow -f

find "$AIRFLOW_HOME/logs" -type f
grep -RniE "ERROR|FAILED|Exception|Traceback" "$AIRFLOW_HOME/logs"

sudo ss -ltnp | grep 8090
ps aux | grep '[a]irflow'
```
