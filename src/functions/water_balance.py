"""Soil water balance and water stress coefficient."""

import numpy as np
import pandas as pd
from config import theta_FC, theta_WP, root_depth_max, p_depletion


def calc_Ks(Dr: float, TAW: float, RAW: float) -> float:
    """Water stress coefficient - FAO-56 Eq. 84"""
    if Dr <= RAW:
        return 1.0
    elif Dr < TAW:
        return (TAW - Dr) / (TAW - RAW)
    return 0.0


def calc_soil_water_balance(df: pd.DataFrame,
                            Zr_max: float = root_depth_max,
                            p: float = p_depletion) -> tuple:
    """Calculate daily soil water balance - FAO-56 Eqs. 82-86"""
    AW_per_m = 1000 * (theta_FC - theta_WP)

    n = len(df)
    Dr = np.zeros(n)
    Ks_arr = np.ones(n)
    Zr = np.zeros(n)
    TAW = np.zeros(n)
    RAW = np.zeros(n)

    Dr[0] = 0
    Zr[0] = 0.3

    for i in range(len(df)):
        if i > 0:
            Zr[i] = min(Zr[0] + (Zr_max - Zr[0]) * i / max(n - 1, 1), Zr_max)
            Zr[i] = min(Zr[i], Zr_max)
        else:
            Zr[i] = Zr[0]

        TAW[i] = AW_per_m * Zr[i]
        RAW[i] = p * TAW[i]

        if i > 0:
            ETc = df.loc[i - 1, 'ETc_mm_period']
            rain = df.loc[i - 1].get('rain_mm', 0)
            Dr[i] = Dr[i - 1] - rain + ETc
            Dr[i] = max(0, min(Dr[i], TAW[i]))

        Ks_arr[i] = calc_Ks(Dr[i], TAW[i], RAW[i])

    return Dr, Ks_arr, Zr, TAW, RAW