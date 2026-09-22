# Capstone: Trusted Sales and Customer Analytics

# Work in progress

## Business problem

A growing distributor uses Odoo to manage customers, products, and sales orders. Its warehouse team supplies stock spreadsheets, suppliers publish product reference files, and a payment gateway sends transaction notifications. Management currently relies on manually combined reports that disagree because of duplicate records, missing references, customer changes, and late updates.

Build a data platform that turns these operational feeds into reliable sales analytics. The platform must preserve source evidence, separate invalid data, maintain customer history, process incremental changes safely, and explain how published totals were calculated. A small event pipeline must also make incoming sales events visible in the data lake.

Your role is the data engineering team. Treat Odoo and its PostgreSQL database as upstream systems owned by another team. You are not required to develop Odoo modules or administer the infrastructure.

## Time and expected outcome

You have **five full implementation days** within a 17-day training period. Use the other 12 training days to understand the source contracts, inspect examples, confirm access, and review the business definitions. Completion must not depend on substantial implementation during those training days.

By the end of Day 3, demonstrate a working batch path from source ingestion through the lake into Snowflake, including customer history and reconciled business results. Days 4 and 5 are for orchestration, the small streaming pipeline, recovery checks, and submission. Attempt optional extensions only after the core acceptance criteria pass.

## Business questions to answer

1. What is the net value of confirmed sales orders by day and month?
2. Which products and categories generate the highest net sales value?
3. Who are the top customers, and how do sales vary by the customer's segment and city at the time of the order?
4. What is the average order value for each day?
5. How many source records were rejected, superseded, or identified as duplicates, and why?

In this project, **net sales value means ordered sales value, not recognized accounting revenue or cash collected**. Inventory availability, invoice aging, and payment settlement are outside the core analytical scope.

## What the trainer provides

The following are prerequisites for the implementation sprint. Students must not spend the sprint provisioning replacement infrastructure.

| Provided item | Scope |
|---|---|
| Ready-to-use local environment | Odoo, PostgreSQL, Spark, HDFS, Kafka, and Airflow; documented start/stop commands and verified connectivity |
| Snowflake access | An available training warehouse, student database/schema permissions, and a tested connection/loading example independent of AWS |
| Source interfaces | Read-only sales views, a documented customer API or adapter, product exports, and source-to-business mappings |
| Source documentation | Explicit schemas, keys, pagination rules, timestamp semantics, status definitions, and extraction boundaries |
| Controlled data packs | Initial data, two ordered change packs, malformed samples, and an independent expected-results manifest |
| Extraction scaffolding | Connection examples and API authentication/pagination examples; these are starting points, not completed pipelines |
| Event simulator | A working producer for one `sales-events` topic and repeatable normal, duplicate, malformed, and late-event fixtures |
| File-interface exercise pack | Small CSV, JSON, XML, and Excel examples with parsing helpers and expected record counts |
| Optional cloud environment | Temporary AWS access, prepared S3/EMR configuration, compatible dependencies, and execution instructions |

The trainer exposes only seven business entities: customer, product, sales order, sales order line, inventory snapshot, supplier product reference, and payment event. Students do not reverse engineer Odoo tables. Invoices, payment allocation, and warehouse master modelling are excluded from the core.

## What you must implement

Implement extraction control, source landing, reusable PySpark transformations, data quality checks, quarantine, incremental processing, warehouse tables and loads, customer history, business aggregates, a small streaming consumer, Airflow orchestration, and evidence of reconciliation and recovery.

You may reuse the provided connectors and parsing helpers. You remain responsible for configuration, traceability, validation, and the correctness of the outputs. Do not modify upstream source records to make checks pass.

## Source contracts and ingestion scope

| Business source | Interface | Required student outcome |
|---|---|---|
| Odoo sales orders and lines | Read-only PostgreSQL views | Extract initial and incremental data into Bronze; fully integrate into sales analytics |
| Odoo customers | Trainer-provided HTTP API/adapter | Handle documented pagination and updates; fully integrate into customer history |
| Odoo products | CSV export | Land and validate snapshots; fully integrate into the product dimension |
| Warehouse inventory snapshots | Excel | Preserve the file; parse the supplied worksheet, validate its schema, and report accepted/rejected counts |
| Supplier product references | XML | Preserve the file; parse supplied records, validate their schema, and report accepted/rejected counts |
| Payment gateway events | JSON | Preserve the payload/file; validate supplied records and isolate malformed input |
| Sales event simulator | Kafka | Implement the bounded streaming requirements below |

The Excel, XML, and payment JSON feeds are **small interface exercises**. Produce standardized landing outputs and quarantine evidence for them; no cross-system joins, additional fact tables, or related KPIs are required. Do not duplicate the same business dataset across formats just to demonstrate ingestion.

Each release has a stable `batch_id` and extraction boundary. Core records have a business key, source modification timestamp, and source version or equivalent deterministic ordering field. Customer changes also have a business-effective timestamp. The trainer supplies these through the source contract; students do not infer undocumented Odoo semantics.

## Business rules

- Use one supplied currency, INR, and normalize timestamps to UTC. Daily reporting uses the UTC order date.
- An order line is identified by `(order_id, line_id)`. Customers and products have stable source IDs.
- Quantity must be greater than zero, unit price must be nonnegative, and discount percentage must be between 0 and 100. Missing price is invalid; zero price is valid.
- Calculate line net value as `quantity × unit_price × (1 − discount_percentage / 100)`, using decimal arithmetic and rounding each line to two decimal places before aggregation.
- Only confirmed orders contribute to sales KPIs. Draft and cancelled orders remain traceable and are excluded from the published sales measures.
- An order cancellation updates the existing order and its analytical contribution. It must not create additional sales lines.
- Taxes, shipping, returns, credit notes, exchange rates, and hard deletes are outside scope.
- Average order value is eligible line net value divided by the number of distinct eligible orders in the same reporting group. A group with no eligible orders has a null average.
- Missing or unknown customer/product references are quarantined. Automatic repair or later replay of those rejected records is optional.
- Undeclared extra fields must be logged and preserved in Bronze. A missing required field or incompatible type must produce a visible validation failure or quarantine record.

## Lake and transformation requirements

Use PySpark as the primary transformation engine and implement these logical areas on HDFS:

| Area | Required purpose |
|---|---|
| `bronze/` | Preserve original files or extracted source records and their ingestion context |
| `silver/` | Hold typed, standardized, validated data with deterministic keys and update handling |
| `gold/` | Hold daily sales, product performance, and customer sales aggregates |
| `quarantine/` | Retain invalid records or raw-file references with actionable rejection reasons |
| `audit/` or control tables | Record batch attempts, counts, outcomes, and successful progress boundaries |

Use explicit schemas, decimal money types, appropriate joins, deterministic deduplication, and business-rule validation. Use window functions where they help select source versions or construct customer history; there is no requirement to demonstrate arbitrary APIs.

For each ingested record or its associated manifest, retain `source_system`, `source_reference`, `batch_id`, and `ingestion_timestamp`. The source reference must identify the file, extraction, or Kafka topic/partition/offset. Preserve business keys and source timestamps where supplied. Streaming records also require `event_id`, `event_time`, and `processing_timestamp`.

Every quarantined record must include its raw payload or recoverable location, batch/source context, an error code, and an error description. A parsing failure must remain recoverable even when no business key can be read. Do not silently drop invalid input.

Physical formats and update strategies are your choice. A transactional lake format is not mandatory. If using Parquet, document how affected partitions or keyed datasets are replaced safely during retries. Do not rebuild the entire platform for every change pack.

## Incremental processing and customer history

Process the releases in order:

| Release | Required situations |
|---|---|
| Pack 01: initial load | Customers, products, orders, and lines with a small set of known bad records |
| Pack 02: changes | New orders, changed customer city/segment, product attribute corrections, duplicate deliveries, and invalid references |
| Pack 03: subsequent changes | Another customer change, a late-arriving order, a cancelled order, and replayed records |

Use a stable batch ledger and/or source high-water mark. Advance successful progress only when the required publication and reconciliation steps succeed. Document how equal modification timestamps are handled so that records at a boundary are not lost.

For a given business key, select updates by source version/modification order, not ingestion time. Exact replays must not create new logical rows. Conflicting records with the same key and source version must be surfaced rather than selected arbitrarily.

Implement **SCD Type 2 for customer city and segment**. Use surrogate keys, business keys, effective-from/effective-to timestamps, and a current-row indicator. Effective intervals must not overlap; use `[effective_from, effective_to)` semantics. Unchanged replays must not create new versions. The initial fixture supplies an effective date that covers all initial orders.

Associate each sales fact with the customer version effective at the order timestamp. A late-arriving order must resolve to the appropriate historical customer version, not automatically the current version. Customer changes arrive in effective-time order in the core fixtures; retroactive corrections and late-arriving dimension records are optional extensions.

Implement **SCD Type 1 for product descriptive attributes**, such as product name and category. Product corrections overwrite those attributes. Historical product reporting therefore uses the latest product description/category; customer city/segment reporting preserves order-time history.

## Snowflake warehouse and Gold outputs

Create only the following required star-schema tables:

| Table | Grain and purpose |
|---|---|
| `DIM_CUSTOMER` | One row per historical customer version; SCD Type 2 |
| `DIM_PRODUCT` | One row per product; SCD Type 1 |
| `DIM_DATE` | One row per calendar date required by the supplied orders |
| `FACT_SALES` | One row per sales-order line, representing its latest accepted business state |

Document business keys, surrogate keys, joins, measures, and fact grain. Store order ID, line ID, order timestamp/date, status, quantity, unit price, discount, and line net value in the fact. Retain cancelled lines with their current status and exclude them from sales KPI queries. Load dimensions before resolving and loading fact foreign keys.

Publish three Gold datasets: daily sales, product performance, and customer sales by historical city/segment. Provide Snowflake SQL answering all five business questions. Gold may be calculated from trusted Silver data with customer history available to the transformation; Snowflake results must reconcile to the equivalent Gold outputs under the same filters and source cutoff.

Snowflake remains required even when AWS access expires. Use the supplied local-to-Snowflake loading path; a persistent S3 staging bucket must not be necessary.

## Data quality, audit, and publication gate

Check required keys, parseable timestamps, numeric types, business ranges, known references, and duplicate business keys. Record counts for each source and batch attempt, including records read, accepted, rejected, replayed, and superseded. Record start/end time, attempt ID, status, and the last successful source boundary.

Before publishing Gold or loading warehouse business tables, require:

- Zero null required keys in the candidate trusted output.
- Zero duplicate keys at the declared Silver and fact grains.
- Zero invalid customer/product references in candidate sales data.
- Zero invalid quantities, prices, discounts, or calculated amounts in candidate sales data.
- A rejected-record rate of at most 5% for each core source in that batch, configurable for trainer fixtures. The denominator is records read before duplicate handling; an empty source has a 0% rate.

An individual invalid record can be quarantined while valid records continue if the gate passes. If the gate fails, preserve Bronze, quarantine, and audit evidence; mark the batch failed and do not publish its Gold or warehouse changes. The trainer provides both a passing fixture and a fixture that deliberately exceeds the threshold.

For each input batch, reconcile mutually exclusive outcomes:

`records_read = accepted_records + rejected_records + duplicate_records + superseded_records`

Define the classification order, including how records with multiple errors are counted once. For an unreadable file whose record count cannot be determined, record a file-level failure and mark record reconciliation incomplete; do not invent a record count or report success.

Reconcile financial totals between the latest valid, eligible source state, Gold, and Snowflake at the same source cutoff. Provide a bridge explaining exclusions, cancellations, invalid rows, and superseded versions. Do not compare raw delivered totals containing duplicate updates directly with current-state warehouse totals. Monetary discrepancies after applying the declared rounding rules must be zero.

## Small streaming requirement

Consume the single trainer-owned `sales-events` topic with Spark Structured Streaming. Use an explicit schema and persist Kafka payloads and offsets in Bronze, including malformed messages. Retain checkpoints outside temporary process directories.

For valid events, create a small deduplicated event landing dataset using `event_id`; quarantine malformed or invalid events. A finite fixture replay must produce one accepted logical event per distinct valid event ID, including when an event is delivered again after a consumer restart. Demonstrate a persistent deduplication strategy sufficient for the fixture; checkpointing alone does not remove producer duplicates.

Preserve event and processing time and flag an event as late when processing time is more than 10 minutes after event time. Retain late valid events in this core landing dataset. Watermark-based window aggregation is optional.

In a running local demonstration, valid test events must appear in the lake within 60 seconds of production. Restart the consumer with the same checkpoint and show that the logical accepted event count remains correct. Keep the streaming consumer separately runnable; Airflow need not own a continuously running process.

The core stream provides event visibility only. Batch Odoo data is authoritative for `FACT_SALES`; do not add event amounts to the same sales facts or KPIs. Direct streaming into Snowflake and batch/stream conflict resolution are outside scope.

## Orchestration and portability

Create one parameterized Airflow DAG covering extraction, Bronze landing, Silver validation, the quality gate, customer/product preparation, Gold publication, warehouse loading, and reconciliation. Choose dependencies that ensure customer history is available before historical joins and dimensions are loaded before facts.

Keep business logic in reusable Python, Spark, or SQL modules. Demonstrate task dependencies, a schedule, retries, useful failure logs, and rerunning a selected batch. Do not run overlapping publication attempts for the same batch.

Inject one controlled failure after an intermediate write and before successful completion. Resume the batch and demonstrate that Silver keys, dimension history, fact counts, and financial totals match a clean execution. Failed attempts must remain visible in the audit history.

Externalize paths, connections, and credentials. The required execution environment is local Spark with HDFS and the provided Snowflake account. Include a documented S3/EMR configuration profile so transformation code does not embed HDFS-only paths. A live AWS run is optional and must not delay the core submission.

## Five-day implementation milestones

| Day | Expected milestone |
|---|---|
| 1 | Confirm grain and source rules; ingest core sources into Bronze; run the small file-interface exercises |
| 2 | Produce validated Silver and quarantine; implement audit accounting, increment handling, and dimension history |
| 3 | Deliver the batch MVP in Snowflake with Gold outputs, analytical queries, and initial/increment reconciliation |
| 4 | Add the Airflow DAG and bounded streaming pipeline; verify quality-gate failure and event replay |
| 5 | Verify restart recovery and historical joins; finalize evidence and documentation; attempt extensions only if core is complete |

## Acceptance criteria

The trainer evaluates observable results against the supplied fixtures and expected-results manifest.

| ID | Required demonstration | Pass condition |
|---|---|---|
| AC01 | Core ingestion and interface exercises | PostgreSQL, customer API, CSV, Excel, XML, and JSON are processed at the declared scope with source traceability and expected input accounting |
| AC02 | Layer separation | Source evidence is recoverable; Silver is validated; Gold contains the three business aggregates; invalid input has actionable quarantine details |
| AC03 | Data quality gate | Known bad records are identified; trusted outputs meet all invariant checks; the excessive-rejection fixture fails without publication |
| AC04 | Incremental changes | All three packs apply correctly; additions, corrections, late orders, and cancellations match expected state without a platform-wide reload |
| AC05 | Idempotency | Replaying a completed pack leaves logical Silver data, customer versions, fact rows, and KPI totals unchanged; retry/audit entries may increase |
| AC06 | Customer and product history | Customer intervals do not overlap and have one current version per key; supplied historical and late orders join correctly; product corrections overwrite descriptions |
| AC07 | Warehouse correctness | Declared grains hold; fact foreign keys resolve; cancelled lines remain traceable and do not contribute to sales KPIs |
| AC08 | Business answers | SQL answers all five questions; Gold and Snowflake results match the independent expected counts and monetary values |
| AC09 | Reconciliation | Batch accounting balances, financial differences are zero after documented adjustments, and failed/unreadable inputs are visibly incomplete |
| AC10 | Streaming | Valid events land within 60 seconds during the test; duplicate replay and restart preserve distinct event counts; malformed and late events are accounted for |
| AC11 | Orchestration and recovery | The DAG runs the batch flow; an injected failure is retried/resumed successfully without duplicate facts or customer versions |
| AC12 | Reproducibility | A reviewer can execute the documented local workflow with configuration and supplied services, without active AWS access or hard-coded credentials |

## Submission and evaluation

Submit a repository containing a concise README, architecture diagram, source mappings, fact/dimension grains, configurable jobs, Airflow DAG, Snowflake DDL and analytical SQL, data quality rules, and a compact evidence report. Include exact run/replay commands, batch IDs, audit counts, expected-versus-actual KPI results, customer-history examples, streaming restart results, and the controlled-failure demonstration. Do not submit credentials or depend solely on screenshots of successful tasks.

| Evaluation area | Weight |
|---|---:|
| Source handling, traceability, and lake transformations | 15% |
| Data quality, quarantine, and reconciliation | 25% |
| Incremental correctness, idempotency, and recovery | 20% |
| Dimensional model, SCD correctness, and business answers | 25% |
| Streaming, orchestration, and reproducible documentation | 15% |

Technology presence alone earns no correctness credit. Optional extensions do not compensate for missing core acceptance criteria.

## Optional extensions

Choose at most one after completing the core:

- **Cloud execution:** Run one existing Bronze-to-Silver-to-Gold transformation on EMR with S3 using configuration changes, then compare its results with the local run. Preserve evidence before the lab expires.
- **AI summary:** Generate a short business or pipeline-health summary from aggregate outputs and audit metrics. Include the reporting period and supporting values; verify each numeric claim. Exclude personal customer details, and keep model access optional to pipeline success.
- **Inventory analytics:** Integrate the supplied Excel snapshots and supplier references to answer one clearly defined stock-availability question.
- **Advanced event handling:** Add one event-time window aggregate with a declared watermark and demonstrate how events inside and outside its lateness boundary are accounted for.

Production infrastructure, real-time warehouse serving, a dashboard application, CDC administration, invoice/payment modelling, and retroactive SCD repair are not required deliverables.
