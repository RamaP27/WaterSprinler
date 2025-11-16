# Firebase & Cloud Run Deployment Guide

This guide will help you deploy your Water Sprinkler Prediction app and get a public URL.

## Quick Deployment (Recommended)

The easiest way to get a public URL is to deploy directly to **Google Cloud Run**. This will give you a public URL immediately.

### Step 1: Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Google Cloud SDK** installed:
   ```bash
   # macOS
   brew install google-cloud-sdk
   
   # Or download from: https://cloud.google.com/sdk/docs/install
   ```

3. **Login to Google Cloud**:
   ```bash
   gcloud auth login
   ```

### Step 2: Deploy Using the Script

Run the deployment script:

```bash
./deploy_firebase.sh
```

The script will:
- ✅ Ask for your Google Cloud Project ID
- ✅ Enable required APIs
- ✅ Build the Docker image
- ✅ Deploy to Cloud Run
- ✅ Give you a public URL immediately

**You'll get a URL like:** `https://water-sprinkler-api-xxxxx-uc.a.run.app`

### Step 3: Test Your Deployment

Once deployed, test your app:

```bash
# Get your service URL
gcloud run services describe water-sprinkler-api \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'

# Test health endpoint
curl https://YOUR-SERVICE-URL/api/health

# Open in browser
open https://YOUR-SERVICE-URL
```

---

## Manual Deployment Steps

If you prefer to deploy manually:

### 1. Set Your Project

```bash
# Set your Google Cloud project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
```

### 2. Build and Deploy

```bash
# Build the container
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/water-sprinkler-api

# Deploy to Cloud Run
gcloud run deploy water-sprinkler-api \
  --image gcr.io/YOUR_PROJECT_ID/water-sprinkler-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300 \
  --min-instances 0 \
  --max-instances 10
```

### 3. Get Your Public URL

```bash
gcloud run services describe water-sprinkler-api \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'
```

---

## Firebase Hosting Setup (Optional)

Firebase Hosting can be used to:
- Get a cleaner domain (e.g., `your-project.web.app`)
- Set up custom domain
- Use Firebase CDN

**Note:** Since your Flask app serves both UI and API, Firebase Hosting will proxy API requests to Cloud Run while serving the main app directly from Cloud Run.

### Option A: Use Cloud Run URL Directly (Simplest)

The Cloud Run URL is already public and works great! No additional setup needed.

### Option B: Firebase Hosting with Cloud Run Integration

1. **Install Firebase CLI**:
   ```bash
   npm install -g firebase-tools
   firebase login
   ```

2. **Update `.firebaserc`**:
   Replace `your-project-id` with your actual Firebase project ID:
   ```json
   {
     "projects": {
       "default": "your-actual-project-id"
     }
   }
   ```

3. **Initialize Firebase** (if not already done):
   ```bash
   firebase init hosting
   ```
   - Select your Firebase project
   - Public directory: `public` (we'll create this)
   - Configure as single-page app: No
   - Set up automatic builds: No

4. **Note:** Your current `firebase.json` is configured to proxy `/api/**` requests to Cloud Run. However, since your Flask app serves the entire UI, you'll need to either:
   - Keep using Cloud Run URL directly (recommended), OR
   - Extract the frontend to static files in a `public/` directory

---

## Important Notes

### Model Files

The deployment includes:
- ✅ `sprinkler_lstm_keras.h5` (trained model)
- ✅ `artifacts/` directory (preprocessing artifacts)

These are automatically included in the Docker image.

### Environment Variables

The app uses the `PORT` environment variable (defaults to 8080 for Cloud Run). No additional configuration needed.

### Memory and CPU

The deployment uses:
- **Memory:** 4GB (required for TensorFlow)
- **CPU:** 2 vCPUs
- **Timeout:** 300 seconds (5 minutes)

### Costs

- **Free Tier:** 2 million requests/month free
- **Pricing:** ~$0.40 per million requests after free tier
- **Estimated:** $10-50/month for moderate usage

---

## Troubleshooting

### Deployment Fails

1. **Check billing is enabled**:
   ```bash
   gcloud billing projects describe YOUR_PROJECT_ID
   ```

2. **Check quotas**:
   Visit: https://console.cloud.google.com/iam-admin/quotas

3. **View build logs**:
   ```bash
   gcloud builds list --limit=1
   ```

### Service Not Responding

1. **Check service logs**:
   ```bash
   gcloud run services logs read water-sprinkler-api \
     --region us-central1 \
     --limit 50
   ```

2. **Verify service is running**:
   ```bash
   gcloud run services describe water-sprinkler-api \
     --platform managed \
     --region us-central1
   ```

### Model Not Loading

- Ensure model files exist locally before deployment
- Check that `sprinkler_lstm_keras.h5` and `artifacts/` are not in `.gcloudignore`

### CORS Errors

The app already includes CORS headers. If you still see errors, check:
- Cloud Run CORS settings
- Browser console for specific errors

---

## Updating Your Deployment

To update after code changes:

```bash
# Simply run the deployment script again
./deploy_firebase.sh
```

Or manually:
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/water-sprinkler-api
gcloud run deploy water-sprinkler-api \
  --image gcr.io/YOUR_PROJECT_ID/water-sprinkler-api \
  --platform managed \
  --region us-central1
```

---

## Custom Domain (Optional)

### Cloud Run Custom Domain

1. Map a domain in Cloud Run:
   ```bash
   gcloud run domain-mappings create \
     --service water-sprinkler-api \
     --domain your-domain.com \
     --region us-central1
   ```

2. Follow DNS configuration instructions provided

### Firebase Custom Domain

1. Go to Firebase Console > Hosting
2. Click "Add custom domain"
3. Follow the setup wizard

---

## Security Recommendations

1. **Enable Authentication** (for production):
   ```bash
   # Remove --allow-unauthenticated and use IAM
   gcloud run services update water-sprinkler-api \
     --no-allow-unauthenticated \
     --region us-central1
   ```

2. **Set up API keys** for rate limiting
3. **Use Cloud Armor** for DDoS protection
4. **Monitor costs** in Cloud Console

---

## Quick Reference

```bash
# Deploy
./deploy_firebase.sh

# View logs
gcloud run services logs read water-sprinkler-api --region us-central1

# Get URL
gcloud run services describe water-sprinkler-api \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'

# Delete service (if needed)
gcloud run services delete water-sprinkler-api \
  --platform managed \
  --region us-central1
```

---

## Need Help?

- Cloud Run Docs: https://cloud.google.com/run/docs
- Firebase Docs: https://firebase.google.com/docs/hosting
- Project Issues: Check logs and Cloud Console

