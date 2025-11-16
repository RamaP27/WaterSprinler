#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Standalone script to train the water sprinkler LSTM model"""

import os
import sys
import argparse
from model import SprinklerLSTMModel
from sklearn.model_selection import train_test_split

def train_model(csv_path, epochs=50, batch_size=32, window_size=10):
    """
    Train the LSTM model from a CSV file.
    
    Args:
        csv_path: ../training_data/TARP.csv
        epochs: Number of training epochs (default: 50)
        batch_size: Batch size for training (default: 32)
        window_size: LSTM window size (default: 10)
    """
    if not os.path.exists(csv_path):
        print(f"[ERROR] Data file not found: {csv_path}")
        sys.exit(1)
    
    print(f"[INFO] Starting model training...")
    print(f"[INFO] Data file: {csv_path}")
    print(f"[INFO] Epochs: {epochs}, Batch size: {batch_size}, Window size: {window_size}")
    print("-" * 60)
    
    # Initialize model
    model = SprinklerLSTMModel(window_size=window_size)
    
    # Load and preprocess data
    print("[INFO] Loading and preprocessing data...")
    df = model.load_and_preprocess_data(csv_path)
    print(f"[INFO] Data shape: {df.shape}")
    
    # Prepare sequences
    print("[INFO] Creating sequences...")
    X, y = model.prepare_data(df)
    print(f"[INFO] Sequences created. X shape: {X.shape}, y shape: {y.shape}")
    
    # Check if we have enough classes
    unique_classes = len(set(y))
    if unique_classes < 2:
        print(f"[ERROR] Target variable has only {unique_classes} class(es). Need at least 2 classes.")
        sys.exit(1)
    
    # Split data
    print("[INFO] Splitting data into train/validation/test sets...")
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=0.25, random_state=42, stratify=y_temp
    )
    print(f"[INFO] Train: {X_train.shape[0]}, Validation: {X_val.shape[0]}, Test: {X_test.shape[0]}")
    
    # Build model
    print("[INFO] Building LSTM model...")
    model.build_model(input_shape=(X_train.shape[1], X_train.shape[2]))
    
    # Train model
    print("[INFO] Training model...")
    print("-" * 60)
    history = model.train_model(
        X_train, y_train, X_val, y_val,
        epochs=epochs, batch_size=batch_size, patience=12
    )
    print("-" * 60)
    
    # Evaluate model
    print("[INFO] Evaluating model on test set...")
    results = model.evaluate_model(X_test, y_test)
    
    print("\n" + "=" * 60)
    print("TRAINING RESULTS")
    print("=" * 60)
    print(f"Accuracy:  {results.get('accuracy', 'N/A'):.4f}" if results.get('accuracy') else "Accuracy:  N/A")
    print(f"Precision: {results.get('precision', 'N/A'):.4f}" if results.get('precision') else "Precision: N/A")
    print(f"Recall:    {results.get('recall', 'N/A'):.4f}" if results.get('recall') else "Recall:    N/A")
    print(f"AUC:       {results.get('auc', 'N/A'):.4f}" if results.get('auc') else "AUC:       N/A")
    print(f"Loss:      {results.get('loss', 'N/A'):.4f}" if results.get('loss') else "Loss:      N/A")
    print("=" * 60)
    
    # Save model
    print("\n[INFO] Saving model...")
    model.save_model()
    
    print("\n[SUCCESS] Model training completed!")
    print(f"[INFO] Model saved to: sprinkler_lstm_keras.h5")
    print(f"[INFO] Artifacts saved to: artifacts/")
    print(f"[INFO] Feature columns: {model.feature_columns}")
    print("\nYou can now run the Flask app: python app.py")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train the Water Sprinkler LSTM Model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python train_model.py data.csv
  python train_model.py data.csv --epochs 100 --batch-size 64
  python train_model.py data.csv --window-size 15
        """
    )
    
    parser.add_argument(
        "csv_path",
        type=str,
        help="Path to the CSV training data file"
    )
    
    parser.add_argument(
        "--epochs",
        type=int,
        default=50,
        help="Number of training epochs (default: 50)"
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch size for training (default: 32)"
    )
    
    parser.add_argument(
        "--window-size",
        type=int,
        default=10,
        help="LSTM window size (default: 10)"
    )
    
    args = parser.parse_args()
    
    train_model(
        csv_path=args.csv_path,
        epochs=args.epochs,
        batch_size=args.batch_size,
        window_size=args.window_size
    )

