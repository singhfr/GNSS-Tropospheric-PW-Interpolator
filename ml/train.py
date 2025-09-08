#!/usr/bin/env python3
"""
GNSS PW Interpolation Model Training Script

This script trains multiple ML models for GNSS precipitable water interpolation:
- Gaussian Process Regression (GPR) for spatial interpolation
- LSTM for temporal forecasting
- Baseline methods (IDW, Kriging)
"""

import pandas as pd
import numpy as np
import os
import sys
import joblib
from datetime import datetime
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel, ConstantKernel, Matern
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import torch
import torch.nn as nn
import pytorch_lightning as pl
from torch.utils.data import DataLoader, TensorDataset

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class LSTMPredictor(pl.LightningModule):
    """LSTM model for temporal PW forecasting"""
    
    def __init__(self, input_size=4, hidden_size=64, num_layers=2, output_size=1, learning_rate=0.001):
        super().__init__()
        self.save_hyperparameters()
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_size, output_size)
        self.learning_rate = learning_rate
        
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        # Use last timestep output
        output = self.fc(lstm_out[:, -1, :])
        return output
    
    def training_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self(x)
        loss = nn.MSELoss()(y_hat, y)
        self.log('train_loss', loss)
        return loss
    
    def validation_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self(x)
        loss = nn.MSELoss()(y_hat, y)
        self.log('val_loss', loss)
        return loss
    
    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=self.learning_rate)


class GNSSModelTrainer:
    """Main training class for GNSS PW interpolation models"""
    
    def __init__(self, data_path="data/mock_gnss_zwd.csv", models_dir="ml/models"):
        self.data_path = data_path
        self.models_dir = models_dir
        os.makedirs(models_dir, exist_ok=True)
        
        self.results = {}
        
    def load_and_preprocess_data(self):
        """Load and preprocess GNSS data"""
        print("Loading and preprocessing data...")
        
        # Load data
        df = pd.read_csv(self.data_path)
        print(f"Loaded {len(df)} records from {len(df['station_id'].unique())} stations")
        
        # Convert timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Convert ZWD to PW (simplified conversion factor)
        pw_conversion_factor = 6.2  # mm PW per 0.1m ZWD
        df['pw'] = df['zenith_wet_delay'] * pw_conversion_factor * 10
        
        # Add temporal features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_year'] = df['timestamp'].dt.dayofyear
        
        # Basic data cleaning
        df = df.dropna()
        df = df[df['pw'] > 0]  # Remove invalid PW values
        df = df[df['pw'] < 100]  # Remove extreme outliers
        
        print(f"After preprocessing: {len(df)} records")
        print(f"PW range: {df['pw'].min():.2f} - {df['pw'].max():.2f} mm")
        
        return df
    
    def train_gpr_model(self, df):
        """Train Gaussian Process Regression model"""
        print("\nTraining Gaussian Process Regression model...")
        
        # Prepare features: lat, lon, elevation, azimuth, hour
        features = df[['latitude', 'longitude', 'elevation', 'azimuth', 'hour']].values
        targets = df['pw'].values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features, targets, test_size=0.2, random_state=42
        )
        
        # Scale features
        scaler_X = StandardScaler()
        scaler_y = StandardScaler()
        
        X_train_scaled = scaler_X.fit_transform(X_train)
        X_test_scaled = scaler_X.transform(X_test)
        y_train_scaled = scaler_y.fit_transform(y_train.reshape(-1, 1)).ravel()
        
        # Define multiple kernels to try
        kernels = {
            'RBF': ConstantKernel(1.0) * RBF(length_scale=1.0) + WhiteKernel(noise_level=0.1),
            'Matern': ConstantKernel(1.0) * Matern(length_scale=1.0, nu=2.5) + WhiteKernel(noise_level=0.1),
            'RBF+Matern': ConstantKernel(1.0) * RBF(length_scale=1.0) + \
                         ConstantKernel(1.0) * Matern(length_scale=1.0, nu=1.5) + \
                         WhiteKernel(noise_level=0.1)
        }
        
        best_score = -np.inf
        best_model = None
        best_kernel_name = None
        
        for kernel_name, kernel in kernels.items():
            print(f"  Testing {kernel_name} kernel...")
            
            # Train model
            gpr = GaussianProcessRegressor(
                kernel=kernel, 
                alpha=1e-6, 
                normalize_y=False,  # We're doing manual scaling
                random_state=42
            )
            
            # Cross-validation
            cv_scores = cross_val_score(gpr, X_train_scaled, y_train_scaled, cv=3, scoring='r2')
            avg_cv_score = cv_scores.mean()
            
            print(f"    CV R² Score: {avg_cv_score:.4f} ± {cv_scores.std():.4f}")
            
            if avg_cv_score > best_score:
                best_score = avg_cv_score
                best_model = gpr
                best_kernel_name = kernel_name
        
        # Train best model on full training set
        print(f"\nTraining final GPR model with {best_kernel_name} kernel...")
        best_model.fit(X_train_scaled, y_train_scaled)
        
        # Evaluate on test set
        y_pred_scaled = best_model.predict(X_test_scaled)
        y_pred = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).ravel()
        
        # Metrics
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"GPR Test Results:")
        print(f"  RMSE: {rmse:.3f} mm")
        print(f"  MAE:  {mae:.3f} mm")
        print(f"  R²:   {r2:.4f}")
        
        # Save model and scalers
        model_path = os.path.join(self.models_dir, "gpr_model.pkl")
        scaler_X_path = os.path.join(self.models_dir, "gpr_scaler_features.pkl")
        scaler_y_path = os.path.join(self.models_dir, "gpr_scaler_target.pkl")
        
        joblib.dump(best_model, model_path)
        joblib.dump(scaler_X, scaler_X_path)
        joblib.dump(scaler_y, scaler_y_path)
        
        self.results['gpr'] = {
            'rmse': rmse,
            'mae': mae,
            'r2': r2,
            'best_kernel': best_kernel_name,
            'cv_score': best_score,
            'model_path': model_path
        }
        
        return best_model, scaler_X, scaler_y
    
    def prepare_lstm_data(self, df, sequence_length=24):
        """Prepare data for LSTM training"""
        print(f"\nPreparing LSTM data with sequence length {sequence_length}...")
        
        # Group by station and create sequences
        sequences = []
        targets = []
        
        for station_id in df['station_id'].unique():
            station_data = df[df['station_id'] == station_id].sort_values('timestamp')
            
            if len(station_data) < sequence_length + 1:
                continue  # Skip stations with insufficient data
            
            # Create features: pw, hour, azimuth, elevation (normalized)
            features = station_data[['pw', 'hour', 'azimuth', 'elevation']].values
            
            # Normalize features
            scaler = MinMaxScaler()
            features_scaled = scaler.fit_transform(features)
            
            # Create sequences
            for i in range(len(features_scaled) - sequence_length):
                seq = features_scaled[i:i+sequence_length]
                target = features_scaled[i+sequence_length, 0]  # Next PW value
                
                sequences.append(seq)
                targets.append(target)
        
        print(f"Created {len(sequences)} sequences from {df['station_id'].nunique()} stations")
        
        return np.array(sequences), np.array(targets)
    
    def train_lstm_model(self, df):
        """Train LSTM model for temporal forecasting"""
        print("\nTraining LSTM model...")
        
        # Prepare data
        X, y = self.prepare_lstm_data(df, sequence_length=12)  # 12-hour sequences
        
        if len(X) < 50:
            print("Insufficient data for LSTM training, skipping...")
            self.results['lstm'] = {'error': 'Insufficient data'}
            return None
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Convert to tensors
        X_train_tensor = torch.FloatTensor(X_train)
        y_train_tensor = torch.FloatTensor(y_train).unsqueeze(1)
        X_test_tensor = torch.FloatTensor(X_test)
        y_test_tensor = torch.FloatTensor(y_test).unsqueeze(1)
        
        # Create data loaders
        train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
        test_dataset = TensorDataset(X_test_tensor, y_test_tensor)
        
        train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
        test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
        
        # Initialize model
        model = LSTMPredictor(input_size=4, hidden_size=32, num_layers=1)
        
        # Train model
        trainer = pl.Trainer(
            max_epochs=50,
            accelerator='auto',
            enable_progress_bar=True,
            enable_model_summary=False,
            logger=False,
            enable_checkpointing=False
        )
        
        trainer.fit(model, train_loader, test_loader)
        
        # Evaluate
        model.eval()
        with torch.no_grad():
            y_pred = model(X_test_tensor)
            
        y_pred_np = y_pred.numpy().ravel()
        y_test_np = y_test
        
        rmse = np.sqrt(mean_squared_error(y_test_np, y_pred_np))
        mae = mean_absolute_error(y_test_np, y_pred_np)
        r2 = r2_score(y_test_np, y_pred_np)
        
        print(f"LSTM Test Results:")
        print(f"  RMSE: {rmse:.4f}")
        print(f"  MAE:  {mae:.4f}")
        print(f"  R²:   {r2:.4f}")
        
        # Save model
        model_path = os.path.join(self.models_dir, "lstm_model.pt")
        torch.save(model.state_dict(), model_path)
        
        self.results['lstm'] = {
            'rmse': rmse,
            'mae': mae,
            'r2': r2,
            'model_path': model_path
        }
        
        return model
    
    def train_baseline_models(self, df):
        """Train baseline models (IDW, simple averaging)"""
        print("\nTraining baseline models...")
        
        # For baseline evaluation, we'll use spatial cross-validation
        # Leave-one-station-out cross-validation
        
        stations = df['station_id'].unique()
        idw_errors = []
        avg_errors = []
        
        for test_station in stations[:5]:  # Test on first 5 stations for speed
            train_data = df[df['station_id'] != test_station]
            test_data = df[df['station_id'] == test_station]
            
            if len(test_data) == 0:
                continue
            
            for _, test_row in test_data.iterrows():
                test_lat, test_lon = test_row['latitude'], test_row['longitude']
                true_pw = test_row['pw']
                
                # IDW prediction
                distances = np.sqrt(
                    (train_data['latitude'] - test_lat)**2 + 
                    (train_data['longitude'] - test_lon)**2
                )
                
                # Avoid division by zero
                distances = np.maximum(distances, 1e-10)
                weights = 1 / (distances**2)
                weights = weights / weights.sum()
                
                idw_pred = np.sum(weights * train_data['pw'])
                idw_errors.append(abs(idw_pred - true_pw))
                
                # Simple average prediction
                avg_pred = train_data['pw'].mean()
                avg_errors.append(abs(avg_pred - true_pw))
        
        idw_mae = np.mean(idw_errors)
        avg_mae = np.mean(avg_errors)
        
        print(f"Baseline Results:")
        print(f"  IDW MAE:     {idw_mae:.3f} mm")
        print(f"  Average MAE: {avg_mae:.3f} mm")
        
        self.results['baselines'] = {
            'idw_mae': idw_mae,
            'average_mae': avg_mae
        }
    
    def run_training(self):
        """Run complete training pipeline"""
        print("=== GNSS PW Interpolation Model Training ===")
        print(f"Started at: {datetime.now()}")
        
        # Load data
        df = self.load_and_preprocess_data()
        
        # Train models
        self.train_gpr_model(df)
        self.train_lstm_model(df)
        self.train_baseline_models(df)
        
        # Save training results
        results_path = os.path.join(self.models_dir, "training_results.json")
        import json
        with open(results_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n=== Training Complete ===")
        print(f"Results saved to: {results_path}")
        print(f"Models saved to: {self.models_dir}")
        
        return self.results


if __name__ == "__main__":
    trainer = GNSSModelTrainer()
    results = trainer.run_training()
    
    print("\n=== Final Results Summary ===")
    for model_name, metrics in results.items():
        print(f"{model_name.upper()}:")
        for metric, value in metrics.items():
            if isinstance(value, float):
                print(f"  {metric}: {value:.4f}")
            else:
                print(f"  {metric}: {value}")
        print()
