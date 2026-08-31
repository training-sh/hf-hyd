- Downgrade Hadoop 4.0.1 to 4.0.0 for Spark 3.5.9 compatibility 
- HBase and Sqoop Introduction
- Spark Excercises from D32 will be performed
- About 50% students off due to mid-semester exam, we cover non-important components


## DIY

- whitelist MariaDB port 3306 accessible from pluralsight vm in Security Group

MariaDB is flavor of MySQL, same codebase

```
sudo apt update
sudo apt install -y mariadb-client
```

```
mariadb --version
```

```
2. Get the RDS connection details

AWS Console:

RDS → Databases → your database → Connectivity & security

Copy:

Endpoint, such as mydb.xxxxxx.ap-south-1.rds.amazonaws.com
Port, normally 3306
Master username from the Configuration tab
```


```
mariadb -h "$RDS_ENDPOINT" -P 3306 -u admin -p
```
