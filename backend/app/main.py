from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import os
from datetime import datetime
import json

from .models import *
from .api.interpolate import router as interpolate_router
from .api.validate import router as validate_router
from .api.station import router as station_router

app = FastAPI(
    title="GNSS Tropospheric PW Interpolator API",
    description="API for GNSS atmospheric water vapor interpolation and forecasting",
    version="1.0.0"
)

# Configure CORS for development and production
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001", 
    "http://frontend:3000",
    "https://gnss-frontend.onrender.com",  # Render frontend URL
    "https://*.onrender.com",  # Allow all Render subdomains
]

# Add environment-specific origins
if os.getenv("ENVIRONMENT") == "production":
    # Add your custom domain here if you have one
    frontend_url = os.getenv("FRONTEND_URL")
    if frontend_url:
        allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(interpolate_router, prefix="/api", tags=["interpolation"])
app.include_router(validate_router, prefix="/api", tags=["validation"])
app.include_router(station_router, prefix="/api", tags=["stations"])

# Create uploads directory
os.makedirs("uploads", exist_ok=True)


@app.get("/")
async def root():
    return {"message": "GNSS Tropospheric PW Interpolator API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}


@app.post("/api/upload-data", response_model=UploadResponse)
async def upload_data(file: UploadFile = File(...)):
    """Upload GNSS ZWD data CSV file"""
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
        # Save uploaded file
        file_path = f"uploads/{file.filename}"
        content = await file.read()
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Validate CSV structure
        df = pd.read_csv(file_path)
        required_columns = [
            'station_id', 'timestamp', 'latitude', 'longitude', 
            'elevation', 'azimuth', 'zenith_wet_delay'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {missing_columns}"
            )
        
        # Basic data validation
        if df.empty:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        
        # Generate metadata
        metadata = {
            "stations_count": df['station_id'].nunique(),
            "time_range": {
                "start": df['timestamp'].min(),
                "end": df['timestamp'].max()
            },
            "geographic_bounds": {
                "lat_min": float(df['latitude'].min()),
                "lat_max": float(df['latitude'].max()),
                "lon_min": float(df['longitude'].min()),
                "lon_max": float(df['longitude'].max())
            },
            "zwd_statistics": {
                "min": float(df['zenith_wet_delay'].min()),
                "max": float(df['zenith_wet_delay'].max()),
                "mean": float(df['zenith_wet_delay'].mean()),
                "std": float(df['zenith_wet_delay'].std())
            }
        }
        
        return UploadResponse(
            message="File uploaded successfully",
            filename=file.filename,
            records_count=len(df),
            metadata=metadata
        )
        
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="Invalid CSV file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
