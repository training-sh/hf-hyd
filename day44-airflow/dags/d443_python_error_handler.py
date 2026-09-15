"""A second DAG receives the failed program's report through dag_run.conf.
Normally triggered by d448_python_exit_branch. Manual example:
airflow dags test d449_python_error_handler --conf '{"report":{"returncode":7,"stderr":"Example failure"}}'
See ../PYTHON_BASICS.md. This example only prints; it sends no notifications.
"""
from datetime import datetime, timezone
from airflow.sdk import DAG, task

with DAG(
    "d449_python_error_handler", schedule=None, catchup=False, is_paused_upon_creation=False,
    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc), doc_md=__doc__,
    tags=["d44", "python_basics"],
) as dag:
    @task
    def print_error(dag_run=None):
        report = dag_run.conf.get("report", {})
        print("Error handler received:", report)
        print("Exit code:", report.get("returncode"))
        print("Details:", report.get("stderr"))
        return {"handled": True, "returncode": report.get("returncode")}

    print_error()
