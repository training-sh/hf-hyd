import logging

# you may copy this code into your existing lambda, code is given just for reference

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("Invoice pipeline started")
    logger.info("Processing invoice 1001")

    return {"statusCode": 200}
