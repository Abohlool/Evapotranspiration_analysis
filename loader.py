"""Data loading, cleaning, and preprocessing module."""

import pandas as pd
import numpy as np

def extract_number(value):
    """Extract numeric value from string with units."""
    if pd.isna(value) or value == '--' or value == '':
        return np.nan
    
    if isinstance(value, (int, float)):
        return float(value)
    
    value_str = str(value).strip()
    # Remove common units
    for unit in ['W/m2', '°C', '%', 'km/h', 'kPa', 'mm', 'W/m²']:
        value_str = value_str.replace(unit, '')
    value_str = value_str.strip()
    
    try:
        return float(value_str)
    except ValueError:
        return np.nan


def detect_columns(df):
    """Detect and map column names to standard English names."""
    # Priority-ordered patterns (first match wins)
    column_patterns = [
        # Time column - check for exact matches first
        (['زمان', 'time', 'time_rounded', 'datetime', 'date', 'date_time'], 'time'),
        
        # Temperature
        (['دما', 'temp', 'temperature', 'T', 'دمای'], 'temp_C'),
        
        # Humidity
        (['رطوبت', 'humidity', 'RH', 'رطوبت نسبی'], 'humidity_pct'),
        
        # Pressure
        (['فشار هوا', 'فشار', 'pressure', 'P', 'kPa', 'فشار اتمسفر'], 'pressure_kPa'),
        
        # Solar radiation
        (['تابش خورشیدی', 'تابش', 'solar', 'radiation', 'Rs', 'تشعشع'], 'solar_Wm2'),
        
        # Wind speed
        (['سرعت باد', 'wind_speed', 'wind', 'u', 'سرعت'], 'wind_kmh'),
        
        # Wind direction
        (['جهت باد', 'wind_dir', 'direction', 'جهت'], 'wind_dir'),
        
        # Rainfall
        (['باران', 'rain', 'rainfall', 'precipitation', 'بارش'], 'rain_mm'),
        
        # Greenhouse
        (['گلخانه', 'greenhouse'], 'greenhouse'),
        
        # Device
        (['دستگاه', 'device'], 'device'),
    ]
    
    col_map = {}
    mapped_cols = set()  # Track which source columns are already mapped
    
    # First pass: exact matches
    for patterns, eng_name in column_patterns:
        for col in df.columns:
            if col in mapped_cols:
                continue
            if col in patterns:
                col_map[col] = eng_name
                mapped_cols.add(col)
                break
    
    # Second pass: partial matches for remaining columns
    for patterns, eng_name in column_patterns:
        if any(eng_name == v for v in col_map.values()):
            continue  # Already found this type
        for col in df.columns:
            if col in mapped_cols:
                continue
            # Check if column name contains any of the patterns (but not as substring of already mapped)
            for pattern in patterns:
                if pattern.lower() in col.lower():
                    col_map[col] = eng_name
                    mapped_cols.add(col)
                    break
            if col in mapped_cols:
                break
    
    return col_map


def parse_datetime_from_string(time_str):
    """Parse datetime from string - handles multiple formats."""
    if pd.isna(time_str) or str(time_str).strip() == '':
        return None
    
    time_str = str(time_str).strip().strip('"')
    
    # Try common datetime formats
    formats = [
        '%Y-%m-%d %H:%M:%S',    # 2025-12-03 00:00:00
        '%Y-%m-%d %H:%M',       # 2025-12-03 00:00
        '%Y/%m/%d %H:%M:%S',    # 2025/12/03 00:00:00
        '%Y/%m/%d %H:%M',       # 2025/12/03 00:00
    ]
    
    for fmt in formats:
        try:
            return pd.to_datetime(time_str, format=fmt)
        except:
            continue
    
    # If no format works, try pandas default parser
    try:
        return pd.to_datetime(time_str)
    except:
        return None


def load_and_clean(csv_path):
    """Load weather CSV and return cleaned DataFrame."""
    print("=" * 70)
    print("LOADING AND CLEANING DATA")
    print("=" * 70)
    
    # Read the CSV
    df = pd.read_csv(csv_path, encoding='utf-8')
    print(f"Raw data shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Show sample of first column (time)
    first_col = df.columns[0]
    print(f"\nFirst column name: '{first_col}'")
    print(f"Sample values from first column:")
    for val in df[first_col].head(5):
        print(f"  '{val}'")
    
    # Detect column mapping
    col_map = detect_columns(df)
    print(f"\nDetected column mapping: {col_map}")
    
    # Rename columns
    df = df.rename(columns=col_map)
    print(f"Renamed columns: {df.columns.tolist()}")
    
    # Check for required columns
    required_cols = ['time', 'temp_C', 'humidity_pct']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        print(f"\nERROR: Missing required columns: {missing}")
        print(f"Available columns: {df.columns.tolist()}")
        raise ValueError(f"Missing required columns: {missing}")
    
    # Parse datetime directly from the time column
    # Since your format has full datetime: "2025-12-03 00:00:00"
    print("\nParsing datetime from time column...")
    df['datetime'] = df['time'].apply(parse_datetime_from_string)
    
    # Check parsing success
    n_parsed = df['datetime'].notna().sum()
    print(f"Successfully parsed {n_parsed}/{len(df)} datetimes")
    
    if n_parsed == 0:
        print("\nWARNING: Could not parse any datetimes!")
        print("Sample values that failed:")
        for val in df['time'].head(5):
            print(f"  '{val}'")
        raise ValueError("Could not parse datetime from time column")
    
    # Drop rows where datetime parsing failed
    df = df.dropna(subset=['datetime']).reset_index(drop=True)
    
    # Parse numeric columns
    numeric_cols = ['solar_Wm2', 'temp_C', 'humidity_pct', 'wind_kmh', 
                    'pressure_kPa', 'rain_mm', 'wind_dir']
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].apply(extract_number)
    
    # Fill missing values with sensible defaults
    if 'solar_Wm2' in df.columns:
        df['solar_Wm2'] = df['solar_Wm2'].fillna(0)
    else:
        df['solar_Wm2'] = 0
        print("WARNING: No solar radiation column, using 0")
    
    if 'wind_kmh' in df.columns:
        df['wind_kmh'] = df['wind_kmh'].fillna(0)
    else:
        df['wind_kmh'] = 0
        print("WARNING: No wind speed column, using 0")
    
    if 'rain_mm' in df.columns:
        df['rain_mm'] = df['rain_mm'].fillna(0)
    else:
        df['rain_mm'] = 0
    
    # Drop rows missing critical data (temperature, humidity)
    before_drop = len(df)
    df = df.dropna(subset=['temp_C', 'humidity_pct'])
    print(f"Records after removing missing T/RH: {len(df)} (dropped {before_drop - len(df)})")
    
    # Handle pressure - estimate from elevation if missing
    if 'pressure_kPa' not in df.columns or df['pressure_kPa'].isna().all():
        P0 = 101.325  # kPa at sea level
        elevation = 1500  # m (Torbat-e Heydarieh)
        df['pressure_kPa'] = P0 * ((293 - 0.0065 * elevation) / 293) ** 5.26
        print(f"WARNING: Estimating pressure from elevation ({elevation}m): {df['pressure_kPa'].iloc[0]:.1f} kPa")
    else:
        df['pressure_kPa'] = df['pressure_kPa'].ffill().bfill()
    # Convert pressure if needed (if values are in Pa or hPa instead of kPa)
    if df['pressure_kPa'].max() > 200:
        print("Converting pressure from Pa/hPa to kPa...")
        if df['pressure_kPa'].max() > 10000:
            df['pressure_kPa'] = df['pressure_kPa'] / 1000  # Pa to kPa
        elif df['pressure_kPa'].max() > 500:
            df['pressure_kPa'] = df['pressure_kPa'] / 10  # hPa to kPa
    
    # Sort by datetime
    df = df.sort_values('datetime').reset_index(drop=True)
    
    # Add time-related columns
    df['day_of_year'] = df['datetime'].dt.dayofyear
    df['date'] = df['datetime'].dt.date
    df['hour'] = df['datetime'].dt.hour
    df['month'] = df['datetime'].dt.month
    df['year'] = df['datetime'].dt.year
    
    # Add time_clean for compatibility (HH:MM format)
    df['time_clean'] = df['datetime'].dt.strftime('%H:%M')
    df['greg_date'] = df['datetime'].dt.strftime('%Y-%m-%d')
    
    if len(df) > 0:
        print(f"\nPeriod: {df['datetime'].iloc[0]} to {df['datetime'].iloc[-1]}")
        print(f"Records: {len(df)}")
        
        # Detect interval
        if len(df) > 1:
            time_diff = (df['datetime'].iloc[1] - df['datetime'].iloc[0]).total_seconds() / 60
            print(f"Detected interval: ~{time_diff:.0f} minutes")
        
        # Print data quality summary
        print("\nData Quality Summary:")
        print(f"  Temperature: {df['temp_C'].min():.1f} - {df['temp_C'].max():.1f} °C (mean: {df['temp_C'].mean():.1f})")
        print(f"  Humidity: {df['humidity_pct'].min():.1f} - {df['humidity_pct'].max():.1f} % (mean: {df['humidity_pct'].mean():.1f})")
        print(f"  Pressure: {df['pressure_kPa'].min():.1f} - {df['pressure_kPa'].max():.1f} kPa")
        
        if 'solar_Wm2' in df.columns:
            day_solar = df[df['solar_Wm2'] > 0]['solar_Wm2']
            if len(day_solar) > 0:
                print(f"  Solar radiation: 0 - {df['solar_Wm2'].max():.0f} W/m² (mean daytime: {day_solar.mean():.0f})")
            else:
                print(f"  Solar radiation: 0 W/m² (all nighttime?)")
        
        if 'wind_kmh' in df.columns:
            print(f"  Wind speed: {df['wind_kmh'].min():.1f} - {df['wind_kmh'].max():.1f} km/h (mean: {df['wind_kmh'].mean():.1f})")
        
        if 'rain_mm' in df.columns:
            print(f"  Total rainfall: {df['rain_mm'].sum():.1f} mm")
        
        # Missing data report
        print(f"\n  Missing values:")
        for col in ['temp_C', 'humidity_pct', 'pressure_kPa', 'solar_Wm2', 'wind_kmh', 'rain_mm']:
            if col in df.columns:
                n_missing = df[col].isna().sum()
                if n_missing > 0:
                    print(f"    {col}: {n_missing} records ({100*n_missing/len(df):.1f}%)")
    else:
        print("\nWARNING: No valid records after cleaning!")
    
    return df
