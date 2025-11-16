# Deployment Guide

## Quick Start

### 1. Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Open http://localhost:5000 in your browser
```

### 2. Deploy to Google Cloud Run (Recommended)

#### Prerequisites
- Google Cloud account
- Google Cloud SDK installed
- Docker (optional, for local testing)

#### Steps

1. **Set up Google Cloud Project:**
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

2. **Enable required APIs:**
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
```

3. **Deploy using the script:**
```bash
./deploy.sh
```

Or manually:
```bash
# Build and push container
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/water-sprinkler-api

# Deploy to Cloud Run
gcloud run deploy water-sprinkler-api \
  --image gcr.io/YOUR_PROJECT_ID/water-sprinkler-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300
```

4. **Get your service URL:**
```bash
gcloud run services describe water-sprinkler-api \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'
```

### 3. Firebase Hosting Setup (Optional)

If you want to use Firebase Hosting for the frontend:

1. **Install Firebase CLI:**
```bash
npm install -g firebase-tools
firebase login
```

2. **Initialize Firebase:**
```bash
firebase init hosting
# Select your project
# Set public directory to "public" (or create a build process)
```

3. **Update firebase.json:**
Update the `run.serviceId` in `firebase.json` to match your Cloud Run service name.

4. **Deploy:**
```bash
firebase deploy --only hosting
```

### 4. Environment Variables (Optional)

For Cloud Run, you can set environment variables:

```bash
gcloud run services update water-sprinkler-api \
  --update-env-vars KEY=VALUE \
  --region us-central1
```

## Configuration

### Update .firebaserc

Edit `.firebaserc` and replace `your-project-id` with your actual Firebase project ID.

### Update firebase.json

If using Cloud Run, update the `serviceId` in `firebase.json` to match your deployed service name.

## Troubleshooting

### Model not loading
- Ensure `sprinkler_lstm_keras.h5` and `artifacts/` folder exist
- Check file permissions
- Verify model was trained and saved correctly

### Deployment fails
- Check Google Cloud quotas
- Ensure billing is enabled
- Verify APIs are enabled

### CORS errors
- The Flask app includes CORS headers
- If issues persist, check Cloud Run CORS settings

### Memory issues
- Increase Cloud Run memory allocation (currently 4Gi)
- Consider using Cloud Run with more resources

## Cost Estimation

- Cloud Run: Pay per request, ~$0.40 per million requests
- Memory: 4GB allocated
- CPU: 2 vCPUs
- Estimated cost: ~$10-50/month for moderate usage

## Security Notes

- The API is currently unauthenticated (`--allow-unauthenticated`)
- For production, consider adding authentication
- Use Firebase Authentication or Cloud IAM

## Monitoring

View logs:
```bash
gcloud run services logs read water-sprinkler-api --region us-central1
```

View metrics in Google Cloud Console:
- Navigate to Cloud Run > water-sprinkler-api > Metrics

