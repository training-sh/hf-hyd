import boto3
import pandas as pd
import io

s3 = boto3.client("s3")


def lambda_handler(event, context):

    bucket = "datalake"
    input_key = "bronze/movielens/ratings/ratings.csv"
    output_key = "gold/movielens/ratings_summary.csv"

    # --------------------------------------------------
    # Read CSV from S3
    # --------------------------------------------------

    response = s3.get_object(
        Bucket=bucket,
        Key=input_key
    )

    df = pd.read_csv(response["Body"])

    print("Rows read:", len(df))
    print(df.head())

    # --------------------------------------------------
    # Calculate statistics
    # --------------------------------------------------

    total_count = len(df)
    average_rating = df["rating"].mean()

    print("Total ratings:", total_count)
    print("Average rating:", average_rating)

    # --------------------------------------------------
    # Create output DataFrame
    # --------------------------------------------------

    result_df = pd.DataFrame([{
        "total_ratings": total_count,
        "average_rating": round(average_rating, 2)
    }])

    # --------------------------------------------------
    # Convert DataFrame to CSV
    # --------------------------------------------------

    csv_buffer = io.StringIO()
    result_df.to_csv(csv_buffer, index=False)

    # --------------------------------------------------
    # Write result to S3
    # --------------------------------------------------

    s3.put_object(
        Bucket=bucket,
        Key=output_key,
        Body=csv_buffer.getvalue()
    )

    print(
        f"Result written to "
        f"s3://{bucket}/{output_key}"
    )

    return {
        "statusCode": 200,
        "total_ratings": total_count,
        "average_rating": round(average_rating, 2),
        "output": f"s3://{bucket}/{output_key}"
    }
