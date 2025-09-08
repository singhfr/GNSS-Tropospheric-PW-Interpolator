# 📁 Demo Files for GNSS Dashboard

This directory contains sample data files for demonstrating all features of the GNSS Tropospheric PW Interpolator.

## 📊 Available Demo Files

### 1. **demo_gnss_upload.csv** - GNSS ZWD Data
- **Purpose**: Demonstrate data upload functionality
- **Format**: CSV with GNSS Zenith Wet Delay measurements
- **Stations**: 4 demo stations (DEMO001-DEMO004)
- **Time Range**: 6 hours (2024-01-02 00:00-05:00 UTC)
- **Location**: Northeastern US region

**Columns**:
- `station_id` - Unique station identifier
- `timestamp` - ISO 8601 timestamp
- `latitude` - Station latitude (decimal degrees)
- `longitude` - Station longitude (decimal degrees)
- `elevation` - Station elevation (meters)
- `azimuth` - Satellite azimuth angle (degrees)
- `zenith_wet_delay` - Zenith wet delay measurement (meters)
- `temperature` - Air temperature (°C)
- `humidity` - Relative humidity (%)
- `pressure` - Atmospheric pressure (hPa)

### 2. **demo_validation_data.csv** - Validation Reference Data
- **Purpose**: Demonstrate error validation functionality
- **Format**: CSV with reference wet delay measurements
- **Stations**: Same 4 demo stations
- **Time Range**: Same 6-hour period
- **Use**: Compare against GNSS-derived values

**Columns**:
- `timestamp` - ISO 8601 timestamp
- `station_id` - Station identifier
- `latitude` - Station latitude
- `longitude` - Station longitude
- `wet_delay_mm` - Reference wet delay (millimeters)

### 3. **demo_radiosonde_data.csv** - Radiosonde Reference Data
- **Purpose**: Demonstrate validation with radiosonde data
- **Format**: CSV with radiosonde-derived wet delay
- **Stations**: 3 radiosonde stations (RADIO001-RADIO003)
- **Time Range**: Same 6-hour period
- **Source**: Simulated radiosonde measurements

**Columns**:
- `timestamp` - ISO 8601 timestamp
- `station_id` - Radiosonde station ID
- `latitude` - Station latitude
- `longitude` - Station longitude
- `wet_delay_mm` - Radiosonde wet delay (millimeters)
- `data_source` - Data source identifier

## 🎥 Demo Video Usage

### Upload Data Demo:
1. Navigate to "Upload Data" tab
2. Upload `demo_gnss_upload.csv` as GNSS ZWD data
3. Upload `demo_validation_data.csv` as validation data
4. Show successful processing and record counts

### Error Validation Demo:
1. Navigate to "Error Validation" tab
2. Upload `demo_validation_data.csv` or `demo_radiosonde_data.csv`
3. Show validation results with RMSE/MAE metrics
4. Demonstrate station-by-station error analysis

### Expected Results:
- **RMSE**: ~0.5-1.5 mm (realistic validation error)
- **MAE**: ~0.3-1.2 mm (mean absolute error)
- **Correlation**: >0.95 (high correlation)
- **Station Count**: 4 stations processed

## 📋 Data Quality Notes

### Realistic Data Characteristics:
- **Temporal Variation**: Natural diurnal patterns
- **Spatial Variation**: Geographic differences across stations
- **Measurement Noise**: Realistic sensor noise levels
- **Atmospheric Conditions**: Representative winter conditions

### Validation Accuracy:
- **Small Errors**: Validation data has small, realistic differences
- **Bias Patterns**: Some stations show slight systematic bias
- **Random Noise**: Natural measurement uncertainty included

## 🚀 Quick Start

1. **Copy files to accessible location**:
   ```bash
   cp demo_files/*.csv ~/Downloads/
   ```

2. **Start demo preparation**:
   ```bash
   python demo_automation_script.py
   ```

3. **Follow demo script**:
   - Open `demo_script.md`
   - Follow scene-by-scene instructions
   - Use files in order specified

## 🔧 Customization

### Creating Your Own Demo Data:
1. **Follow the CSV format** exactly as shown
2. **Use realistic coordinates** for your region
3. **Maintain temporal consistency** in timestamps
4. **Include measurement noise** for realism
5. **Test upload functionality** before recording

### Data Validation:
- Ensure all timestamps are in ISO 8601 format
- Verify latitude/longitude are in decimal degrees
- Check that wet delay values are reasonable (0-50mm typical)
- Validate station IDs are consistent across files

---

**Note**: These demo files are designed for demonstration purposes only and contain simulated data based on realistic atmospheric conditions.

