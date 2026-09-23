import boto3
import time

# demo code using chat

session = boto3.Session(
    profile_name="training",
    region_name="us-east-1"
)

logs = session.client("logs")

LOG_GROUP = "/training/dataeng"
LOG_STREAM = "demo"

logs.put_log_events(
    logGroupName=LOG_GROUP,
    logStreamName=LOG_STREAM,
    logEvents=[
        {
            "timestamp": int(time.time() * 1000),
            "message": "Invoice pipeline started"
        }
    ]
)

print("Log written to CloudWatch")
