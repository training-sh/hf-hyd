"""MovieLens: local CSV -> bronze -> silver Parquet -> gold (4 formats) -> MySQL.
Run: airflow dags test d446_movielens_pipeline -f ~/airflow/dags/d44_course/d446_movielens_pipeline.py
Or trigger manually in the UI. See ~/D44_DAG/MOVIELENS.md for deployment/parameters.
Reruns replace this dataset's silver/gold outputs and MySQL table.
Bronze is archived only after JDBC verification. No automatic schedule.
"""
from datetime import datetime, timezone, timedelta
from pathlib import Path
import socket
from airflow.sdk import DAG, Param
from airflow.providers.standard.operators.bash import BashOperator

HOME = str(Path.home())
# Pass parameters through environment variables, never interpolate them into shell code.
ENV = {
    "JAVA_HOME": "/usr/lib/jvm/java-11-openjdk-amd64",
    "HADOOP_HOME": "/opt/hadoop", "HADOOP_CONF_DIR": "/opt/hadoop/etc/hadoop",
    "SPARK_HOME": "/opt/spark", "PYSPARK_PYTHON": HOME + "/dataengenv/bin/python",
    "LOCAL_DATA": "{{ params.local_data }}", "SCRIPTS": "{{ params.scripts }}",
    "MASTER": "{{ params.master }}", "BRONZE": "{{ params.bronze }}",
    "SILVER": "{{ params.silver }}", "GOLD": "{{ params.gold }}",
    "MIN_RATING": "{{ params.min_rating }}", "MIN_RATINGS": "{{ params.min_ratings }}",
    "MIN_AVERAGE": "{{ params.min_average }}", "MYSQL_HOST": "{{ params.mysql_host }}",
    "MYSQL_PORT": "{{ params.mysql_port }}", "MYSQL_DATABASE": "{{ params.mysql_database }}",
    "MYSQL_TABLE": "{{ params.mysql_table }}", "MYSQL_USER": "{{ params.mysql_user }}",
    "JDBC_JAR": "{{ params.jdbc_jar }}", "ARCHIVE": "{{ params.archive_bronze }}",
    "RUN_ID": "{{ run_id }}",
}
PREFIX = r'''set -euo pipefail
export PATH="$JAVA_HOME/bin:$HADOOP_HOME/bin:$SPARK_HOME/bin:$PATH"
# This exercise uses the requested test-system root/root login.
export MYSQL_PWD="${MYSQL_PWD:-root}"
submit() {
  spark-submit --master "$MASTER" --deploy-mode client --total-executor-cores 2 \
    --executor-memory 1g --conf spark.sql.shuffle.partitions=2 "$@"
}
'''
with DAG(
    dag_id="d446_movielens_pipeline", schedule=None, catchup=False, max_active_runs=1,
    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc), doc_md=__doc__,
    default_args={"retries": 0, "execution_timeout": timedelta(minutes=15)},
    tags=["d44", "movielens"],
    params={
        "local_data": Param(HOME + "/D44_DAG/movielens", type="string"),
        "scripts": Param(HOME + "/D44_DAG/scripts", type="string"),
        "master": Param("spark://" + socket.gethostname() + ":7077", type="string"),
        "bronze": Param("/bronze/movielens", type="string", pattern="^/bronze/.+"),
        "silver": Param("/silver/movielens", type="string", pattern="^/silver/.+"),
        "gold": Param("/gold/movielens/popular-movies", type="string", pattern="^/gold/.+"),
        "min_rating": Param(0.5, type="number"),
        "min_ratings": Param(100, type="integer", minimum=1),
        "min_average": Param(3.5, type="number"),
        "mysql_host": Param("127.0.0.1", type="string"),
        "mysql_port": Param(3306, type="integer", minimum=1, maximum=65535),
        "mysql_database": Param("movielens", type="string", pattern="^[A-Za-z][A-Za-z0-9_]*$"),
        "mysql_table": Param("popular_movies", type="string", pattern="^[A-Za-z][A-Za-z0-9_]*$"),
        "mysql_user": Param("root", type="string"),
        "jdbc_jar": Param("/opt/spark/jars/mysql-connector-j-8.4.0.jar", type="string"),
        "archive_bronze": Param(True, type="boolean"),
    },
) as dag:
    def task(name, command):
        return BashOperator(task_id=name, bash_command=PREFIX + command,
                            env=ENV, append_env=True)

    # Validate both local files before uploading either. All paths below are HDFS paths.
    upload = task("upload_bronze", r'''
test -s "$LOCAL_DATA/movies.csv"
test -s "$LOCAL_DATA/ratings.csv"
test -f "$JDBC_JAR"
for kind in movies ratings; do
  hdfs dfs -mkdir -p "$BRONZE/$kind"
  hdfs dfs -put -f "$LOCAL_DATA/$kind.csv" "$BRONZE/$kind/$kind.csv"
done
hdfs dfs -ls -R "$BRONZE"
''')
    movies = task("movies_to_silver", r'''
submit "$SCRIPTS/Movies-Bronze-To-Silver.py" --input "hdfs://$BRONZE/movies/movies.csv" --output "hdfs://$SILVER/movies" --partitions 2
''')
    ratings = task("ratings_to_silver", r'''
submit "$SCRIPTS/Ratings-Bronze-To-Silver.py" --input "hdfs://$BRONZE/ratings/ratings.csv" --output "hdfs://$SILVER/ratings" --partitions 2 --min-rating "$MIN_RATING"
''')
    gold = task("join_to_gold", r'''
submit "$SCRIPTS/MovieLensAnalytics.py" --movies "hdfs://$SILVER/movies" --ratings "hdfs://$SILVER/ratings" --output "hdfs://$GOLD" --min-ratings "$MIN_RATINGS" --min-average "$MIN_AVERAGE" --partitions 1
''')
    database = task("create_database", r'''
# Validate again at the shell boundary before using an SQL identifier.
[[ "$MYSQL_DATABASE" =~ ^[A-Za-z][A-Za-z0-9_]*$ ]]
mysql --host="$MYSQL_HOST" --port="$MYSQL_PORT" --user="$MYSQL_USER" \
  --execute="CREATE DATABASE IF NOT EXISTS $MYSQL_DATABASE CHARACTER SET utf8mb4;"
''')
    jdbc = task("gold_to_mysql", r'''
submit --jars "$JDBC_JAR" "$SCRIPTS/Gold-PopularMovies-To-OLTP.py" \
  --input "hdfs://$GOLD/parquet" \
  --jdbc-url "jdbc:mysql://$MYSQL_HOST:$MYSQL_PORT/$MYSQL_DATABASE?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=UTC" \
  --table "$MYSQL_TABLE" --user "$MYSQL_USER" --password-env MYSQL_PWD
''')
    archive = task("archive_bronze", r'''
if [[ "${ARCHIVE,,}" == true ]]; then
  key=$(printf '%s' "$RUN_ID" | sha256sum | cut -c1-12)
  for kind in movies ratings; do
    src="$BRONZE/$kind/$kind.csv"
    dest="$BRONZE/processed/$kind/$key"
    hdfs dfs -mkdir -p "$dest"
    if hdfs dfs -test -e "$src"; then
      hdfs dfs -mv "$src" "$dest/$kind.csv"
    else
      # Clearing only this task is safe after a successful move.
      hdfs dfs -test -e "$dest/$kind.csv"
    fi
  done
fi
''')
    # Sequential silver jobs keep this small standalone Spark machine lightly loaded.
    upload >> movies >> ratings >> gold >> database >> jdbc >> archive
