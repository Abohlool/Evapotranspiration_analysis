"""Soil water balance calculations."""

import numpy as np
import pandas as pd
from config import THETA_FC, THETA_WP, ROOT_DEPTH_MAX, P_DEPLETION

def calc_Ks(Dr, TAW, RAW):
    """Water stress coefficient."""
    if Dr <= RAW:
        return 1.0
    elif Dr < TAW:
        return (TAW - Dr) / (TAW - RAW)
    return 0.0

def calc_soil_water_balance(df, Zr_max=ROOT_DEPTH_MAX, p=P_DEPLETION):
    """Calculate daily soil water balance."""
    AW_per_m = 1000 * (THETA_FC - THETA_WP)  # mm/m
    
    n = len(df)
    Dr = np.zeros(n)
    Ks_arr = np.ones(n)
    Zr = np.zeros(n)
    TAW = np.zeros(n)
    RAW = np.zeros(n)
    
    Dr[0] = 0
    Zr[0] = 0.3  # Initial root depth (m)
    
    for i in range(n):
        # Root growth (linear increase to max depth)
        if i > 0:
            Zr[i] = min(Zr[0] + (Zr_max - Zr[0]) * i / max(n-1, 1), Zr_max)
        else:
            Zr[i] = Zr[0]
        
        TAW[i] = AW_per_m * Zr[i]
        RAW[i] = p * TAW[i]
        
        # Water balance
        if i > 0:
            ETc = df.loc[i-1, 'ETc_mm_period'] if 'ETc_mm_period' in df.columns else 0
            rain = df.loc[i-1].get('rain_mm', 0)
            Dr[i] = Dr[i-1] - rain + ETc
            Dr[i] = max(0, min(Dr[i], TAW[i]))
        
        Ks_arr[i] = calc_Ks(Dr[i], TAW[i], RAW[i])
    
    return Dr, Ks_arr, Zr, TAW, RAW
