"""Main entry point for pistachio ET analysis."""

import traceback
import numpy as np
import pandas as pd
from data_processor import read_and_clean_data
from et_functions import calc_R_n, calc_G, calc_ETo_interval, get_Kc, e_sat
from water_balance import calc_soil_water_balance
from visualization import plot_results
from config import t_0


def run_simulation(csv_file: str) -> pd.DataFrame:
    """Run the full ET simulation and return results DataFrame."""

    # Read and clean data
    df = read_and_clean_data(csv_file)

    if len(df) == 0:
        raise ValueError("No valid data after cleaning!")

    n = len(df)
    R_n_arr = np.zeros(n)
    G_arr = np.zeros(n)
    ETo_arr = np.zeros(n)
    ETc_arr = np.zeros(n)
    Kc_arr = np.zeros(n)

    print("\nCalculating ET for each timestep...")

    for i in range(n):
        T = df.loc[i, 'temp_C']
        RH = df.loc[i, 'humidity_pct']
        R_s_Wm2 = df.loc[i, 'solar_Wm2']
        u_kmh = df.loc[i, 'wind_kmh']
        P = df.loc[i, 'pressure_kPa']
        day = int(df.loc[i, 'day_of_year'])

        dt = df.loc[i, 'datetime']
        t = dt.hour + dt.minute / 60.0

        e_s = e_sat(T)
        e_a = e_s * (RH / 100)
        u2 = u_kmh / 3.6
        is_daytime = R_s_Wm2 > 5

        R_n = calc_R_n(R_s_Wm2, t, day, T, RH)
        R_n_arr[i] = R_n
        G = calc_G(R_n, is_daytime)
        G_arr[i] = G

        ETo = calc_ETo_interval(R_n, G, T, u2, e_s, e_a, P, t_0)
        ETo_arr[i] = ETo

        Kc = get_Kc(stage='mid', u2=u2, RHmin=RH)
        Kc_arr[i] = Kc
        ETc_arr[i] = Kc * ETo

        if (i + 1) % 5000 == 0:
            print(f"  Processed {i + 1}/{n} records...")

    print(f"  Complete: {n} records processed")

    # Store results
    df['Rn_MJ_period'] = R_n_arr
    df['G_MJ_period'] = G_arr
    df['ETo_mm_period'] = ETo_arr
    df['Kc'] = Kc_arr
    df['ETc_mm_period'] = ETc_arr
    df['ETo_mm_h'] = df['ETo_mm_period'] / t_0
    df['ETc_mm_h'] = df['ETc_mm_period'] / t_0
    df['cum_ETo'] = df['ETo_mm_period'].cumsum()
    df['cum_ETc'] = df['ETc_mm_period'].cumsum()

    # Soil water balance
    Dr, Ks_arr, Zr_arr, TAW_arr, RAW_arr = calc_soil_water_balance(df)
    df['Dr_mm'] = Dr
    df['Ks'] = Ks_arr
    df['Zr_m'] = Zr_arr
    df['TAW_mm'] = TAW_arr
    df['RAW_mm'] = RAW_arr
    df['ETc_adj_mm_period'] = df['ETc_mm_period'] * df['Ks']
    df['ETc_adj_mm_h'] = df['ETc_adj_mm_period'] / t_0
    df['cum_ETc_adj'] = df['ETc_adj_mm_period'].cumsum()

    return df


def main():
    csv_file = "weather_conditions_formatted.csv"

    try:
        print("=" * 70)
        print("PISTACHIO ORCHARD EVAPOTRANSPIRATION SIMULATION")
        print("FAO-56 Penman-Monteith Method")
        print("Torbat-e Heydarieh (35.29°N, 59.22°E)")
        print("=" * 70)

        df = run_simulation(csv_file)

        # Print results
        print("\n" + "=" * 70)
        print("SIMULATION RESULTS")
        print("=" * 70)
        print(f"Period: {df['datetime'].iloc[0]} to {df['datetime'].iloc[-1]}")
        print(f"Total ETo (Grass): {df['ETo_mm_period'].sum():.2f} mm")
        print(f"Total ETc (Pistachio): {df['ETc_mm_period'].sum():.2f} mm")
        print(f"Avg ETo rate: {df['ETo_mm_h'].mean():.4f} mm/h")
        print(f"Avg ETc rate: {df['ETc_mm_h'].mean():.4f} mm/h")
        print(f"Peak ETo: {df['ETo_mm_h'].max():.4f} mm/h")
        print(f"Peak ETc: {df['ETc_mm_h'].max():.4f} mm/h")
        print(f"Avg Kc: {df['Kc'].mean():.2f}")

        # Plot
        plot_results(df, filename='pistachio_et_simulation.png')

        # Export
        export_cols = ['datetime', 'time_clean', 'temp_C', 'humidity_pct',
                       'solar_Wm2', 'wind_kmh', 'pressure_kPa',
                       'Rn_MJ_period', 'G_MJ_period', 'ETo_mm_period',
                       'Kc', 'ETc_mm_period', 'ETo_mm_h', 'ETc_mm_h']
        available_cols = [c for c in export_cols if c in df.columns]
        df[available_cols].round(6).to_csv('pistachio_et_results.csv',
                                           index=False, encoding='utf-8')
        print("\n✓ Results exported to 'pistachio_et_results.csv'")

    except FileNotFoundError:
        print(f"\nError: File '{csv_file}' not found!")
    except Exception as e:
        print(f"\nError: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()