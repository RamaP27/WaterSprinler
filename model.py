# -*- coding: utf-8 -*-
"""Water Sprinkler LSTM Model - Clean Implementation"""

import os
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import joblib

from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve

try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    from tensorflow.keras.regularizers import l2
    from tensorflow.keras.metrics import Precision, Recall
except Exception as e:
    raise ImportError("TensorFlow (tf) must be installed to use this script. Error: " + str(e))


class SprinklerLSTMModel:
    def __init__(self, window_size=10, random_seed=42):
        self.window_size = int(window_size)
        self.scaler = MinMaxScaler()
        self.label_encoder = LabelEncoder()
        self.model = None
        self.feature_columns = None
        np.random.seed(random_seed)
        tf.random.set_seed(random_seed)

    def load_and_preprocess_data(self, csv_path):
        """Load CSV, normalize column names if needed, encode status, return DataFrame."""
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Data file not found: {csv_path}")

        df = pd.read_csv(csv_path)
        print(f"[INFO] Loaded data shape: {df.shape}")

        # If columns are unnamed (0,1,2.. or Unnamed), assume last column is Status
        last_col = df.columns[-1]
        if isinstance(last_col, int) or "Unnamed" in str(last_col):
            print("[INFO] Detected unnamed columns — renaming and assuming last column is 'Status'.")
            num_cols = len(df.columns)
            feature_names = [f"Feature_{i}" for i in range(num_cols - 1)] + ["Status"]
            df.columns = feature_names
            print(f"[INFO] Columns renamed: {df.columns.tolist()}")

        # If 'Status' not present, rename last column to 'Status'
        if "Status" not in df.columns:
            df = df.rename(columns={df.columns[-1]: "Status"})
            print("[INFO] Renamed last column to 'Status'.")

        # Clean Status column
        df["Status"] = df["Status"].astype(str).str.strip()

        # Fill numeric missing values with mean; fill non-numeric with mode
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        non_numeric_cols = [c for c in df.columns if c not in numeric_cols]

        if numeric_cols:
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
        for c in non_numeric_cols:
            if df[c].isnull().any():
                df[c] = df[c].fillna(df[c].mode().iloc[0] if not df[c].mode().empty else "")

        print(f"[INFO] Unique Status values (raw):\n{df['Status'].value_counts()}")

        # Encode Status
        df["Status"] = self.label_encoder.fit_transform(df["Status"])
        print(f"[INFO] Encoded Status classes: {list(self.label_encoder.classes_)}")
        self.feature_columns = [c for c in df.columns if c != "Status"]
        print(f"[INFO] Feature columns: {self.feature_columns}")

        return df

    def create_sequences(self, data, labels):
        """Create sliding window sequences for LSTM."""
        X, y = [], []
        n = len(data)
        for i in range(n - self.window_size):
            X.append(data[i : i + self.window_size])
            y.append(labels[i + self.window_size])
        X = np.array(X)
        y = np.array(y)
        return X, y

    def prepare_data(self, df):
        """Scale features and create sequences for model training/inference."""
        if self.feature_columns is None:
            raise ValueError("feature_columns not set. Run load_and_preprocess_data first.")

        features = df[self.feature_columns].values.astype(float)
        labels = df["Status"].values.astype(int)

        scaled = self.scaler.fit_transform(features)
        X, y = self.create_sequences(scaled, labels)
        print(f"[INFO] Created sequences. X shape: {X.shape}, y shape: {y.shape}")
        return X, y

    def build_model(self, input_shape,
                    l2_reg=0.001,
                    dropout_rate=0.3,
                    dense_units=(32, 16),
                    lstm_units=(128, 64)):
        """Construct and compile the LSTM model."""
        model = Sequential()
        model.add(LSTM(units=lstm_units[0], return_sequences=True,
                       input_shape=input_shape,
                       kernel_regularizer=l2(l2_reg)))
        model.add(BatchNormalization())
        model.add(Dropout(dropout_rate))

        model.add(LSTM(units=lstm_units[1], return_sequences=False,
                       kernel_regularizer=l2(l2_reg)))
        model.add(BatchNormalization())
        model.add(Dropout(dropout_rate))

        model.add(Dense(dense_units[0], activation="relu", kernel_regularizer=l2(l2_reg)))
        model.add(Dropout(0.2))
        model.add(Dense(dense_units[1], activation="relu"))
        model.add(Dense(1, activation="sigmoid"))

        model.compile(
            optimizer="adam",
            loss="binary_crossentropy",
            metrics=["accuracy", Precision(name="precision"), Recall(name="recall")]
        )
        self.model = model
        print("[INFO] Model built and compiled.")
        return model

    def train_model(self, X_train, y_train, X_val, y_val,
                    epochs=50, batch_size=32, patience=10, reduce_factor=0.5, min_lr=1e-5):
        if self.model is None:
            print("[INFO] Building model automatically based on training data shape.")
            self.build_model(input_shape=(X_train.shape[1], X_train.shape[2]))

        callbacks = [
            EarlyStopping(monitor="val_loss", patience=patience, restore_best_weights=True, verbose=1),
            ReduceLROnPlateau(monitor="val_loss", factor=reduce_factor, patience=max(3, patience//3),
                              min_lr=min_lr, verbose=1)
        ]

        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs, batch_size=batch_size,
            callbacks=callbacks, verbose=1
        )
        return history

    def evaluate_model(self, X_test, y_test):
        if self.model is None:
            raise RuntimeError("Model not built/trained. Call build_model/train_model first.")

        y_pred_proba = self.model.predict(X_test, verbose=0).ravel()
        y_pred = (y_pred_proba > 0.5).astype(int)

        metrics = {}
        eval_res = self.model.evaluate(X_test, y_test, verbose=0)
        metrics["loss"] = float(eval_res[0])
        metrics["accuracy"] = float(eval_res[1]) if len(eval_res) > 1 else None
        if len(eval_res) >= 4:
            metrics["precision"] = float(eval_res[2])
            metrics["recall"] = float(eval_res[3])
        else:
            metrics["precision"] = None
            metrics["recall"] = None

        try:
            metrics["auc"] = float(roc_auc_score(y_test, y_pred_proba))
        except Exception:
            metrics["auc"] = None

        metrics["predictions"] = y_pred.tolist()
        metrics["probabilities"] = y_pred_proba.tolist()
        metrics["confusion_matrix"] = confusion_matrix(y_test, y_pred).tolist()
        return metrics

    def save_model(self, model_path="sprinkler_lstm_keras.h5", artifacts_path="artifacts"):
        """Save Keras model and preprocessing artifacts."""
        if self.model is None:
            raise RuntimeError("No trained model to save.")
        os.makedirs(artifacts_path, exist_ok=True)
        self.model.save(model_path)
        joblib.dump(self.scaler, os.path.join(artifacts_path, "scaler.joblib"))
        joblib.dump(self.label_encoder, os.path.join(artifacts_path, "label_encoder.joblib"))
        joblib.dump(self.feature_columns, os.path.join(artifacts_path, "feature_columns.joblib"))
        print(f"[INFO] Model saved to {model_path} and artifacts in {artifacts_path}")

    def load_saved_model(self, model_path="sprinkler_lstm_keras.h5", artifacts_path="artifacts"):
        """Load model and artifacts."""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        self.model = tf.keras.models.load_model(model_path, compile=True)
        scaler_path = os.path.join(artifacts_path, "scaler.joblib")
        encoder_path = os.path.join(artifacts_path, "label_encoder.joblib")
        feat_path = os.path.join(artifacts_path, "feature_columns.joblib")
        if os.path.exists(scaler_path):
            self.scaler = joblib.load(scaler_path)
        if os.path.exists(encoder_path):
            self.label_encoder = joblib.load(encoder_path)
        if os.path.exists(feat_path):
            self.feature_columns = joblib.load(feat_path)
        print(f"[INFO] Loaded model and artifacts from {model_path} and {artifacts_path}")

    def predict(self, raw_feature_array):
        """Predict for a single set of features."""
        if self.model is None:
            raise RuntimeError("Model not loaded/trained.")
        arr = np.array(raw_feature_array, dtype=float)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        if arr.ndim == 2 and arr.shape[0] == self.window_size:
            arr_seq = arr.reshape(1, arr.shape[0], arr.shape[1])
        elif arr.ndim == 2 and arr.shape[1] == len(self.feature_columns):
            arr_seq = np.repeat(arr.reshape(1, 1, arr.shape[1]), self.window_size, axis=1)
        else:
            raise ValueError("Input shape not compatible with window size and feature count.")
        scaled = self.scaler.transform(arr_seq.reshape(-1, arr_seq.shape[-1])).reshape(arr_seq.shape)
        proba = self.model.predict(scaled, verbose=0).ravel()[0]
        label = int(proba > 0.5)
        return {
            "probability": float(proba),
            "label": label,
            "label_name": self.label_encoder.inverse_transform([label])[0]
        }

