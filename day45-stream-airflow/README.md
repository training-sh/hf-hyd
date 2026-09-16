- First half day cover spark streaming introduction
- Spark Streaming hands-on with Ecomm data
- Second half, we will continue airflow with map-reduce, yarn, spark submit over WSL


```python
COUNTRY_PARQUET_PATH = HDFS_ROOT + "/gold/ecomm/country_hourly_sales-parquet"
COUNTRY_PARQUET_CHECKPOINT = HDFS_ROOT + "/checkpoints/ecomm/parquet-country-sales"
# create respective hdfs directory

country_hourly_sales_df2 = (silver_df
    .withWatermark("InvoiceDate", "20 years") # we have too old dataset
    .groupBy(F.window("InvoiceDate", "1 hour"), "Country") # order does not matter, consider both columsn
    # .groupBy( "Country", F.window("InvoiceDate", "1 hour")) # order does not matter, consider both columsn
    .agg(F.sum("Amount").alias("TotalSales"))
    .select(F.col("window.start").alias("HourStart"),
            F.col("window.end").alias("HourEnd"), "Country", "TotalSales")
                            )
 

ecomm_country_hourly_parquet = (country_hourly_sales_df2
    .writeStream
    .format("parquet")
    .outputMode("append")
    .option("checkpointLocation", COUNTRY_PARQUET_CHECKPOINT)
    .trigger(processingTime="1 minute")
    .queryName("ecomm_country_hourly_parquet")
    .start(COUNTRY_PARQUET_PATH))
```

File rename fix for hdfs/rename space with -

```
for f in *" "*; do mv -- "$f" "${f// /-}"; done
```

notes..

```


(apple, 2) <-- event <--
(apple, 3) <--
(orange, 1) <--
(apple, 1)

df.filter (name == 'apple')  <--  stateless
	(apple, 2)
	(apple, 3)


df.groupBy(name)
	.sum(value) <-- stateful function

state calculation 




apple   5 (old value 2) <-- inserted for (apple, 2) event, new result now apple is 5, updated for (apple, 3) event, updated for (apple, 1)
orange  1  <-- insert

State table in memory internally (insert/update)
apple 6 <-- insert event , update to 5, update to 6
orange 1

Whenever is there change in table state change, you stream the output, table change as stream 

(apple, 2)
(apple, 5)
(orange, 1)
(apple, 6)
```

```

(IN, 10, 16-09-2026 14:10 PM)
(IN, 15, 16-09-2026 14:45 PM)
(IN, 30, 16-09-2026 15:30 PM)
(USA, 45, 16-09-2026 15:30 PM)

table 1: country - from beginning upto now, total will be kept per country , no day/time window

country    total_sales_amount GROUP BY .groupBy(country)
IN              55
USA             45

table 2 (time window + country) hourly   .groupBy(window(country, time, 1 hour))

country     start_time                    end_time                   total_sales_amount
IN          16-09-2026 14:00            16-09-2026 15:00               25 (was 10/insert, was 15, sum 10 +)
IN          16-09-2026 15:00            16-09-2026 16:00               30 (insert)
USA         16-09-2026 15:00            16-09-2026 16:00               45 (insert)

```










```
