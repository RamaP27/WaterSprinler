# -*- coding: utf-8 -*-
"""Flask API for Water Sprinkler Prediction"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import json
from model import SprinklerLSTMModel

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Global model instance
model_instance = None

def load_model():
    """Load the trained model if available."""
    global model_instance
    if model_instance is None:
        model_path = os.path.join(os.path.dirname(__file__), "sprinkler_lstm_keras.h5")
        artifacts_path = os.path.join(os.path.dirname(__file__), "artifacts")
        
        if os.path.exists(model_path) and os.path.exists(artifacts_path):
            try:
                model_instance = SprinklerLSTMModel()
                model_instance.load_saved_model(model_path, artifacts_path)
                print("[INFO] Model loaded successfully")
            except Exception as e:
                print(f"[ERROR] Failed to load model: {e}")
                model_instance = None
        else:
            print("[WARN] Model files not found. Please train the model first.")
    return model_instance

@app.route('/')
def index():
    """Serve the main UI."""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    model = load_model()
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None,
        "feature_columns": model.feature_columns if model else None
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    """Predict sprinkler status from input features."""
    try:
        model = load_model()
        if model is None:
            return jsonify({
                "error": "Model not loaded. Please train and save the model first."
            }), 503

        data = request.get_json()
        if not data or 'features' not in data:
            return jsonify({"error": "Missing 'features' in request body"}), 400

        features = data['features']
        
        # Validate feature count
        if len(features) != len(model.feature_columns):
            return jsonify({
                "error": f"Expected {len(model.feature_columns)} features, got {len(features)}",
                "expected_features": model.feature_columns
            }), 400

        # Make prediction
        prediction = model.predict(features)
        
        return jsonify({
            "success": True,
            "prediction": prediction,
            "status": prediction["label_name"],
            "probability": prediction["probability"],
            "confidence": abs(prediction["probability"] - 0.5) * 2  # Normalize to 0-1
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/features', methods=['GET'])
def get_features():
    """Get the list of required features."""
    model = load_model()
    if model is None:
        return jsonify({
            "error": "Model not loaded",
            "features": []
        }), 503
    
    return jsonify({
        "features": model.feature_columns,
        "window_size": model.window_size
    })

@app.route('/api/train', methods=['POST'])
def train():
    """Train the model from uploaded CSV file."""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Save uploaded file temporarily
        upload_path = os.path.join(os.path.dirname(__file__), "temp_data.csv")
        file.save(upload_path)

        # Train model
        from sklearn.model_selection import train_test_split
        global model_instance
        
        model_instance = SprinklerLSTMModel(window_size=10)
        df = model_instance.load_and_preprocess_data(upload_path)
        X, y = model_instance.prepare_data(df)
        
        if len(set(y)) < 2:
            return jsonify({"error": "Target variable has only one class"}), 400

        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=0.25, random_state=42, stratify=y_temp
        )

        model_instance.build_model(input_shape=(X_train.shape[1], X_train.shape[2]))
        
        epochs = int(request.form.get('epochs', 50))
        batch_size = int(request.form.get('batch_size', 32))
        
        history = model_instance.train_model(
            X_train, y_train, X_val, y_val,
            epochs=epochs, batch_size=batch_size, patience=12
        )

        results = model_instance.evaluate_model(X_test, y_test)
        model_instance.save_model()

        # Clean up temp file
        if os.path.exists(upload_path):
            os.remove(upload_path)

        return jsonify({
            "success": True,
            "accuracy": results.get("accuracy"),
            "precision": results.get("precision"),
            "recall": results.get("recall"),
            "auc": results.get("auc"),
            "feature_columns": model_instance.feature_columns
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Try to load model on startup
    load_model()
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)

