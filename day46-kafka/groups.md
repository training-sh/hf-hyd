
## Consumer group

repurposed  old notes with chat, not tested

# Kafka Consumer Groups and Offset Management

Topic used in the examples:

```text
invoices
```

Consumer group:

```text
python-invoice-consumer
```

## List All Consumer Groups

```bash
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --list
```

## Describe a Consumer Group

```bash
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --group python-invoice-consumer
```

## Offset Reset Modes

There are two modes when resetting offsets:

1. `--dry-run` — shows the planned offset changes without applying them.
2. `--execute` — applies the offset changes.

It is safer to use `--dry-run` first and then use `--execute`.

## Topic Selection

There are two common options:

1. `--topic invoices` — reset offsets for a specific topic.
2. `--all-topics` — reset offsets for all topics associated with the consumer group.

## Reset Offset to Earliest

Reset the offsets of the `invoices` topic to the earliest available offsets:

```bash
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --group python-invoice-consumer \
  --reset-offsets \
  --to-earliest \
  --execute \
  --topic invoices
```

## Reset Offset to Latest

Reset the offsets to the latest available offsets:

```bash
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --group python-invoice-consumer \
  --reset-offsets \
  --to-latest \
  --execute \
  --topic invoices
```

## Reset Offset to a Specific Date and Time

Use:

```text
YYYY-MM-DDTHH:mm:ss.sss
```

Example:

```bash
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --group python-invoice-consumer \
  --reset-offsets \
  --to-datetime 2021-06-15T11:01:01.999 \
  --execute \
  --topic invoices
```

## Check the Offset After Reset

```bash
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --group python-invoice-consumer
```

## Shift Current Offset Forward

Move the current offsets forward by 10:

```bash
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --group python-invoice-consumer \
  --reset-offsets \
  --shift-by 10 \
  --execute \
  --topic invoices
```

## Shift Current Offset Backward

Move the current offsets backward by 5:

```bash
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --group python-invoice-consumer \
  --reset-offsets \
  --shift-by -5 \
  --execute \
  --topic invoices
```

## Reset a Specific Partition to a Specific Offset

Reset partition `1` to offset `4`:

```bash
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --group python-invoice-consumer \
  --reset-offsets \
  --to-offset 4 \
  --execute \
  --topic invoices:1
```

Reset partitions `1` and `2` to offset `4`:

```bash
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --group python-invoice-consumer \
  --reset-offsets \
  --to-offset 4 \
  --execute \
  --topic invoices:1,2
```

## Reset Offsets for All Topics

Reset all topics associated with the consumer group to their earliest offsets:

```bash
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --group python-invoice-consumer \
  --reset-offsets \
  --to-earliest \
  --execute \
  --all-topics
```

# Dry Run

`--dry-run` displays the proposed offset changes without actually changing the committed offsets.

It is safer to perform a dry run first:

```bash
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --group python-invoice-consumer \
  --reset-offsets \
  --shift-by -5 \
  --dry-run \
  --topic invoices
```

Then, if the proposed offsets are correct:

```bash
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --group python-invoice-consumer \
  --reset-offsets \
  --shift-by -5 \
  --execute \
  --topic invoices
```

## Dry Run with Date and Time

```bash
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --group python-invoice-consumer \
  --reset-offsets \
  --to-datetime 2021-06-15T07:01:01.999 \
  --dry-run \
  --topic invoices
```

## Important

The consumer group should normally be inactive before resetting its offsets.

Check the group before performing a reset:

```bash
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --group python-invoice-consumer
```

After resetting, describe the group again to verify the new committed offsets:

```bash
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --group python-invoice-consumer
```
