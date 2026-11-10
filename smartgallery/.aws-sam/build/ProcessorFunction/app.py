import os, time
from decimal import Decimal
from urllib.parse import unquote_plus
import boto3

rekognition = boto3.client("rekognition")
table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])


def handler(event, context):
    """Triggered by S3 ObjectCreated: label the image with Rekognition, store result in DynamoDB."""
    for record in event["Records"]:
        bucket = record["s3"]["bucket"]["name"]
        key = unquote_plus(record["s3"]["object"]["key"])
        size = record["s3"]["object"].get("size", 0)
        print(f"Processing s3://{bucket}/{key}")

        result = rekognition.detect_labels(
            Image={"S3Object": {"Bucket": bucket, "Name": key}},
            MaxLabels=8,
            MinConfidence=75,
        )
        labels = [
            {"name": l["Name"], "confidence": Decimal(str(round(l["Confidence"], 1)))}
            for l in result["Labels"]
        ]
        table.put_item(Item={
            "imageId": key,
            "labels": labels,
            "sizeBytes": size,
            "uploadedAt": int(time.time()),
        })
    return {"status": "ok"}
