#!/usr/bin/env bash
# Usage: ./deploy.sh [region]     (default: ap-south-1)
set -euo pipefail
REGION="${1:-ap-south-1}"
STACK="smartgallery"

sam build
sam deploy --stack-name "$STACK" --region "$REGION" --resolve-s3 \
  --capabilities CAPABILITY_IAM --no-confirm-changeset --no-fail-on-empty-changeset

out() { aws cloudformation describe-stacks --stack-name "$STACK" --region "$REGION" \
  --query "Stacks[0].Outputs[?OutputKey=='$1'].OutputValue" --output text; }

API_URL=$(out ApiUrl); SITE_BUCKET=$(out FrontendBucketName); SITE_URL=$(out WebsiteUrl)
sed "s|__API_URL__|$API_URL|" frontend/index.html > /tmp/index.html
aws s3 cp /tmp/index.html "s3://$SITE_BUCKET/index.html" --content-type text/html --region "$REGION"
echo "Done. Open: $SITE_URL"
