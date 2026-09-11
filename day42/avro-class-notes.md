```
Why avro, problems with text formats

xml/csv/json/logs - NO SCHEMA
xml/csv/json/logs - TEXT BASED FORMAT/STRING/EVERYTING STORED AS TEXT/STRING
COST - deserialization 
            parsing - type casting, 
            customer_id stored as string, my app need this to be int 
                int(customer_id) to use in app
            same for bool and float..

Serialization 
        to convert the data from tables, to xml/csv/json/logs
            str(123) -> "123" then saved into xml/csv/json/logs
    
other issues 

missing values
column names not standazrided 
    invoice_id
    inovice_no 
    invoice_number
    inv
    invoiceNumber

customer_id,customername, is_active,age
123,arun,true,34.4 <-- all are strings/text only, 18 chars

<customer> <-- 138 chars
<customer_id>123</customer_id>
<customer_name>arun</customer_name>
<is_active>true</is_active>
<age>34.4</age>
</customer>

json {"customer_id": 123.....}

--

AVRO

SPECIFICATION

    SCHEMA - json format

    FILE FORMAT .avro
    FILE Data will be stored in binary format, row based, data in transit
    stored into hdfs, s3, datalakes
```
    
