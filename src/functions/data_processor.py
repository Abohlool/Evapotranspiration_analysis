"""Data reading, cleaning, and datetime parsing."""

import re
import numpy as np
import pandas as pd
from config import t_0


def extract_time_and_date(time_str):
    """Extract HH:MM and Gregorian date (YYYY-MM-DD) from combined time field."""
    if pd.isna(time_str):
        return None, None

    time_str = str(time_str).strip()

    # Extract time (HH:MM)
    time_match = re.search(r'(\d{1,2}):(\d{2})', time_str)
    if not time_match:
        return None, None

    hour = int(time_match.group(1))
    minute = int(time_match.group(2))
    time_clean = f"{hour:02d}:{minute:02d}"

    # Extract Gregorian date (YYYY-MM-DD)
    date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', time_str)
    if date_match:
        y, m, d = int(date_match.group(1)), int(date_match.group(2)), int(date_match.group(3))
        return time_clean, f"{y:04d}-{m:02d}-{d:02d}"

    return time_clean, None


def extract_number(value):
    """Extract numeric value from string with units."""
    if pd.isna(value) or value == '--':
        return np.nan

    if isinstance(value, (int, float)):
        return float(value)

    value_str = str(value).strip()
    for unit in ['W/m2', 'W/m²', '°C', '%', 'km/h', 'kPa', 'mm']:
        value_str = value_str.replace(unit, '')
    value_str = value_str.strip()

    try:
        return float(value_str)
    except ValueError:
        return np.nan


def read_and_clean_data(csv_file: str) -> pd.DataFrame:
    """Read CSV, clean data, and return ready-to-use DataFrame."""
    print(f"Reading: {csv_file}")
    df = pd.read_csv(csv_file, encoding='utf-8')
    print(f"Data shape: {df.shape}")

    # Rename columns
    col_map = {
        'زمان': 'time',
        'باران 6 (mm)': 'rain_mm',
        'تابش خورشیدی 7 (W/m2)': 'solar_Wm2',
        'جهت باد 5 (degree)': 'wind_dir',
        'دما 1 (°C)': 'temp_C',
        'رطوبت 2 (%)': 'humidity_pct',
        'سرعت باد 4 (km/h)': 'wind_kmh',
        'فشار هوا 3 (kPa)': 'pressure_kPa'
    }
    df = df.rename(columns=col_map)

    # Extract time and date
    results = df['time'].apply(extract_time_and_date)
    df['time_clean'] = results.apply(lambda x: x[0] if x else None)
    df['greg_date'] = results.apply(lambda x: x[1] if x else None)

    df['greg_date'] = df['greg_date'].ffill()
    df = df.dropna(subset=['time_clean']).reset_index(drop=True)
    print(f"Records after time cleaning: {len(df)}")

    # Parse numeric values
    numeric_cols = ['solar_Wm2', 'temp_C', 'humidity_pct', 'wind_kmh',
                    'pressure_kPa', 'rain_mm']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].apply(extract_number)

    df['solar_Wm2'] = df['solar_Wm2'].fillna(0)
    df['wind_kmh'] = df['wind_kmh'].fillna(0)
    df['rain_mm'] = df['rain_mm'].fillna(0)

    df = df.dropna(subset=['temp_C', 'humidity_pct', 'pressure_kPa'])
    df = df.reset_index(drop=True)
    print(f"Records after numeric cleaning: {len(df)}")

    # Pressure unit conversion
    if df['pressure_kPa'].max() > 200:
        if df['pressure_kPa'].max() > 10000:
            df['pressure_kPa'] = df['pressure_kPa'] / 1000
        elif df['pressure_kPa'].max() > 500:
            df['pressure_kPa'] = df['pressure_kPa'] / 10

    # Create datetime
    df['greg_date'] = df['greg_date'].fillna('2000-01-01')
    df['time_clean'] = df['time_clean'].fillna('00:00')
    date_part = pd.to_datetime(df['greg_date'], format='%Y-%m-%d')
    time_part = pd.to_timedelta(df['time_clean'].astype(str) + ':00')
    df['datetime'] = date_part + time_part
    df = df.sort_values('datetime').reset_index(drop=True)

    df['day_of_year'] = df['datetime'].dt.dayofyear

    print(f"Period: {df['datetime'].iloc[0]} to {df['datetime'].iloc[-1]}")
    print(f"Records: {len(df)} | Interval: ~{t_0 * 60:.0f} min")
    print(f"T: {df['temp_C'].min():.1f}-{df['temp_C'].max():.1f}°C | "
          f"RH: {df['humidity_pct'].min():.1f}-{df['humidity_pct'].max():.1f}% | "
          f"Rs: {df['solar_Wm2'].min():.0f}-{df['solar_Wm2'].max():.0f} W/m²")

    return df