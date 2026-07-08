"""Export data to CSV files."""

import os

def export_results(df, daily, weekly, monthly, output_dir='output/csv'):
    """Export all results to CSV files."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Export full timeseries results
    export_cols = ['datetime', 'time_clean', 'greg_date', 'temp_C', 'humidity_pct', 
                   'solar_Wm2', 'wind_kmh', 'pressure_kPa', 'rain_mm',
                   'Rn_MJ_period', 'G_MJ_period', 'ETo_mm_period', 'Kc', 
                   'ETc_mm_period', 'ETo_mm_h', 'ETc_mm_h', 'cum_ETo', 'cum_ETc']
    
    available_cols = [col for col in export_cols if col in df.columns]
    df[available_cols].round(6).to_csv(f'{output_dir}/et_results_timeseries.csv', 
                                        index=False, encoding='utf-8')
    
    # Export daily summary
    daily.to_csv(f'{output_dir}/et_daily_summary.csv', index=False, encoding='utf-8')
    
    # Export weekly summary
    weekly.to_csv(f'{output_dir}/et_weekly_summary.csv', index=False, encoding='utf-8')
    
    # Export monthly summary
    monthly.to_csv(f'{output_dir}/et_monthly_summary.csv', index=False, encoding='utf-8')
    
    print("\n" + "=" * 70)
    print("EXPORT COMPLETE")
    print("=" * 70)
    print(f"✓ {output_dir}/et_results_timeseries.csv")
    print(f"✓ {output_dir}/et_daily_summary.csv")
    print(f"✓ {output_dir}/et_weekly_summary.csv")
    print(f"✓ {output_dir}/et_monthly_summary.csv")
    