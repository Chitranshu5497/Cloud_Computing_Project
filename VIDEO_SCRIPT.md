# 10-Minute Video Script (3 presenters)

Tip: record with Zoom/Meet/OBS, everyone on camera at least briefly. Keep to ~10:00.

| Time | Presenter | Content |
|---|---|---|
| 0:00-1:00 | Member 1 | Introduce group, project name, problem statement (photos are hard to search, manual tagging is slow). |
| 1:00-2:00 | Member 1 | Objectives and why serverless on AWS. |
| 2:00-4:00 | Member 1 | Architecture diagram walkthrough: follow one image through steps 1-6. Name each service and its role. |
| 4:00-6:30 | Member 2 | Show code: `template.yaml` (resources, IAM, S3 trigger), then the three Lambda functions. Explain pre-signed URLs and Rekognition call. |
| 6:30-8:30 | Member 3 | **Live demo** in AWS Console: CloudFormation stack, S3 bucket, Lambda, DynamoDB. Then open website, upload an image, show labels. Show CloudWatch logs. |
| 8:30-9:15 | Member 3 | Results: test cases, latency, cost estimate. |
| 9:15-10:00 | Member 2 | Challenges, future work, conclusion, thanks. |

## Pre-recording checklist
- [ ] Stack deployed and tested the day before
- [ ] Sample images ready (dog, car, food, landscape)
- [ ] Console tabs pre-opened: CloudFormation, S3, Lambda, DynamoDB, CloudWatch
- [ ] Hide account ID / access keys in screen recording
- [ ] Rehearse once with a timer
- [ ] Run `./cleanup.sh` AFTER final submission, not before

## Sample narration (opening)
"Hello, we are Group [X]. Our project, SmartGallery, is a serverless cloud application on AWS that automatically recognises what is in a photo. Imagine thousands of photos with no tags. Our system uses S3, Lambda, API Gateway, DynamoDB and Amazon Rekognition to label every upload within seconds, without any servers to manage..."
