import json, os
from decimal import Decimal
import boto3
from botocore.config import Config

s3 = boto3.client(
    "s3",
    region_name=os.environ["AWS_REGION"],
    config=Config(signature_version="s3v4", s3={"addressing_style": "virtual"}),
)
table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])
BUCKET = os.environ["BUCKET_NAME"]


def _default(o):
    if isinstance(o, Decimal):
        return float(o)
    raise TypeError


def handler(event, context):
    """Return all images with labels and a temporary view URL from Amazon Recognition service from aws"""
    items = table.scan().get("Items", [])
    items.sort(key=lambda i: i.get("uploadedAt", 0), reverse=True)
    for item in items:
        item["url"] = s3.generate_presigned_url(
            print("printing presedigned url..")
            "get_object",
            Params={"Bucket": BUCKET, "Key": item["imageId"]},
            ExpiresIn=900,
        )
    return {"statusCode": 200, "headers": {"Content-Type": "application/json"},
            "body": json.dumps(items, default=_default)}
