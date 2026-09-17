## Start Apache Kafka

created from confluent kafka notes..


This setup runs a **single Apache Kafka broker** using ZooKeeper.

### Terminal 1 — Start ZooKeeper

Open the first terminal and start ZooKeeper:

```bash
$KAFKA_HOME/bin/zookeeper-server-start.sh \
  $KAFKA_HOME/config/zookeeper.properties
```

Keep this terminal running.

### Terminal 2 — Start Kafka Broker

Open a second terminal and start the Kafka broker:

```bash
$KAFKA_HOME/bin/kafka-server-start.sh \
  $KAFKA_HOME/config/server.properties
```

Keep this terminal running.

The default broker configuration uses:

```properties
broker.id=0
listeners=PLAINTEXT://:9092
log.dirs=/tmp/kafka-logs
```

Kafka is now running with:

```text
Terminal 1 : ZooKeeper
Terminal 2 : Kafka Broker
              └── Broker ID: 0
              └── Port: 9092
```
