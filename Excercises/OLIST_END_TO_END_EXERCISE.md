# D44 — Olist End-to-End Airflow Exercise

Build and submit a **working Airflow DAG with supporting Python scripts** that processes the Olist e-commerce dataset from source CSV files through **Bronze → Silver → Gold**. Your Gold output must be an analytical **seller profile, customer profile, or product profile**. Choose any one profile.

This is a student assignment. You must implement and run the pipeline; a DAG diagram, notebook-only solution, or collection of queries without orchestration is not sufficient.

The code must have input and output parameter configuration, may accept hdfs or s3 file paths so that it could be suitable for EMR and local HDFS clusters.

## 1. Technology and starting point

Use **Hive SQL, Spark DataFrames, Spark SQL, or a documented combination** for data processing. Airflow must orchestrate the complete flow. Submit Python scripts even if your transformations use Hive: Python scripts can invoke the Hive jobs and validate their results. Include any SQL files those scripts require.

Use the existing course environment and your local Olist dataset, typically at `/mnt/c/data/olist`. Make source paths, output locations, and database names configurable. Record your actual software versions and execution environment in your submission README.

Use these course exercises as references:

- [D250: Olist HDFS and Hive ingestion](../D25_Hive2/D250_Olist_HDFS_Hive_Ingestion_Exercises.ipynb)
- [D252: Olist HiveSQL CTE exercises](../D25_Hive2/D252_Olist_HiveSQL_CTE_Exercises.ipynb), also provided as pasted reference material
- [D322: Olist Bronze and Silver with Spark](../D32_SparkWindowFunctions/D322_Olist_Bronze_Silver_Exercises.ipynb)

Adapt the reference analytics into a persisted Gold profile. The earlier CTE lab's restrictions on permanent tables and window functions do **not** apply here. This assignment requires persisted layer outputs; use CTEs or window functions where useful.

## 2. Required end-to-end flow

```text
Check source files
        ↓
Ingest Bronze → Validate Bronze
                       ↓
                Transform Silver → Validate Silver
                                          ↓
                                   Build Gold profile
                                          ↓
                                   Validate Gold
                                          ↓
                              Publish run summary and preview
```

Implement these stages as separate Airflow tasks, with explicit dependencies. You may split ingestion and transformation into tasks per dataset. Validation must finish successfully before dependent processing starts. Do not hide the entire pipeline inside a single task.

One DAG run must perform the full processing flow from existing source CSVs to a queryable Gold output. Initial environment setup is allowed outside the DAG; manually running transformation scripts between tasks is not.

## 3. Bronze: preserve and register the source data

1. Ingest all nine Olist datasets: customers, orders, order items, payments, reviews, products, sellers, geolocation, and product category translation.
2. Preserve the original source values in a raw storage area. Record source filename, ingestion time, and run or batch identifier in columns or a separate manifest.
3. Register queryable Bronze tables and document the mapping from CSV filenames to tables. Handle CSV headers, quoted delimiters, and multiline fields correctly, especially review text.
4. Validate that all required files and tables exist and contain data. Record parsed record counts, column checks, and malformed records; do not use physical line counts as CSV record counts.

**Deliverable:** raw data locations, Bronze table definitions, and ingestion audit results.

## 4. Silver: create clean, typed datasets

Create persisted Silver tables for all nine datasets using Parquet or ORC. Apply and document the following rules:

- Convert timestamps, numeric measures, and monetary amounts to appropriate types. Preserve identifiers and ZIP-code prefixes as strings; use decimal types for money.
- Normalize text where appropriate and define handling for missing values, invalid casts, duplicates, and rejected records. Do not silently discard bad records.
- State each table's grain and business key. Order items use `(order_id, order_item_id)`; customer records use `customer_id`, while repeat-customer analysis uses `customer_unique_id`.
- Define a deterministic policy for repeated reviews. Geolocation can contain multiple rows per ZIP-code prefix: keep its documented source grain or produce a deterministic location lookup before joining it to profiles.
- Validate required keys, applicable uniqueness rules, and relationships such as items to orders/products/sellers and orders to customers. Report unmatched records and explain whether they block the pipeline or are retained under a documented rule.
- Reconcile Bronze and Silver counts, including records removed, deduplicated, or quarantined.

**Deliverable:** Silver tables, transformation scripts, and a quality report with pass/fail results and rejected-record counts.

## 5. Gold: choose ONE profile

Persist one analytical table with the following minimum fields. State whether the output contains all dimension entities or only those with qualifying orders, and define the order-status filter used for each metric. Define revenue as the sum of item `price`, excluding freight, unless you explicitly label a different measure.

| Choice | Required grain | Minimum profile fields |
| --- | --- | --- |
| Seller profile | One row per `seller_id` | Seller city/state, distinct order count, item count, item revenue, freight total, average item price, first/last purchase timestamp, revenue rank |
| Customer profile | One row per `customer_unique_id` | Distinct order count, item spend, payment total, average order value, first/last purchase timestamp, recency in days, spending segment |
| Product profile | One row per `product_id` | Original and translated category, distinct order count, item count, item revenue, average item price, distinct seller count, revenue rank within category |

For the customer profile, calculate average order value as item spend divided by qualifying order count, define segment thresholds, and use a configurable fixed `as_of_date` for recency so reruns are reproducible. If including customer location, explain how you choose among multiple customer records. For ranked profiles, define tie behavior; for product categories, define a fallback when translation is missing.

You may extend the profile with review scores, delivery performance, or other measures inspired by the attached exercises. Explain the business meaning and calculation of every added field.

**Join correctness is required:** items, payments, and reviews can each have multiple rows per order. Aggregate each to the intended join grain before combining them. An order may contain multiple sellers or products; document any allocation of order-level measures. Do not duplicate payment totals across item rows or attribute an entire order's revenue to every seller.

Validate Gold key uniqueness, required fields, and totals reconciled to the eligible Silver records. Provide at least three analytical queries against the persisted profile, with saved results, and manually reconcile one selected entity to its Silver records.

## 6. Airflow and Python requirements

- Submit a discoverable DAG with a meaningful DAG ID, explicit dependencies, a documented schedule or manual trigger, and a retry policy.
- Keep ingestion and transformation work inside task execution, not at DAG import time. Put reusable processing logic in supporting Python scripts; keep the DAG focused on orchestration.
- Pass configuration into scripts. Include required SQL files, dependencies, and deployment instructions. Use connections or environment configuration for credentials rather than embedding secrets.
- Wait for submitted Hive or Spark jobs to finish and propagate errors to Airflow. A script or data-quality failure must fail its task and prevent downstream Gold publication.
- Persist data between tasks. Use task messages only for small metadata such as paths or counts. Explain how workers access scripts, input files, and intermediate outputs.
- Make reruns safe: choose a full refresh, partition replacement, or another documented approach that avoids duplicate rows. Limit cleanup to your assignment's own output locations.
- Write a run summary containing run ID, source and target locations, row counts per layer, quality results, selected profile, and completion status. Publish success only after Gold validation passes.

## 7. Execution evidence

Demonstrate all of the following:

1. **Successful run:** trigger the DAG through Airflow and capture the graph and task logs showing the complete Bronze-to-Silver-to-Gold flow.
2. **Safe rerun:** run again with unchanged input and the same logical processing parameters. Show that business row counts and metrics remain stable and no duplicate business keys are introduced; audit timestamps may change.
3. **Failure and recovery:** using an isolated test input or configuration, introduce a missing required file or a failing quality check. Show the failed task and blocked downstream work, correct the issue, and rerun successfully. Do not alter the shared source dataset.
4. **Queryable result:** show the Gold schema, row count, sample rows, three analytical query results, and the single-entity reconciliation.

## 8. Submission package

Use a structure similar to this; filenames may differ:

```text
student_id_olist_pipeline/
├── README.md
├── dags/
│   └── olist_bronze_silver_gold.py
├── scripts/
│   ├── ingest_bronze.py
│   ├── transform_silver.py
│   ├── build_gold.py
│   └── validate_layers.py
├── sql/                     # Include if your scripts load SQL files
├── config/                  # Example configuration without credentials
├── requirements.txt
└── evidence/
    ├── successful_run/
    ├── rerun/
    ├── failure_recovery/
    └── gold_results/
```

Your README must explain prerequisites, configuration, script deployment, DAG discovery and triggering, layer locations, table grains, cleansing rules, metric definitions, rerun strategy, and how to reproduce your evidence. Include exact commands appropriate to your environment. Submit code and evidence, with accessible output locations; you do not need to package the entire source dataset.

## 9. Assessment rubric

| Area | Marks |
| --- | ---: |
| Complete, executable Airflow flow and supporting Python scripts | 25 |
| Bronze ingestion, source preservation, and auditability | 15 |
| Silver types, cleansing, keys, and quality checks | 20 |
| Gold profile, correct grain/joins, and analytical results | 20 |
| Safe reruns, failure propagation, and recovery evidence | 10 |
| Reproducible setup instructions and submission evidence | 10 |
| **Total** | **100** |

**Completion requirement:** submit a working DAG and Python scripts that demonstrate the full source → Bronze → Silver → Gold flow, using any one of the three profile choices.
