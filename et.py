"""FAO-56 Penman-Monteith evapotranspiration calculations."""

import numpy as np
from config import INTERVAL_HOURS, KC_INI, KC_MID, KC_END, TREE_HEIGHT
from weather import calc_Delta, calc_gamma, e_sat
from radiation import calc_R_n, calc_G

def calc_ETo_interval(R_n, G, T, u2, e_s, e_a, P, interval_hours=INTERVAL_HOURS):
    """FAO-56 Penman-Monteith ETo for sub-hourly period."""
    Delta = calc_Delta(T)
    gamma = calc_gamma(P)
    vpd = e_s - e_a
    
    # Constants for sub-hourly
    Cn = 37 * interval_hours
    Cd = 0.24
    
    numerator = (0.408 * Delta * (R_n - G) + 
                 gamma * (Cn / (T + 273.16)) * u2 * vpd)
    denominator = Delta + gamma * (1 + Cd * u2)
    
    ETo = numerator / denominator
    return max(ETo, 0)

def get_Kc(stage='mid', u2=2.0, RHmin=45):
    """Get climate-adjusted Kc for pistachio."""
    Kc_table = {'ini': KC_INI, 'mid': KC_MID, 'end': KC_END}
    Kc = Kc_table.get(stage, KC_MID)
    
    # Climate adjustment for mid and end stages
    if stage in ['mid', 'end']:
        Kc = Kc + (0.04 * (u2 - 2) - 0.004 * (RHmin - 45)) * (TREE_HEIGHT/3)**0.3
    
    return Kc

def calculate_ET(df, stage='mid'):
    """Calculate ETo and ETc for all timesteps in DataFrame."""
    import warnings
    warnings.filterwarnings("ignore")
    
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
        
        # Vapor pressures
        e_s = e_sat(T)
        e_a = e_s * (RH / 100)
        
        # Wind speed at 2m
        u2 = u_kmh / 3.6
        
        # Daytime flag
        is_daytime = R_s_Wm2 > 5
        
        # Net radiation
        R_n = calc_R_n(R_s_Wm2, t, day, T, RH)
        R_n_arr[i] = R_n
        
        # Soil heat flux
        G = calc_G(R_n, is_daytime)
        G_arr[i] = G
        
        # Reference ET
        ETo = calc_ETo_interval(R_n, G, T, u2, e_s, e_a, P)
        ETo_arr[i] = ETo
        
        # Crop coefficient
        Kc = get_Kc(stage=stage, u2=u2, RHmin=RH)
        Kc_arr[i] = Kc
        
        # Crop ET
        ETc = Kc * ETo
        ETc_arr[i] = ETc
        
        # Progress indicator
        if (i + 1) % 5000 == 0:
            print(f"  Processed {i+1}/{n} records...")
    
    print(f"  Complete: {n} records processed")
    
    # Store results
    df['Rn_MJ_period'] = R_n_arr
    df['G_MJ_period'] = G_arr
    df['ETo_mm_period'] = ETo_arr
    df['Kc'] = Kc_arr
    df['ETc_mm_period'] = ETc_arr
    
    # Hourly rates
    df['ETo_mm_h'] = df['ETo_mm_period'] / INTERVAL_HOURS
    df['ETc_mm_h'] = df['ETc_mm_period'] / INTERVAL_HOURS
    
    # Cumulative
    df['cum_ETo'] = df['ETo_mm_period'].cumsum()
    df['cum_ETc'] = df['ETc_mm_period'].cumsum()
    
    return df
