"""04 - HDFS operations through an Airflow hook-backed operator.

Run: airflow dags test d443_hdfs_operator
Or unpause and manually trigger this DAG in the Airflow UI.
Requires d44_webhdfs: type webhdfs, host localhost, port 9870, login cloud_user.

The installed HDFS provider has WebHDFSHook, not a generic HDFS file operator.
HdfsFileOperator below is our small custom operator, not a built-in provider class.
Compare these tasks with the hdfs CLI tasks in d442_hdfs_cli.py.
"""
from datetime import datetime, timezone, timedelta
import getpass
import hashlib
from pathlib import Path

from airflow.sdk import DAG, BaseOperator
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.apache.hdfs.hooks.webhdfs import WebHDFSHook


class HdfsFileOperator(BaseOperator):
    """One small file action per task. Only this DAG's staging files are touched."""

    def __init__(self, *, action, **kwargs):
        super().__init__(**kwargs)
        self.action = action

    def execute(self, context):
        # The same run key as the preceding Bash task; avoids shared fixed outputs.
        key = hashlib.sha256(context["run_id"].encode()).hexdigest()[:12]
        local = Path.home() / "d44_stage" / "04_hdfs_operator" / key
        directory = f"/user/{getpass.getuser()}/d44_stage/04_hdfs_operator/{key}"
        original = directory + "/message.txt"
        copied = directory + "/message-copy.txt"
        client = WebHDFSHook(webhdfs_conn_id="d44_webhdfs").get_conn()

        if self.action == "upload":
            client.makedirs(directory)
            client.upload(original, str(local / "message.txt"), overwrite=True)
            self.log.info("Uploaded local file to %s", original)
        elif self.action == "list":
            self.log.info("Files: %s", client.list(directory))
        elif self.action == "read":
            with client.read(original, encoding="utf-8") as stream:
                content = stream.read()
            self.log.info("Content: %s", content)
            assert content == "hello webhdfs\nhello airflow\n"
        elif self.action == "copy":
            # WebHDFS has no generic cp call: read/write is adequate for this tiny file.
            # Use the HDFS CLI or a distributed copy tool for large copy workloads.
            with client.read(original, encoding="utf-8") as stream:
                content = stream.read()
            client.write(copied, data=content, encoding="utf-8", overwrite=True)
            self.log.info("Copied to %s", copied)
        elif self.action == "download":
            client.download(copied, str(local / "downloaded.txt"), overwrite=True)
            assert (local / "downloaded.txt").read_bytes() == (local / "message.txt").read_bytes()
            self.log.info("Downloaded bytes match the original")
        elif self.action == "delete":
            client.delete(copied)  # Never delete the staging root or the source dataset.
            assert client.status(copied, strict=False) is None
            self.log.info("Deleted only %s", copied)
        else:
            raise ValueError(f"Unknown action: {self.action}")


with DAG(
    dag_id="d443_hdfs_operator",
    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
    schedule=None, catchup=False, max_active_runs=1,
    default_args={"retries": 0, "execution_timeout": timedelta(minutes=3)},
    tags=["d44", "webhdfs"], doc_md=__doc__,
) as dag:
    prepare_local = BashOperator(
        task_id="prepare_local", append_env=True,
        env={"D44_RUN_ID": "{{ run_id }}"},
        bash_command=r'''
set -euo pipefail
RUN_KEY=$(printf '%s' "$D44_RUN_ID" | sha256sum | cut -c1-12)
STAGE="$HOME/d44_stage/04_hdfs_operator/$RUN_KEY"
mkdir -p "$STAGE"
printf '%s\n' 'hello webhdfs' 'hello airflow' | tee "$STAGE/message.txt" >/dev/null
''',
    )
    upload = HdfsFileOperator(task_id="upload", action="upload")
    list_files = HdfsFileOperator(task_id="list_files", action="list")
    read_file = HdfsFileOperator(task_id="read_file", action="read")
    copy_file = HdfsFileOperator(task_id="copy_file", action="copy")
    download = HdfsFileOperator(task_id="download", action="download")
    delete_copy = HdfsFileOperator(task_id="delete_copy", action="delete")

    prepare_local >> upload >> list_files >> read_file >> copy_file >> download >> delete_copy
