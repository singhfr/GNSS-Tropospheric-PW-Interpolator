from fastapi import APIRouter, HTTPException
import pandas as pd
import numpy as np
from typing import Dict, Any

from ..models import StationTimeSeriesResponse

router = APIRouter()


@router.get("/station/{station_id}", response_model=StationTimeSeriesResponse)
async def get_station_data(station_id: str):
    """Get detailed time series data for a specific GNSS station"""
    try:
        # Load GNSS data
        df = pd.read_csv("../data/mock_gnss_zwd.csv")
        
        # Filter by station
        station_data = df[df['station_id'] == station_id]
        
        if station_data.empty:
            raise HTTPException(status_code=404, detail=f"Station {station_id} not found")
        
        # Get station location (use first record)
        first_record = station_data.iloc[0]
        location = {
            "latitude": float(first_record['latitude']),
            "longitude": float(first_record['longitude'])
        }
        elevation = float(first_record['elevation'])
        
        # Convert ZWD to PW for time series
        pw_conversion_factor = 6.2  # mm PW per 0.1m ZWD (approximate)
        station_data = station_data.copy()
        station_data['pw'] = station_data['zenith_wet_delay'] * pw_conversion_factor * 10
        
        # Sort by timestamp
        station_data = station_data.sort_values('timestamp')
        
        # Create time series data
        time_series = []
        for _, row in station_data.iterrows():
            time_series.append({
                'timestamp': row['timestamp'],
                'zenith_wet_delay': float(row['zenith_wet_delay']),
                'precipitable_water': float(row['pw']),
                'azimuth': float(row['azimuth']),
                'temperature': float(row.get('temperature', 0)) if pd.notna(row.get('temperature')) else None,
                'humidity': float(row.get('humidity', 0)) if pd.notna(row.get('humidity')) else None,
                'pressure': float(row.get('pressure', 0)) if pd.notna(row.get('pressure')) else None
            })
        
        # Calculate statistics
        zwd_values = station_data['zenith_wet_delay'].values
        pw_values = station_data['pw'].values
        
        statistics = {
            'zwd_min': float(zwd_values.min()),
            'zwd_max': float(zwd_values.max()),
            'zwd_mean': float(zwd_values.mean()),
            'zwd_std': float(zwd_values.std()),
            'pw_min': float(pw_values.min()),
            'pw_max': float(pw_values.max()),
            'pw_mean': float(pw_values.mean()),
            'pw_std': float(pw_values.std()),
            'data_points': len(station_data)
        }
        
        # Determine status (simplified)
        latest_time = pd.to_datetime(station_data['timestamp'].max())
        current_time = pd.Timestamp.now(tz='UTC')
        hours_since_last = (current_time - latest_time).total_seconds() / 3600
        
        status = "Active" if hours_since_last < 24 else "Inactive"
        
        return StationTimeSeriesResponse(
            station_id=station_id,
            location=location,
            elevation=elevation,
            status=status,
            time_series=time_series,
            statistics=statistics
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get station data: {str(e)}")


@router.get("/stations")
async def get_all_stations():
    """Get list of all available GNSS stations"""
    try:
        df = pd.read_csv("../data/mock_gnss_zwd.csv")
        
        stations = []
        for station_id in df['station_id'].unique():
            station_data = df[df['station_id'] == station_id]
            first_record = station_data.iloc[0]
            latest_record = station_data.iloc[-1]
            
            # Convert ZWD to PW
            pw_conversion_factor = 6.2
            current_pw = latest_record['zenith_wet_delay'] * pw_conversion_factor * 10
            
            stations.append({
                'station_id': station_id,
                'latitude': float(first_record['latitude']),
                'longitude': float(first_record['longitude']),
                'elevation': float(first_record['elevation']),
                'current_pw': float(current_pw),
                'last_update': latest_record['timestamp'],
                'data_points': len(station_data)
            })
        
        return {"stations": stations, "total_count": len(stations)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stations list: {str(e)}")
