### WSL 

Open Command Prompt, run

```
wsl
```

Hadoop/hive start commands

```
start-dfs.sh
```
```
start-yarn.sh
```
```
mapred --daemon start historyserver
```

```
nohup hive --service metastore > "$HOME/hive-logs/metastore.log" 2>&1 &
```
```
nohup hiveserver2 > "$HOME/hive-logs/hiveserver2.log" 2>&1 &
```
```
jps
```


```
jupyter lab  --notebook-dir=/mnt/c/training
```


```
pip install jupyterlab_sql_editor
```

validate extensions

```
jupyter labextension list
```


```python
from IPython.core.magic import register_cell_magic
from IPython.core.magic import register_line_cell_magic

# for whole cell magic
@register_cell_magic
def sql(line, cell):
    """
    Usage:
        %%sql
        SELECT * FROM customers;
    """
    print ("inside sql", line, cell)
    return execute_sql(cell)

@register_line_cell_magic
def sql(line, cell=None):
    statement = cell if cell is not None else line
    return execute_sql(statement)
```

Dont copy this code

```
def execute_sql(sql_text, params=None, *, many=False):
    """Execute SQL and print results or the affected-row count."""

    active_connection = connect()

    if active_connection is None:
        return None

    cursor = active_connection.cursor(buffered=True)

    try:
        if many:
            cursor.executemany(sql_text, params or [])
        else:
            cursor.execute(sql_text, params or ())

        result_sets = []
        affected_rows = 0

        while True:
            if cursor.with_rows:
                columns = [item[0] for item in cursor.description]
                rows = cursor.fetchall()  # consumes the complete result set

                print_rows(columns, rows)
                result_sets.append(rows)
            else:
                affected_rows += max(cursor.rowcount, 0)

            if not cursor.nextset():
                break

        if result_sets:
            return (
                result_sets[0]
                if len(result_sets) == 1
                else result_sets
            )

        active_connection.commit()
        print(f"Rows impacted: {affected_rows}")
        return affected_rows

    except Error as exc:
        active_connection.rollback()
        print(f"MySQL execution failed: {exc}")
        return None

    finally:
        cursor.close()
```


```
ssh -v -N \
  -o PreferredAuthentications=password \
  -o PubkeyAuthentication=no \
  -o GSSAPIAuthentication=no \
  -o ConnectTimeout=15 \
  -o ExitOnForwardFailure=yes \
  -L 8888:127.0.0.1:8888 \
  user@remote-vm
```
