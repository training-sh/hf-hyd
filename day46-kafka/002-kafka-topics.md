## Create and Test a Kafka Topic

ZooKeeper and the Kafka broker should already be running.

from confluent notes to apache kafka notes.. chat changes.. not verified yet.

### Terminal 3 — Create and Inspect Topic

Create a topic named `test` with one partition and replication factor 1:

```bash
kafka-topics.sh \
  --create \
  --bootstrap-server localhost:9092 \
  --replication-factor 1 \
  --partitions 1 \
  --topic test
```

List all topics:

```bash
kafka-topics.sh \
  --list \
  --bootstrap-server localhost:9092
```

Describe the `test` topic:

```bash
kafka-topics.sh \
  --describe \
  --bootstrap-server localhost:9092 \
  --topic test
```

---

## Start a Producer

### Terminal 3 — Producer

Start a console producer:

```bash
kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic test
```

Enter some text and press **Enter**.

Each line entered is published as one Kafka message.

For example:

```text
>hello
>message one
>learning kafka
```

Press **Ctrl+C** to stop the producer.

---

## Start a Consumer

### Terminal 4 — Consumer

Open another terminal and listen for new messages:

```bash
kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic test
```

Messages published after the consumer starts will be displayed.

Press **Ctrl+C** to stop the consumer.

### Read Messages from the Beginning

Read existing messages from the beginning and then continue listening for new messages:

```bash
kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic test \
  --from-beginning
```

### Read from a Specific Partition

Read messages from partition `0`:

```bash
kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic test \
  --partition 0 \
  --from-beginning
```

### Read from a Specific Offset

Read partition `0` starting from offset `4`:

```bash
kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic test \
  --partition 0 \
  --offset 4
```

This starts reading at **offset 4 and continues with subsequent messages**.
