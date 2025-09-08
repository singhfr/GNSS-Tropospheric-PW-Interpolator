import pandas as pd
import numpy as np
try:
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import RBF, WhiteKernel, ConstantKernel
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from typing import List, Dict, Any, Optional, Tuple
import joblib
import os
from datetime import datetime, timedelta

from ..models import GridPoint


class MLService:
    """Machine Learning service for GNSS PW interpolation and forecasting"""
    
    def __init__(self):
        self.gpr_model = None
        self.scaler_features = StandardScaler()
        self.scaler_target = StandardScaler()
        self.models_dir = "ml/models"
        os.makedirs(self.models_dir, exist_ok=True)
        
    def _preprocess_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Preprocess GNSS data for ML models"""
        # Convert ZWD to PW (simplified conversion)
        pw_conversion_factor = 6.2  # mm PW per 0.1m ZWD
        df = df.copy()
        df['pw'] = df['zenith_wet_delay'] * pw_conversion_factor * 10
        
        # Create features: lat, lon, elevation, azimuth
        features = df[['latitude', 'longitude', 'elevation', 'azimuth']].values
        targets = df['pw'].values
        
        return features, targets
    
    def _create_grid(self, bounds: Dict[str, float], resolution: float) -> np.ndarray:
        """Create interpolation grid"""
        lat_min, lat_max = bounds['lat_min'], bounds['lat_max']
        lon_min, lon_max = bounds['lon_min'], bounds['lon_max']
        
        lats = np.arange(lat_min, lat_max + resolution, resolution)
        lons = np.arange(lon_min, lon_max + resolution, resolution)
        
        lat_grid, lon_grid = np.meshgrid(lats, lons)
        
        # Create grid points with default elevation and azimuth
        grid_points = []
        for i in range(lat_grid.shape[0]):
            for j in range(lat_grid.shape[1]):
                grid_points.append([
                    lat_grid[i, j], 
                    lon_grid[i, j], 
                    100.0,  # default elevation
                    180.0   # default azimuth
                ])
        
        return np.array(grid_points)
    
    def _inverse_distance_weighting(self, grid_features: np.ndarray, features: np.ndarray, targets: np.ndarray) -> tuple:
        """Perform Inverse Distance Weighting interpolation"""
        predictions = []
        uncertainties = []
        
        for grid_point in grid_features:
            # Calculate distances to all stations
            distances = np.sqrt(
                (features[:, 0] - grid_point[0])**2 + 
                (features[:, 1] - grid_point[1])**2
            )
            
            # Avoid division by zero
            distances = np.maximum(distances, 1e-10)
            
            # IDW weights (power = 2)
            weights = 1 / (distances**2)
            weights = weights / weights.sum()
            
            # Weighted prediction
            pred = np.sum(weights * targets)
            predictions.append(pred)
            
            # Simple uncertainty estimate based on distance to nearest station
            min_distance = distances.min()
            uncertainty = min_distance * 2.0  # Simple heuristic
            uncertainties.append(uncertainty)
        
        return np.array(predictions), np.array(uncertainties)

    async def interpolate_pw(self, df: pd.DataFrame, model_type: str = "gpr", 
                           grid_resolution: float = 0.05) -> List[GridPoint]:
        """Interpolate PW values across a spatial grid"""
        try:
            # Preprocess data
            features, targets = self._preprocess_data(df)
            
            if len(features) == 0:
                raise ValueError("No valid data points for interpolation")
            
            # Calculate bounds
            bounds = {
                'lat_min': df['latitude'].min() - 0.5,
                'lat_max': df['latitude'].max() + 0.5,
                'lon_min': df['longitude'].min() - 0.5,
                'lon_max': df['longitude'].max() + 0.5
            }
            
            # Create interpolation grid
            grid_features = self._create_grid(bounds, grid_resolution)
            
            if model_type == "gpr" and SKLEARN_AVAILABLE:
                # Gaussian Process Regression
                try:
                    kernel = ConstantKernel(1.0, constant_value_bounds="fixed") * \
                            RBF(length_scale=1.0, length_scale_bounds=(0.1, 10.0)) + \
                            WhiteKernel(noise_level=0.1, noise_level_bounds=(1e-5, 1e+1))
                    
                    gpr = GaussianProcessRegressor(kernel=kernel, alpha=1e-6, 
                                                 normalize_y=True, random_state=42)
                    
                    # Fit model
                    gpr.fit(features, targets)
                    
                    # Predict on grid
                    predictions, uncertainties = gpr.predict(grid_features, return_std=True)
                except Exception as e:
                    print(f"GPR failed, falling back to IDW: {e}")
                    predictions, uncertainties = self._inverse_distance_weighting(grid_features, features, targets)
                
            else:
                # Default to IDW or fallback
                predictions, uncertainties = self._inverse_distance_weighting(grid_features, features, targets)
            
            # Convert to GridPoint objects
            grid_points = []
            for i, (grid_feat, pred, unc) in enumerate(zip(grid_features, predictions, uncertainties)):
                # Skip points with very high uncertainty or invalid predictions
                if np.isfinite(pred) and np.isfinite(unc) and pred > 0:
                    grid_points.append(GridPoint(
                        latitude=float(grid_feat[0]),
                        longitude=float(grid_feat[1]),
                        pw_value=float(pred),
                        uncertainty=float(unc)
                    ))
            
            return grid_points
            
        except Exception as e:
            print(f"Interpolation error: {e}")
            # Return empty grid on error
            return []
    
    async def forecast_pw(self, df: pd.DataFrame, horizon_hours: int = 24, 
                        model_type: str = "lstm", area_bounds: Optional[Dict] = None) -> List[GridPoint]:
        """Generate PW forecast using temporal models"""
        try:
            # For this MVP, we'll create a simple forecast by:
            # 1. Using latest data as baseline
            # 2. Adding temporal trend and uncertainty
            
            # Get latest timestamp data
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            latest_time = df['timestamp'].max()
            latest_data = df[df['timestamp'] == latest_time]
            
            if latest_data.empty:
                latest_data = df.iloc[-5:]  # Use last 5 records
            
            # Base interpolation on latest data
            base_grid = await self.interpolate_pw(latest_data, model_type="gpr", grid_resolution=0.1)
            
            # Apply forecast modifications
            forecast_grid = []
            for point in base_grid:
                # Simple forecast: add temporal trend and increase uncertainty
                trend_factor = 1.0 + 0.001 * horizon_hours  # Small positive trend
                noise_factor = 0.02 * horizon_hours  # Increasing uncertainty
                
                forecast_pw = point.pw_value * trend_factor + np.random.normal(0, noise_factor)
                forecast_uncertainty = point.uncertainty * (1.0 + 0.1 * horizon_hours)
                
                forecast_grid.append(GridPoint(
                    latitude=point.latitude,
                    longitude=point.longitude,
                    pw_value=max(0.0, float(forecast_pw)),  # Ensure positive
                    uncertainty=float(forecast_uncertainty)
                ))
            
            return forecast_grid
            
        except Exception as e:
            print(f"Forecast error: {e}")
            return []
    
    def train_models(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train and save ML models"""
        try:
            features, targets = self._preprocess_data(df)
            
            if len(features) < 10:
                raise ValueError("Insufficient data for training")
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                features, targets, test_size=0.2, random_state=42
            )
            
            # Train Gaussian Process Regressor
            kernel = ConstantKernel(1.0) * RBF(length_scale=1.0) + WhiteKernel(noise_level=0.1)
            gpr = GaussianProcessRegressor(kernel=kernel, alpha=1e-6, normalize_y=True, random_state=42)
            gpr.fit(X_train, y_train)
            
            # Evaluate
            train_score = gpr.score(X_train, y_train)
            test_score = gpr.score(X_test, y_test)
            
            # Save model
            model_path = os.path.join(self.models_dir, "gpr_model.pkl")
            joblib.dump(gpr, model_path)
            
            # Save training info
            training_info = {
                "model_type": "GaussianProcessRegressor",
                "train_score": float(train_score),
                "test_score": float(test_score),
                "training_samples": len(X_train),
                "test_samples": len(X_test),
                "trained_at": datetime.now().isoformat(),
                "model_path": model_path
            }
            
            return training_info
            
        except Exception as e:
            print(f"Training error: {e}")
            return {"error": str(e)}
    
    def load_model(self, model_path: str = None):
        """Load trained model"""
        if model_path is None:
            model_path = os.path.join(self.models_dir, "gpr_model.pkl")
        
        if os.path.exists(model_path):
            self.gpr_model = joblib.load(model_path)
            return True
        return False
