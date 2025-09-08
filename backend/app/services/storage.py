import os
import pandas as pd
from typing import Optional, Dict, Any
import aiofiles
from datetime import datetime


class StorageService:
    """Service for handling file uploads and data storage"""
    
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)
    
    async def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """Save uploaded file and return path"""
        file_path = os.path.join(self.upload_dir, filename)
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        return file_path
    
    def validate_csv_structure(self, file_path: str, required_columns: list) -> Dict[str, Any]:
        """Validate CSV file structure and return metadata"""
        try:
            df = pd.read_csv(file_path)
            
            # Check required columns
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Generate metadata
            metadata = {
                "rows": len(df),
                "columns": list(df.columns),
                "missing_columns": missing_columns,
                "file_size_mb": os.path.getsize(file_path) / (1024 * 1024),
                "validated_at": datetime.now().isoformat()
            }
            
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                metadata["time_range"] = {
                    "start": df['timestamp'].min().isoformat(),
                    "end": df['timestamp'].max().isoformat()
                }
            
            if 'latitude' in df.columns and 'longitude' in df.columns:
                metadata["geographic_bounds"] = {
                    "lat_min": float(df['latitude'].min()),
                    "lat_max": float(df['latitude'].max()),
                    "lon_min": float(df['longitude'].min()),
                    "lon_max": float(df['longitude'].max())
                }
            
            return metadata
            
        except Exception as e:
            raise ValueError(f"CSV validation failed: {str(e)}")
    
    def list_uploaded_files(self) -> list:
        """List all uploaded files with metadata"""
        files = []
        
        for filename in os.listdir(self.upload_dir):
            if filename.endswith('.csv'):
                file_path = os.path.join(self.upload_dir, filename)
                stat = os.stat(file_path)
                
                files.append({
                    "filename": filename,
                    "size_mb": stat.st_size / (1024 * 1024),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "path": file_path
                })
        
        return sorted(files, key=lambda x: x['modified'], reverse=True)
    
    def delete_file(self, filename: str) -> bool:
        """Delete uploaded file"""
        file_path = os.path.join(self.upload_dir, filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
