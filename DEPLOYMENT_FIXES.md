# Deployment Fixes Applied

## Issues Fixed

### 1. Model Not Loading After Deployment ✅

**Problem:** Model files (`sprinkler_lstm_keras.h5` and `artifacts/`) were not being included in the Docker image.

**Root Cause:** The `.dockerignore` file was excluding:
- `artifacts/` directory
- `*.h5` files

**Fix Applied:**
- Commented out the exclusions in `.dockerignore`
- Added verification step in Dockerfile to check for model files
- Updated `.gcloudignore` documentation to clarify model files must be included

**Files Changed:**
- `.dockerignore` - Removed exclusions for model files
- `Dockerfile` - Added verification step

### 2. Training Endpoint Timeout Error ✅

**Problem:** Training requests were timing out with "Service Unavailable" error, and JavaScript was trying to parse HTML error pages as JSON.

**Root Causes:**
1. Gunicorn timeout was only 120 seconds (2 minutes)
2. Cloud Run timeout is 300 seconds (5 minutes)
3. Training can take longer than these timeouts
4. JavaScript error handling didn't handle non-JSON responses

**Fixes Applied:**
1. **Increased Gunicorn timeout** from 120s to 600s (10 minutes)
   - This prevents premature worker termination
   - Note: Cloud Run still has a 300s limit, but this helps with edge cases

2. **Improved JavaScript error handling:**
   - Check content-type before parsing JSON
   - Handle non-JSON responses gracefully
   - Show user-friendly error messages for timeouts
   - Specific message for 503 Service Unavailable errors

**Files Changed:**
- `Dockerfile` - Increased gunicorn timeout to 600s
- `static/script.js` - Improved error handling for training endpoint

## Important Notes

### Cloud Run Timeout Limitation

Cloud Run has a **maximum timeout of 300 seconds (5 minutes)** for HTTP requests. If your training takes longer than this:

1. **Reduce training parameters:**
   - Use fewer epochs (e.g., 20-30 instead of 50)
   - Use smaller batch sizes
   - Use a smaller dataset

2. **Alternative Solutions (for future):**
   - Implement async training with background jobs
   - Use Cloud Tasks or Cloud Functions for long-running tasks
   - Split training into smaller chunks

### Model Files Must Be Present

Before deploying, ensure:
- ✅ `sprinkler_lstm_keras.h5` exists in project root
- ✅ `artifacts/` directory exists with:
  - `scaler.joblib`
  - `label_encoder.joblib`
  - `feature_columns.joblib`

If these don't exist, train the model locally first:
```bash
python train_model.py training_data/TARP.csv
```

## Next Steps

1. **Rebuild and redeploy:**
   ```bash
   ./deploy_firebase.sh
   ```

2. **Verify model is loaded:**
   - Check the health endpoint: `curl https://YOUR-URL/api/health`
   - Should show `"model_loaded": true`

3. **Test training:**
   - Try with fewer epochs (e.g., 10-20) to stay under 5-minute limit
   - Monitor the error messages - they should now be more helpful

## Testing Checklist

After redeployment:

- [ ] Model loads successfully (check `/api/health`)
- [ ] Prediction endpoint works (`/api/predict`)
- [ ] Training endpoint accepts requests (even if it times out, error should be clear)
- [ ] Error messages are user-friendly
- [ ] No JSON parsing errors in browser console

## Troubleshooting

### Model Still Not Loading

1. Check Docker build logs for model file warnings
2. Verify model files exist locally before building
3. Check Cloud Run logs: `gcloud run services logs read water-sprinkler-api --region us-central1`

### Training Still Times Out

1. Reduce epochs to 10-20
2. Use smaller CSV files for testing
3. Check Cloud Run logs for actual error messages
4. Consider implementing async training for production

