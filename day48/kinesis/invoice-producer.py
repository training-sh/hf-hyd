import boto3
import random
import uuid
import datetime
import json
import time

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

KINESIS_STREAM_NAME = "gks-invoices"
AWS_REGION = "us-east-1"

SAMPLES = 10000
DELAY = 5  # seconds between invoices

countries = [
    "USA", "CA", "IN", "AT", "BE", "BG", "HR", "CY", "CZ", "DK",
    "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT", "LV", "LT",
    "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE"
]

stock_codes = [
    "85123A",
    "71053",
    "84406B",
    "84406G",
    "84406E"
]

customer_codes = [
    17850,
    13047,
    12583,
    17850
]


# ---------------------------------------------------------
# Kinesis Client
# ---------------------------------------------------------

kinesis_client = boto3.client(
    "kinesis",
    region_name=AWS_REGION
)


# ---------------------------------------------------------
# Generate invoices
# ---------------------------------------------------------

for i in range(SAMPLES):

    # Generate invoice number
    invoice_no = uuid.uuid4().hex[:8].upper()

    customer_code = random.choice(customer_codes)
    country = random.choice(countries)

    # UTC timestamp in ISO-8601 format
    invoice_date = datetime.datetime.now(
        datetime.timezone.utc
    ).isoformat()

    # Each invoice contains 3-10 items
    number_of_items = random.randint(3, 10)

    print(
        f"\nInvoice {i + 1}/{SAMPLES}: "
        f"{invoice_no} | "
        f"Customer={customer_code} | "
        f"Country={country} | "
        f"Items={number_of_items}"
    )

    for j in range(number_of_items):

        quantity = random.randint(1, 10)
        unit_price = float(random.randint(1, 5))
        stock_code = random.choice(stock_codes)

        invoice = {
            "InvoiceNo": invoice_no,
            "StockCode": stock_code,
            "Quantity": quantity,
            "Description": "TODO",
            "InvoiceDate": invoice_date,
            "UnitPrice": unit_price,
            "CustomerID": customer_code,
            "Country": country
        }

        # Convert Python dictionary to JSON
        invoice_str = json.dumps(invoice)

        print("Sending:", invoice_str)

        # Send one invoice-line event to Kinesis
        response = kinesis_client.put_record(
            StreamName=KINESIS_STREAM_NAME,
            Data=invoice_str.encode("utf-8"),
            PartitionKey=country
        )

        print(
            "Kinesis:",
            "ShardId =", response["ShardId"],
            "SequenceNumber =", response["SequenceNumber"]
        )

    # Wait before generating the next invoice
    time.sleep(DELAY)
