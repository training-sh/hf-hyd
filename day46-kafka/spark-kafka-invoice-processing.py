from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType,
    StructField,
    IntegerType,
    StringType,
    DoubleType
)

# taken from preivous workshops code samples for quick demo
# you may run as jupyter notebook step by step at your own

# ============================================================
# CONSTANTS
# ============================================================

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"

KAFKA_INPUT_TOPIC = "invoices"
KAFKA_OUTPUT_TOPIC = "aggregated-invoices"

# you must run python invoice producer
# python invoice-producer.py

# below is output from spark aggregate, yesterday we wrote to delta

# kafka-console-consumer.sh  --bootstrap-server localhost:9092   --topic aggregated-invoices --from-beginning


HDFS_NAMENODE = "hdfs://localhost:9000"

# hdfs dfs -mkdir -p /checkpoints/invoices/console
# hdfs dfs -mkdir -p /checkpoints/invoices/kafka

CONSOLE_CHECKPOINT_PATH = (
    f"{HDFS_NAMENODE}/checkpoints/invoices/console"
)

KAFKA_CHECKPOINT_PATH = (
    f"{HDFS_NAMENODE}/checkpoints/invoices/kafka"
)


# ============================================================
# SPARK SESSION
# ============================================================

spark = (
    SparkSession.builder
        .master("local[*]")
        .appName("SparkStreamingKafkaInvoiceStream")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")


# ============================================================
# INVOICE JSON SCHEMA
# ============================================================

invoice_schema = StructType([
    StructField("InvoiceNo", IntegerType(), True),
    StructField("StockCode", StringType(), True),
    StructField("Quantity", IntegerType(), True),
    StructField("Description", StringType(), True),
    StructField("InvoiceDate", StringType(), True),
    StructField("UnitPrice", DoubleType(), True),
    StructField("CustomerID", IntegerType(), True),
    StructField("Country", StringType(), True)
])


# ============================================================
# READ STREAM FROM KAFKA
# ============================================================

kafka_df = (
    spark.readStream
        .format("kafka")
        .option(
            "kafka.bootstrap.servers",
            KAFKA_BOOTSTRAP_SERVERS
        )
        .option(
            "subscribe",
            KAFKA_INPUT_TOPIC
        )
        .option(
            "startingOffsets",
            "earliest"
        )
        .load()
)

kafka_df.printSchema()


# ============================================================
# CONVERT KAFKA BINARY VALUE -> STRING
# ============================================================

invoice_json_df = kafka_df.selectExpr(
    "timestamp",
    "CAST(value AS STRING) AS value"
)


# ============================================================
# PARSE JSON
# ============================================================

parsed_df = invoice_json_df.select(
    "timestamp",
    F.from_json(
        F.col("value"),
        invoice_schema
    ).alias("invoice")
)


# Extract JSON fields
invoice_df = parsed_df.select(
    "timestamp",
    "invoice.*"
)


# ============================================================
# CALCULATE AMOUNT
# ============================================================

invoice_df = invoice_df.withColumn(
    "Amount",
    F.col("Quantity") * F.col("UnitPrice")
)


# ============================================================
# WINDOW AGGREGATION
#
# Total sales by country for each 60-second window
# ============================================================

aggregated_df = (
    invoice_df
        .groupBy(
            "Country",
            F.window(
                F.col("timestamp"),
                "60 seconds",
                "60 seconds"
            )
        )
        .agg(
            F.sum("Amount").alias("TotalAmount")
        )
)


# ============================================================
# CONVERT AGGREGATION TO JSON FOR KAFKA
# ============================================================

kafka_output_df = aggregated_df.select(
    F.to_json(
        F.struct(
            F.col("Country"),
            F.col("window"),
            F.col("TotalAmount")
        )
    ).alias("value")
)


# ============================================================
# OUTPUT 1: CONSOLE
# ============================================================

console_query = (
    aggregated_df
        .writeStream
        .format("console")
        .outputMode("complete")
        .option("truncate", "false")
        .option(
            "checkpointLocation",
            CONSOLE_CHECKPOINT_PATH
        )
        .start()
)


# ============================================================
# OUTPUT 2: KAFKA
# ============================================================

kafka_query = (
    kafka_output_df
        .writeStream
        .format("kafka")
        .outputMode("complete")
        .option(
            "kafka.bootstrap.servers",
            KAFKA_BOOTSTRAP_SERVERS
        )
        .option(
            "topic",
            KAFKA_OUTPUT_TOPIC
        )
        .option(
            "checkpointLocation",
            KAFKA_CHECKPOINT_PATH
        )
        .start()
)


# ============================================================
# WAIT FOR STREAMING QUERIES
# ============================================================

spark.streams.awaitAnyTermination()
