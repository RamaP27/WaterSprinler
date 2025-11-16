#!/bin/bash

# Firebase Deployment Script for Water Sprinkler App
# This script deploys the app to Cloud Run and optionally configures Firebase Hosting

set -e

echo "🚀 Water Sprinkler Firebase Deployment"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Error: Google Cloud SDK is not installed.${NC}"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if Firebase CLI is installed (optional)
FIREBASE_AVAILABLE=false
if command -v firebase &> /dev/null; then
    FIREBASE_AVAILABLE=true
fi

# Get project ID
if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
    read -p "Enter your Google Cloud Project ID: " PROJECT_ID
else
    PROJECT_ID=$GOOGLE_CLOUD_PROJECT
fi

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ Error: Project ID is required${NC}"
    exit 1
fi

# Set project
echo -e "${BLUE}📋 Setting Google Cloud project to: $PROJECT_ID${NC}"
gcloud config set project $PROJECT_ID

# Check if user wants to enable APIs
read -p "Do you want to enable required Google Cloud APIs? (y/n) [y]: " ENABLE_APIS
ENABLE_APIS=${ENABLE_APIS:-y}

if [ "$ENABLE_APIS" = "y" ]; then
    echo -e "${BLUE}🔧 Enabling required APIs...${NC}"
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable run.googleapis.com
    gcloud services enable compute.googleapis.com
    echo -e "${GREEN}✅ APIs enabled${NC}"
fi

# Get region
read -p "Enter deployment region (default: us-central1): " REGION
REGION=${REGION:-us-central1}

# Service name
SERVICE_NAME="water-sprinkler-api"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo ""
echo -e "${BLUE}📦 Step 1: Building Docker image...${NC}"
echo "This may take several minutes..."
gcloud builds submit --tag $IMAGE_NAME

echo ""
echo -e "${BLUE}🚀 Step 2: Deploying to Cloud Run...${NC}"
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
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --format 'value(status.url)')

echo ""
echo -e "${GREEN}✅ Cloud Run deployment complete!${NC}"
echo -e "${GREEN}🌐 Public URL: $SERVICE_URL${NC}"
echo ""

# Test the deployment
echo -e "${BLUE}🧪 Testing deployment...${NC}"
sleep 3
if curl -s -f "$SERVICE_URL/api/health" > /dev/null; then
    echo -e "${GREEN}✅ Service is responding!${NC}"
else
    echo -e "${YELLOW}⚠️  Service may still be starting up. Please wait a moment.${NC}"
fi

# Firebase Hosting setup
if [ "$FIREBASE_AVAILABLE" = true ]; then
    echo ""
    read -p "Do you want to set up Firebase Hosting with a custom domain? (y/n) [n]: " SETUP_FIREBASE
    SETUP_FIREBASE=${SETUP_FIREBASE:-n}
    
    if [ "$SETUP_FIREBASE" = "y" ]; then
        # Update .firebaserc if needed
        if grep -q "your-project-id" .firebaserc; then
            echo -e "${BLUE}📝 Updating .firebaserc with project ID...${NC}"
            # Check if they want to use the same project or different Firebase project
            read -p "Use the same project ID for Firebase? (y/n) [y]: " SAME_PROJECT
            SAME_PROJECT=${SAME_PROJECT:-y}
            
            if [ "$SAME_PROJECT" = "y" ]; then
                sed -i.bak "s/your-project-id/$PROJECT_ID/g" .firebaserc
                FIREBASE_PROJECT=$PROJECT_ID
            else
                read -p "Enter Firebase Project ID: " FIREBASE_PROJECT
                sed -i.bak "s/your-project-id/$FIREBASE_PROJECT/g" .firebaserc
            fi
        fi
        
        # Update firebase.json with service name
        echo -e "${BLUE}📝 Updating firebase.json...${NC}"
        # The firebase.json already has the correct serviceId, so we just need to verify
        echo "Firebase Hosting is configured to proxy API requests to Cloud Run."
        echo "For full Firebase Hosting setup, you'll need to:"
        echo "  1. Create a 'public' directory with static files (optional)"
        echo "  2. Run: firebase deploy --only hosting"
        echo ""
        echo "Currently, your app is fully accessible at the Cloud Run URL above."
    fi
else
    echo ""
    echo -e "${YELLOW}ℹ️  Firebase CLI not found. Install it with: npm install -g firebase-tools${NC}"
    echo "You can still use the Cloud Run URL directly: $SERVICE_URL"
fi

echo ""
echo "=" * 60
echo -e "${GREEN}🎉 Deployment Summary${NC}"
echo "=" * 60
echo -e "${GREEN}✅ Service deployed successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Details:${NC}"
echo "  Project ID: $PROJECT_ID"
echo "  Service Name: $SERVICE_NAME"
echo "  Region: $REGION"
echo ""
echo -e "${GREEN}🌐 Your public URLs:${NC}"
echo "  Direct URL: $SERVICE_URL"
echo "  Health Check: $SERVICE_URL/api/health"
echo "  Web UI: $SERVICE_URL"
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo "  1. Test the API: curl $SERVICE_URL/api/health"
echo "  2. Open the UI in browser: $SERVICE_URL"
echo "  3. (Optional) Set up custom domain in Firebase Hosting"
echo ""
echo -e "${YELLOW}💡 Tip: Share the URL above to access your application!${NC}"
echo ""

