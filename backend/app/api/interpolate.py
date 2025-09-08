from fastapi import APIRouter, HTTPException
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any
import os

from ..models import InterpolationRequest, InterpolationResponse, GridPoint, ForecastRequest, ForecastResponse
from ..services.ml_service import MLService

router = APIRouter()
ml_service = MLService()


@router.post("/interpolate", response_model=InterpolationResponse)
async def interpolate_pw(request: InterpolationRequest):
    """Interpolate precipitable water from GNSS ZWD data"""
    try:
        # Load data from file or use provided data
        if request.data_path:
            file_path = f"uploads/{request.data_path}" if not request.data_path.startswith('/') else request.data_path
            if not os.path.exists(file_path):
                # Try default data path
                file_path = "../data/mock_gnss_zwd.csv"
                if not os.path.exists(file_path):
                    raise HTTPException(status_code=404, detail="Data file not found")
            
            df = pd.read_csv(file_path)
        elif request.stations_data:
            # Convert stations data to DataFrame
            data_list = []
            for station in request.stations_data:
                data_list.append({
                    'station_id': station.station_id,
                    'timestamp': station.timestamp,
                    'latitude': station.latitude,
                    'longitude': station.longitude,
                    'elevation': station.elevation,
                    'azimuth': station.azimuth,
                    'zenith_wet_delay': station.zenith_wet_delay,
                    'temperature': station.temperature,
                    'humidity': station.humidity,
                    'pressure': station.pressure
                })
            df = pd.DataFrame(data_list)
        else:
            # Use default mock data
            df = pd.read_csv("../data/mock_gnss_zwd.csv")
        
        # Filter by timestamp if provided
        if request.timestamp:
            target_time = pd.to_datetime(request.timestamp)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            # Find closest time within 1 hour
            time_diff = np.abs((df['timestamp'] - target_time).dt.total_seconds())
            df = df[time_diff <= 3600]  # Within 1 hour
            
            if df.empty:
                raise HTTPException(status_code=404, detail="No data found for the specified timestamp")
        
        # Perform interpolation
        grid_points = await ml_service.interpolate_pw(
            df, 
            model_type=request.model_type,
            grid_resolution=request.grid_resolution
        )
        
        # Calculate bounds
        lat_bounds = [df['latitude'].min() - 0.5, df['latitude'].max() + 0.5]
        lon_bounds = [df['longitude'].min() - 0.5, df['longitude'].max() + 0.5]
        
        metadata = {
            "grid_bounds": {
                "lat_min": lat_bounds[0],
                "lat_max": lat_bounds[1],
                "lon_min": lon_bounds[0],
                "lon_max": lon_bounds[1]
            },
            "grid_resolution": request.grid_resolution,
            "model_type": request.model_type,
            "stations_used": len(df['station_id'].unique()),
            "timestamp": request.timestamp or "latest"
        }
        
        return InterpolationResponse(grid=grid_points, metadata=metadata)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interpolation failed: {str(e)}")


@router.post("/forecast", response_model=ForecastResponse)
async def forecast_pw(request: ForecastRequest):
    """Generate PW forecast using temporal models"""
    try:
        # Load historical data
        df = pd.read_csv("../data/mock_gnss_zwd.csv")
        
        # Perform forecast
        grid_points = await ml_service.forecast_pw(
            df,
            horizon_hours=request.horizon_hours,
            model_type=request.model_type,
            area_bounds=request.area_bounds
        )
        
        # Calculate forecast time
        forecast_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Calculate bounds
        if request.area_bounds:
            bounds = request.area_bounds
        else:
            bounds = {
                "lat_min": df['latitude'].min() - 0.5,
                "lat_max": df['latitude'].max() + 0.5,
                "lon_min": df['longitude'].min() - 0.5,
                "lon_max": df['longitude'].max() + 0.5
            }
        
        metadata = {
            "grid_bounds": bounds,
            "forecast_horizon_hours": request.horizon_hours,
            "model_type": request.model_type,
            "generated_at": forecast_time,
            "confidence_level": 0.95
        }
        
        return ForecastResponse(
            grid=grid_points, 
            metadata=metadata,
            forecast_time=forecast_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast failed: {str(e)}")


@router.get("/demo-data")
async def load_demo_data():
    """Load demo data for initial visualization"""
    try:
        df = pd.read_csv("../data/mock_gnss_zwd.csv")
        
        # Get latest timestamp data
        latest_time = df['timestamp'].max()
        latest_data = df[df['timestamp'] == latest_time]
        
        # Perform interpolation on latest data
        grid_points = await ml_service.interpolate_pw(
            latest_data, 
            model_type="gpr",
            grid_resolution=0.05
        )
        
        metadata = {
            "grid_bounds": {
                "lat_min": float(df['latitude'].min() - 0.5),
                "lat_max": float(df['latitude'].max() + 0.5),
                "lon_min": float(df['longitude'].min() - 0.5),
                "lon_max": float(df['longitude'].max() + 0.5)
            },
            "grid_resolution": 0.05,
            "model_type": "gpr",
            "stations_used": len(latest_data['station_id'].unique()),
            "timestamp": latest_time
        }
        
        return InterpolationResponse(grid=grid_points, metadata=metadata)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load demo data: {str(e)}")
