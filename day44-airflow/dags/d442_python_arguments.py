"""Pass two CLI arguments -> parse a dictionary -> pass its sum to another program.
Run: airflow dags test d447_python_arguments --conf '{"a":2,"b":3}'
Expected dictionary: {"input": 5, "factor": 10, "result": 50}.
Deploy programs to ~/D44_DAG/programs; see ../PYTHON_BASICS.md.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import subprocess
import sys
from airflow.sdk import DAG, Param, task

with DAG(
    "d447_python_arguments", schedule=None, catchup=False, max_active_runs=1,
    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc), doc_md=__doc__,
    params={"a": Param(2, type="integer"), "b": Param(3, type="integer")},
    tags=["d44", "python_basics"],
) as dag:
    @task(multiple_outputs=False)
    def add(params=None):
        # Argument list avoids shell quoting. Nonzero exit raises and fails this task.
        result = subprocess.run(
            [sys.executable, str(Path.home() / "D44_DAG/programs/add.py"),
             "--a", str(params["a"]), "--b", str(params["b"])],
            capture_output=True, text=True, check=True, timeout=30,
        )
        value = json.loads(result.stdout)
        print("Returned dictionary:", value)
        return value  # Airflow stores this small dictionary in XCom (return_value).

    @task(multiple_outputs=False)
    def multiply(previous):
        # Airflow resolves the upstream XCom into a real Python dict automatically.
        result = subprocess.run(
            [sys.executable, str(Path.home() / "D44_DAG/programs/multiply.py"),
             "--value", str(previous["sum"]), "--factor", "10"],
            capture_output=True, text=True, check=True, timeout=30,
        )
        value = json.loads(result.stdout)
        print("Final dictionary:", value)
        return value

    multiply(add())  # Also declares add -> multiply dependency.
