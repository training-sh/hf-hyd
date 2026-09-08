# Snowflake Time Travel

Snowflake Time Travel allows you to query and recover older states of a table within its configured retention period.

> `DATA_RETENTION_TIME_IN_DAYS` does **not** mean current table data is deleted after that many days.
> It means Snowflake keeps historical versions of changed or deleted data for that many days.

---

## 1. Create an Example Table

```sql
CREATE OR REPLACE TABLE sales (
    id      INT,
    product VARCHAR,
    amount  NUMBER
)
DATA_RETENTION_TIME_IN_DAYS = 1;
```

Insert sample data:

```sql
INSERT INTO sales VALUES
    (1, 'Laptop', 50000),
    (2, 'Phone', 30000),
    (3, 'Tablet', 20000);
```

Check the current data:

```sql
SELECT * FROM sales;
```

Expected result:

| id | product | amount |
| -: | ------- | -----: |
|  1 | Laptop  |  50000 |
|  2 | Phone   |  30000 |
|  3 | Tablet  |  20000 |

---

## 2. What Does `DATA_RETENTION_TIME_IN_DAYS` Mean?

```sql
DATA_RETENTION_TIME_IN_DAYS = 1
```

means:

```text
Current table data
    |
    | remains normally until UPDATE / DELETE / DROP
    |
    +--------------------------------------------

Historical data
    |
    | retained for Time Travel
    |
    +---- 1 day
```

It does **not** mean:

```text
Create table
    |
    +---- after 1 day
             |
             X delete current data
```

Current data is not automatically removed when the retention period expires.

Retention controls how long **historical states** are available.

---

## 3. Make Some Changes

Update a row:

```sql
UPDATE sales
SET amount = 55000
WHERE id = 1;
```

Delete a row:

```sql
DELETE FROM sales
WHERE id = 3;
```

Insert a new row:

```sql
INSERT INTO sales VALUES
    (4, 'Monitor', 15000);
```

Current data:

```sql
SELECT * FROM sales;
```

Expected result:

| id | product | amount |
| -: | ------- | -----: |
|  1 | Laptop  |  55000 |
|  2 | Phone   |  30000 |
|  4 | Monitor |  15000 |

Snowflake still retains previous table states within the Time Travel retention period.

---

# Time Travel Methods

Snowflake provides three important ways to locate historical data:

1. `OFFSET`
2. `TIMESTAMP`
3. `STATEMENT`

---

## 4. Time Travel Using OFFSET

`OFFSET` is measured in seconds relative to the current time.

### One minute ago

```sql
SELECT *
FROM sales
AT(OFFSET => -60);
```

### Five minutes ago

```sql
SELECT *
FROM sales
AT(OFFSET => -60 * 5);
```

### One hour ago

```sql
SELECT *
FROM sales
AT(OFFSET => -60 * 60);
```

Equivalent:

```sql
SELECT *
FROM sales
AT(OFFSET => -3600);
```

### One day ago

```sql
SELECT *
FROM sales
AT(OFFSET => -60 * 60 * 24);
```

Equivalent:

```sql
SELECT *
FROM sales
AT(OFFSET => -86400);
```

Common values:

| Time       |   OFFSET |
| ---------- | -------: |
| 1 minute   |    `-60` |
| 5 minutes  |   `-300` |
| 30 minutes |  `-1800` |
| 1 hour     |  `-3600` |
| 2 hours    |  `-7200` |
| 1 day      | `-86400` |

Example:

```sql
SELECT *
FROM sales
AT(OFFSET => -3600);
```

Meaning:

> Show the `sales` table as it existed one hour ago.

---

## 5. Time Travel Using TIMESTAMP

You can query a table at an exact timestamp.

```sql
SELECT *
FROM sales
AT(
    TIMESTAMP =>
    '2025-04-16 08:00:00 +05:30'::TIMESTAMP_TZ
);
```

Meaning:

> Show the `sales` table as it existed at 8:00 AM IST on April 16, 2025.

You can also calculate the timestamp dynamically:

```sql
SELECT *
FROM sales
AT(
    TIMESTAMP =>
    DATEADD(hour, -2, CURRENT_TIMESTAMP())::TIMESTAMP_TZ
);
```

Meaning:

> Show the table as it existed two hours ago.

---

## 6. Time Travel Using STATEMENT

This is especially useful after an accidental:

```text
DELETE
UPDATE
MERGE
```

Suppose somebody executes:

```sql
DELETE FROM sales;
```

Now:

```sql
SELECT * FROM sales;
```

returns:

```text
0 rows
```

The table is empty, but the old state may still be available through Time Travel.

---

## 7. Find the Query ID

Snowflake records SQL statements in query history.

```sql
SELECT
    query_id,
    query_text,
    start_time
FROM TABLE(
    INFORMATION_SCHEMA.QUERY_HISTORY()
)
WHERE query_text ILIKE '%DELETE FROM sales%'
ORDER BY start_time DESC;
```

Example:

| query_id      | query_text          | start_time         |
| ------------- | ------------------- | ------------------ |
| `01abc123...` | `DELETE FROM sales` | `2025-04-16 08:30` |

The important value is the `QUERY_ID`.

---

## 8. Query the Table Before a Statement

Suppose the accidental DELETE query ID is:

```text
01abc123...
```

Use:

```sql
SELECT *
FROM sales
BEFORE(
    STATEMENT => '01abc123...'
);
```

Expected historical data:

| id | product | amount |
| -: | ------- | -----: |
|  1 | Laptop  |  55000 |
|  2 | Phone   |  30000 |
|  4 | Monitor |  15000 |

Meaning:

> Show the table exactly as it existed immediately before this SQL statement executed.

This is one of the most useful Snowflake recovery techniques.

---

# AT vs BEFORE

## AT

`AT` means:

> Give me the table state at a particular point.

Examples:

```sql
SELECT *
FROM sales
AT(OFFSET => -3600);
```

or:

```sql
SELECT *
FROM sales
AT(
    TIMESTAMP =>
    '2025-04-16 08:00:00 +05:30'::TIMESTAMP_TZ
);
```

---

## BEFORE

`BEFORE` means:

> Give me the table state immediately before a particular point or statement.

Example:

```sql
SELECT *
FROM sales
BEFORE(
    STATEMENT => '01abc123...'
);
```

This is particularly useful for recovering from bad DML.

---

# Rollback / Recovery

Snowflake does not normally use syntax such as:

```sql
ROLLBACK TABLE sales TO VERSION 5;
```

Snowflake does not expose ordinary table history as numbered versions in the same way as Delta Lake.

The common recovery method is:

```text
Historical state
      |
      v
Create a clone
      |
      v
Validate clone
      |
      v
Swap it with production table
```

---

## 9. Restore Using a Statement ID

Suppose the bad DELETE query was:

```text
01abc123...
```

Create a restored copy:

```sql
CREATE TABLE sales_restored
CLONE sales
BEFORE(
    STATEMENT => '01abc123...'
);
```

Check it:

```sql
SELECT * FROM sales_restored;
```

Expected result:

| id | product | amount |
| -: | ------- | -----: |
|  1 | Laptop  |  55000 |
|  2 | Phone   |  30000 |
|  4 | Monitor |  15000 |

---

## 10. Restore Using TIMESTAMP

You can also recover the table from an exact timestamp.

```sql
CREATE TABLE sales_restored
CLONE sales
AT(
    TIMESTAMP =>
    '2025-04-16 08:00:00 +05:30'::TIMESTAMP_TZ
);
```

Meaning:

> Create `sales_restored` using the historical state of `sales` at 8:00 AM.

---

## 11. Restore Using OFFSET

You can also create a clone from a relative time.

```sql
CREATE TABLE sales_restored
CLONE sales
AT(
    OFFSET => -3600
);
```

Meaning:

> Create `sales_restored` from the state of `sales` one hour ago.

---

## 12. Replace the Damaged Table

After validating the restored table:

```sql
SELECT * FROM sales_restored;
```

you can swap the two tables:

```sql
ALTER TABLE sales_restored
SWAP WITH sales;
```

After the swap:

```text
sales
    -> restored historical data

sales_restored
    -> damaged/current version
```

This is useful because the damaged copy is still retained for investigation.

---

# Recovering a Dropped Table

Suppose somebody executes:

```sql
DROP TABLE sales;
```

Snowflake supports:

```sql
UNDROP TABLE sales;
```

Then:

```sql
SELECT * FROM sales;
```

works again, provided the object is still within its Time Travel retention period.

---

# Listing Historical Versions

Snowflake differs from Delta Lake here.

Delta Lake exposes explicit versions such as:

```text
Version 0
Version 1
Version 2
Version 3
```

and supports concepts such as:

```sql
DESCRIBE HISTORY sales;
```

and:

```sql
SELECT *
FROM sales
VERSION AS OF 3;
```

Snowflake does **not** normally expose table states as numbered versions.

Instead, you inspect the statements that changed the table.

---

## 13. View Query History

```sql
SELECT
    query_id,
    query_text,
    start_time,
    end_time,
    user_name
FROM TABLE(
    INFORMATION_SCHEMA.QUERY_HISTORY()
)
WHERE query_text ILIKE '%SALES%'
ORDER BY start_time DESC;
```

Example:

| Time  | Query ID | Operation               |
| ----- | -------- | ----------------------- |
| 08:30 | `q004`   | `DELETE FROM sales`     |
| 08:20 | `q003`   | `UPDATE sales ...`      |
| 08:10 | `q002`   | `INSERT INTO sales ...` |
| 08:00 | `q001`   | `INSERT INTO sales ...` |

Conceptually:

```text
08:00
  |
  | INSERT
  v
08:10
  |
  | UPDATE
  v
08:20
  |
  | DELETE
  v
08:30
  |
  v
NOW
```

You can then use one of those statements:

```sql
SELECT *
FROM sales
BEFORE(
    STATEMENT => 'q004'
);
```

---

# Complete Demo

The following example can be executed sequentially during a class.

---

## Step 1 - Create the Table

```sql
CREATE OR REPLACE TABLE sales (
    id      INT,
    product VARCHAR,
    amount  NUMBER
)
DATA_RETENTION_TIME_IN_DAYS = 1;
```

---

## Step 2 - Insert Initial Data

```sql
INSERT INTO sales VALUES
    (1, 'Laptop', 50000),
    (2, 'Phone', 30000),
    (3, 'Tablet', 20000);
```

Check:

```sql
SELECT * FROM sales;
```

Expected:

```text
1   Laptop   50000
2   Phone    30000
3   Tablet   20000
```

---

## Step 3 - Update Data

```sql
UPDATE sales
SET amount = 55000
WHERE id = 1;
```

Check:

```sql
SELECT * FROM sales;
```

Expected:

```text
1   Laptop   55000
2   Phone    30000
3   Tablet   20000
```

---

## Step 4 - Delete a Row

```sql
DELETE FROM sales
WHERE id = 3;
```

Check:

```sql
SELECT * FROM sales;
```

Expected:

```text
1   Laptop   55000
2   Phone    30000
```

---

## Step 5 - Insert Another Row

```sql
INSERT INTO sales VALUES
    (4, 'Monitor', 15000);
```

Check:

```sql
SELECT * FROM sales;
```

Expected:

```text
1   Laptop    55000
2   Phone     30000
4   Monitor   15000
```

---

## Step 6 - Query Using OFFSET

```sql
SELECT *
FROM sales
AT(OFFSET => -60);
```

This requests the state approximately one minute ago.

For a classroom demo, make the changes slowly enough that the requested offset falls inside the period you want to inspect.

---

## Step 7 - Query Using TIMESTAMP

First capture the current timestamp:

```sql
SELECT CURRENT_TIMESTAMP();
```

Then later query an earlier timestamp:

```sql
SELECT *
FROM sales
AT(
    TIMESTAMP =>
    '2025-04-16 08:00:00 +05:30'::TIMESTAMP_TZ
);
```

---

## Step 8 - Cause an Accidental Delete

```sql
DELETE FROM sales;
```

Check:

```sql
SELECT * FROM sales;
```

Expected:

```text
0 rows
```

---

## Step 9 - Find the DELETE Query ID

```sql
SELECT
    query_id,
    query_text,
    start_time
FROM TABLE(
    INFORMATION_SCHEMA.QUERY_HISTORY()
)
WHERE query_text ILIKE 'DELETE FROM SALES%'
ORDER BY start_time DESC;
```

Suppose the query ID returned is:

```text
01abc123...
```

---

## Step 10 - Inspect the State Before DELETE

```sql
SELECT *
FROM sales
BEFORE(
    STATEMENT => '01abc123...'
);
```

Expected:

```text
1   Laptop    55000
2   Phone     30000
4   Monitor   15000
```

---

## Step 11 - Restore the Historical State

```sql
CREATE TABLE sales_restored
CLONE sales
BEFORE(
    STATEMENT => '01abc123...'
);
```

Validate:

```sql
SELECT * FROM sales_restored;
```

---

## Step 12 - Swap the Restored Table

```sql
ALTER TABLE sales_restored
SWAP WITH sales;
```

Now:

```sql
SELECT * FROM sales;
```

returns the recovered data.

---

# Time Travel Mental Model

Think of Snowflake history as a timeline.

```text
08:00
Initial table
    |
    v
08:10
INSERT
    |
    v
08:20
UPDATE
    |
    v
08:30
DELETE
    |
    v
08:40
Current state
```

You can navigate this timeline in three main ways.

### Relative time

```sql
AT(OFFSET => -3600)
```

Meaning:

```text
one hour ago
```

### Exact time

```sql
AT(
    TIMESTAMP =>
    '2025-04-16 08:00:00 +05:30'::TIMESTAMP_TZ
)
```

Meaning:

```text
exact state at 08:00
```

### Before a particular operation

```sql
BEFORE(
    STATEMENT => '<query_id>'
)
```

Meaning:

```text
state immediately before this query
```

---

# Snowflake vs Delta Lake

| Feature                        | Snowflake | Delta Lake          |
| ------------------------------ | --------- | ------------------- |
| Historical data                | Yes       | Yes                 |
| Time Travel                    | Yes       | Yes                 |
| Timestamp based access         | Yes       | Yes                 |
| Relative OFFSET                | Yes       | Different approach  |
| Numeric table versions         | No        | Yes                 |
| `VERSION AS OF`                | No        | Yes                 |
| Query/statement based recovery | Yes       | Different mechanism |
| Historical clone               | Yes       | Different mechanism |
| Recover dropped table          | `UNDROP`  | Different mechanism |

Conceptually:

```text
DELTA LAKE

Version 0
   |
Version 1
   |
Version 2
   |
Version 3

SELECT *
FROM sales
VERSION AS OF 2;
```

Snowflake is better thought of as a timeline:

```text
SNOWFLAKE

08:00
  |
INSERT
  |
08:10
  |
UPDATE
  |
08:20
  |
DELETE
  |
08:30
```

Access it using:

```sql
AT(OFFSET => ...)
```

or:

```sql
AT(TIMESTAMP => ...)
```

or:

```sql
BEFORE(STATEMENT => ...)
```

---

# Quick Cheat Sheet

```sql
-- Current data
SELECT * FROM sales;


-- One minute ago
SELECT *
FROM sales
AT(OFFSET => -60);


-- One hour ago
SELECT *
FROM sales
AT(OFFSET => -3600);


-- Exact timestamp
SELECT *
FROM sales
AT(
    TIMESTAMP =>
    '2025-04-16 08:00:00 +05:30'::TIMESTAMP_TZ
);


-- Find query history
SELECT
    query_id,
    query_text,
    start_time
FROM TABLE(
    INFORMATION_SCHEMA.QUERY_HISTORY()
)
WHERE query_text ILIKE '%SALES%'
ORDER BY start_time DESC;


-- State before a bad statement
SELECT *
FROM sales
BEFORE(
    STATEMENT => '<query_id>'
);


-- Restore using query ID
CREATE TABLE sales_restored
CLONE sales
BEFORE(
    STATEMENT => '<query_id>'
);


-- Restore using timestamp
CREATE TABLE sales_restored
CLONE sales
AT(
    TIMESTAMP =>
    '2025-04-16 08:00:00 +05:30'::TIMESTAMP_TZ
);


-- Restore using offset
CREATE TABLE sales_restored
CLONE sales
AT(
    OFFSET => -3600
);


-- Replace damaged table with restored table
ALTER TABLE sales_restored
SWAP WITH sales;


-- Recover dropped table
UNDROP TABLE sales;
```

---

# Key Keywords

```text
DATA_RETENTION_TIME_IN_DAYS
    |
    +--> How long historical data is available


AT
    |
    +--> Access a historical point


OFFSET
    |
    +--> Relative time in seconds


TIMESTAMP
    |
    +--> Exact historical time


BEFORE
    |
    +--> State immediately before something


STATEMENT
    |
    +--> Identify a historical point using query ID


CLONE
    |
    +--> Create a table from a historical state


SWAP
    |
    +--> Exchange restored and damaged tables


UNDROP
    |
    +--> Recover a dropped object
```

---

# One-Line Summary

> Snowflake Time Travel keeps historical table states for the configured retention period and lets you access or recover them using `AT`, `OFFSET`, `TIMESTAMP`, `BEFORE`, `STATEMENT`, `CLONE`, and `UNDROP`.
