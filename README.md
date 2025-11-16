# Water Sprinkler Prediction System

AI-powered LSTM model for predicting water sprinkler status based on environmental and sensor data.

## Features

- 🧠 LSTM-based machine learning model
- 🌐 Modern web UI for predictions
- 📊 Model training interface
- ☁️ Firebase/Google Cloud deployment ready

## Project Structure

```
.
├── app.py              # Flask API backend
├── model.py            # LSTM model class
├── main.py             # Cloud Run entry point
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container configuration
├── app.yaml            # App Engine configuration
├── firebase.json       # Firebase configuration
├── templates/          # HTML templates
│   └── index.html
└── static/             # CSS and JavaScript
    ├── style.css
    └── script.js
```

## Local Development

### Prerequisites

- Python 3.11+
- pip

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Train a model (optional - if you have training data):
```python
from model import SprinklerLSTMModel
from sklearn.model_selection import train_test_split

model = SprinklerLSTMModel(window_size=10)
df = model.load_and_preprocess_data("your_data.csv")
X, y = model.prepare_data(df)

X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.25, random_state=42, stratify=y_temp)

model.build_model(input_shape=(X_train.shape[1], X_train.shape[2]))
history = model.train_model(X_train, y_train, X_val, y_val, epochs=50, batch_size=32)
results = model.evaluate_model(X_test, y_test)
model.save_model()
```

3. Run the Flask app:
```bash
python app.py
```

4. Open your browser to `http://localhost:5000`

## Deployment Options

### Option 1: Google Cloud Run (Recommended)

1. Install Google Cloud SDK:
```bash
# Follow instructions at https://cloud.google.com/sdk/docs/install
```

2. Build and deploy:
```bash
# Set your project ID
gcloud config set project YOUR_PROJECT_ID

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
  --timeout 300
```

3. Update `firebase.json` with your Cloud Run service URL

### Option 2: App Engine

1. Update `app.yaml` with your project settings

2. Deploy:
```bash
gcloud app deploy
```

### Option 3: Firebase Hosting (Frontend) + Cloud Run (Backend)

1. Build static files (if needed):
```bash
# The Flask app serves static files, but you can also build a separate frontend
```

2. Deploy backend to Cloud Run (see Option 1)

3. Deploy frontend to Firebase Hosting:
```bash
firebase init hosting
firebase deploy --only hosting
```

## API Endpoints

### Health Check
```
GET /api/health
```
Returns model status and feature information.

### Get Features
```
GET /api/features
```
Returns list of required feature columns.

### Predict
```
POST /api/predict
Content-Type: application/json

{
  "features": [value1, value2, ...]
}
```

### Train Model
```
POST /api/train
Content-Type: multipart/form-data

file: CSV file
epochs: 50 (optional)
batch_size: 32 (optional)
```

## Data Format

The CSV file should have:
- Feature columns (numeric values)
- A 'Status' column (last column) with categorical values (e.g., "ON"/"OFF", "1"/"0")

Example:
```csv
Soil Moisture,Temperature,Humidity,Status
45.2,25.3,60.1,ON
42.1,24.8,58.5,OFF
...
```

## Environment Variables

- `PORT`: Server port (default: 5000 for local, 8080 for Cloud Run)

## Notes

- The model requires TensorFlow, which has large dependencies. Cloud Run is recommended over Firebase Functions due to size limits.
- For production, consider using Cloud Storage for model artifacts instead of local filesystem.
- The model uses a sliding window of 10 time steps by default.

## License

MIT

