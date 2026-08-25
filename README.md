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

Spark master
```
/opt/spark/sbin/start-master.sh
```

Spark worker

```
/opt/spark/sbin/start-worker.sh "spark://$(hostname):7077"
```


```
nohup hive --service metastore > "$HOME/hive-logs/metastore.log" 2>&1 &
```
```
nohup hiveserver2 > "$HOME/hive-logs/hiveserver2.log" 2>&1 &
```

```
beeline -u 'jdbc:hive2://localhost:10000/default' -n "$USER"
```



## Web interfaces

Open these URLs in the Windows browser while Hadoop is running in WSL:

| Interface | URL | What to inspect |
|---|---|---|
|Spark UI | [http://localhost:8080](http://localhost:8080) | Spark UI |
| ResourceManager | [http://localhost:8088](http://localhost:8088) | Applications, states, queues, nodes, memory, and vCores |
| ResourceManager applications | [http://localhost:8088/cluster/apps](http://localhost:8088/cluster/apps) | Running, completed, and failed applications |
| ResourceManager nodes | [http://localhost:8088/cluster/nodes](http://localhost:8088/cluster/nodes) | NodeManager health and available resources |
| NodeManager | [http://localhost:8042](http://localhost:8042) | Containers and local logs on this node |
| MapReduce JobHistory | [http://localhost:19888](http://localhost:19888) | Completed MapReduce jobs, tasks, attempts, counters, and logs |
| NameNode | [http://localhost:9870](http://localhost:9870) | HDFS files, DataNodes, capacity, and cluster storage |

WSL normally forwards listening ports to Windows `localhost`. If a page does not open, confirm that the Hadoop daemons are running:

~~~bash
jps
~~~

We needed HDFS and Yarn up, Spark Master and Worker up and running. 

Check which ports are listening:

~~~bash
ss -ltnp
~~~
Set this property before orc, later view

```
SET mapreduce.job.user.classpath.first=true;
```


```
jps
```

```
export AWS_ACCESS_KEY_ID=key-from-plural-sight
export AWS_SECRET_ACCESS_KEY=secret-from-plural-sight
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
