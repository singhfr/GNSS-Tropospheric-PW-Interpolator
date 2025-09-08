from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class StationData(BaseModel):
    station_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    elevation: float
    azimuth: float
    zenith_wet_delay: float
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None


class InterpolationRequest(BaseModel):
    data_path: Optional[str] = None
    timestamp: Optional[str] = None
    stations_data: Optional[List[StationData]] = None
    grid_resolution: Optional[float] = 0.05
    model_type: Optional[str] = "gpr"


class GridPoint(BaseModel):
    latitude: float
    longitude: float
    pw_value: float
    uncertainty: float


class InterpolationResponse(BaseModel):
    grid: List[GridPoint]
    metadata: Dict[str, Any]


class ValidationRequest(BaseModel):
    validation_data: List[Dict[str, Any]]


class ValidationResponse(BaseModel):
    rmse: float
    mae: float
    n: int
    comparison_samples: List[Dict[str, Any]]


class ForecastRequest(BaseModel):
    horizon_hours: int
    area_bounds: Optional[Dict[str, float]] = None
    model_type: Optional[str] = "lstm"


class ForecastResponse(BaseModel):
    grid: List[GridPoint]
    metadata: Dict[str, Any]
    forecast_time: str


class StationTimeSeriesResponse(BaseModel):
    station_id: str
    location: Dict[str, float]
    elevation: float
    status: str
    time_series: List[Dict[str, Any]]
    statistics: Dict[str, float]


class UploadResponse(BaseModel):
    message: str
    filename: str
    records_count: int
    metadata: Dict[str, Any]
