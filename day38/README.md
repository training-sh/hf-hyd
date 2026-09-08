- snowflake introduction
- Stages, ETL
- Datawarehouse problem statements, business problem discussion

You will be using learning db
```
SNOWFLAKE_LEARNING_DB
```

```
CREATE SCHEMA yourname;
```

then use the schema daily basic

just redo one more time  the movies.md

```

WITH xml_sales AS (
    SELECT PARSE_XML(SOURCE_DOCUMENT) AS invoice
    FROM RAW.SALES_BHARATLINK
)
SELECT
   XMLGET(F.VALUE, 'invoice_no'):"$"::STRING       AS INVOICE_NO,
    f.value AS sale_xml
FROM xml_sales,
LATERAL FLATTEN(INPUT => invoice:"$") f
WHERE GET(f.value, '@')::VARCHAR = 'sale';
```

- FLATTEN(INPUT => invoice:"$") basically get all child elements inside invoice that is weeklySales xml document element
- GET(f.value, '@')::VARCHAR gets XML element name <sale .../>
- XMLGET(F.VALUE, 'invoice_no'):"$"::STRING , here we get invoice_no which is an element <invoice_no>123</invoice_no>
- to get attribute within element , you must use @attribute name , example below, GET(invoice, '@partner')::VARCHAR AS partner reads partner attribute from weekly sales

```

WITH xml_sales AS (
    SELECT PARSE_XML(SOURCE_DOCUMENT) AS invoice
    FROM RAW.SALES_BHARATLINK
)
SELECT
    GET(invoice, '@partner')::VARCHAR AS partner
FROM xml_sales;
```
