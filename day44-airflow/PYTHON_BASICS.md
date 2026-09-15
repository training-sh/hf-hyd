# Python arguments, results and failure paths

Three small DAGs use the standalone programs in `programs/`. No Spark or Hadoop is involved.

- `d447_python_arguments`: `add.py --a 2 --b 3` prints `{"a":2,"b":3,"sum":5}`. Airflow parses JSON and returns a dict through XCom. The next task passes `--value 5 --factor 10` to `multiply.py`, which returns `{"input":5,"factor":10,"result":50}`.
- `d448_python_exit_branch`: runs `maybe_fail.py`, captures its status, and branches. Success prints a message; failure triggers a separate DAG.
- `d449_python_error_handler`: receives the report through `dag_run.conf` and prints it.

A separate process cannot return a Python dict directly to its caller: it prints JSON, and the caller uses `json.loads`. XCom carries the resulting small dict between Airflow tasks. The next program receives the needed value as a normal CLI argument. Keep diagnostic prints on stderr when stdout contains JSON.

## Run the programs directly

```bash
source ~/dataengenv/bin/activate
cd ~/D44_DAG
python programs/add.py --a 2 --b 3
python programs/multiply.py --value 5 --factor 10
python programs/maybe_fail.py --mode success
python programs/maybe_fail.py --mode exit
echo "Exit code: $?"  # 7; read immediately after the program
python programs/maybe_fail.py --mode crash
echo "Exit code: $?"  # 1; stderr contains the traceback
```

## Deploy and run the DAGs

Copy `programs/` to `~/D44_DAG/programs` on the Airflow machine, then deploy:

```bash
DAG_DIR=$(airflow config get-value core dags_folder)
mkdir -p "$DAG_DIR/d44_course"
for file in "$HOME/D44_DAG/dags/"d44[789]*.py; do
  tee "$DAG_DIR/d44_course/${file##*/}" < "$file" >/dev/null
done
# Wait until Airflow discovers all three DAGs. Keep scheduler/DAG processor running.
airflow dags unpause d449_python_error_handler
airflow dags test d447_python_arguments --conf '{"a":2,"b":3}'
airflow dags test d448_python_exit_branch --conf '{"mode":"success"}'
airflow dags test d448_python_exit_branch --conf '{"mode":"exit"}'
airflow dags test d448_python_exit_branch --conf '{"mode":"crash"}'
```

You can also trigger them in the UI; use its parameters form to change `a`, `b`, or `mode`. Inspect task logs and XCom `return_value`. The unselected branch is **skipped**. For failure cases, open the triggered `d449_python_error_handler` run to see its report.

`check=True` in the first example raises on a nonzero exit: that task fails and its normal downstream task does not run. `check=False` in the branching example captures the child's failure as data, so its Airflow task succeeds and the branch can execute. The parent DAG can therefore succeed even though the child program failed. It does not wait for the error-handler DAG to finish.

An unhandled exception normally exits with code 1, but code 1 alone does not prove a crash; inspect stderr. `sys.exit(7)` deliberately returns 7. A timeout, Airflow worker crash, or missing executable is a different failure and is not handled by this simple exit-code branch. Each child process has a 30-second timeout. These examples assume programs are installed on the same Airflow worker.

## Validation

Program tests passed: sum 5, final result 50, exit codes 0/7/1. On the VM, `airflow dags test` passed for d447, all three d448 modes, and d449 with a sample error report. The two failure branches created real handler DAG runs, but their scheduler-driven completion remained pending when checked. Direct handler execution passed. Logs: `~/d44_stage/test-logs/d447.log`, `d448-{success,exit,crash}.log`, and `d449.log`.
