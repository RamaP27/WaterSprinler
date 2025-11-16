# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Train Your Model (Optional)

If you have training data (CSV file), you can train the model:

**Option A: Using the Web UI**
1. Run the app: `python app.py`
2. Open http://localhost:5000
3. Go to "Train Model" section
4. Upload your CSV file
5. Click "Train Model"

**Option B: Using Python**
```python
from model import SprinklerLSTMModel
from sklearn.model_selection import train_test_split

# Initialize model
model = SprinklerLSTMModel(window_size=10)

# Load and preprocess data
df = model.load_and_preprocess_data("your_data.csv")

# Prepare sequences
X, y = model.prepare_data(df)

# Split data
X_temp, X_test, y_temp, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
X_train, X_val, y_train, y_val = train_test_split(
    X_temp, y_temp, test_size=0.25, random_state=42, stratify=y_temp
)

# Build and train
model.build_model(input_shape=(X_train.shape[1], X_train.shape[2]))
history = model.train_model(X_train, y_train, X_val, y_val, epochs=50, batch_size=32)

# Evaluate
results = model.evaluate_model(X_test, y_test)
print(f"Accuracy: {results['accuracy']:.4f}")

# Save model
model.save_model()
```

### Step 3: Run the Application

```bash
python app.py
```

Then open your browser to: **http://localhost:5000**

## 📋 Data Format

Your CSV file should have:
- **Feature columns**: Numeric values (e.g., Soil Moisture, Temperature, Humidity)
- **Status column**: Last column with categorical values (e.g., "ON"/"OFF", "1"/"0")

Example CSV:
```csv
Soil Moisture,Temperature,Humidity,Status
45.2,25.3,60.1,ON
42.1,24.8,58.5,OFF
48.5,26.1,62.3,ON
```

## 🌐 Deploy to Cloud

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

Quick deploy to Cloud Run:
```bash
./deploy.sh
```

## 🎯 Features

- ✅ Predict sprinkler status from input features
- ✅ Train new models via web UI
- ✅ View prediction probabilities and confidence
- ✅ Modern, responsive UI
- ✅ RESTful API

## 📝 API Usage

### Health Check
```bash
curl http://localhost:5000/api/health
```

### Get Features
```bash
curl http://localhost:5000/api/features
```

### Make Prediction
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [45.2, 25.3, 60.1]}'
```

### Train Model
```bash
curl -X POST http://localhost:5000/api/train \
  -F "file=@your_data.csv" \
  -F "epochs=50" \
  -F "batch_size=32"
```

## ❓ Troubleshooting

**Model not loading?**
- Make sure `sprinkler_lstm_keras.h5` and `artifacts/` folder exist
- Train a model first if you don't have one

**Import errors?**
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (3.11+ recommended)

**Port already in use?**
- Change the port in `app.py`: `app.run(port=5001)`

## 📚 More Information

- Full documentation: [README.md](README.md)
- Deployment guide: [DEPLOYMENT.md](DEPLOYMENT.md)

