- Downgrade Hadoop 4.0.1 to 4.0.0 for Spark 3.5.9 compatibility 
- HBase and Sqoop Introduction
- Spark Excercises from D32 will be performed
 

## DIY

- whitelist MysQL/MariaDB port 3306 accessible from pluralsight vm in Security Group

  

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
