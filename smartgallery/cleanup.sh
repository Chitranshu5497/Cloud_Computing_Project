#!/usr/bin/env bash
# Usage: ./cleanup.sh [region]  - deletes everything to avoid charges
set -euo pipefail
REGION="${1:-ap-south-1}"; STACK="smartgallery"
ACC=$(aws sts get-caller-identity --query Account --output text)
aws s3 rm "s3://$STACK-images-$ACC" --recursive --region "$REGION" || true
SITE=$(aws cloudformation describe-stacks --stack-name $STACK --region "$REGION" \
  --query "Stacks[0].Outputs[?OutputKey=='FrontendBucketName'].OutputValue" --output text)
aws s3 rm "s3://$SITE" --recursive --region "$REGION" || true
aws cloudformation delete-stack --stack-name $STACK --region "$REGION"
echo "Stack deletion started."
