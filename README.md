# ☁️ SmartGallery — Serverless AI Image Labeling on AWS

> **Cloud Computing Course Project** · Fully serverless · Event-driven · Infrastructure as Code

**🔗 Live Demo:** [http://smartgallery-frontendbucket-lvlvy2a2cjii.s3-website.ap-south-1.amazonaws.com/](http://smartgallery-frontendbucket-lvlvy2a2cjii.s3-website.ap-south-1.amazonaws.com/)

**Region:** `ap-south-1` (Asia Pacific – Mumbai)

---

## 📌 Overview

SmartGallery is a serverless web application built entirely on **Amazon Web Services (AWS)**. A user uploads a JPEG/PNG image from the browser; AWS automatically analyses it with **Amazon Rekognition**, stores the detected labels in **Amazon DynamoDB**, and displays them in a gallery, with no servers to provision, patch or scale.

The whole stack is defined as code in a single **AWS SAM / CloudFormation** template, so it can be deployed (or destroyed) with one command.

## 🎯 Problem Statement

Photos pile up with no descriptive metadata, which makes them hard to search. Manual tagging is slow and inconsistent, and traditional solutions need always-on servers and ML infrastructure. SmartGallery provides a cloud-native alternative that stores images durably, tags them automatically, scales on demand, and charges only for actual usage.

## 🏗️ Architecture

```
 Browser ──(1) POST /upload-url──▶ API Gateway ──▶ Lambda: UploadFunction
    │                                                 │ returns pre-signed PUT URL
    │◀────────────────────────────────────────────────┘
    ├──(2) PUT image ────────────────▶ S3 (private images bucket)
    │                                   │ (3) ObjectCreated event
    │                                   ▼
    │                            Lambda: ProcessorFunction ──▶ Amazon Rekognition
    │                                   │ (4) save labels
    │                                   ▼
    │                               DynamoDB
    ├──(5) GET /images ──▶ API Gateway ──▶ Lambda: ListFunction ──▶ DynamoDB + S3 pre-signed GET URLs
    └── static site served from S3 website hosting

 CloudWatch collects logs & metrics from all Lambdas · IAM governs every permission
```

### Data flow

1. The browser calls `POST /upload-url`, declaring the file's content type.
2. **UploadFunction** validates the type and returns a **5-minute pre-signed S3 PUT URL**.
3. The browser uploads the image **directly to S3**, so large files never pass through Lambda.
4. S3 emits an `ObjectCreated` event that triggers **ProcessorFunction**.
5. ProcessorFunction calls Rekognition `DetectLabels` and writes the labels to DynamoDB.
6. The gallery calls `GET /images`; **ListFunction** returns the labels plus **15-minute pre-signed GET URLs**.

## ☁️ AWS Services Used

| AWS Service | Category | Role in this project |
|---|---|---|
| **Amazon S3** (images bucket) | Storage | Private image store; SSE-S3 encryption, public access blocked, CORS, event notifications |
| **Amazon S3** (frontend bucket) | Storage / Hosting | Static website hosting for the UI |
| **AWS Lambda** (×3) | Compute (FaaS) | Upload-URL generation, image processing, gallery listing |
| **Amazon API Gateway** (HTTP API) | Networking / API | Public endpoints `/upload-url` and `/images` with CORS |
| **Amazon DynamoDB** | NoSQL database | Stores image labels and metadata (on-demand billing) |
| **Amazon Rekognition** | AI / ML | Pre-trained object and scene detection |
| **AWS IAM** | Security | Least-privilege role per Lambda function |
| **Amazon CloudWatch** | Monitoring | Logs and metrics for every function |
| **AWS CloudFormation / SAM** | Infrastructure as Code | Provisions the entire stack from `template.yaml` |

### Cloud concepts demonstrated

Serverless computing · Event-driven architecture · Elastic auto-scaling · Pay-as-you-go pricing · Managed AI services · Encryption at rest · Least-privilege security · Infrastructure as Code

## 📂 Project Structure

```
Cloud_Computing_Project/
├── REPORT.md                  # Full project report
├── VIDEO_SCRIPT.md            # Presentation / demo video script
├── Project_Report.pdf         # Final report (PDF)
└── smartgallery/
    ├── template.yaml          # All AWS resources (SAM / CloudFormation)
    ├── deploy.sh              # Build + deploy + publish frontend
    ├── cleanup.sh             # Tear down everything to avoid charges
    ├── frontend/
    │   └── index.html         # Web UI (contains __API_URL__ placeholder)
    └── src/
        ├── upload_api/app.py  # UploadFunction: pre-signed PUT URL
        ├── processor/app.py   # ProcessorFunction: Rekognition → DynamoDB
        └── list_api/app.py    # ListFunction: gallery data + pre-signed GET URLs
```

## ⚙️ Lambda Functions

| Function | Trigger | What it does |
|---|---|---|
| `UploadFunction` | `POST /upload-url` | Accepts only `image/jpeg` and `image/png`; returns a pre-signed PUT URL for `uploads/<uuid>.<ext>` (valid 5 min) |
| `ProcessorFunction` | S3 `ObjectCreated` on `uploads/` | Calls `rekognition.detect_labels` (max 8 labels, min 75% confidence); saves `imageId`, `labels`, `sizeBytes`, `uploadedAt` to DynamoDB |
| `ListFunction` | `GET /images` | Scans DynamoDB, sorts newest-first, attaches 15-minute pre-signed GET URLs |

Runtime: **Python 3.12** · Memory: 256 MB · Timeout: 30 s (processor: 60 s)

## 🔐 Security

- **Images bucket is fully private**: all four S3 Block Public Access settings are on; images are only reachable via short-lived pre-signed URLs.
- **Server-side encryption** (AES-256 / SSE-S3) is enabled on the images bucket.
- **Least-privilege IAM**: each Lambda role is limited to the exact actions and resources it needs (e.g. UploadFunction can only `s3:PutObject` on `uploads/*`).
- **Input validation**: only JPEG and PNG content types are accepted.

## 🚀 Deployment

### Prerequisites

1. An AWS account (Free Tier is sufficient)
2. [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html), configured with `aws configure`
3. [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
4. Python 3.12 (or Docker, with `sam build --use-container`)

### Deploy

```bash
cd smartgallery
chmod +x deploy.sh cleanup.sh
./deploy.sh ap-south-1
```

`deploy.sh` will:

1. Run `sam build`
2. Run `sam deploy` to create the CloudFormation stack (`smartgallery`)
3. Read the `ApiUrl` output and inject it into `frontend/index.html`
4. Upload the page to the S3 frontend bucket
5. Print the website URL

### CloudFormation outputs

| Output | Description |
|---|---|
| `ApiUrl` | HTTP API endpoint base URL |
| `WebsiteUrl` | S3 static website URL |
| `FrontendBucketName` | Name of the frontend bucket |
| `ImageBucketName` | Name of the private images bucket |

## 🧪 Usage

1. Open the [live demo](http://smartgallery-frontendbucket-lvlvy2a2cjii.s3-website.ap-south-1.amazonaws.com/)
2. Choose a **JPEG or PNG** image
3. Click **Upload**
4. Wait a few seconds; the image appears with its AI-detected labels (e.g. *Dog, Animal, Pet*)

## 📊 Monitoring & Debugging

```bash
sam logs --stack-name smartgallery --name ProcessorFunction --tail --region ap-south-1
```

Logs and metrics for all functions are also available in **Amazon CloudWatch**.

## 💰 Cost Estimate (~1,000 images / month)

| Service | Approx. cost |
|---|---|
| Lambda, API Gateway, DynamoDB, S3 | Free Tier / under $0.10 |
| Rekognition | ~$1.00 per 1,000 images beyond Free Tier (first 1,000 images/month free for 12 months) |
| **Total** | **≈ $0 – $1 per month** |

*Estimates only; check [aws.amazon.com/pricing](https://aws.amazon.com/pricing) for current rates.*

## 🧹 Cleanup (avoid charges)

```bash
./cleanup.sh ap-south-1
```

Empties both S3 buckets and deletes the CloudFormation stack.

## 🧩 Challenges & Solutions

| Challenge | Solution |
|---|---|
| Circular dependency between the S3 bucket and Lambda in CloudFormation | Built the bucket name deterministically (`${StackName}-images-${AccountId}`) and referenced it by string in IAM policies |
| CORS errors on direct browser upload | Added CORS rules to both the S3 bucket and the HTTP API |
| DynamoDB rejects Python floats | Converted Rekognition confidence values to `Decimal` |

## 🔮 Future Work

- User authentication with **Amazon Cognito**
- Search by label
- **CloudFront** CDN with HTTPS
- Thumbnail generation
- **SNS** notifications
- CI/CD with **CodePipeline**
- Content moderation with Rekognition

## 👥 Team

| Name | Roll No. | Contribution |
|---|---|---|
| [Name 1] | [Roll No.] | Architecture design, IaC template, deployment scripts |
| [Name 2] | [Roll No.] | Lambda functions, Rekognition & DynamoDB integration, testing |
| [Name 3] | [Roll No.] | Frontend, monitoring, cost analysis, documentation & video |

**Course:** Cloud Computing  ·  **Group:** [Group No.]  ·  **Submission Date:** [Date]

## 📚 References

1. [AWS Lambda Developer Guide](https://docs.aws.amazon.com/lambda)
2. [Amazon S3 User Guide](https://docs.aws.amazon.com/s3)
3. [Amazon Rekognition Developer Guide](https://docs.aws.amazon.com/rekognition)
4. [Amazon DynamoDB Developer Guide](https://docs.aws.amazon.com/dynamodb)
5. [AWS SAM Developer Guide](https://docs.aws.amazon.com/serverless-application-model)
