import pytest
import pandas as pd
import numpy as np
from fastapi.testclient import TestClient
import tempfile
import os

from app.main import app

client = TestClient(app)


class TestAPI:
    """Test suite for FastAPI endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns correct information"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_stations_endpoint(self):
        """Test stations listing endpoint"""
        response = client.get("/api/stations")
        assert response.status_code == 200
        data = response.json()
        assert "stations" in data
        assert "total_count" in data
        assert isinstance(data["stations"], list)
    
    def test_station_detail_endpoint(self):
        """Test individual station data endpoint"""
        response = client.get("/api/station/GNSS001")
        assert response.status_code == 200
        data = response.json()
        assert data["station_id"] == "GNSS001"
        assert "location" in data
        assert "time_series" in data
        assert "statistics" in data
    
    def test_station_not_found(self):
        """Test station endpoint with non-existent station"""
        response = client.get("/api/station/NONEXISTENT")
        assert response.status_code == 404
    
    def test_interpolate_endpoint(self):
        """Test interpolation endpoint"""
        payload = {
            "model_type": "idw",
            "grid_resolution": 0.1
        }
        response = client.post("/api/interpolate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "grid" in data
        assert "metadata" in data
        assert isinstance(data["grid"], list)
    
    def test_demo_data_endpoint(self):
        """Test demo data loading endpoint"""
        response = client.get("/api/demo-data")
        assert response.status_code == 200
        data = response.json()
        assert "grid" in data
        assert "metadata" in data
        assert len(data["grid"]) > 0
    
    def test_forecast_endpoint(self):
        """Test forecast generation endpoint"""
        payload = {
            "horizon_hours": 12,
            "model_type": "simple"
        }
        response = client.post("/api/forecast", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "grid" in data
        assert "metadata" in data
        assert "forecast_time" in data
    
    def test_validate_endpoint_with_data(self):
        """Test validation endpoint with sample data"""
        validation_data = [
            {
                "station_id": "VAL001",
                "timestamp": "2024-01-01T12:00:00Z",
                "latitude": 40.7000,
                "longitude": -74.0100,
                "pw_measurement": 24.1
            }
        ]
        payload = {"validation_data": validation_data}
        response = client.post("/api/validate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "rmse" in data
        assert "mae" in data
        assert "n" in data
        assert "comparison_samples" in data
    
    def test_upload_data_endpoint(self):
        """Test data upload endpoint"""
        # Create a temporary CSV file
        csv_content = """station_id,timestamp,latitude,longitude,elevation,azimuth,zenith_wet_delay
TEST001,2024-01-01T00:00:00Z,40.0,-74.0,100.0,180.0,0.250
TEST001,2024-01-01T01:00:00Z,40.0,-74.0,100.0,185.0,0.255"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                response = client.post(
                    "/api/upload-data",
                    files={"file": ("test.csv", f, "text/csv")}
                )
            
            assert response.status_code == 200
            data = response.json()
            assert data["filename"] == "test.csv"
            assert data["records_count"] == 2
            assert "metadata" in data
            
        finally:
            os.unlink(temp_path)
    
    def test_upload_invalid_file(self):
        """Test upload endpoint with invalid file"""
        response = client.post(
            "/api/upload-data",
            files={"file": ("test.txt", b"invalid content", "text/plain")}
        )
        assert response.status_code == 400
    
    def test_interpolate_with_timestamp(self):
        """Test interpolation with specific timestamp"""
        payload = {
            "timestamp": "2024-01-01T12:00:00Z",
            "model_type": "idw",
            "grid_resolution": 0.2
        }
        response = client.post("/api/interpolate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["timestamp"] == "2024-01-01T12:00:00Z"
    
    def test_forecast_with_bounds(self):
        """Test forecast with area bounds"""
        payload = {
            "horizon_hours": 6,
            "area_bounds": {
                "lat_min": 30.0,
                "lat_max": 45.0,
                "lon_min": -120.0,
                "lon_max": -70.0
            }
        }
        response = client.post("/api/forecast", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["forecast_horizon_hours"] == 6


@pytest.fixture
def sample_gnss_data():
    """Fixture providing sample GNSS data for testing"""
    return pd.DataFrame({
        'station_id': ['TEST001', 'TEST002', 'TEST003'] * 10,
        'timestamp': pd.date_range('2024-01-01', periods=30, freq='H'),
        'latitude': [40.0, 41.0, 42.0] * 10,
        'longitude': [-74.0, -75.0, -76.0] * 10,
        'elevation': [100.0, 150.0, 200.0] * 10,
        'azimuth': [180.0, 185.0, 190.0] * 10,
        'zenith_wet_delay': np.random.normal(0.25, 0.05, 30)
    })


class TestMLService:
    """Test suite for ML service functionality"""
    
    def test_data_preprocessing(self, sample_gnss_data):
        """Test data preprocessing pipeline"""
        from app.services.ml_service import MLService
        
        ml_service = MLService()
        features, targets = ml_service._preprocess_data(sample_gnss_data)
        
        assert features.shape[0] == len(sample_gnss_data)
        assert features.shape[1] == 4  # lat, lon, elevation, azimuth
        assert len(targets) == len(sample_gnss_data)
        assert np.all(targets > 0)  # PW should be positive
    
    def test_grid_creation(self):
        """Test interpolation grid creation"""
        from app.services.ml_service import MLService
        
        ml_service = MLService()
        bounds = {
            'lat_min': 40.0,
            'lat_max': 42.0,
            'lon_min': -76.0,
            'lon_max': -74.0
        }
        
        grid = ml_service._create_grid(bounds, resolution=0.5)
        
        assert grid.shape[1] == 4  # lat, lon, elevation, azimuth
        assert np.all(grid[:, 0] >= bounds['lat_min'])
        assert np.all(grid[:, 0] <= bounds['lat_max'])
        assert np.all(grid[:, 1] >= bounds['lon_min'])
        assert np.all(grid[:, 1] <= bounds['lon_max'])
    
    @pytest.mark.asyncio
    async def test_interpolation_idw(self, sample_gnss_data):
        """Test IDW interpolation"""
        from app.services.ml_service import MLService
        
        ml_service = MLService()
        result = await ml_service.interpolate_pw(
            sample_gnss_data.head(10), 
            model_type="idw", 
            grid_resolution=0.5
        )
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Check first result
        point = result[0]
        assert hasattr(point, 'latitude')
        assert hasattr(point, 'longitude')
        assert hasattr(point, 'pw_value')
        assert hasattr(point, 'uncertainty')
        assert point.pw_value > 0
        assert point.uncertainty >= 0
    
    @pytest.mark.asyncio
    async def test_forecast_generation(self, sample_gnss_data):
        """Test forecast generation"""
        from app.services.ml_service import MLService
        
        ml_service = MLService()
        result = await ml_service.forecast_pw(
            sample_gnss_data, 
            horizon_hours=12
        )
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Check forecast properties
        point = result[0]
        assert hasattr(point, 'pw_value')
        assert hasattr(point, 'uncertainty')
        assert point.pw_value > 0


class TestDataValidation:
    """Test suite for data validation functionality"""
    
    def test_csv_validation_success(self):
        """Test successful CSV validation"""
        from app.services.storage import StorageService
        
        # Create valid CSV
        csv_content = """station_id,timestamp,latitude,longitude,elevation,azimuth,zenith_wet_delay
TEST001,2024-01-01T00:00:00Z,40.0,-74.0,100.0,180.0,0.250"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            storage = StorageService()
            required_cols = ['station_id', 'timestamp', 'latitude', 'longitude', 
                           'elevation', 'azimuth', 'zenith_wet_delay']
            
            metadata = storage.validate_csv_structure(temp_path, required_cols)
            
            assert metadata['rows'] == 1
            assert len(metadata['missing_columns']) == 0
            assert 'time_range' in metadata
            assert 'geographic_bounds' in metadata
            
        finally:
            os.unlink(temp_path)
    
    def test_csv_validation_missing_columns(self):
        """Test CSV validation with missing columns"""
        from app.services.storage import StorageService
        
        # Create CSV with missing columns
        csv_content = """station_id,timestamp,latitude,longitude
TEST001,2024-01-01T00:00:00Z,40.0,-74.0"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            storage = StorageService()
            required_cols = ['station_id', 'timestamp', 'latitude', 'longitude', 
                           'elevation', 'azimuth', 'zenith_wet_delay']
            
            with pytest.raises(ValueError) as exc_info:
                storage.validate_csv_structure(temp_path, required_cols)
            
            assert "Missing required columns" in str(exc_info.value)
            
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__])
