"""Plotting functions for ET analysis."""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from constants.config import t_0, Kc_mid
from functions.atmosphere import e_sat


def plot_results(df, filename=None):
    """Create 4x2 subplot visualization for a single period."""
    fig, axes = plt.subplots(4, 2, figsize=(16, 13))

    t_start = df['datetime'].iloc[0].strftime('%H:%M')
    t_end = df['datetime'].iloc[-1].strftime('%H:%M')

    fig.suptitle(
        f'Pistachio Orchard Evapotranspiration\n{t_start} - {t_end} '
        f'(~{(df["datetime"].iloc[-1] - df["datetime"].iloc[0]).total_seconds() / 3600:.1f} hours)',
        fontsize=14, fontweight='bold')

    x = df['datetime']
    fmt = mdates.DateFormatter('%H:%M')

    # 1. Temperature and Humidity
    ax1 = axes[0, 0]
    ax1_twin = ax1.twinx()
    ax1.plot(x, df['temp_C'], color='red', marker='.', linewidth=1.5)
    ax1_twin.plot(x, df['humidity_pct'], color='blue', marker='.', linewidth=1.5)
    ax1.set_ylabel('Temperature (°C)', color='red')
    ax1_twin.set_ylabel('Humidity (%)', color='blue')
    ax1.set_title('Temperature and Humidity')
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(fmt)

    # 2. Solar Radiation
    ax2 = axes[0, 1]
    ax2.fill_between(x, df['solar_Wm2'], alpha=0.3, color='orange')
    ax2.plot(x, df['solar_Wm2'], color='orange', linewidth=1.5)
    ax2.set_ylabel('Solar Radiation (W/m²)')
    ax2.set_title('Solar Radiation')
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(fmt)

    # 3. Wind Speed
    ax3 = axes[1, 0]
    ax3.plot(x, df['wind_kmh'] / 3.6, color='green', marker='.', linewidth=1.5)
    ax3.set_ylabel('Wind Speed (m/s)')
    ax3.set_title('Wind Speed at 2m')
    ax3.grid(True, alpha=0.3)
    ax3.xaxis.set_major_formatter(fmt)

    # 4. Energy Fluxes
    ax4 = axes[1, 1]
    solar_MJ = df['solar_Wm2'] * t_0 * 3600 / 1e6
    ax4.plot(x, solar_MJ, color='orange', marker='.', linewidth=1.5, alpha=0.5, label='Rs')
    ax4.plot(x, df['Rn_MJ_period'], color='red', marker='.', linewidth=1.5, label='Rn')
    ax4.plot(x, df['G_MJ_period'], color='brown', marker='.', linewidth=1.5, label='G')
    ax4.set_ylabel('Energy (MJ/m²/period)')
    ax4.set_title('Energy Fluxes: Rs, Rn, G')
    ax4.legend(fontsize=8)
    ax4.grid(True, alpha=0.3)
    ax4.xaxis.set_major_formatter(fmt)

    # 5. Hourly ET Rates
    ax5 = axes[2, 0]
    ax5.plot(x, df['ETo_mm_h'], color='green', marker='.', linewidth=1.5,
             label=f'ETo Grass ({df["cum_ETo"].iloc[-1]:.3f} mm)')
    ax5.plot(x, df['ETc_mm_h'], color='saddlebrown', marker='.', linewidth=1.5,
             label=f'ETc Pistachio ({df["cum_ETc"].iloc[-1]:.3f} mm)')
    if 'Ks' in df.columns and df['Ks'].min() < 1:
        ax5.plot(x, df['ETc_adj_mm_h'], color='red', linestyle='--', linewidth=1.5,
                 label=f'ETc adj ({df["cum_ETc_adj"].iloc[-1]:.3f} mm)')
    ax5.set_ylabel('ET Rate (mm/hour)')
    ax5.set_title('Hourly Evapotranspiration Rates')
    ax5.legend(fontsize=8)
    ax5.grid(True, alpha=0.3)
    ax5.xaxis.set_major_formatter(fmt)

    # 6. Cumulative ET
    ax6 = axes[2, 1]
    ax6.plot(x, df['cum_ETo'], color='green', linewidth=2,
             label=f'ETo Grass ({df["cum_ETo"].iloc[-1]:.3f} mm)')
    ax6.plot(x, df['cum_ETc'], color='saddlebrown', linewidth=2,
             label=f'ETc Pistachio ({df["cum_ETc"].iloc[-1]:.3f} mm)')
    ax6.set_ylabel('Cumulative ET (mm)')
    ax6.set_title('Cumulative Evapotranspiration')
    ax6.legend(fontsize=8)
    ax6.grid(True, alpha=0.3)
    ax6.xaxis.set_major_formatter(fmt)

    # 7. Crop Coefficient
    ax7 = axes[3, 0]
    ax7.plot(x, df['Kc'], color='purple', linewidth=2)
    ax7.axhline(y=Kc_mid, color='gray', linestyle='--', alpha=0.5,
                label=f'Kc_mid = {Kc_mid}')
    ax7.set_ylabel('Kc')
    ax7.set_title('Crop Coefficient (Kc)')
    ax7.legend(fontsize=8)
    ax7.grid(True, alpha=0.3)
    ax7.xaxis.set_major_formatter(fmt)

    # 8. Summary Statistics
    ax8 = axes[3, 1]
    ax8.axis('off')
    duration = (df['datetime'].iloc[-1] - df['datetime'].iloc[0]).total_seconds() / 3600

    summary_text = (
        f"SUMMARY\n{'─' * 35}\n"
        f"Period: {t_start} - {t_end}\n"
        f"Duration: {duration:.1f} hours\n"
        f"Records: {len(df)} ({t_0 * 60:.0f}-min intervals)\n\n"
        f"Weather:\n"
        f"  T: {df['temp_C'].min():.1f} - {df['temp_C'].max():.1f}°C\n"
        f"  RH: {df['humidity_pct'].min():.1f} - {df['humidity_pct'].max():.1f}%\n"
        f"  Rs max: {df['solar_Wm2'].max():.0f} W/m²\n"
        f"  Wind: {df['wind_kmh'].mean() / 3.6:.1f} m/s (avg)\n\n"
        f"Total ET:\n"
        f"  ETo Grass: {df['ETo_mm_period'].sum():.4f} mm\n"
        f"  ETc Pistachio: {df['ETc_mm_period'].sum():.4f} mm\n\n"
        f"Average ET rate:\n"
        f"  ETo: {df['ETo_mm_h'].mean():.4f} mm/h\n"
        f"  ETc: {df['ETc_mm_h'].mean():.4f} mm/h\n"
        f"  Kc: {df['Kc'].mean():.2f}"
    )
    ax8.text(0.05, 0.5, summary_text, transform=ax8.transAxes, fontsize=9,
             verticalalignment='center', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

    plt.tight_layout()
    if filename:
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"✓ Plot saved as '{filename}'")
    plt.show()


# (Add aggregate_daily, plot_daily_et, plot_weekly_summary, plot_single_day
#  functions here — same as before, importing from other modules)