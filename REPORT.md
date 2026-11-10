# SmartGallery: A Serverless Image Upload and AI Labeling System on AWS

**Course:** Cloud Computing  **Group:** [Group No.]
**Members:** [Name 1 - Roll No.], [Name 2 - Roll No.], [Name 3 - Roll No.]
**Submission date:** [Date]

---

## 1. Abstract
SmartGallery is a fully serverless web application deployed on Amazon Web Services (AWS). Users upload images through a browser; the cloud automatically analyses each image with Amazon Rekognition, stores the detected labels in DynamoDB and shows them in a gallery. The system scales automatically, requires no server management, and costs nearly nothing when idle.

## 2. Problem Statement
Organisations and individuals accumulate large numbers of photos that are hard to search because they carry no descriptive metadata. Manually tagging images is slow and inconsistent. Traditional solutions require running and maintaining servers and machine-learning infrastructure, which is expensive and needs specialised skills. A cloud-native solution is needed that stores images durably, tags them automatically, scales with demand, and charges only for actual usage.

## 3. Objectives
1. Design and deploy a cloud-native application on a public cloud (AWS).
2. Use multiple services: storage, compute, database, API management, AI/ML, monitoring and security.
3. Achieve automatic image tagging without manual work, using an event-driven design.
4. Ensure security through private storage, pre-signed URLs and least-privilege IAM roles.
5. Define all infrastructure as code so the deployment is repeatable.
6. Evaluate performance, scalability and cost.

## 4. Scope
In scope: JPEG/PNG upload, automatic labeling, gallery view. Out of scope (future work): user authentication, search by label, video analysis.

## 5. System Architecture

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
    CloudWatch collects logs and metrics from all Lambdas; IAM governs every permission.
```
*(Insert the draw.io / AWS architecture diagram screenshot here.)*

### Data flow
1. The browser asks the API for an upload URL, declaring the file type.
2. The Lambda validates the type and returns a 5-minute pre-signed S3 URL.
3. The browser uploads directly to S3, so large files never pass through Lambda.
4. S3 emits an event that triggers the processor Lambda.
5. The processor calls Rekognition `DetectLabels` and writes labels to DynamoDB.
6. The gallery calls the list API, which returns labels and temporary image URLs.

## 6. Cloud Services Used

| Service | Category | Role in the project | Why chosen |
|---|---|---|---|
| Amazon S3 (images bucket) | Storage | Stores uploaded images; encrypted (SSE-S3), public access blocked, CORS enabled, event notifications | 11-nines durability, cheap, event source |
| Amazon S3 (website bucket) | Storage / hosting | Hosts static frontend | No web server needed |
| AWS Lambda (3 functions) | Compute (FaaS) | Upload URL generation, image processing, listing | Pay per execution, auto-scaling |
| Amazon API Gateway (HTTP API) | Networking / API | Public REST endpoints with CORS | Managed, low cost |
| Amazon DynamoDB | NoSQL database | Stores labels and metadata (on-demand mode) | Serverless, single-digit-ms latency |
| Amazon Rekognition | AI/ML | Detects objects and scenes | Pre-trained model, no ML expertise needed |
| AWS IAM | Security | Least-privilege role per function | Principle of least privilege |
| Amazon CloudWatch | Monitoring | Logs and metrics | Built-in observability |
| AWS CloudFormation / SAM | IaC | Provisions whole stack from `template.yaml` | Repeatable, versioned |

### Cloud features demonstrated
Elasticity and auto-scaling, pay-as-you-go pricing, event-driven architecture, serverless computing, managed AI service, encryption at rest, infrastructure as code, high availability across multiple Availability Zones (managed by AWS).

## 7. Implementation

### 7.1 Environment setup
AWS account, AWS CLI, SAM CLI, Python 3.12. Region: ap-south-1 (Mumbai).

### 7.2 Infrastructure as code
`template.yaml` declares the buckets, table, HTTP API, three functions with their IAM policies, and the S3 trigger. Deploy with `./deploy.sh`, which runs `sam build`, `sam deploy` and publishes the frontend with the generated API URL.

### 7.3 Backend functions
- **UploadFunction** validates MIME type (JPEG/PNG only) and returns a pre-signed PUT URL for a random UUID key under `uploads/`.
- **ProcessorFunction** receives the S3 event, calls `detect_labels` (max 8 labels, min confidence 75%), and stores `imageId`, `labels`, `sizeBytes`, `uploadedAt` in DynamoDB.
- **ListFunction** scans the table, sorts newest-first, and attaches 15-minute pre-signed GET URLs.

### 7.4 Frontend
A single HTML/JavaScript page using `fetch` to call the API and upload directly to S3.

### 7.5 Security measures
- Images bucket is fully private; access only through short-lived pre-signed URLs.
- Server-side encryption enabled.
- Each Lambda role limited to the exact actions and resources it needs.
- Input validation on file type.

### 7.6 Team contributions
| Member | Contribution |
|---|---|
| [Name 1] | Architecture design, IaC template, deployment scripts |
| [Name 2] | Lambda functions, Rekognition and DynamoDB integration, testing |
| [Name 3] | Frontend, monitoring, cost analysis, documentation and video |

*(Adjust to reflect the real division of work. Every member must contribute.)*

## 8. Results and Evaluation

### 8.1 Functional results
Insert screenshots: (a) CloudFormation stack CREATE_COMPLETE, (b) S3 buckets, (c) Lambda functions, (d) DynamoDB items, (e) web UI with labelled images, (f) CloudWatch logs.

### 8.2 Test cases
| # | Test | Expected | Actual |
|---|---|---|---|
| 1 | Upload a JPEG of a dog | Labels such as Dog, Animal, Pet appear | [fill in] |
| 2 | Upload a PNG | Accepted and labelled | [fill in] |
| 3 | Upload a PDF | Rejected with error message | [fill in] |
| 4 | Upload 10 images at once | All processed without errors | [fill in] |
| 5 | Open image URL after expiry | Access denied | [fill in] |

### 8.3 Performance
Measure and record: upload-to-label latency (typically 1-3 seconds), Lambda duration and cold-start time (CloudWatch), API response time. Fill in your measured values.

### 8.4 Cost analysis (approximate, 1,000 images/month)
| Service | Estimate |
|---|---|
| Lambda, API Gateway, DynamoDB, S3 | Within Free Tier / under $0.10 |
| Rekognition | ~$1.00 per 1,000 images beyond free tier (first 1,000 images/month free for 12 months) |
| **Total** | **about $0-$1 per month** |
A comparable always-on EC2 solution would cost far more and need patching and scaling work. Verify current prices at aws.amazon.com/pricing.

### 8.5 Challenges and solutions
- *Circular dependency between S3 bucket and Lambda in CloudFormation:* solved by building the bucket name deterministically and referencing it by string in IAM policies.
- *CORS errors on direct upload:* added CORS rules to the bucket and the API.
- *DynamoDB rejects Python floats:* converted confidence values to `Decimal`.

## 9. Conclusion
SmartGallery shows that a useful AI-enabled application can be built and deployed in a public cloud without managing a single server. Using S3, Lambda, API Gateway, DynamoDB and Rekognition we achieved automatic, scalable, secure and low-cost image tagging, deployed repeatably through infrastructure as code. The project gave the team practical experience in event-driven design, IAM security, and cost-aware cloud architecture.

## 10. Future Work
User authentication with Amazon Cognito; search by label; CloudFront CDN with HTTPS; thumbnails; SNS notifications; CI/CD with CodePipeline; moderation using Rekognition content moderation.

## 11. References
1. AWS Lambda Developer Guide - docs.aws.amazon.com/lambda
2. Amazon S3 User Guide - docs.aws.amazon.com/s3
3. Amazon Rekognition Developer Guide - docs.aws.amazon.com/rekognition
4. Amazon DynamoDB Developer Guide - docs.aws.amazon.com/dynamodb
5. AWS SAM Developer Guide - docs.aws.amazon.com/serverless-application-model

## Appendix: How to run
See `README.md` in the source code folder.
