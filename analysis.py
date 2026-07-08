"""Daily, weekly, and monthly summary calculations."""

import pandas as pd
import numpy as np
from weather import e_sat

def aggregate_daily(df):
    """Aggregate sub-hourly data to daily values."""
    df_copy = df.copy()
    df_copy['date'] = df_copy['datetime'].dt.date
    
    daily = df_copy.groupby('date').agg({
        'temp_C': ['min', 'max', 'mean'],
        'humidity_pct': ['min', 'max', 'mean'],
        'solar_Wm2': ['max', 'sum'],
        'wind_kmh': 'mean',
        'pressure_kPa': 'mean',
        'rain_mm': 'sum',
        'ETo_mm_period': 'sum',
        'ETc_mm_period': 'sum',
        'ETc_adj_mm_period': 'sum' if 'ETc_adj_mm_period' in df_copy.columns else lambda x: np.nan,
        'Rn_MJ_period': 'sum',
        'G_MJ_period': 'sum',
        'Kc': 'mean',
        'Ks': 'min' if 'Ks' in df_copy.columns else lambda x: np.nan,
        'Dr_mm': 'max' if 'Dr_mm' in df_copy.columns else lambda x: np.nan,
    }).round(4)
    
    # Flatten multi-level columns
    daily.columns = ['_'.join(col).strip() for col in daily.columns.values]
    daily = daily.reset_index()
    
    # Rename for clarity
    daily = daily.rename(columns={
        'ETo_mm_period_sum': 'ETo_mm_day',
        'ETc_mm_period_sum': 'ETc_mm_day',
        'rain_mm_sum': 'rain_mm_day',
        'solar_Wm2_max': 'solar_max',
        'solar_Wm2_sum': 'solar_sum',
        'wind_kmh_mean': 'wind_kmh_mean',
        'temp_C_min': 'T_min',
        'temp_C_max': 'T_max',
        'temp_C_mean': 'T_mean',
        'humidity_pct_min': 'RH_min',
        'humidity_pct_max': 'RH_max',
        'humidity_pct_mean': 'RH_mean',
    })
    
    # Convert date to datetime
    daily['date'] = pd.to_datetime(daily['date'])
    
    # Add VPD
    e_s_mean = daily.apply(lambda row: e_sat(row['T_mean']), axis=1)
    e_a_mean = e_s_mean * daily['RH_mean'] / 100
    daily['VPD_kPa'] = (e_s_mean - e_a_mean).round(3)
    
    return daily

def aggregate_weekly(daily):
    """Aggregate daily data to weekly values."""
    daily_copy = daily.copy()
    daily_copy['week'] = daily_copy['date'].dt.isocalendar().week
    daily_copy['year'] = daily_copy['date'].dt.isocalendar().year
    
    weekly = daily_copy.groupby(['year', 'week']).agg({
        'ETo_mm_day': 'sum',
        'ETc_mm_day': 'sum',
        'rain_mm_day': 'sum',
        'T_mean': 'mean',
        'RH_mean': 'mean',
        'Kc_mean': 'mean',
        'VPD_kPa': 'mean',
        'solar_sum': 'sum',
    }).round(2)
    
    weekly = weekly.reset_index()
    # Create a week label
    weekly['week_label'] = weekly.apply(lambda row: f"W{int(row['week']):02d}", axis=1)
    
    return weekly

def aggregate_monthly(daily):
    """Aggregate daily data to monthly values."""
    daily_copy = daily.copy()
    daily_copy['year'] = daily_copy['date'].dt.year
    daily_copy['month'] = daily_copy['date'].dt.month
    
    monthly = daily_copy.groupby(['year', 'month']).agg({
        'ETo_mm_day': 'sum',
        'ETc_mm_day': 'sum',
        'rain_mm_day': 'sum',
        'T_mean': 'mean',
        'T_max': 'max',
        'T_min': 'min',
        'RH_mean': 'mean',
        'Kc_mean': 'mean',
        'VPD_kPa': 'mean',
        'solar_sum': 'sum',
    }).round(2)
    
    monthly = monthly.reset_index()
    monthly['month_name'] = monthly['month'].apply(
        lambda m: ['Jan','Feb','Mar','Apr','May','Jun',
                   'Jul','Aug','Sep','Oct','Nov','Dec'][int(m)-1]
    )
    
    return monthly

def get_period_summary(df):
    """Get summary statistics for the entire period."""
    summary = {
        'start_date': df['datetime'].iloc[0],
        'end_date': df['datetime'].iloc[-1],
        'duration_days': (df['datetime'].iloc[-1] - df['datetime'].iloc[0]).total_seconds() / 86400,
        'n_records': len(df),
        'T_min': df['temp_C'].min(),
        'T_max': df['temp_C'].max(),
        'T_mean': df['temp_C'].mean(),
        'RH_min': df['humidity_pct'].min(),
        'RH_max': df['humidity_pct'].max(),
        'RH_mean': df['humidity_pct'].mean(),
        'solar_max': df['solar_Wm2'].max(),
        'wind_mean': df['wind_kmh'].mean(),
        'rain_total': df['rain_mm'].sum(),
        'ETo_total': df['ETo_mm_period'].sum(),
        'ETc_total': df['ETc_mm_period'].sum(),
        'ETo_mean_rate': df['ETo_mm_h'].mean(),
        'ETc_mean_rate': df['ETc_mm_h'].mean(),
        'ETo_peak': df['ETo_mm_h'].max(),
        'ETc_peak': df['ETc_mm_h'].max(),
        'Kc_mean': df['Kc'].mean(),
    }
    
    return summary
