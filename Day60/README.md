# Day60: Streamlit and DuckDB over a local Hadoop data lake

## What students download

Download `Day60-student.zip` and extract it on the Linux machine where your local
HDFS cluster is running. **No data directory is needed.** Setup generates all
sample data, creates the Delta/Iceberg tables and uploads the HDFS datasets.
Generate Iceberg data locally because its metadata records filesystem locations.

The complete setup uses **15 required files**:

| File | Purpose |
|---|---|
| `README.md` | Step-by-step instructions |
| `requirements.txt` | Python package dependencies |
| `env.sh.example` | Editable Hadoop and dashboard configuration template |
| `config.py` | Discover Hadoop client, NameNode URI, username and lab paths |
| `app.py` | Streamlit dashboard |
| `native_access.py` | DuckDB source readers and parameterized SQL filters |
| `iceberg_hdfs_io.py` | Explicit HDFS-to-WebHDFS transport adapter |
| `stage_data.py` | Generate 5,000 fictional sales rows as CSV and Parquet |
| `stage_native.py` | Create partitioned Parquet, Linux Delta/Iceberg, HDFS copies |
| `probe_extensions.py` | Install and test DuckDB extensions |
| `probe_storage.py` | Record whether Delta's reader supports HDFS |
| `test_iceberg_hdfs.py` | Create and verify HDFS Iceberg, snapshots and pruning |
| `verify.py` | Verify all working sources and dashboard controls |
| `setup.sh` | Run the full installation, staging and checks |
| `start.sh` | Start the dashboard in the foreground |

The ZIP contains **18 files total**, including three optional conveniences:
`launch.sh` (background start), `restart.sh` (checked restart), and
`requirements.lock.txt` (Python versions from a successful reference run).
After setup, many additional files appear under `data/` and in HDFS; they are
outputs rather than files students must download.

## 1. Prerequisites

Use a Linux machine with Python 3.12, pip/venv, Java and an already running HDFS
NameNode and DataNode. WebHDFS must be enabled, and the current Hadoop user must
be allowed to create its lab directory. Internet access is needed for pip and
DuckDB extension installation. Spark, MySQL, SSH keys and Tailscale are not
required by this lab. This package targets a local non-Kerberos teaching cluster.

Unzip the package and open a terminal inside the extracted directory. For example:

```bash
unzip Day60-student.zip -d Day60
cd Day60
python3 --version
```

## 2. Configure your own Hadoop installation

```bash
cp env.sh.example env.sh
# Edit env.sh using your preferred text editor.
source env.sh
```

Defaults:

- Hadoop executable: `hdfs` on PATH; otherwise `$HADOOP_HOME/bin/hdfs` or
  `/opt/hadoop/bin/hdfs` as a conventional fallback.
- NameNode URI: discovered using `hdfs getconf -confKey fs.defaultFS`.
- Hadoop user: `$HADOOP_USER_NAME`, otherwise the current OS username.
- HDFS lab directory: `/user/<your-username>/day60`.
- WebHDFS: `localhost:9870`.
- Streamlit: `127.0.0.1:8501`.

Uncomment/edit settings in `env.sh` if yours differ. Example settings:

```bash
export HADOOP_HOME=/path/to/your/hadoop
export HADOOP_CONF_DIR="$HADOOP_HOME/etc/hadoop"
export HDFS_BIN="$HADOOP_HOME/bin/hdfs"
export HDFS_URI=hdfs://localhost:9000
export HADOOP_USER_NAME="$(id -un)"
export DAY60_HDFS_BASE="/user/$(id -un)/day60"
export WEBHDFS_HOST=localhost
export WEBHDFS_PORT=9870
export STREAMLIT_BIND_ADDRESS=127.0.0.1
```

`HDFS_URI` is the NameNode RPC address; `WEBHDFS_PORT` is its HTTP API port.
They are different endpoints. The HDFS URI authority must identify the same
cluster exposed by WebHDFS. The adapter rejects URIs for another NameNode.
`HADOOP_USER_NAME` supplies a teaching-cluster identity; it is not authentication.

## 3. Check HDFS and WebHDFS

Use your configured Hadoop executable, or `hdfs` if it is on PATH:

```bash
${HDFS_BIN:-hdfs} getconf -confKey fs.defaultFS
${HDFS_BIN:-hdfs} dfs -ls /
jps
curl --noproxy '*' --fail "http://${WEBHDFS_HOST:-localhost}:${WEBHDFS_PORT:-9870}/webhdfs/v1/?op=LISTSTATUS&user.name=${HADOOP_USER_NAME:-$(id -un)}"
```

You should get the HDFS URI, a directory listing and WebHDFS JSON. If WebHDFS is
disabled, enable `dfs.webhdfs.enabled` using your cluster's normal administration
procedure. The lab never formats HDFS or restarts Hadoop. If your HDFS home is
not writable, ask the administrator to create it or set `DAY60_HDFS_BASE` to a
writable lab directory.

## 4. Run the complete setup

```bash
bash setup.sh
```

The script loads `env.sh`, creates an isolated `.venv`, installs packages,
generates the datasets, attempts extension installation, uploads data into your
HDFS lab directory, tests HDFS Iceberg and verifies the dashboard. It records
installed Python packages in `requirements.lock.txt` inside the extracted
working folder. A missing native HDFS extension is recorded and the WebHDFS
adapter is used; Delta/Iceberg extension installation and working sources are
required for verification to pass.

For the same Python versions as the reference run, install the optional
`requirements.lock.txt` after creating the venv, then follow the manual staging
steps below. Extension binaries are installed separately and must match the
DuckDB version/platform; the package lock does not pin extension binaries.

## 5. Equivalent manual setup, one step at a time

```bash
source env.sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python stage_data.py --hdfs
.venv/bin/python probe_extensions.py
.venv/bin/python stage_native.py
.venv/bin/python probe_storage.py
.venv/bin/python test_iceberg_hdfs.py
.venv/bin/python verify.py
```

`stage_data.py` creates 5,000 deterministic fictional orders from January-June
2026 with columns `order_id`, `order_date`, `region`, `category`, `quantity`,
`revenue`, `profit`. Monetary values are INR.

Generated Linux data includes CSV, Parquet, six monthly Parquet partitions,
a region-partitioned Delta table, an Iceberg table, SQLite staging catalogs and
metadata pointer files. Generated HDFS data includes the CSV, monthly Parquet,
a Delta copy for the compatibility test and a region-partitioned Iceberg table.
Only files inside this lab's configured directories are written. Reruns restore
the same 5,000 current rows; Delta/Iceberg historical files can remain.

## 6. Start the dashboard

```bash
bash start.sh
```

Open **http://localhost:8501** on the Linux machine. Keep the terminal running.
To reach a VM from another machine, set `STREAMLIT_BIND_ADDRESS` in `env.sh` to
an address reachable from that machine (or `0.0.0.0`) and use
`http://<your-vm-address>:8501`, subject to your network/firewall rules.

Optional background start and checks:

```bash
bash launch.sh
curl --noproxy '*' --fail "http://${STREAMLIT_BIND_ADDRESS:-127.0.0.1}:8501/_stcore/health"
tail -50 streamlit.log
```

If binding to `0.0.0.0`, use `127.0.0.1` for the curl check. Expected response:
`ok`. `restart.sh` checks the recorded PID's working directory and command before
stopping this lab's instance. There is no automatic restart after reboot.

## 7. Try the sources and partition filters

| Source | Reader |
|---|---|
| Linux Parquet | DuckDB `read_parquet` |
| Linux partitioned Parquet | DuckDB Parquet reader with Hive-style partitions |
| Linux Delta | Native `delta_scan` |
| Linux Iceberg | Native `iceberg_scan` |
| HDFS Parquet (WebHDFS adapter) | fsspec transport + DuckDB Parquet reader |
| HDFS Iceberg (WebHDFS adapter) | Explicit HDFS transport adapter + native Iceberg reader |

Choose a source, filter regions/categories/dates, and inspect the query plan.
On monthly partitioned Parquet choose month 1 to see January-only access.
DuckDB runs SQL directly against file-backed views. pandas receives result
DataFrames rather than the entire dataset before filtering. Metrics cover all
matching rows; the preview and downloadable CSV are limited to 500 rows.
Query results are cached for 60 seconds; Refresh data clears them.

## 8. Verify table semantics and pruning

```bash
source env.sh
cat extension-probe.json
cat storage-probe.json
cat iceberg-hdfs-results.json
cat validation-results.json
cat plan-hdfs.txt
cat plan-iceberg-hdfs.txt
```

All six adapter-based/reference sources should contain 5,000 rows and revenue
29,198,368.54 INR. Verification compares all rows, SQL totals and dashboard
region/date/month/empty filters.

For January Parquet, plans should show one file read out of six monthly files.
Constant filters show `Scanning Files: 1/6`; bound parameters may prune earlier
and show `Scanning Files: 1/1`. The test also checks file filters and one file read.

The HDFS Iceberg test stages metadata JSON, manifest lists, Avro manifests and
Parquet in HDFS with HDFS URIs. It creates an older snapshot with 5,001 rows,
restores 5,000 current rows and verifies `snapshot_from_id` time travel. In a
fresh DuckDB instance, a South-region aggregate must open only the South
partition's Parquet file. File-access tracing verifies HDFS access rather than
silently reading a Linux copy.

## 9. Understand the native-extension limitations

The reference run used DuckDB 1.5.6. Native Delta/Iceberg readers worked. The
native HDFS community-extension download returned 404, so HDFS reads used
WebHDFS adapters. Iceberg without an adapter failed to open its HDFS metadata;
with the explicit adapter it passed, including snapshots and partition pruning.
Delta Kernel rejected `hdfs://` in the reference run. Your probe records your
own installed-version result rather than assuming every storage format works.

Native Iceberg interpretation plus adapter-based HDFS transport is distinct from
native HDFS RPC access. Query execution remains on one machine. Passing the
small dataset tests is not a large-scale performance benchmark. Never query a
Delta/Iceberg table by globbing all its Parquet files: that bypasses snapshot/log
metadata and may include obsolete rows.

## 10. Troubleshooting

- HDFS command missing: set `HDFS_BIN`, `HADOOP_HOME` and/or your PATH.
- Wrong NameNode or user: set `HDFS_URI`, `HADOOP_USER_NAME`, `DAY60_HDFS_BASE`.
- WebHDFS errors: check the port, permissions, API and DataNode redirects.
- Extension failures: inspect `extension-probe.json` and outbound connectivity.
- Stale local Iceberg paths after moving the folder: regenerate the data in its
  final location. Do not distribute already-generated Iceberg metadata.
- Setup failure: rerun the failed manual step and read its traceback. Avoid
  restaging while a dashboard query is active.

## References

- [DuckDB fsspec filesystems](https://duckdb.org/docs/current/guides/python/filesystems)
- [DuckDB Hive partitioning](https://duckdb.org/docs/current/data/partitioning/hive_partitioning)
- [DuckDB Delta extension](https://duckdb.org/docs/current/core_extensions/delta)
- [DuckDB Iceberg extension](https://duckdb.org/docs/current/core_extensions/iceberg/overview)
- [DuckDB HDFS community extension](https://duckdb.org/community_extensions/extensions/hdfs)
