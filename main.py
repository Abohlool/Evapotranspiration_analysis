"""Main pipeline for pistachio orchard evapotranspiration simulation."""

import os
import warnings
import traceback
from datetime import datetime

from config import ROOT_DEPTH_MAX, P_DEPLETION
from loader import load_and_clean
from et import calculate_ET
from soil import calc_soil_water_balance
from analysis import (
    aggregate_daily, 
    aggregate_weekly, 
    aggregate_monthly, 
    get_period_summary
)
from plotting import (
    plot_timeseries_overview,
    plot_daily_summary,
    plot_weekly_summary,
    plot_single_day,
    plot_fill_between_day,
    plot_monthly_summary
)
from export import export_results

warnings.filterwarnings("ignore")

def main():
    """Run the complete ET simulation pipeline."""
    print("=" * 70)
    print("PISTACHIO ORCHARD EVAPOTRANSPIRATION SIMULATION")
    print("FAO-56 Penman-Monteith Method")
    print("Torbat-e Heydarieh (35.29°N, 59.22°E)")
    print("=" * 70)
    
    # Create output directories
    os.makedirs('output/figures', exist_ok=True)
    os.makedirs('output/csv', exist_ok=True)
    
    try:
        # 1. Load and clean data
        df = load_and_clean('input/weather.csv')
        
        # 2. Calculate ET
        df = calculate_ET(df, stage='mid')
        
        # 3. Calculate soil water balance
        Dr, Ks_arr, Zr_arr, TAW_arr, RAW_arr = calc_soil_water_balance(
            df, Zr_max=ROOT_DEPTH_MAX, p=P_DEPLETION
        )
        df['Dr_mm'] = Dr
        df['Ks'] = Ks_arr
        df['Zr_m'] = Zr_arr
        df['TAW_mm'] = TAW_arr
        df['RAW_mm'] = RAW_arr
        df['ETc_adj_mm_period'] = df['ETc_mm_period'] * df['Ks']
        df['ETc_adj_mm_h'] = df['ETc_adj_mm_period'] / (10/60)
        df['cum_ETc_adj'] = df['ETc_adj_mm_period'].cumsum()
        
        # 4. Print summary
        summary = get_period_summary(df)
        print("\n" + "=" * 70)
        print("SIMULATION RESULTS")
        print("=" * 70)
        print(f"Period: {summary['start_date']} to {summary['end_date']}")
        print(f"Duration: {summary['duration_days']:.1f} days")
        print(f"Records: {summary['n_records']}")
        print(f"\nWeather Summary:")
        print(f"  Temperature: {summary['T_min']:.1f} to {summary['T_max']:.1f} °C (mean: {summary['T_mean']:.1f})")
        print(f"  Humidity: {summary['RH_min']:.1f} to {summary['RH_max']:.1f} % (mean: {summary['RH_mean']:.1f})")
        print(f"  Solar max: {summary['solar_max']:.0f} W/m²")
        print(f"  Wind mean: {summary['wind_mean']:.1f} km/h")
        print(f"  Rain total: {summary['rain_total']:.1f} mm")
        print(f"\nET Summary:")
        print(f"  Total ETo (Grass): {summary['ETo_total']:.2f} mm")
        print(f"  Total ETc (Pistachio): {summary['ETc_total']:.2f} mm")
        print(f"  Mean ETo rate: {summary['ETo_mean_rate']:.4f} mm/h")
        print(f"  Mean ETc rate: {summary['ETc_mean_rate']:.4f} mm/h")
        print(f"  Peak ETo: {summary['ETo_peak']:.4f} mm/h")
        print(f"  Peak ETc: {summary['ETc_peak']:.4f} mm/h")
        print(f"  Mean Kc: {summary['Kc_mean']:.2f}")
        
        # 5. Aggregate data
        daily = aggregate_daily(df)
        weekly = aggregate_weekly(daily)
        monthly = aggregate_monthly(daily)
        
        # 6. Generate plots
        print("\n" + "=" * 70)
        print("GENERATING PLOTS")
        print("=" * 70)
        
        # Timeseries overview
        plot_timeseries_overview(df, save_path='output/figures/01_timeseries_overview.png')
        
        # Daily summary
        plot_daily_summary(daily, save_path='output/figures/02_daily_summary.png')
        
        # Weekly summary
        plot_weekly_summary(weekly, save_path='output/figures/03_weekly_summary.png')
        
        # Monthly summary
        plot_monthly_summary(monthly, save_path='output/figures/04_monthly_summary.png')
        
        # Diurnal fill-between plot
        plot_fill_between_day(df, daily, save_path='output/figures/05_diurnal_fill_between.png')
        
        # Single day plots (first, middle, last)
        first_date = daily['date'].iloc[0].strftime('%Y-%m-%d')
        mid_idx = len(daily) // 2
        mid_date = daily['date'].iloc[mid_idx].strftime('%Y-%m-%d')
        last_date = daily['date'].iloc[-1].strftime('%Y-%m-%d')
        
        plot_single_day(df, first_date, save_path='output/figures/06_detail_first_day.png')
        plot_single_day(df, mid_date, save_path='output/figures/07_detail_mid_day.png')
        plot_single_day(df, last_date, save_path='output/figures/08_detail_last_day.png')
        
        # 7. Export data
        print("\n" + "=" * 70)
        print("EXPORTING DATA")
        print("=" * 70)
        export_results(df, daily, weekly, monthly)
        
        print("\n" + "=" * 70)
        print("PIPELINE COMPLETE")
        print("=" * 70)
        print(f"All outputs saved to 'output/' directory")
        print(f"  - figures/: 8 plot files")
        print(f"  - csv/: 4 data files")
        
        return df, daily, weekly, monthly
        
    except FileNotFoundError as e:
        print(f"\nError: File not found - {e}")
        print("Please ensure 'input/weather.csv' exists.")
        return None
    except Exception as e:
        print(f"\nError: {e}")
        traceback.print_exc()
        return None


if __name__ == "__main__":
    results = main()
    