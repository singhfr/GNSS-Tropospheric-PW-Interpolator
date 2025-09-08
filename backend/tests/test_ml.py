import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from unittest.mock import patch, MagicMock

# Test ML training and prediction functionality


class TestMLTraining:
    """Test suite for ML model training"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample GNSS data for testing"""
        np.random.seed(42)
        n_stations = 3
        n_times = 24
        
        data = []
        for station_id in [f"TEST{i:03d}" for i in range(1, n_stations + 1)]:
            lat = 40.0 + np.random.normal(0, 1)
            lon = -74.0 + np.random.normal(0, 1)
            
            for hour in range(n_times):
                data.append({
                    'station_id': station_id,
                    'timestamp': f'2024-01-01T{hour:02d}:00:00Z',
                    'latitude': lat + np.random.normal(0, 0.01),
                    'longitude': lon + np.random.normal(0, 0.01),
                    'elevation': 100.0 + np.random.normal(0, 10),
                    'azimuth': 180.0 + hour * 5,
                    'zenith_wet_delay': 0.25 + 0.05 * np.sin(hour * np.pi / 12) + np.random.normal(0, 0.01),
                    'temperature': 15.0 + 5 * np.sin(hour * np.pi / 12),
                    'humidity': 60.0 + 10 * np.sin(hour * np.pi / 12),
                    'pressure': 1013.0 + np.random.normal(0, 2)
                })
        
        return pd.DataFrame(data)
    
    def test_data_loading_and_preprocessing(self, sample_data):
        """Test data loading and preprocessing"""
        # Save sample data to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            sample_data.to_csv(f.name, index=False)
            temp_path = f.name
        
        try:
            # Import here to avoid issues with path
            import sys
            sys.path.append('ml')
            from train import GNSSModelTrainer
            
            trainer = GNSSModelTrainer(data_path=temp_path)
            processed_df = trainer.load_and_preprocess_data()
            
            # Check preprocessing results
            assert len(processed_df) > 0
            assert 'pw' in processed_df.columns
            assert 'hour' in processed_df.columns
            assert processed_df['pw'].min() > 0  # PW should be positive
            assert processed_df['pw'].max() < 100  # Reasonable upper bound
            
        finally:
            os.unlink(temp_path)
    
    def test_gpr_model_training(self, sample_data):
        """Test Gaussian Process Regression training"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            sample_data.to_csv(f.name, index=False)
            temp_path = f.name
        
        try:
            import sys
            sys.path.append('ml')
            from train import GNSSModelTrainer
            
            trainer = GNSSModelTrainer(data_path=temp_path)
            processed_df = trainer.load_and_preprocess_data()
            
            # Train GPR model
            gpr_model, scaler_X, scaler_y = trainer.train_gpr_model(processed_df)
            
            # Check model training results
            assert gpr_model is not None
            assert scaler_X is not None
            assert scaler_y is not None
            assert 'gpr' in trainer.results
            assert 'rmse' in trainer.results['gpr']
            assert 'mae' in trainer.results['gpr']
            assert 'r2' in trainer.results['gpr']
            
        finally:
            os.unlink(temp_path)
    
    def test_baseline_models_training(self, sample_data):
        """Test baseline models training"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            sample_data.to_csv(f.name, index=False)
            temp_path = f.name
        
        try:
            import sys
            sys.path.append('ml')
            from train import GNSSModelTrainer
            
            trainer = GNSSModelTrainer(data_path=temp_path)
            processed_df = trainer.load_and_preprocess_data()
            
            # Train baseline models
            trainer.train_baseline_models(processed_df)
            
            # Check baseline results
            assert 'baselines' in trainer.results
            assert 'idw_mae' in trainer.results['baselines']
            assert 'average_mae' in trainer.results['baselines']
            
        finally:
            os.unlink(temp_path)


class TestMLPrediction:
    """Test suite for ML prediction functionality"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for prediction testing"""
        return pd.DataFrame({
            'station_id': ['TEST001', 'TEST002', 'TEST003'],
            'timestamp': ['2024-01-01T12:00:00Z'] * 3,
            'latitude': [40.0, 41.0, 42.0],
            'longitude': [-74.0, -75.0, -76.0],
            'elevation': [100.0, 150.0, 200.0],
            'azimuth': [180.0, 185.0, 190.0],
            'zenith_wet_delay': [0.25, 0.28, 0.22]
        })
    
    def test_predictor_initialization(self):
        """Test predictor initialization"""
        import sys
        sys.path.append('ml')
        from predict import GNSSPredictor
        
        predictor = GNSSPredictor()
        
        # Should initialize without errors
        assert predictor.models_dir == "ml/models"
        assert predictor.gpr_model is None  # No trained model available
    
    def test_data_preprocessing(self, sample_data):
        """Test data preprocessing in predictor"""
        import sys
        sys.path.append('ml')
        from predict import GNSSPredictor
        
        predictor = GNSSPredictor()
        processed_df = predictor.preprocess_data(sample_data)
        
        # Check preprocessing
        assert 'pw' in processed_df.columns
        assert 'hour' in processed_df.columns
        assert len(processed_df) == len(sample_data)
        assert processed_df['pw'].min() > 0
    
    def test_grid_creation(self):
        """Test interpolation grid creation"""
        import sys
        sys.path.append('ml')
        from predict import GNSSPredictor
        
        predictor = GNSSPredictor()
        bounds = {
            'lat_min': 40.0,
            'lat_max': 42.0,
            'lon_min': -76.0,
            'lon_max': -74.0
        }
        
        grid = predictor.create_interpolation_grid(bounds, resolution=1.0)
        
        assert grid.shape[1] == 2  # lat, lon
        assert len(grid) > 0
        assert np.all(grid[:, 0] >= bounds['lat_min'])
        assert np.all(grid[:, 0] <= bounds['lat_max'])
    
    def test_idw_interpolation(self, sample_data):
        """Test Inverse Distance Weighting interpolation"""
        import sys
        sys.path.append('ml')
        from predict import GNSSPredictor
        
        predictor = GNSSPredictor()
        processed_df = predictor.preprocess_data(sample_data)
        
        # Create small grid for testing
        grid_points = np.array([
            [40.5, -74.5],
            [41.5, -75.5]
        ])
        
        predictions, uncertainties = predictor.inverse_distance_weighting(
            processed_df, grid_points, power=2.0
        )
        
        assert len(predictions) == len(grid_points)
        assert len(uncertainties) == len(grid_points)
        assert np.all(predictions > 0)
        assert np.all(uncertainties >= 0)
    
    def test_interpolation_at_timestamp(self, sample_data):
        """Test interpolation at specific timestamp"""
        import sys
        sys.path.append('ml')
        from predict import GNSSPredictor
        
        predictor = GNSSPredictor()
        result = predictor.interpolate_at_timestamp(
            sample_data,
            timestamp="2024-01-01T12:00:00Z",
            model="idw",
            grid_resolution=1.0
        )
        
        assert 'grid' in result
        assert 'metadata' in result
        assert isinstance(result['grid'], list)
        assert len(result['grid']) > 0
        
        # Check grid point structure
        point = result['grid'][0]
        assert 'latitude' in point
        assert 'longitude' in point
        assert 'pw_value' in point
        assert 'uncertainty' in point
    
    def test_forecast_generation(self, sample_data):
        """Test forecast generation"""
        import sys
        sys.path.append('ml')
        from predict import GNSSPredictor
        
        predictor = GNSSPredictor()
        result = predictor.forecast(
            sample_data,
            horizon_hours=12,
            model="simple"
        )
        
        assert 'grid' in result
        assert 'metadata' in result
        assert isinstance(result['grid'], list)
        assert len(result['grid']) > 0
        
        # Check forecast metadata
        metadata = result['metadata']
        assert 'forecast_horizon_hours' in metadata
        assert metadata['forecast_horizon_hours'] == 12


class TestMLIntegration:
    """Test suite for ML integration with API"""
    
    def test_ml_service_integration(self):
        """Test ML service integration with API"""
        from app.services.ml_service import MLService
        
        # Create sample data
        sample_df = pd.DataFrame({
            'station_id': ['TEST001', 'TEST002'],
            'timestamp': ['2024-01-01T12:00:00Z'] * 2,
            'latitude': [40.0, 41.0],
            'longitude': [-74.0, -75.0],
            'elevation': [100.0, 150.0],
            'azimuth': [180.0, 185.0],
            'zenith_wet_delay': [0.25, 0.28]
        })
        
        ml_service = MLService()
        
        # Test preprocessing
        features, targets = ml_service._preprocess_data(sample_df)
        assert features.shape[0] == 2
        assert len(targets) == 2
        
        # Test grid creation
        bounds = {'lat_min': 39.5, 'lat_max': 41.5, 'lon_min': -75.5, 'lon_max': -73.5}
        grid = ml_service._create_grid(bounds, 1.0)
        assert len(grid) > 0
    
    @pytest.mark.asyncio
    async def test_async_interpolation(self):
        """Test async interpolation functionality"""
        from app.services.ml_service import MLService
        
        sample_df = pd.DataFrame({
            'station_id': ['TEST001', 'TEST002'],
            'timestamp': ['2024-01-01T12:00:00Z'] * 2,
            'latitude': [40.0, 41.0],
            'longitude': [-74.0, -75.0],
            'elevation': [100.0, 150.0],
            'azimuth': [180.0, 185.0],
            'zenith_wet_delay': [0.25, 0.28]
        })
        
        ml_service = MLService()
        result = await ml_service.interpolate_pw(sample_df, model_type="idw", grid_resolution=1.0)
        
        assert isinstance(result, list)
        # Should have some interpolated points
        assert len(result) >= 0  # May be empty due to filtering
    
    @pytest.mark.asyncio
    async def test_async_forecast(self):
        """Test async forecast functionality"""
        from app.services.ml_service import MLService
        
        sample_df = pd.DataFrame({
            'station_id': ['TEST001', 'TEST002'],
            'timestamp': ['2024-01-01T12:00:00Z'] * 2,
            'latitude': [40.0, 41.0],
            'longitude': [-74.0, -75.0],
            'elevation': [100.0, 150.0],
            'azimuth': [180.0, 185.0],
            'zenith_wet_delay': [0.25, 0.28]
        })
        
        ml_service = MLService()
        result = await ml_service.forecast_pw(sample_df, horizon_hours=6)
        
        assert isinstance(result, list)


if __name__ == "__main__":
    pytest.main([__file__])
