from confluent_kafka import Consumer, TopicPartition
import json

# repurposed code from previous workshops, check topic names, configurations

TOPIC = "invoices"

consumer = Consumer({
    "bootstrap.servers": "localhost:9092",
    "group.id": "python-commit-offset-invoice-consumer",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False
})

consumer.subscribe([TOPIC])

print("Waiting for messages...")

try:
    while True:

        msg = consumer.poll(1.0)

        if msg is None:
            continue

        if msg.error():
            print("Consumer error:", msg.error())
            continue


        # Parse JSON
        invoice = json.loads(
            msg.value().decode("utf-8")
        )

        print("\n-----------------------------")
        print("Topic          :", msg.topic())
        print("Partition      :", msg.partition())
        print("Message Offset :", msg.offset())
        print("Invoice        :", invoice)


        # Partition of the current message
        partition = TopicPartition(
            msg.topic(),
            msg.partition()
        )
 
        # BEFORE COMMIT
       

        before = consumer.committed(
            [partition],
            timeout=5
        )[0]

        print("Before Commit  :", before.offset)

        # MANUAL COMMIT

        consumer.commit(
            message=msg,
            asynchronous=False
        )
 
        # AFTER COMMIT 
      
        after = consumer.committed(
            [partition],
            timeout=5
        )[0]

        print("After Commit   :", after.offset)


except KeyboardInterrupt:
    print("\nStopping consumer...")


finally:
    consumer.close()
