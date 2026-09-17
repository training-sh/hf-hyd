from confluent_kafka import Consumer, KafkaError
import json

# Just print the message, no data processing..
# an example for consumer written in python, manual commit offset

TOPIC = "invoices"

consumer = Consumer({
    "bootstrap.servers": "localhost:9092",

    # Consumer group is required
    "group.id": "python-invoice-consumer",

    # Start from earliest if this group has no committed offset
    "auto.offset.reset": "earliest",

    # Manual commit
    "enable.auto.commit": False
})


consumer.subscribe([TOPIC])

print("Waiting for messages...")


try:

    while True:

        # Poll for one message
        msg = consumer.poll(1.0)

        if msg is None:
            continue

        if msg.error():
            print("Consumer error:", msg.error())
            continue


        # Parse JSON message
        invoice_str = msg.value().decode("utf-8")
        invoice = json.loads(invoice_str)


        # Display Kafka metadata
        print("\n-----------------------------")
        print("Topic     :", msg.topic())
        print("Partition :", msg.partition())
        print("Offset    :", msg.offset())

        if msg.key():
            print("Key       :", msg.key().decode("utf-8"))


        # Display parsed invoice
        print("InvoiceNo :", invoice["InvoiceNo"])
        print("StockCode :", invoice["StockCode"])
        print("Quantity  :", invoice["Quantity"])
        print("Price     :", invoice["UnitPrice"])
        print("Customer  :", invoice["CustomerID"])
        print("Country   :", invoice["Country"])


        # Commit ONLY after successful processing
        consumer.commit(message=msg, asynchronous=False)

        print("Offset committed")


except KeyboardInterrupt:

    print("\nStopping consumer...")


finally:

    consumer.close()
