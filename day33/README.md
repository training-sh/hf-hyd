- Downgrade Hadoop 4.0.1 to 4.0.0 for Spark 3.5.9 compatibility 
- HBase and Sqoop Introduction
- Spark Excercises from D32 will be performed
 

## DIY

- whitelist MysQL/MariaDB port 3306 accessible from pluralsight vm in Security Group

- use mysql from aws cloud shell

```

yarn application -list -appStates ALL
```

```
yarn application -kill application_1788167517234_0003
```

```
export HADOOP_CLIENT_OPTS="-Xms128m -Xmx256m"
```
```
sqoop import \
  -D mapreduce.map.memory.mb=512 \
  -D mapreduce.map.java.opts='-Xms128m -Xmx384m' \
  -D mapreduce.map.cpu.vcores=1 \
  -D yarn.app.mapreduce.am.resource.mb=384 \
  -D yarn.app.mapreduce.am.command-opts='-Xms128m -Xmx256m' \
  --connect "${JDBC_URL}" \
  --driver org.mariadb.jdbc.Driver \
  --username "${DB_USER}" \
  --password-file "file://${PASSWORD_FILE}" \
  --table customers \
  --columns 'customer_id,customer_name,city,signup_date' \
  --target-dir /user/hadoop/d335/customers \
  --fields-terminated-by ',' \
  --null-string '\\N' \
  --null-non-string '\\N' \
  --num-mappers 1

```

  
export local hdfs data into mysql

```
export HADOOP_CLIENT_OPTS="-Xms128m -Xmx256m"
```

```
sqoop export \
  -D mapreduce.map.memory.mb=512 \
  -D mapreduce.map.java.opts='-Xms128m -Xmx384m' \
  -D mapreduce.map.cpu.vcores=1 \
  -D yarn.app.mapreduce.am.resource.mb=384 \
  -D yarn.app.mapreduce.am.command-opts='-Xms128m -Xmx256m' \
  --connect "${JDBC_URL}" \
  --driver org.mariadb.jdbc.Driver \
  --username "${DB_USER}" \
  --password-file "file://${PASSWORD_FILE}" \
  --table customer_scores \
  --columns 'customer_id,score,segment' \
  --export-dir /user/hadoop/d335/customer_scores \
  --input-fields-terminated-by ',' \
  --input-null-string '\\N' \
  --input-null-non-string '\\N' \
  --num-mappers 1
```




```
mysql --version
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

Replace $RDS_ENDPOINT or assign to variable RDS_ENDPOINT=hostname


```
curl -o global-bundle.pem https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem
```

or else 

```
curl --fail --location \
  --output global-bundle.pem \
  https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem
```

check global-bundle.pem exists or not

```
ls
```

it is certificate file

```
head -n 2 global-bundle.pem
```

you may copy this from aws console itself

```
mysql -h yourdbhost.rds.amazonaws.com -P 3306 -u admin -p --ssl-verify-server-cert --ssl-ca=./global-bundle.pem
```


```
mysql -h "$RDS_ENDPOINT" -P 3306 -u admin -p
```
