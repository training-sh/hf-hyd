"""06 - Hadoop Pi estimation on YARN

Two maps with 1000 samples each keep the example small. The result should be near 3.14; this is an estimate, not an exact equality test. The Hadoop example manages its own temporary HDFS files.

Run from Ubuntu after activating dataengenv:
    airflow dags test d445_mapreduce_pi
Or unpause and trigger d445_mapreduce_pi manually in the Airflow UI.
There is no schedule; retries are disabled so failures remain visible.
"""
from datetime import datetime, timezone, timedelta
from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator

# Explicit environment: Airflow tasks do not run an interactive .bashrc.
ENV = {
    "JAVA_HOME": "/usr/lib/jvm/java-11-openjdk-amd64",
    "HADOOP_HOME": "/opt/hadoop",
    "HADOOP_CONF_DIR": "/opt/hadoop/etc/hadoop",
    "HADOOP_MAPRED_HOME": "/opt/hadoop",
    "D44_RUN_ID": "{{ run_id }}",  # Pass templated values through env, not shell code.
}

PREFIX = r'''set -euo pipefail
export PATH="$JAVA_HOME/bin:$HADOOP_HOME/bin:$PATH"
RUN_KEY=$(printf '%s' "$D44_RUN_ID" | sha256sum | cut -c1-12)
STAGE="$HOME/d44_stage/06_pi/$RUN_KEY"
HDFS_STAGE="/user/$USER/d44_stage/06_pi/$RUN_KEY"
'''

with DAG(
    dag_id='d445_mapreduce_pi',
    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
    schedule=None, catchup=False, max_active_runs=1,
    default_args={"retries": 0, "execution_timeout": timedelta(minutes=10)},
    tags=["d44", "06_pi"], doc_md=__doc__,
) as dag:
    # The two positional arguments are number of maps and samples per map.
    estimate_pi = BashOperator(
        task_id='estimate_pi', append_env=True, env=ENV,
        bash_command=PREFIX + r'''
mkdir -p "$STAGE"
hadoop jar "$HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.6.jar" pi 2 1000 | tee "$STAGE/pi.txt"
''',
    )

    # Check that the result exists and is within a broad sensible range.
    check_estimate = BashOperator(
        task_id='check_estimate', append_env=True, env=ENV,
        bash_command=PREFIX + r'''
awk '/Estimated value of Pi is/ {seen=1; value=$NF; print "Pi estimate:", value} END {exit !(seen && value>3.0 && value<3.3)}' "$STAGE/pi.txt"
''',
    )

    estimate_pi >> check_estimate
