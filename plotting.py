"""Visualization module for evapotranspiration analysis."""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from datetime import datetime
from config import INTERVAL_HOURS, KC_MID
from weather import e_sat

plt.rcParams["font.family"] = "DejaVu Sans"

def plot_timeseries_overview(df, save_path=None):
    """Create comprehensive timeseries overview plot."""
    fig, axes = plt.subplots(4, 2, figsize=(16, 14))
    
    x = df['datetime']
    fmt = mdates.DateFormatter('%b %d\n%H:%M')
    
    # 1. Temperature & Humidity
    ax1 = axes[0, 0]
    ax1_twin = ax1.twinx()
    ax1.plot(x, df['temp_C'], color='red', linewidth=0.5, alpha=0.7, label='Temperature')
    ax1_twin.plot(x, df['humidity_pct'], color='blue', linewidth=0.5, alpha=0.7, label='Humidity')
    ax1.set_ylabel('Temperature (°C)', color='red')
    ax1_twin.set_ylabel('Humidity (%)', color='blue')
    ax1.set_title('Temperature & Humidity')
    lines1 = ax1.get_lines() + ax1_twin.get_lines()
    labels1 = [l.get_label() for l in lines1]
    ax1.legend(lines1, labels1, loc='upper right', fontsize=8)
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(fmt)
    
    # 2. Solar Radiation
    ax2 = axes[0, 1]
    ax2.fill_between(x, df['solar_Wm2'], alpha=0.3, color='orange')
    ax2.plot(x, df['solar_Wm2'], color='orange', linewidth=0.5)
    ax2.set_ylabel('Solar Radiation (W/m²)')
    ax2.set_title('Solar Radiation')
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(fmt)
    
    # 3. Net Radiation & Soil Heat Flux
    ax3 = axes[1, 0]
    solar_MJ = df['solar_Wm2'] * INTERVAL_HOURS * 3600 / 1e6
    ax3.plot(x, solar_MJ, color='orange', linewidth=0.5, alpha=0.5, label='Rs')
    ax3.plot(x, df['Rn_MJ_period'], color='red', linewidth=0.5, label='Rn')
    ax3.plot(x, df['G_MJ_period'], color='brown', linewidth=0.5, label='G')
    ax3.set_ylabel('Energy (MJ/m²/period)')
    ax3.set_title('Energy Fluxes')
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)
    ax3.xaxis.set_major_formatter(fmt)
    
    # 4. Wind Speed & VPD
    ax4 = axes[1, 1]
    ax4_twin = ax4.twinx()
    vpd = e_sat(df['temp_C']) * (1 - df['humidity_pct']/100)
    ax4.plot(x, df['wind_kmh']/3.6, color='green', linewidth=0.5, alpha=0.7, label='Wind')
    ax4_twin.plot(x, vpd, color='purple', linewidth=0.5, alpha=0.7, label='VPD')
    ax4.set_ylabel('Wind Speed (m/s)', color='green')
    ax4_twin.set_ylabel('VPD (kPa)', color='purple')
    ax4.set_title('Wind Speed & Vapor Pressure Deficit')
    lines4 = ax4.get_lines() + ax4_twin.get_lines()
    labels4 = [l.get_label() for l in lines4]
    ax4.legend(lines4, labels4, loc='upper right', fontsize=8)
    ax4.grid(True, alpha=0.3)
    ax4.xaxis.set_major_formatter(fmt)
    
    # 5. Hourly ET Rates
    ax5 = axes[2, 0]
    ax5.plot(x, df['ETo_mm_h'], color='green', linewidth=0.5, alpha=0.7, 
             label=f'ETo ({df["cum_ETo"].iloc[-1]:.1f} mm)')
    ax5.plot(x, df['ETc_mm_h'], color='saddlebrown', linewidth=0.5, alpha=0.7, 
             label=f'ETc ({df["cum_ETc"].iloc[-1]:.1f} mm)')
    ax5.set_ylabel('ET Rate (mm/h)')
    ax5.set_title('Evapotranspiration Rates')
    ax5.legend(fontsize=8)
    ax5.grid(True, alpha=0.3)
    ax5.xaxis.set_major_formatter(fmt)
    
    # 6. Cumulative ET
    ax6 = axes[2, 1]
    ax6.fill_between(x, df['cum_ETc'], alpha=0.2, color='saddlebrown')
    ax6.plot(x, df['cum_ETo'], color='green', linewidth=1.5, label='ETo')
    ax6.plot(x, df['cum_ETc'], color='saddlebrown', linewidth=1.5, label='ETc')
    ax6.set_ylabel('Cumulative ET (mm)')
    ax6.set_title('Cumulative Evapotranspiration')
    ax6.legend(fontsize=8)
    ax6.grid(True, alpha=0.3)
    ax6.xaxis.set_major_formatter(fmt)
    
    # 7. Crop Coefficient
    ax7 = axes[3, 0]
    ax7.plot(x, df['Kc'], color='darkgreen', linewidth=0.5)
    ax7.axhline(y=KC_MID, color='gray', linestyle='--', alpha=0.5, label=f'Kc_mid = {KC_MID}')
    ax7.set_ylabel('Kc')
    ax7.set_title('Crop Coefficient')
    ax7.legend(fontsize=8)
    ax7.grid(True, alpha=0.3)
    ax7.xaxis.set_major_formatter(fmt)
    
    # 8. Summary Text
    ax8 = axes[3, 1]
    ax8.axis('off')
    duration_hours = (df['datetime'].iloc[-1] - df['datetime'].iloc[0]).total_seconds() / 3600
    summary_text = (
        f"SUMMARY\n{'─'*40}\n"
        f"Records: {len(df)}\n"
        f"Duration: {duration_hours:.1f} hours\n"
        f"Interval: {INTERVAL_HOURS*60:.0f} min\n\n"
        f"ETo Total: {df['ETo_mm_period'].sum():.2f} mm\n"
        f"ETc Total: {df['ETc_mm_period'].sum():.2f} mm\n"
        f"ETo Mean: {df['ETo_mm_h'].mean():.4f} mm/h\n"
        f"ETc Mean: {df['ETc_mm_h'].mean():.4f} mm/h\n"
        f"Kc Mean: {df['Kc'].mean():.2f}"
    )
    ax8.text(0.05, 0.95, summary_text, transform=ax8.transAxes, fontsize=9,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    plt.suptitle('Pistachio Orchard - Timeseries Overview', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Timeseries overview saved to '{save_path}'")
    plt.close()


def plot_daily_summary(daily, save_path=None):
    """Plot daily ET values with weather variables."""
    fig, axes = plt.subplots(3, 2, figsize=(18, 12))
    x = daily['date']
    
    # 1. Daily ETo and ETc
    ax1 = axes[0, 0]
    ax1.fill_between(x, daily['ETc_mm_day'], alpha=0.3, color='saddlebrown')
    ax1.plot(x, daily['ETc_mm_day'], color='saddlebrown', linewidth=1.5, label=f'ETc ({daily["ETc_mm_day"].sum():.0f} mm)')
    ax1.plot(x, daily['ETo_mm_day'], color='green', linewidth=1.5, label=f'ETo ({daily["ETo_mm_day"].sum():.0f} mm)')
    ax1.set_ylabel('ET (mm/day)')
    ax1.set_title('Daily Evapotranspiration')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Cumulative ET
    ax2 = axes[0, 1]
    ax2.fill_between(x, daily['ETc_mm_day'].cumsum(), alpha=0.2, color='saddlebrown')
    ax2.plot(x, daily['ETc_mm_day'].cumsum(), color='saddlebrown', linewidth=2, 
             label=f'ETc ({daily["ETc_mm_day"].sum():.0f} mm)')
    ax2.plot(x, daily['ETo_mm_day'].cumsum(), color='green', linewidth=2, 
             label=f'ETo ({daily["ETo_mm_day"].sum():.0f} mm)')
    ax2.set_ylabel('Cumulative ET (mm)')
    ax2.set_title('Cumulative Evapotranspiration')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax2.tick_params(axis='x', rotation=45)
    
    # 3. Temperature Range
    ax3 = axes[1, 0]
    ax3.fill_between(x, daily['T_min'], daily['T_max'], alpha=0.3, color='red')
    ax3.plot(x, daily['T_mean'], color='darkred', linewidth=1.5, label='T mean')
    ax3.set_ylabel('Temperature (°C)')
    ax3.set_title('Daily Temperature Range')
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3)
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax3.tick_params(axis='x', rotation=45)
    
    # 4. Humidity & VPD
    ax4 = axes[1, 1]
    ax4_twin = ax4.twinx()
    ax4.fill_between(x, daily['RH_min'], daily['RH_max'], alpha=0.2, color='blue')
    ax4.plot(x, daily['RH_mean'], color='darkblue', linewidth=1.5, label='RH mean')
    ax4_twin.plot(x, daily['VPD_kPa'], color='purple', linewidth=1, linestyle='--', alpha=0.7, label='VPD')
    ax4.set_ylabel('Humidity (%)', color='blue')
    ax4_twin.set_ylabel('VPD (kPa)', color='purple')
    ax4.set_title('Humidity & Vapor Pressure Deficit')
    ax4.legend(loc='upper left', fontsize=7)
    ax4_twin.legend(loc='upper right', fontsize=7)
    ax4.grid(True, alpha=0.3)
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax4.tick_params(axis='x', rotation=45)
    
    # 5. Crop Coefficient
    ax5 = axes[2, 0]
    ax5.plot(x, daily['Kc_mean'], color='darkgreen', linewidth=1.5, label='Kc')
    ax5.axhline(y=KC_MID, color='gray', linestyle='--', alpha=0.5, label=f'Kc_mid = {KC_MID}')
    ax5.set_ylabel('Kc')
    ax5.set_title('Crop Coefficient')
    ax5.legend(fontsize=9)
    ax5.grid(True, alpha=0.3)
    ax5.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax5.tick_params(axis='x', rotation=45)
    
    # 6. Water Balance
    ax6 = axes[2, 1]
    ax6.bar(x, daily['rain_mm_day'], color='blue', alpha=0.5, label='Rainfall', width=1)
    ax6_twin = ax6.twinx()
    if 'Dr_mm_max' in daily.columns:
        ax6_twin.plot(x, daily['Dr_mm_max'], color='saddlebrown', linewidth=1.5, label='Soil Depletion')
        ax6_twin.fill_between(x, 0, daily['Dr_mm_max'], alpha=0.15, color='saddlebrown')
    ax6.set_ylabel('Rainfall (mm)', color='blue')
    ax6_twin.set_ylabel('Soil Depletion (mm)', color='saddlebrown')
    ax6.set_title('Water Balance: Rainfall & Soil Depletion')
    ax6.legend(loc='upper left', fontsize=7)
    ax6_twin.legend(loc='upper right', fontsize=7)
    ax6.grid(True, alpha=0.3)
    ax6.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax6.tick_params(axis='x', rotation=45)
    
    plt.suptitle('Pistachio Orchard - Daily Summary', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Daily summary saved to '{save_path}'")
    plt.close()


def plot_weekly_summary(weekly, save_path=None):
    """Create weekly summary bar chart."""
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    x = range(len(weekly))
    weeks = weekly['week_label'].tolist()
    
    # Weekly ET and Rainfall
    ax1 = axes[0]
    width = 0.35
    ax1.bar([i - width/2 for i in x], weekly['ETc_mm_day'], width, 
            color='saddlebrown', alpha=0.8, label='ETc (Pistachio)')
    ax1.bar([i + width/2 for i in x], weekly['rain_mm_day'], width, 
            color='blue', alpha=0.5, label='Rainfall')
    ax1.set_ylabel('mm/week', fontsize=12)
    ax1.set_title('Weekly Water Balance (ETc vs Rainfall)', fontsize=13)
    ax1.set_xticks(x)
    ax1.set_xticklabels(weeks, rotation=45)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Weekly Kc
    ax2 = axes[1]
    ax2.bar(x, weekly['Kc_mean'], color='darkgreen', alpha=0.7)
    ax2.axhline(y=KC_MID, color='gray', linestyle='--', alpha=0.5, linewidth=1)
    ax2.set_ylabel('Kc', fontsize=12)
    ax2.set_title('Weekly Average Crop Coefficient', fontsize=13)
    ax2.set_xticks(x)
    ax2.set_xticklabels(weeks, rotation=45)
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle('Pistachio Orchard - Weekly Summary', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Weekly summary saved to '{save_path}'")
    plt.close()


def plot_single_day(df, target_date, save_path=None):
    """Detailed plot for a single day."""
    df_copy = df.copy()
    df_copy['date_only'] = df_copy['datetime'].dt.date
    
    mask = df_copy['date_only'] == pd.to_datetime(target_date).date()
    day_df = df_copy[mask].copy()
    
    if len(day_df) == 0:
        print(f"No data found for {target_date}")
        return
    
    fig, axes = plt.subplots(3, 2, figsize=(16, 10))
    x = day_df['datetime']
    fmt = mdates.DateFormatter('%H:%M')
    
    # 1. Temperature & Humidity
    ax1 = axes[0, 0]
    ax1_twin = ax1.twinx()
    ax1.plot(x, day_df['temp_C'], color='red', linewidth=2, label='Temperature')
    ax1_twin.plot(x, day_df['humidity_pct'], color='blue', linewidth=2, label='Humidity')
    ax1.set_ylabel('Temperature (°C)', color='red')
    ax1_twin.set_ylabel('Humidity (%)', color='blue')
    ax1.set_title(f'Temperature & Humidity - {target_date}')
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(fmt)
    lines1 = ax1.get_lines() + ax1_twin.get_lines()
    labels1 = [l.get_label() for l in lines1]
    ax1.legend(lines1, labels1, loc='upper right', fontsize=8)
    
    # 2. Solar & Net Radiation
    ax2 = axes[0, 1]
    solar_MJ = day_df['solar_Wm2'] * INTERVAL_HOURS * 3600 / 1e6
    ax2.fill_between(x, 0, solar_MJ, alpha=0.15, color='orange')
    ax2.plot(x, solar_MJ, color='orange', linewidth=1.5, alpha=0.8, label='Rs (Solar)')
    ax2.plot(x, day_df['Rn_MJ_period'], color='red', linewidth=2, label='Rn (Net)')
    ax2.plot(x, day_df['G_MJ_period'], color='brown', linewidth=1, label='G (Soil)')
    ax2.set_ylabel('Energy (MJ/m²/period)')
    ax2.set_title('Energy Fluxes')
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(fmt)
    
    # 3. Wind Speed & VPD
    ax3 = axes[1, 0]
    ax3_twin = ax3.twinx()
    vpd = e_sat(day_df['temp_C']) * (1 - day_df['humidity_pct']/100)
    ax3.fill_between(x, 0, day_df['wind_kmh']/3.6, alpha=0.15, color='green')
    ax3.plot(x, day_df['wind_kmh']/3.6, color='green', linewidth=1.5, label='Wind')
    ax3_twin.plot(x, vpd, color='purple', linewidth=1.5, label='VPD')
    ax3.set_ylabel('Wind Speed (m/s)', color='green')
    ax3_twin.set_ylabel('VPD (kPa)', color='purple')
    ax3.set_title('Wind Speed & Vapor Pressure Deficit')
    lines3 = ax3.get_lines() + ax3_twin.get_lines()
    labels3 = [l.get_label() for l in lines3]
    ax3.legend(lines3, labels3, loc='upper right', fontsize=8)
    ax3.grid(True, alpha=0.3)
    ax3.xaxis.set_major_formatter(fmt)
    
    # 4. Pressure
    ax4 = axes[1, 1]
    ax4.plot(x, day_df['pressure_kPa'], color='gray', linewidth=1.5)
    ax4.set_ylabel('Pressure (kPa)')
    ax4.set_title('Atmospheric Pressure')
    ax4.grid(True, alpha=0.3)
    ax4.xaxis.set_major_formatter(fmt)
    
    # 5. Hourly ET Rates
    ax5 = axes[2, 0]
    ax5.fill_between(x, 0, day_df['ETo_mm_h'], alpha=0.15, color='green')
    ax5.fill_between(x, 0, day_df['ETc_mm_h'], alpha=0.2, color='saddlebrown')
    ax5.plot(x, day_df['ETo_mm_h'], color='green', linewidth=2, label='ETo (Grass)')
    ax5.plot(x, day_df['ETc_mm_h'], color='saddlebrown', linewidth=2, label='ETc (Pistachio)')
    ax5.set_ylabel('ET Rate (mm/h)')
    ax5.set_title('Hourly Evapotranspiration Rates')
    ax5.legend(fontsize=9)
    ax5.grid(True, alpha=0.3)
    ax5.xaxis.set_major_formatter(fmt)
    
    # 6. Cumulative ET
    ax6 = axes[2, 1]
    cum_ETo = day_df['ETo_mm_period'].cumsum()
    cum_ETc = day_df['ETc_mm_period'].cumsum()
    ax6.fill_between(x, 0, cum_ETc, alpha=0.2, color='saddlebrown')
    ax6.plot(x, cum_ETc, color='saddlebrown', linewidth=2, 
             label=f'ETc ({cum_ETc.iloc[-1]:.2f} mm)')
    ax6.plot(x, cum_ETo, color='green', linewidth=2, 
             label=f'ETo ({cum_ETo.iloc[-1]:.2f} mm)')
    ax6.set_ylabel('Cumulative ET (mm)')
    ax6.set_title('Cumulative Daily Evapotranspiration')
    ax6.legend(fontsize=9)
    ax6.grid(True, alpha=0.3)
    ax6.xaxis.set_major_formatter(fmt)
    
    plt.suptitle(f'Pistachio Orchard - Daily Analysis\n{target_date}',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Daily detail saved to '{save_path}'")
    plt.close()

def plot_fill_between_day(df, daily, save_path=None):
    """Create fill between plot showing min/max/mean for a typical day pattern."""
    # Group by hour to get diurnal pattern
    df_copy = df.copy()
    df_copy['hour_decimal'] = df_copy['datetime'].dt.hour + df_copy['datetime'].dt.minute/60
    
    # Round to nearest interval for grouping
    df_copy['time_bin'] = (df_copy['hour_decimal'] // INTERVAL_HOURS * INTERVAL_HOURS).round(2)
    
    # Aggregate by time bin across all days
    diurnal = df_copy.groupby('time_bin').agg({
        'temp_C': ['mean', 'min', 'max'],
        'humidity_pct': ['mean', 'min', 'max'],
        'solar_Wm2': ['mean', 'min', 'max'],
        'ETo_mm_h': ['mean', 'min', 'max'],
        'ETc_mm_h': ['mean', 'min', 'max'],
        'Rn_MJ_period': ['mean', 'min', 'max'],
        'wind_kmh': ['mean', 'min', 'max'],
    })
    
    # Flatten columns
    diurnal.columns = ['_'.join(col).strip() for col in diurnal.columns.values]
    diurnal = diurnal.reset_index()
    
    # Create figure
    fig, axes = plt.subplots(3, 2, figsize=(16, 12))
    x = diurnal['time_bin']
    
    # 1. Temperature
    ax1 = axes[0, 0]
    ax1.fill_between(x, diurnal['temp_C_min'], diurnal['temp_C_max'], 
                     alpha=0.3, color='red', label='Min-Max Range')
    ax1.plot(x, diurnal['temp_C_mean'], color='darkred', linewidth=2, label='Mean')
    ax1.set_ylabel('Temperature (°C)')
    ax1.set_title('Diurnal Temperature Pattern (All Days)')
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlabel('Hour of Day')
    ax1.set_xlim(0, 24)
    ax1.set_xticks(range(0, 25, 3))
    
    # 2. Solar Radiation
    ax2 = axes[0, 1]
    ax2.fill_between(x, diurnal['solar_Wm2_min'], diurnal['solar_Wm2_max'], 
                     alpha=0.3, color='orange', label='Min-Max Range')
    ax2.plot(x, diurnal['solar_Wm2_mean'], color='darkorange', linewidth=2, label='Mean')
    ax2.set_ylabel('Solar Radiation (W/m²)')
    ax2.set_title('Diurnal Solar Radiation Pattern')
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlabel('Hour of Day')
    ax2.set_xlim(0, 24)
    ax2.set_xticks(range(0, 25, 3))
    
    # 3. Humidity
    ax3 = axes[1, 0]
    ax3.fill_between(x, diurnal['humidity_pct_min'], diurnal['humidity_pct_max'], 
                     alpha=0.3, color='blue', label='Min-Max Range')
    ax3.plot(x, diurnal['humidity_pct_mean'], color='darkblue', linewidth=2, label='Mean')
    ax3.set_ylabel('Humidity (%)')
    ax3.set_title('Diurnal Humidity Pattern')
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)
    ax3.set_xlabel('Hour of Day')
    ax3.set_xlim(0, 24)
    ax3.set_xticks(range(0, 25, 3))
    
    # 4. Wind Speed
    ax4 = axes[1, 1]
    ax4.fill_between(x, diurnal['wind_kmh_min']/3.6, diurnal['wind_kmh_max']/3.6, 
                     alpha=0.3, color='green', label='Min-Max Range')
    ax4.plot(x, diurnal['wind_kmh_mean']/3.6, color='darkgreen', linewidth=2, label='Mean')
    ax4.set_ylabel('Wind Speed (m/s)')
    ax4.set_title('Diurnal Wind Speed Pattern')
    ax4.legend(fontsize=8)
    ax4.grid(True, alpha=0.3)
    ax4.set_xlabel('Hour of Day')
    ax4.set_xlim(0, 24)
    ax4.set_xticks(range(0, 25, 3))
    
    # 5. ET Rates
    ax5 = axes[2, 0]
    ax5.fill_between(x, diurnal['ETc_mm_h_min'], diurnal['ETc_mm_h_max'], 
                     alpha=0.3, color='saddlebrown', label='ETc Range')
    ax5.fill_between(x, diurnal['ETo_mm_h_min'], diurnal['ETo_mm_h_max'], 
                     alpha=0.2, color='green', label='ETo Range')
    ax5.plot(x, diurnal['ETc_mm_h_mean'], color='saddlebrown', linewidth=2, label='ETc Mean')
    ax5.plot(x, diurnal['ETo_mm_h_mean'], color='green', linewidth=2, label='ETo Mean')
    ax5.set_ylabel('ET Rate (mm/h)')
    ax5.set_title('Diurnal ET Pattern (Min-Max Range)')
    ax5.legend(fontsize=8)
    ax5.grid(True, alpha=0.3)
    ax5.set_xlabel('Hour of Day')
    ax5.set_xlim(0, 24)
    ax5.set_xticks(range(0, 25, 3))
    
    # 6. Net Radiation
    ax6 = axes[2, 1]
    ax6.fill_between(x, diurnal['Rn_MJ_period_min'], diurnal['Rn_MJ_period_max'], 
                     alpha=0.3, color='red', label='Rn Range')
    ax6.plot(x, diurnal['Rn_MJ_period_mean'], color='darkred', linewidth=2, label='Rn Mean')
    ax6.set_ylabel('Net Radiation (MJ/m²/period)')
    ax6.set_title('Diurnal Net Radiation Pattern')
    ax6.legend(fontsize=8)
    ax6.grid(True, alpha=0.3)
    ax6.set_xlabel('Hour of Day')
    ax6.set_xlim(0, 24)
    ax6.set_xticks(range(0, 25, 3))
    
    plt.suptitle('Pistachio Orchard - Diurnal Patterns (Min-Max Range Across All Days)',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Diurnal fill-between plot saved to '{save_path}'")
    plt.close()


def plot_monthly_summary(monthly, save_path=None):
    """Create monthly summary bar chart."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    
    x = range(len(monthly))
    labels = monthly.apply(lambda row: f"{row['month_name']}\n{int(row['year'])}", axis=1)
    
    # Monthly ET and Rainfall
    ax1 = axes[0, 0]
    width = 0.35
    ax1.bar([i - width/2 for i in x], monthly['ETc_mm_day'], width, 
            color='saddlebrown', alpha=0.8, label='ETc (Pistachio)')
    ax1.bar([i + width/2 for i in x], monthly['rain_mm_day'], width, 
            color='blue', alpha=0.5, label='Rainfall')
    ax1.set_ylabel('mm/month', fontsize=12)
    ax1.set_title('Monthly Water Balance', fontsize=13)
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Monthly Temperature
    ax2 = axes[0, 1]
    ax2.bar(x, monthly['T_max'] - monthly['T_min'], bottom=monthly['T_min'],
            color='red', alpha=0.3, label='T range')
    ax2.plot(x, monthly['T_mean'], color='darkred', marker='o', linewidth=2, markersize=8, label='T mean')
    ax2.set_ylabel('Temperature (°C)', fontsize=12)
    ax2.set_title('Monthly Temperature', fontsize=13)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Monthly Kc & VPD
    ax3 = axes[1, 0]
    ax3_twin = ax3.twinx()
    ax3.bar(x, monthly['Kc_mean'], color='darkgreen', alpha=0.7, label='Kc')
    ax3_twin.plot(x, monthly['VPD_kPa'], color='purple', marker='s', linewidth=2, markersize=8, label='VPD')
    ax3.set_ylabel('Kc', fontsize=12, color='darkgreen')
    ax3_twin.set_ylabel('VPD (kPa)', fontsize=12, color='purple')
    ax3.set_title('Monthly Kc & VPD', fontsize=13)
    ax3.set_xticks(x)
    ax3.set_xticklabels(labels)
    ax3.legend(loc='upper left', fontsize=9)
    ax3_twin.legend(loc='upper right', fontsize=9)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Monthly Solar Radiation
    ax4 = axes[1, 1]
    ax4.bar(x, monthly['solar_sum']/1000, color='orange', alpha=0.7)
    ax4.set_ylabel('Solar Radiation (MJ/m²/month ÷ 1000)', fontsize=12)
    ax4.set_title('Monthly Solar Radiation', fontsize=13)
    ax4.set_xticks(x)
    ax4.set_xticklabels(labels)
    ax4.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle('Pistachio Orchard - Monthly Summary', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Monthly summary saved to '{save_path}'")
    plt.close()