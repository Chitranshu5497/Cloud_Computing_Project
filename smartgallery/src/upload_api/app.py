import json, os, uuid
import boto3
from botocore.config import Config

s3 = boto3.client(
    "s3",
    region_name=os.environ["AWS_REGION"],
    config=Config(signature_version="s3v4", s3={"addressing_style": "virtual"}),
)
BUCKET = os.environ["BUCKET_NAME"]
ALLOWED = {"image/jpeg": "jpg", "image/png": "png"}


def handler(event, context):
    """Return a short-lived pre-signed URL so the browser uploads straight to S3."""
    try:
        body = json.loads(event.get("body") or "{}")
        content_type = body.get("contentType", "")
        if content_type not in ALLOWED:
            return _resp(400, {"error": "Only JPEG and PNG images are allowed"})
        key = f"uploads/{uuid.uuid4()}.{ALLOWED[content_type]}"
        url = s3.generate_presigned_url(
            "put_object",
            Params={"Bucket": BUCKET, "Key": key, "ContentType": content_type},
            ExpiresIn=300,
        )
        return _resp(200, {"uploadUrl": url, "key": key})
    except Exception as exc:
        print("ERROR", exc)
        return _resp(500, {"error": "Internal error"})


def _resp(code, payload):
    return {"statusCode": code, "headers": {"Content-Type": "application/json"},
            "body": json.dumps(payload)}
