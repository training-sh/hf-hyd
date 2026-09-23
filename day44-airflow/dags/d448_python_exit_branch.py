"""Capture a child program's exit status, then choose a success task or error DAG.
Run: airflow dags test d448_python_exit_branch --conf '{"mode":"success"}'
Use mode "exit" for sys.exit(7), "crash" for an exception (exit 1).
Failures trigger d449_python_error_handler; success prints a message.
See ../PYTHON_BASICS.md. Triggering the handler creates a real DAG run.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import subprocess
import sys
from airflow.sdk import DAG, Param, task
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator

with DAG(
    "d448_python_exit_branch", schedule=None, catchup=False, max_active_runs=1,
    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc), doc_md=__doc__,
    render_template_as_native_obj=True,
    params={"mode": Param("success", enum=["success", "exit", "crash"])},
    tags=["d44", "python_basics"],
) as dag:
    @task(multiple_outputs=False)
    def run_program(params=None):
        # check=False lets Airflow inspect a nonzero status instead of failing here.
        # Timeout/missing executable errors are not child exit statuses and still fail the task.
        result = subprocess.run(
            [sys.executable, str(Path.home() / "D44_DAG/programs/maybe_fail.py"),
             "--mode", params["mode"]],
            capture_output=True, text=True, check=False, timeout=30,
        )
        report = {"mode": params["mode"], "returncode": result.returncode,
                  "output": json.loads(result.stdout) if result.returncode == 0 else None,
                  "stderr": result.stderr.strip()}
        print(report)
        return report

    @task.branch
    def choose(report):
        return "success_message" if report["returncode"] == 0 else "trigger_error_dag"

    @task
    def success_message(report):
        print("Success path:", report["output"])

    report = run_program()
    branch = choose(report)
    success = success_message(report)
    failure = TriggerDagRunOperator(
        task_id="trigger_error_dag", trigger_dag_id="d449_python_error_handler",
        conf={"report": "{{ ti.xcom_pull(task_ids='run_program') }}"},
        # The scheduler executes the handler independently. This task only triggers it.
        wait_for_completion=False,
    )
    branch >> [success, failure]
