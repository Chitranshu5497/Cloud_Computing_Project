# SmartGallery - Serverless Image Labeling on AWS

Upload an image in the browser; AWS automatically detects objects in it and displays labels.

## Architecture
Browser -> API Gateway (HTTP API) -> Lambda (upload-url) -> pre-signed URL -> Browser PUTs image to S3
S3 ObjectCreated event -> Lambda (processor) -> Amazon Rekognition -> DynamoDB
Browser -> API Gateway -> Lambda (list) -> DynamoDB + S3 pre-signed GET URLs
Static website hosted on S3. Logs/metrics in CloudWatch. Permissions via IAM least-privilege roles.
Infrastructure is defined as code in `template.yaml` (AWS SAM / CloudFormation).

## Prerequisites
1. AWS account (Free Tier is sufficient)
2. AWS CLI v2, configured: `aws configure` (use an IAM user with admin or equivalent rights)
3. AWS SAM CLI: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html
4. Python 3.12 (for `sam build`) or use `sam build --use-container` with Docker

## Deploy
```bash
./deploy.sh ap-south-1        # any region that supports Rekognition
```
The script prints the website URL at the end.

## Use
Open the URL -> choose a JPEG/PNG -> Upload -> wait ~5 seconds -> labels appear.

## Monitor / debug
```bash
sam logs --stack-name smartgallery --name ProcessorFunction --tail --region ap-south-1
```

## Delete everything (avoid charges)
```bash
./cleanup.sh ap-south-1
```

## Folder structure
- template.yaml - all AWS resources (IaC)
- src/upload_api, src/processor, src/list_api - Lambda functions (Python)
- frontend/index.html - web UI
- deploy.sh / cleanup.sh - automation
- docs/ - report and video script
