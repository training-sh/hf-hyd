### WSL 

Open Command Prompt, run

```
wsl
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
