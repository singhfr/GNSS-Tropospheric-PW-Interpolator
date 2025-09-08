from fastapi import APIRouter, HTTPException, UploadFile, File
import pandas as pd
import numpy as np
from typing import List, Dict, Any
from sklearn.metrics import mean_squared_error, mean_absolute_error

from ..models import ValidationRequest, ValidationResponse
from ..services.ml_service import MLService

router = APIRouter()
ml_service = MLService()


@router.post("/validate", response_model=ValidationResponse)
async def validate_predictions(request: ValidationRequest):
    """Validate model predictions against reference data"""
    try:
        # Convert validation data to DataFrame
        validation_df = pd.DataFrame(request.validation_data)
        
        # Load GNSS data for interpolation
        gnss_df = pd.read_csv("../data/mock_gnss_zwd.csv")
        
        comparison_samples = []
        predicted_values = []
        observed_values = []
        
        for _, val_row in validation_df.iterrows():
            try:
                # Find nearest GNSS stations and time
                val_time = pd.to_datetime(val_row['timestamp'])
                gnss_df['timestamp'] = pd.to_datetime(gnss_df['timestamp'])
                
                # Filter by time (within 1 hour)
                time_mask = np.abs((gnss_df['timestamp'] - val_time).dt.total_seconds()) <= 3600
                time_filtered = gnss_df[time_mask]
                
                if time_filtered.empty:
                    continue
                
                # Get prediction at validation point
                val_lat, val_lon = val_row['latitude'], val_row['longitude']
                
                # Simple interpolation for validation (could be improved)
                distances = np.sqrt(
                    (time_filtered['latitude'] - val_lat)**2 + 
                    (time_filtered['longitude'] - val_lon)**2
                )
                
                # Inverse distance weighting
                weights = 1 / (distances + 1e-10)
                weights = weights / weights.sum()
                
                # Convert ZWD to PW (simplified conversion factor)
                pw_conversion_factor = 6.2  # mm PW per 0.1m ZWD (approximate)
                predicted_pw = np.sum(weights * time_filtered['zenith_wet_delay'] * pw_conversion_factor * 10)
                
                observed_pw = val_row.get('pw_measurement', val_row.get('observed_wet_delay', 0) * pw_conversion_factor * 10)
                
                predicted_values.append(predicted_pw)
                observed_values.append(observed_pw)
                
                comparison_samples.append({
                    'station_id': val_row['station_id'],
                    'timestamp': val_row['timestamp'],
                    'latitude': val_lat,
                    'longitude': val_lon,
                    'predicted_pw': float(predicted_pw),
                    'observed_pw': float(observed_pw),
                    'error': float(abs(predicted_pw - observed_pw)),
                    'relative_error': float(abs(predicted_pw - observed_pw) / observed_pw * 100) if observed_pw > 0 else 0
                })
                
            except Exception as e:
                print(f"Error processing validation point: {e}")
                continue
        
        if not predicted_values:
            raise HTTPException(status_code=400, detail="No valid comparison points found")
        
        # Calculate metrics
        predicted_values = np.array(predicted_values)
        observed_values = np.array(observed_values)
        
        rmse = float(np.sqrt(mean_squared_error(observed_values, predicted_values)))
        mae = float(mean_absolute_error(observed_values, predicted_values))
        n = len(predicted_values)
        
        return ValidationResponse(
            rmse=rmse,
            mae=mae,
            n=n,
            comparison_samples=comparison_samples
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.post("/validate-file")
async def validate_from_file(file: UploadFile = File(...)):
    """Validate model predictions against uploaded reference data CSV"""
    try:
        # Read uploaded validation file
        content = await file.read()
        
        # Save temporarily and read as CSV
        temp_path = f"uploads/temp_validation_{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(content)
        
        validation_df = pd.read_csv(temp_path)
        
        # Convert to list of dictionaries for processing
        validation_data = validation_df.to_dict('records')
        
        # Clean up temp file
        import os
        os.remove(temp_path)
        
        # Use existing validation logic
        request = ValidationRequest(validation_data=validation_data)
        return await validate_predictions(request)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File validation failed: {str(e)}")
