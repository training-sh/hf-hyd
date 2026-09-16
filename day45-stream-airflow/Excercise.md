# Excercise

```
- Use Ecomm siler layer data
- Compute running total for the invoice
- Invoice has itemized billing
- Group by invoice_no, sum (amount), sum (quantity) , customer_id
- Use merge statement if already invoice present update else insert

use water mark

no use of window f

final output like,

InvoiceNo,TotalAmount,TotalItems,customer_id
```

If you need to debug to print to console, use below examples

```python

country_sales_query_console = (country_hourly_sales_df.writeStream
    .outputMode("update")
    .format("console")
    .trigger(processingTime="1 minute")
    .queryName("ecomm_country_hourly_console")
    .start())

# country_sales_query_console.stop() # to stop the query
```
