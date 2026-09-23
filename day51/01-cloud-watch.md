### 1. Create CloudWatch Log Group

```bash
aws logs create-log-group \
  --log-group-name /training/dataeng \
  --profile training
```

### 2. Create Log Stream

```bash
aws logs create-log-stream \
  --log-group-name /training/dataeng \
  --log-stream-name demo \
  --profile training
```

### 3. Write a Log Message

```bash
aws logs put-log-events \
  --log-group-name /training/dataeng \
  --log-stream-name demo \
  --log-events timestamp=$(date +%s%3N),message="Hello from Data Engineering training" \
  --profile training
```

### 4. Read Log Messages

```bash
aws logs get-log-events \
  --log-group-name /training/dataeng \
  --log-stream-name demo \
  --profile training
```

### 5. Tail Logs Continuously

```bash
aws logs tail /training/dataeng \
  --follow \
  --profile training
```

Keep the above command running in one terminal.

### 6. Send Another Log Message

From another terminal:

```bash
aws logs put-log-events \
  --log-group-name /training/dataeng \
  --log-stream-name demo \
  --log-events timestamp=$(date +%s%3N),message="Invoice pipeline started" \
  --profile training
```

The new message should immediately appear in the terminal running `aws logs tail`.
