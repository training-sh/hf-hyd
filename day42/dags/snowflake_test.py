from datetime import datetime

from airflow.sdk import DAG, task
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook


with DAG(
    dag_id="snowflake_test2",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
):

    @task
    def query_snowflake():

        hook = SnowflakeHook(
            snowflake_conn_id="snowflake"
        )

        result = hook.get_first("""
            SELECT
                CURRENT_USER(),
                CURRENT_DATABASE(),
                CURRENT_SCHEMA(),
                CURRENT_WAREHOUSE()
        """)

        print("Snowflake result:", result)

        return result

    query_snowflake()
