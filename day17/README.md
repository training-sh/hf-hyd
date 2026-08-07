excercises, lab discovery

Replace print_rows,execute_sql in your notebook

```python
def print_rows(columns, rows):
    if not rows:
        print("No rows returned.")
        return
    print(" | ".join(columns))
    print("-+-".join("-" * len(column) for column in columns))
    for row in rows:
        print(" | ".join(str(value) for value in row))


def execute_sql(sql_text, params=None, *, many=False):
    """Execute one SQL statement and print results or the affected-row count."""
    cursor = connection.cursor()
    try:
        if many:
            cursor.executemany(sql_text, params or [])
        else:
            cursor.execute(sql_text, params or ())

        result_sets = []
        affected_rows = cursor.rowcount
        while True:
            if cursor.with_rows:
                columns = [item[0] for item in cursor.description]
                rows = cursor.fetchall()
                print_rows(columns, rows)
                result_sets.append(rows)
            if not cursor.nextset():
                break

        if result_sets:
            return result_sets[0] if len(result_sets) == 1 else result_sets
        connection.commit()
        print(f"Rows impacted: {affected_rows}")
        return affected_rows
    except Error:
        connection.rollback()
        raise
    finally:
        cursor.close()

```
