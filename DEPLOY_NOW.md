# 🚀 Quick Deployment Guide

## Get Your Public URL in 3 Steps

### Step 1: Make sure you're logged in

```bash
gcloud auth login
```

### Step 2: Run the deployment script

```bash
./deploy_firebase.sh
```

The script will:
- Ask for your Google Cloud Project ID
- Enable required APIs
- Build and deploy your app
- **Give you a public URL immediately!**

### Step 3: Access your app

You'll get a URL like:
```
https://water-sprinkler-api-xxxxx-uc.a.run.app
```

**Open it in your browser!** 🎉

---

## What You'll Get

✅ **Public URL** - Share with anyone  
✅ **HTTPS** - Secure by default  
✅ **Auto-scaling** - Handles traffic automatically  
✅ **Global CDN** - Fast worldwide  

---

## Prerequisites

- Google Cloud account with billing enabled
- Google Cloud SDK installed (`gcloud` command)
- Your trained model files (`sprinkler_lstm_keras.h5` and `artifacts/`)

---

## Need Help?

See [FIREBASE_DEPLOYMENT.md](FIREBASE_DEPLOYMENT.md) for detailed instructions.

---

## Quick Test

After deployment:

```bash
# Get your URL
gcloud run services describe water-sprinkler-api \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'

# Test health
curl https://YOUR-URL/api/health
```

