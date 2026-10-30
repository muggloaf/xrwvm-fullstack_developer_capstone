#!/bin/sh
# Run from the repository root in the preconfigured Skills Network lab CLI.
set -eu
: "${SN_ICR_NAMESPACE:?Run this in the Skills Network lab with its namespace set}"
: "${BACKEND_URL:?Set BACKEND_URL to your running Express service URL}"
cd server
docker build -t "us.icr.io/$SN_ICR_NAMESPACE/senti_analyzer" djangoapp/microservices
docker push "us.icr.io/$SN_ICR_NAMESPACE/senti_analyzer"
if ibmcloud ce application get --name sentianalyzer >/dev/null 2>&1; then
  ibmcloud ce application update --name sentianalyzer \
    --image "us.icr.io/$SN_ICR_NAMESPACE/senti_analyzer"
else
  ibmcloud ce application create --name sentianalyzer \
    --image "us.icr.io/$SN_ICR_NAMESPACE/senti_analyzer" \
    --registry-secret icr-secret --port 5000
fi
SENTIMENT_URL=$(ibmcloud ce application get --name sentianalyzer --output url)
docker build -t "us.icr.io/$SN_ICR_NAMESPACE/dealership:latest" .
docker push "us.icr.io/$SN_ICR_NAMESPACE/dealership:latest"
kubectl create deployment dealership \
  --image="us.icr.io/$SN_ICR_NAMESPACE/dealership:latest" \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl set env deployment/dealership \
  backend_url="$BACKEND_URL" sentiment_analyzer_url="$SENTIMENT_URL"
kubectl rollout status deployment/dealership --timeout=300s
kubectl port-forward deployment/dealership 8000:8000
