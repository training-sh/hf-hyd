import os

try:
    import mysql.connector
    from mysql.connector import Error

    MYSQL_CONNECTOR_AVAILABLE = True
    MYSQL_IMPORT_ERROR = None
except ImportError as exc:
    mysql = None
    Error = Exception

    MYSQL_CONNECTOR_AVAILABLE = False
    MYSQL_IMPORT_ERROR = exc

    print(
        "MySQL magic unavailable: mysql-connector-python is not installed.\n"
        "Install it with:\n"
        "    %pip install mysql-connector-python\n"
        "Then restart the kernel."
    )


connection = None


def connect():
    global connection

    if not MYSQL_CONNECTOR_AVAILABLE:
        print(
            "Cannot connect to MySQL because mysql-connector-python "
            "is not installed.\n"
            "Install it with:\n"
            "    %pip install mysql-connector-python\n"
            "Then restart the kernel."
        )
        return None

    try:
        if connection is None or not connection.is_connected():
            connection = mysql.connector.connect(
                host=os.environ.get("MYSQL_HOSTNAME", "127.0.0.1"),
                port=int(os.environ.get("MYSQL_PORT", "3306")),
                user=os.environ.get("MYSQL_USERNAME", "root"),
                password=os.environ.get("MYSQL_PASSWORD", "root"),
                database=os.environ.get(
                    "MYSQL_DATABASE",
                    "olist_import_lab",
                ),
            )

            print("Connected:", connection.is_connected())
            print("MySQL version:", connection.server_info)

        return connection

    except Error as exc:
        print(f"MySQL connection failed: {exc}")
        connection = None
        return None


def print_rows(columns, rows):
    if not rows:
        print("No rows returned.")
        return

    widths = [
        max(
            len(str(column)),
            max(len(str(row[index])) for row in rows),
        )
        for index, column in enumerate(columns)
    ]

    print(
        " | ".join(
            str(column).ljust(widths[index])
            for index, column in enumerate(columns)
        )
    )

    print("-+-".join("-" * width for width in widths))

    for row in rows:
        print(
            " | ".join(
                str(value).ljust(widths[index])
                for index, value in enumerate(row)
            )
        )


def execute_sql(sql_text, params=None, *, many=False):
    """Execute SQL and print results or the affected-row count."""

    active_connection = connect()

    if active_connection is None:
        return None

    cursor = active_connection.cursor()

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
                rows = cursor.fetchall()

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


# Register %sql and %%sql.
try:
    from IPython.core.magic import register_line_cell_magic

    @register_line_cell_magic
    def sql(line, cell=None):
        statement = cell if cell is not None else line

        if not statement.strip():
            print("No SQL statement provided.")
            return None

        return execute_sql(statement)

except (ImportError, NameError) as exc:
    print(f"Could not register the SQL magic: {exc}")


# Optional startup connection test.
# if MYSQL_CONNECTOR_AVAILABLE:
#     execute_sql("SELECT 1 + 2 AS result")
#     execute_sql("SELECT 1 + 3 AS another_result")
