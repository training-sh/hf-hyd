# Inspect Kafka Metadata in ZooKeeper

## 1. Open a New Command Prompt

Open a **new terminal/command prompt** and connect to ZooKeeper:

```bash
zookeeper-shell localhost:2181
```

The above command connects to the ZooKeeper server running on port `2181`.

---

## 2. List ZooKeeper Root Nodes

```bash
ls /
```

This displays the top-level ZooKeeper znodes.

---

## 3. Check Kafka Brokers

List the contents of the Kafka `brokers` znode:

```bash
ls /brokers
```

---

## 4. List Registered Kafka Brokers

```bash
ls /brokers/ids
```

This displays the IDs of Kafka brokers currently registered with ZooKeeper.

---

## 5. View Broker Information

For broker ID `0`:

```bash
get /brokers/ids/0
```

This displays metadata about the Kafka broker, such as its host, port, endpoints, and broker ID.

---

## 6. List Kafka Topics

```bash
ls /brokers/topics
```

This displays the Kafka topics registered in ZooKeeper.

---

## 7. Check Partition State

For topic `test`, inspect the state of partition `0`:

```bash
get /brokers/topics/test/partitions/0/state
```

This displays partition-state information such as the leader, ISR (in-sync replicas), and controller epoch.
