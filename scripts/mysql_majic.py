import os
import mysql.connector
from mysql.connector import Error

"""
ipython profile locate

on the profile directory, create this file, store the content..

~/.ipython/profile_default/startup/mysql_magic.py

"""

connection = None 

def connect():
    global connection

    if not connection or not connection.is_connected():
        connection = mysql.connector.connect(
            host=os.environ.get("MYSQL_HOSTNAME", "127.0.0.1"),
            port=int(os.environ.get("MYSQL_PORT", "3306")),
            user=os.environ.get("MYSQL_USERNAME", "root"),
            password=os.environ.get("MYSQL_PASSWORD", "root"),
            database=os.environ.get("MYSQL_DATABASE", "olist_import_lab"),
        )

        print("Connected:", connection.is_connected())
        print("MySQL version:", connection.server_info)


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
    connect()

    global connection

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

# magic sql part

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



execute_sql("SELECT 1 + 2 as result")
execute_sql("SELECT 1 + 3 as another_result")
