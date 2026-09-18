# Day47

- MySQL CDC with binlog
- SCD1 and SCD 2 with IceBerg and Spark
- Snowflake cli integration
- Snowflake Airflow Integration
- Snowflake Python connector
- Airflow with Hive, HDFS, YARN, Spark Summit

# MySQL CDC to Spark/Iceberg

Build a small ecommerce pipeline that captures product changes from the MySQL binlog,
keeps current and historical product dimensions, and resolves each order's latest business
state even when an older event arrives late. Snowflake is deferred.

## Three notebooks

1. **MySQL_CDC_Source.ipynb** — create isolated MySQL tables, apply separate business
   changes, capture INSERT/UPDATE/DELETE to immutable JSON and incremental order CSV batches.
2. **Spark_Iceberg_SCD1.ipynb** — publish batches to HDFS, preserve event history,
   resolve current orders with a window, and MERGE the current product dimension.
3. **Spark_Iceberg_SCD2.ipynb** — expire/insert historical versions, handle deletes and
   reinserts, verify invariants, and compare booked order value across actual selling prices.

## Execution

Copy the cells into your own Jupyter notebooks. Use kernels with the required dependencies
and the same working directory so the source and ingestion notebooks share raw batches.
HDFS locations are derived directly from `DB`: `/bronze/<DB>` for raw batches and
`/warehouse/<DB>` for Iceberg tables. Your HDFS account needs write access to these locations.

Declare `DB = "cdc_scd_db"` in all three configuration cells. Local batch storage and the
HDFS warehouse use this database name to keep their data together. For a separate dataset,
choose a different DB in all three notebooks and restart the kernels so Spark opens the
corresponding warehouse. Use a distinct `CDC_READER_ID` for concurrent binlog readers.

Run notebook 1's setup cells, **Change 0**, and its capture cell. Pause and run notebook 2,
then notebook 3. Return to notebook 1 for the next change, capture, and repeat 2 → 3.
Process one source change at a time to inspect each transition.
Running all changes is supported and downstream processing still preserves intermediate versions.

| Source change | Change | Product 1 SCD2 versions |
|---|---|---:|
| 0 | Three products; initial orders | 1 |
| 1 | Price 100 → 95; mixed order states | 2 |
| 2 | Black → Silver; equal-time order events | 3 |
| 3 | Premium → Standard; late PAID for delivered order | 4 |
| 4 | Price 95 → 90 | 5 |
| 5 | Timestamp-only update | 5 |
| 6 | Delete product 3 | 5 |
| 7 | Reinsert product 3 | 5 |

After Change 4, orders 1001/1002/1003 are DELIVERED/CANCELLED/PAID. Order 1009 is CREATED.
Product 1's current attributes are Standard/Silver/90. Its history has five versions.
After optional Change 7, product 3 has two lifetimes, only the second current.

Repeat any completed source change: no additional business rows. Capture with no new data:
no new batch. Rerun notebooks 2 and 3: unchanged target rows and SCD2 history.

## Where results are written

D471 writes `products`, `order_events` and `applied_changes` into the MySQL database
selected by `DB`. It also creates `lab_data/cdc_scd_db` relative to the kernel's working
directory when using the default database name. `start.json` stores the initial binlog
position. Under `batches`, each immutable `batch_NNNNNN` directory contains product CDC
JSON, incremental order CSV and a manifest with the next capture position.

D472 copies these batches to `hdfs:///bronze/cdc_scd_db`.
Iceberg tables are stored in `hdfs:///warehouse/cdc_scd_db`. D473 writes
the SCD2 table and its processed-event ledger into that same warehouse. The notebooks
display intermediate results; `validation_report.json` records automated test results.

## Explicit HDFS reset before a fresh copy

Ensure `hdfs` is available in your terminal, then run:

```bash
bash reset_hdfs.sh
```

The script uses `DB="cdc_scd_db"` and deletes `/bronze/cdc_scd_db` and
`/warehouse/cdc_scd_db` if they exist. Change the script's DB variable
if you changed it in the notebooks. Restart Spark kernels afterward, then run notebook 2
to copy the local batches and notebook 3 to rebuild history.

**Do not run this reset between incremental changes.** Normal upload skips existing batches.
An HDFS-only reset retains local raw batches and MySQL data. For a complete source reset,
drop only the selected MySQL database and archive its matching local batch/checkpoint
directory before running notebook 1 from the beginning; old offsets must not be reused
with a recreated source database.

## Environment and scope

- MySQL at `127.0.0.1:3306`, lab defaults root/root, overridable with `MYSQL_HOST`,
  `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`. Database: `cdc_scd_db`.
- MySQL binlog ON, ROW format, FULL image and FULL metadata; uncompressed transactions.
  The source kernel requires `PyMySQL`, `pandas` and `mysql-replication==1.0.17`.
  D471 includes server configuration/restart instructions when binlogs are disabled,
  plus a read-only verification cell that lists any incorrect CDC settings. Server settings
  must already be configured; the notebook does not change persistent server configuration.
  MySQL enables binlogs server-wide; the reader filters the lab database's products table.
- Spark **3.5**, compatible Java, and Hadoop configuration supplied by your kernel environment.
  Make the `hdfs` command available in that environment. Start with a fresh kernel when
  changing Spark configuration.
- A compatible Iceberg Spark runtime must already be configured.
  No JAR download, Hive Metastore, Kafka, Debezium, Airflow, or Snowflake configuration.
- Raw data and the Iceberg warehouse are scoped by database name within your chosen storage locations.

The collector requires a quiet source during capture, one writer and one collector per
run. It checks for concurrent binlog movement. Binlogs must remain available until captured.
Do not delete offsets or alter the product schema during a run. Choose a new database name for a
fresh lab if a source log has been purged. This demonstration starts from empty tables;
it does not implement a snapshot/bootstrap for an existing populated production database.

HDFS ingestion is incremental by immutable batch directory. Downstream reads deliberately
scan the small complete history, simplifying replay. SCD2 uses an applied-event ledger and
deterministic version keys; it is a single-writer, multi-statement implementation.
Consumers should inspect results only after processing finishes.
  

References: [Iceberg Spark MERGE](https://iceberg.apache.org/docs/1.10.0/spark-writes/),
[Iceberg catalog configuration](https://iceberg.apache.org/docs/1.10.0/spark-configuration/),
[MySQL binlog reader](https://github.com/julien-duponchelle/python-mysql-replication).

