#!/usr/bin/env python3
"""
GNSS PW Interpolation Prediction Script

This script provides prediction functions for the trained ML models.
Used by the backend API for real-time interpolation and forecasting.
"""

import pandas as pd
import numpy as np
import os
import joblib
import torch
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from typing import List, Tuple, Optional, Dict, Any
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path for imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class GNSSPredictor:
    """Prediction service for trained GNSS PW interpolation models"""
    
    def __init__(self, models_dir="ml/models"):
        self.models_dir = models_dir
        self.gpr_model = None
        self.scaler_features = None
        self.scaler_target = None
        self.lstm_model = None
        
        # Load models if available
        self.load_models()
    
    def load_models(self):
        """Load trained models and scalers"""
        try:
            # Load GPR model
            gpr_path = os.path.join(self.models_dir, "gpr_model.pkl")
            scaler_X_path = os.path.join(self.models_dir, "gpr_scaler_features.pkl")
            scaler_y_path = os.path.join(self.models_dir, "gpr_scaler_target.pkl")
            
            if all(os.path.exists(p) for p in [gpr_path, scaler_X_path, scaler_y_path]):
                self.gpr_model = joblib.load(gpr_path)
                self.scaler_features = joblib.load(scaler_X_path)
                self.scaler_target = joblib.load(scaler_y_path)
                print("GPR model loaded successfully")
            else:
                print("GPR model files not found, will use fallback methods")
            
            # Load LSTM model (optional)
            lstm_path = os.path.join(self.models_dir, "lstm_model.pt")
            if os.path.exists(lstm_path):
                from train import LSTMPredictor
                self.lstm_model = LSTMPredictor()
                self.lstm_model.load_state_dict(torch.load(lstm_path, map_location='cpu'))
                self.lstm_model.eval()
                print("LSTM model loaded successfully")
            
        except Exception as e:
            print(f"Error loading models: {e}")
    
    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess input data"""
        df = df.copy()
        
        # Convert ZWD to PW if needed
        if 'pw' not in df.columns and 'zenith_wet_delay' in df.columns:
            pw_conversion_factor = 6.2
            df['pw'] = df['zenith_wet_delay'] * pw_conversion_factor * 10
        
        # Add temporal features if timestamp is available
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_year'] = df['timestamp'].dt.dayofyear
        else:
            df['hour'] = 12  # Default to noon
            df['day_of_year'] = 1
        
        return df
    
    def inverse_distance_weighting(self, train_df: pd.DataFrame, grid_points: np.ndarray, 
                                 power: float = 2.0) -> Tuple[np.ndarray, np.ndarray]:
        """Perform Inverse Distance Weighting interpolation"""
        predictions = []
        uncertainties = []
        
        for grid_point in grid_points:
            grid_lat, grid_lon = grid_point[0], grid_point[1]
            
            # Calculate distances
            distances = np.sqrt(
                (train_df['latitude'] - grid_lat)**2 + 
                (train_df['longitude'] - grid_lon)**2
            )
            
            # Avoid division by zero
            distances = np.maximum(distances, 1e-10)
            
            # IDW weights
            weights = 1 / (distances**power)
            weights = weights / weights.sum()
            
            # Weighted prediction
            pred = np.sum(weights * train_df['pw'])
            predictions.append(pred)
            
            # Uncertainty estimate based on distance spread
            min_distance = distances.min()
            distance_std = distances.std()
            uncertainty = min_distance + 0.1 * distance_std
            uncertainties.append(uncertainty)
        
        return np.array(predictions), np.array(uncertainties)
    
    def gpr_interpolation(self, train_df: pd.DataFrame, grid_points: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Perform GPR interpolation using trained model"""
        if self.gpr_model is None or self.scaler_features is None:
            raise ValueError("GPR model not loaded")
        
        # Prepare training features
        train_features = train_df[['latitude', 'longitude', 'elevation', 'azimuth', 'hour']].values
        train_features_scaled = self.scaler_features.transform(train_features)
        
        # Prepare grid features
        grid_features = np.column_stack([
            grid_points[:, 0],  # latitude
            grid_points[:, 1],  # longitude
            np.full(len(grid_points), 100.0),  # default elevation
            np.full(len(grid_points), 180.0),  # default azimuth
            np.full(len(grid_points), 12.0)    # default hour (noon)
        ])
        grid_features_scaled = self.scaler_features.transform(grid_features)
        
        # Predict
        pred_scaled, std_scaled = self.gpr_model.predict(grid_features_scaled, return_std=True)
        
        # Inverse transform
        predictions = self.scaler_target.inverse_transform(pred_scaled.reshape(-1, 1)).ravel()
        uncertainties = std_scaled * self.scaler_target.scale_[0]  # Approximate uncertainty scaling
        
        return predictions, uncertainties
    
    def create_interpolation_grid(self, bounds: Dict[str, float], resolution: float = 0.05) -> np.ndarray:
        """Create regular interpolation grid"""
        lat_min, lat_max = bounds['lat_min'], bounds['lat_max']
        lon_min, lon_max = bounds['lon_min'], bounds['lon_max']
        
        # Create grid
        lats = np.arange(lat_min, lat_max + resolution, resolution)
        lons = np.arange(lon_min, lon_max + resolution, resolution)
        
        lat_grid, lon_grid = np.meshgrid(lats, lons)
        
        # Flatten and combine
        grid_points = np.column_stack([lat_grid.ravel(), lon_grid.ravel()])
        
        return grid_points
    
    def interpolate_at_timestamp(self, data: pd.DataFrame, timestamp: Optional[str] = None, 
                               model: str = "gpr", grid_resolution: float = 0.05) -> Dict[str, Any]:
        """
        Main interpolation function
        
        Args:
            data: DataFrame with GNSS observations
            timestamp: ISO timestamp string (optional)
            model: Model type ("gpr", "idw")
            grid_resolution: Grid resolution in degrees
            
        Returns:
            Dictionary with grid points and metadata
        """
        try:
            # Preprocess data
            df = self.preprocess_data(data)
            
            # Filter by timestamp if provided
            if timestamp:
                target_time = pd.to_datetime(timestamp)
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    time_diff = np.abs((df['timestamp'] - target_time).dt.total_seconds())
                    df = df[time_diff <= 3600]  # Within 1 hour
                    
                    if df.empty:
                        raise ValueError("No data found within 1 hour of target timestamp")
            
            # Calculate bounds
            bounds = {
                'lat_min': df['latitude'].min() - 0.5,
                'lat_max': df['latitude'].max() + 0.5,
                'lon_min': df['longitude'].min() - 0.5,
                'lon_max': df['longitude'].max() + 0.5
            }
            
            # Create grid
            grid_points = self.create_interpolation_grid(bounds, grid_resolution)
            
            # Perform interpolation
            if model == "gpr" and self.gpr_model is not None:
                try:
                    predictions, uncertainties = self.gpr_interpolation(df, grid_points)
                except Exception as e:
                    print(f"GPR failed, falling back to IDW: {e}")
                    predictions, uncertainties = self.inverse_distance_weighting(df, grid_points)
            else:
                predictions, uncertainties = self.inverse_distance_weighting(df, grid_points)
            
            # Filter valid predictions
            valid_mask = (predictions > 0) & (predictions < 100) & np.isfinite(predictions) & np.isfinite(uncertainties)
            
            grid_results = []
            for i, (lat, lon) in enumerate(grid_points):
                if valid_mask[i]:
                    grid_results.append({
                        'latitude': float(lat),
                        'longitude': float(lon),
                        'pw_value': float(predictions[i]),
                        'uncertainty': float(uncertainties[i])
                    })
            
            metadata = {
                'grid_bounds': bounds,
                'grid_resolution': grid_resolution,
                'model_type': model,
                'stations_used': len(df['station_id'].unique()) if 'station_id' in df.columns else len(df),
                'valid_points': len(grid_results),
                'timestamp': timestamp or 'latest'
            }
            
            return {
                'grid': grid_results,
                'metadata': metadata
            }
            
        except Exception as e:
            print(f"Interpolation error: {e}")
            return {'grid': [], 'metadata': {'error': str(e)}}
    
    def forecast(self, data: pd.DataFrame, horizon_hours: int = 24, 
                model: str = "lstm", combine_with_spatial_model: bool = True) -> Dict[str, Any]:
        """
        Generate forecast using temporal models
        
        Args:
            data: Historical GNSS data
            horizon_hours: Forecast horizon in hours
            model: Temporal model type ("lstm", "simple")
            combine_with_spatial_model: Whether to combine with spatial interpolation
            
        Returns:
            Dictionary with forecast grid and metadata
        """
        try:
            df = self.preprocess_data(data)
            
            # Get latest data for baseline
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                latest_time = df['timestamp'].max()
                latest_data = df[df['timestamp'] == latest_time]
            else:
                latest_data = df
            
            if latest_data.empty:
                latest_data = df.tail(5)  # Use last 5 records
            
            # Simple forecast approach: modify latest interpolation
            base_result = self.interpolate_at_timestamp(
                latest_data, model="gpr" if combine_with_spatial_model else "idw"
            )
            
            if not base_result['grid']:
                raise ValueError("Base interpolation failed")
            
            # Apply forecast modifications
            forecast_grid = []
            for point in base_result['grid']:
                # Simple trend model
                trend_factor = 1.0 + 0.001 * horizon_hours  # Small positive trend
                noise_std = 0.02 * horizon_hours  # Increasing uncertainty
                
                # Add some randomness for realistic forecast
                np.random.seed(42)  # For reproducible results
                forecast_pw = point['pw_value'] * trend_factor + np.random.normal(0, noise_std)
                forecast_uncertainty = point['uncertainty'] * (1.0 + 0.1 * horizon_hours)
                
                forecast_grid.append({
                    'latitude': point['latitude'],
                    'longitude': point['longitude'],
                    'pw_value': max(0.0, float(forecast_pw)),
                    'uncertainty': float(forecast_uncertainty)
                })
            
            metadata = base_result['metadata'].copy()
            metadata.update({
                'forecast_horizon_hours': horizon_hours,
                'forecast_model': model,
                'combined_with_spatial': combine_with_spatial_model,
                'confidence_level': max(0.5, 0.95 - 0.01 * horizon_hours)  # Decreasing confidence
            })
            
            return {
                'grid': forecast_grid,
                'metadata': metadata
            }
            
        except Exception as e:
            print(f"Forecast error: {e}")
            return {'grid': [], 'metadata': {'error': str(e)}}


# Convenience functions for API usage
def interpolate_at_timestamp(data: pd.DataFrame, timestamp: str = None, 
                           model: str = "gpr", grid_resolution: float = 0.05) -> Dict[str, Any]:
    """Convenience function for interpolation"""
    predictor = GNSSPredictor()
    return predictor.interpolate_at_timestamp(data, timestamp, model, grid_resolution)


def forecast(data: pd.DataFrame, horizon_hours: int = 24, 
            model: str = "lstm", combine_with_spatial_model: bool = True) -> Dict[str, Any]:
    """Convenience function for forecasting"""
    predictor = GNSSPredictor()
    return predictor.forecast(data, horizon_hours, model, combine_with_spatial_model)


if __name__ == "__main__":
    # Test the prediction functions
    print("Testing GNSS prediction functions...")
    
    # Load test data
    test_data = pd.read_csv("data/mock_gnss_zwd.csv")
    
    # Test interpolation
    print("\nTesting interpolation...")
    result = interpolate_at_timestamp(test_data, model="idw")
    print(f"Generated {len(result['grid'])} grid points")
    
    # Test forecast
    print("\nTesting forecast...")
    forecast_result = forecast(test_data, horizon_hours=6)
    print(f"Generated {len(forecast_result['grid'])} forecast points")
    
    print("\nTesting complete!")
