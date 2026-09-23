"""05 - MapReduce word count on YARN

Requires HDFS and YARN. Expected counts: airflow=2, hadoop=2, yarn=1. MapReduce uses the configured YARN framework; it is not a separate cluster mode.

Run from Ubuntu after activating dataengenv:
    airflow dags test d444_mapreduce_wordcount
Or unpause and trigger d444_mapreduce_wordcount manually in the Airflow UI.
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
STAGE="$HOME/d44_stage/05_wordcount/$RUN_KEY"
HDFS_STAGE="/user/$USER/d44_stage/05_wordcount/$RUN_KEY"
'''

with DAG(
    dag_id='d444_mapreduce_wordcount',
    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
    schedule=None, catchup=False, max_active_runs=1,
    default_args={"retries": 0, "execution_timeout": timedelta(minutes=10)},
    tags=["d44", "05_wordcount"], doc_md=__doc__,
) as dag:
    # Three tiny lines are enough for the complete MapReduce path.
    prepare_input = BashOperator(
        task_id='prepare_input', append_env=True, env=ENV,
        bash_command=PREFIX + r'''
mkdir -p "$STAGE"
printf '%s\n' 'airflow hadoop' 'airflow yarn' 'hadoop' | tee "$STAGE/words.txt" >/dev/null
hdfs dfs -mkdir -p "$HDFS_STAGE/input"
hdfs dfs -put -f "$STAGE/words.txt" "$HDFS_STAGE/input/words.txt"
''',
    )

    # Hadoop requires an absent output directory. Remove only this run's generated output on a manual task rerun.
    run_wordcount = BashOperator(
        task_id='run_wordcount', append_env=True, env=ENV,
        bash_command=PREFIX + r'''
if hdfs dfs -test -e "$HDFS_STAGE/output"; then
  hdfs dfs -rm -r "$HDFS_STAGE/output"
fi
hadoop jar "$HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.6.jar" wordcount "$HDFS_STAGE/input" "$HDFS_STAGE/output"
''',
    )

    # Job submission waits for completion; also verify the actual results.
    read_and_check = BashOperator(
        task_id='read_and_check', append_env=True, env=ENV,
        bash_command=PREFIX + r'''
hdfs dfs -cat "$HDFS_STAGE/output/part-r-*" | tee "$STAGE/counts.txt"
grep -qxF "$(printf 'airflow\t2')" "$STAGE/counts.txt"
grep -qxF "$(printf 'hadoop\t2')" "$STAGE/counts.txt"
grep -qxF "$(printf 'yarn\t1')" "$STAGE/counts.txt"
''',
    )

    prepare_input >> run_wordcount >> read_and_check
