import base64
import json


def lambda_handler(event, context):
    output = []

    for record in event["records"]:
        record_id = record["recordId"]

        try:
            # Decode Firehose record
            payload = base64.b64decode(
                record["data"]
            ).decode("utf-8")

            # Convert JSON string to dict
            data = json.loads(payload)

            # Derive amount
            quantity = float(data.get("Quantity", 0))
            unit_price = float(data.get("UnitPrice", 0))

            data["Amount"] = round(
                quantity * unit_price,
                2
            )

            # Firehose output - newline is useful for JSON files in S3
            transformed_data = (
                json.dumps(data) + "\n"
            ).encode("utf-8")

            output.append({
                "recordId": record_id,
                "result": "Ok",
                "data": base64.b64encode(
                    transformed_data
                ).decode("utf-8")
            })

        except Exception as e:
            print(
                f"Transformation failed for "
                f"{record_id}: {e}"
            )

            output.append({
                "recordId": record_id,
                "result": "ProcessingFailed",
                "data": record["data"]
            })

    return {
        "records": output
    }
