# Running and Testing the UI Locally

## Quick Start

### Step 1: Install Dependencies (if not already done)

```bash
pip install -r requirements.txt
```

### Step 2: Start the Flask Application

```bash
python app.py
```

The app will start on **http://localhost:8000** by default.

You should see output like:
```
[INFO] Model loaded successfully
 * Running on http://0.0.0.0:8000
```

Or if the model isn't trained yet:
```
[WARN] Model files not found. Please train the model first.
 * Running on http://0.0.0.0:8000
```

### Step 3: Open the Web UI

Open your browser and navigate to:
```
http://localhost:8000
```

## Testing the UI

### 1. Check Model Status

When you open the page, you'll see a status indicator at the top:
- **Green "✓ Model loaded and ready"** - Model is ready for predictions
- **Red "✗ Model not loaded"** - You need to train a model first

### 2. Make a Prediction

Once the model is loaded:

1. **Fill in the feature inputs** - The UI will automatically show input fields for each feature column from your trained model
2. **Enter values** for each feature (e.g., Soil Moisture, Temperature, Humidity, etc.)
3. **Click "Predict Status"** button
4. **View the result** showing:
   - Predicted status (ON/OFF)
   - Probability percentage
   - Confidence level
   - Visual progress bar

### 3. Train a New Model (via UI)

If you want to train via the web UI:

1. Scroll to the **"Train Model"** section
2. Click **"Choose File"** and select your CSV file
3. Adjust training parameters (optional):
   - **Epochs**: Number of training iterations (default: 50)
   - **Batch Size**: Training batch size (default: 32)
4. Click **"Train Model"**
5. Wait for training to complete (this may take several minutes)
6. The UI will show training results (accuracy, precision, recall, AUC)

## Testing via API (Command Line)

You can also test the API endpoints directly using `curl`:

### Health Check
```bash
curl http://localhost:8000/api/health
```

### Get Features
```bash
curl http://localhost:8000/api/features
```

### Make a Prediction
```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [45.2, 25.3, 60.1]}'
```

Replace the feature values with actual values matching your model's feature columns.

## Troubleshooting

### Port Already in Use
If port 8000 is already in use, you can change it:
```bash
PORT=5000 python app.py
```

### Model Not Loading
- Make sure `sprinkler_lstm_keras.h5` exists in the project root
- Make sure `artifacts/` folder exists with:
  - `scaler.joblib`
  - `label_encoder.joblib`
  - `feature_columns.joblib`

### Import Errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (3.11+ recommended)

### UI Not Loading
- Check browser console for errors (F12)
- Make sure Flask is running and accessible
- Try accessing `http://127.0.0.1:8000` instead of `localhost`

## Example Workflow

1. **Train the model** (if not done):
   ```bash
   python train_model.py training_data/TARP.csv
   ```

2. **Start the app**:
   ```bash
   python app.py
   ```

3. **Open browser**: http://localhost:8000

4. **Test prediction**: Enter feature values and click "Predict Status"

5. **View results**: See the prediction with probability and confidence

