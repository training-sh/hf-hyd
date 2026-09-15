"""02 - Files in a local staging directory

Uses ~/d44_stage/02_local/<run-key>. The original file is kept; only the copied file is deleted.

Run from Ubuntu after activating dataengenv:
    airflow dags test d441_local_files
Or unpause and trigger d441_local_files manually in the Airflow UI.
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
STAGE="$HOME/d44_stage/02_local/$RUN_KEY"
HDFS_STAGE="/user/$USER/d44_stage/02_local/$RUN_KEY"
'''

with DAG(
    dag_id='d441_local_files',
    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
    schedule=None, catchup=False, max_active_runs=1,
    default_args={"retries": 0, "execution_timeout": timedelta(minutes=10)},
    tags=["d44", "02_local"], doc_md=__doc__,
) as dag:
    # tee writes a small file; no shared course files are used.
    create = BashOperator(
        task_id='create', append_env=True, env=ENV,
        bash_command=PREFIX + r'''
mkdir -p "$STAGE"
printf '%s\n' 'hello airflow' | tee "$STAGE/message.txt" >/dev/null
''',
    )

    # tee -a adds a second line.
    append = BashOperator(
        task_id='append', append_env=True, env=ENV,
        bash_command=PREFIX + r'''
printf '%s\n' 'hello bash' | tee -a "$STAGE/message.txt" >/dev/null
''',
    )

    # List the local directory.
    list_files = BashOperator(
        task_id='list_files', append_env=True, env=ENV,
        bash_command=PREFIX + r'''
ls -lh "$STAGE"
''',
    )

    # Expect two lines.
    read_file = BashOperator(
        task_id='read_file', append_env=True, env=ENV,
        bash_command=PREFIX + r'''
cat "$STAGE/message.txt"
test "$(wc -l < "$STAGE/message.txt")" -eq 2
''',
    )

    # Copy the bytes through tee, then compare both files.
    copy_file = BashOperator(
        task_id='copy_file', append_env=True, env=ENV,
        bash_command=PREFIX + r'''
tee "$STAGE/message-copy.txt" < "$STAGE/message.txt" >/dev/null
cmp "$STAGE/message.txt" "$STAGE/message-copy.txt"
''',
    )

    # Delete only the fixed copy created by the previous task.
    delete_copy = BashOperator(
        task_id='delete_copy', append_env=True, env=ENV,
        bash_command=PREFIX + r'''
rm -f -- "$STAGE/message-copy.txt"
test ! -e "$STAGE/message-copy.txt"
ls -lh "$STAGE"
''',
    )

    create >> append >> list_files >> read_file >> copy_file >> delete_copy
