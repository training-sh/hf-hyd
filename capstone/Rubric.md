# Project Evaluation Rubric

| Evaluation Area | Weight | Evidence Expected |
|---|---:|---|
| **Business Understanding & Source Mapping** | **10%** | Correct meanings, grains, dates, relationships, and explicit scope assumptions. |
| **Presentation & Behavior** | **10%** | Students' presentation skills and problem descriptions. |
| **Ingestion, S3 & WAL CDC** | **15%** | Traceable batch ingestion, valid snapshot/stream handoff, real WAL capture, and bounded incremental processing. |
| **PySpark, Spark SQL, Catalog & EMR** | **15%** | Meaningful transformations, explicit schemas, persistent metadata, query-plan reasoning, and verified EMR execution. |
| **Data Quality, Incremental Correctness & Recovery** | **10%** | Quarantine/audit accounting, quality gates, deterministic replay, idempotency, and demonstrated failure recovery. |
| **Star Schema, SCD1 & SCD2** | **15%** | Stable surrogate keys, correct fact grains, customer history, product overwrite behavior, historical lookup, and safe joins. |
| **Warehouse Analytics & Reconciliation** | **15%** | Correct business SQL with source/lake/warehouse counts and financial totals reconciled at the same cutoff. |
| **Airflow, Documentation & Demonstration** | **10%** | Runnable DAG, retries/configuration, clear commands, reproducible evidence, and a README-led handover. |
| **Total** | **100%** | |
