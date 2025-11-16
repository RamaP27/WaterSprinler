#!/bin/bash

# Water Sprinkler Deployment Script
# This script helps deploy the application to Google Cloud Run

set -e

echo "🚀 Water Sprinkler Deployment Script"
echo "======================================"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: Google Cloud SDK is not installed."
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Get project ID
read -p "Enter your Google Cloud Project ID: " PROJECT_ID
if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: Project ID is required"
    exit 1
fi

# Set project
gcloud config set project $PROJECT_ID

# Get region
read -p "Enter deployment region (default: us-central1): " REGION
REGION=${REGION:-us-central1}

# Service name
SERVICE_NAME="water-sprinkler-api"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo ""
echo "📦 Building Docker image..."
gcloud builds submit --tag $IMAGE_NAME

echo ""
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300 \
  --min-instances 0 \
  --max-instances 10

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

echo ""
echo "✅ Deployment complete!"
echo "Service URL: $SERVICE_URL"
echo ""
echo "📝 Next steps:"
echo "1. Update firebase.json with the service URL if using Firebase Hosting"
echo "2. Test the API: curl $SERVICE_URL/api/health"
echo "3. Open the UI: $SERVICE_URL"

