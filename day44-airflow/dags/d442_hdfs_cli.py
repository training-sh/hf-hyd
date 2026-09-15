"""03 - HDFS file operations using BashOperator

Requires running HDFS. Demonstrates put, ls, cat, cp, get and rm. HDFS paths are distinct from Linux paths.

Run from Ubuntu after activating dataengenv:
    airflow dags test d442_hdfs_cli
Or unpause and trigger d442_hdfs_cli manually in the Airflow UI.
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
STAGE="$HOME/d44_stage/03_hdfs_cli/$RUN_KEY"
HDFS_STAGE="/user/$USER/d44_stage/03_hdfs_cli/$RUN_KEY"
'''

with DAG(
    dag_id='d442_hdfs_cli',
    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
    schedule=None, catchup=False, max_active_runs=1,
    default_args={"retries": 0, "execution_timeout": timedelta(minutes=10)},
    tags=["d44", "03_hdfs_cli"], doc_md=__doc__,
) as dag:
    # Create a local input using tee.
    prepare_local = BashOperator(
        task_id='prepare_local', append_env=True, env=ENV,
        bash_command=PREFIX + r'''
mkdir -p "$STAGE"
printf '%s\n' 'hello hdfs' 'hello airflow' | tee "$STAGE/message.txt" >/dev/null
''',
    )

    # Create an HDFS directory and upload the local file.
    upload = BashOperator(
        task_id='upload', append_env=True, env=ENV,
        bash_command=PREFIX + r'''
hdfs dfs -mkdir -p "$HDFS_STAGE"
hdfs dfs -put -f "$STAGE/message.txt" "$HDFS_STAGE/message.txt"
''',
    )

    # ls reads NameNode metadata; cat below reads the file data.
    list_hdfs = BashOperator(
        task_id='list_hdfs', append_env=True, env=ENV,
        bash_command=PREFIX + r'''
hdfs dfs -ls "$HDFS_STAGE"
''',
    )

    # Read the HDFS file into the task log.
    read_hdfs = BashOperator(
        task_id='read_hdfs', append_env=True, env=ENV,
        bash_command=PREFIX + r'''
hdfs dfs -cat "$HDFS_STAGE/message.txt"
''',
    )

    # Copy from one HDFS path to another, without downloading.
    copy_within_hdfs = BashOperator(
        task_id='copy_within_hdfs', append_env=True, env=ENV,
        bash_command=PREFIX + r'''
hdfs dfs -cp -f "$HDFS_STAGE/message.txt" "$HDFS_STAGE/message-copy.txt"
''',
    )

    # get writes a local runtime output; compare it with the input.
    download = BashOperator(
        task_id='download', append_env=True, env=ENV,
        bash_command=PREFIX + r'''
hdfs dfs -get -f "$HDFS_STAGE/message-copy.txt" "$STAGE/downloaded.txt"
cmp "$STAGE/message.txt" "$STAGE/downloaded.txt"
''',
    )

    # Delete only the staged HDFS copy; keep the original and download.
    delete_hdfs_copy = BashOperator(
        task_id='delete_hdfs_copy', append_env=True, env=ENV,
        bash_command=PREFIX + r'''
hdfs dfs -rm -f "$HDFS_STAGE/message-copy.txt"
if hdfs dfs -test -e "$HDFS_STAGE/message-copy.txt"; then exit 1; fi
hdfs dfs -ls "$HDFS_STAGE"
''',
    )

    prepare_local >> upload >> list_hdfs >> read_hdfs >> copy_within_hdfs >> download >> delete_hdfs_copy
