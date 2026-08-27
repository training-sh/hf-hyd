# Not tested sql

# movielens data

1. create movielens directory in hadoop /user/<<name>>
2. create movies and ratings directory under /user/<<name>>
3. upload movies.csv into movies, ratings.csv into ratings directory
4. in hive, create database called movielens
5. under movielens database, create two tables, movies table, ratings table


```
CREATE EXTERNAL TABLE IF NOT EXISTS my_database.my_table (
    id INT,
    name STRING,
    age INT,
    city STRING
)
ROW FORMAT DELIMITED 
FIELDS TERMINATED BY ',' 
STORED AS TEXTFILE 
LOCATION '/user/hadoop/data/my_csv_folder/'
TBLPROPERTIES ("skip.header.line.count"="1");
```

or below example

```
CREATE EXTERNAL TABLE IF NOT EXISTS my_database.my_table (
    id INT,
    name STRING,
    age INT,
    city STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
   "separatorChar" = ",",
   "quoteChar"     = "\"",
   "escapeChar"    = "\\"
)  
STORED AS TEXTFILE
LOCATION '/user/hadoop/data/my_csv_folder/'
TBLPROPERTIES ("skip.header.line.count"="1");
```
