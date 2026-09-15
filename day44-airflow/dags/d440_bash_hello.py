"""01 - Two Bash tasks

Read task stdout in the Airflow task log. Expected: a greeting, username and Java 11.

Run from Ubuntu after activating dataengenv:
    airflow dags test d440_bash_hello
Or unpause and trigger d440_bash_hello manually in the Airflow UI.
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
STAGE="$HOME/d44_stage/01_hello/$RUN_KEY"
HDFS_STAGE="/user/$USER/d44_stage/01_hello/$RUN_KEY"
'''

with DAG(
    dag_id='d440_bash_hello',
    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
    schedule=None, catchup=False, max_active_runs=1,
    default_args={"retries": 0, "execution_timeout": timedelta(minutes=10)},
    tags=["d44", "01_hello"], doc_md=__doc__,
) as dag:
    # One task runs one shell command.
    hello = BashOperator(
        task_id='hello', append_env=True, env=ENV,
        bash_command=PREFIX + r'''
printf 'Hello from Airflow!\n'
''',
    )

    # The arrow makes this task wait for hello.
    environment = BashOperator(
        task_id='environment', append_env=True, env=ENV,
        bash_command=PREFIX + r'''
whoami
python --version
java -version
''',
    )

    hello >> environment
