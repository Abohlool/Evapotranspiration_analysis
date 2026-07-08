"""Meteorological calculations (vapor pressure, psychrometric constant, etc.)."""

import numpy as np

def e_sat(T):
    """Saturated vapor pressure (kPa)."""
    return 0.6108 * np.exp((17.27 * T) / (T + 237.3))

def calc_e_s(T_max, T_min):
    """Mean saturated vapor pressure (kPa)."""
    return (e_sat(T_max) + e_sat(T_min)) / 2

def calc_e_a(T_min, T_max, RH_min, RH_max):
    """Actual vapor pressure (kPa) from RH extremes."""
    return (e_sat(T_min) * RH_max/100 + e_sat(T_max) * RH_min/100) / 2

def calc_Delta(T):
    """Slope of saturation vapor pressure curve (kPa/°C)."""
    es = e_sat(T)
    return 4098 * es / ((T + 237.3) ** 2)

def calc_gamma(P):
    """Psychrometric constant (kPa/°C)."""
    return 0.000665 * P

def calc_u2(u_z, z=2.0):
    """Convert wind speed to 2m height (m/s)."""
    if z == 2.0:
        return u_z / 3.6
    else:
        return u_z * 4.87 / np.log(67.8 * z - 5.42)