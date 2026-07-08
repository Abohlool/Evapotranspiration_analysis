"""Solar geometry and radiation calculations."""

import numpy as np
from config import LATITUDE, STANDARD_MERIDIAN, LOCAL_MERIDIAN, INTERVAL_HOURS, G_SC, ELEVATION

def calc_delta_solar(day):
    """Solar declination (radians)."""
    return 0.409 * np.sin(2 * np.pi * day / 365 - 1.39)

def calc_d_r(day):
    """Inverse relative Earth-Sun distance."""
    return 1 + 0.033 * np.cos(2 * np.pi * day / 365)

def calc_S_c(day):
    """Seasonal correction for solar time (hours)."""
    b = 2 * np.pi / 364 * (day - 81)
    return 0.1645 * np.sin(2*b) - 0.1255 * np.cos(b) - 0.025 * np.sin(b)

def calc_omega(t, day):
    """Solar time angle at midpoint (radians)."""
    S_c = calc_S_c(day)
    omega = np.pi/12 * ((t + 0.06667*(STANDARD_MERIDIAN - LOCAL_MERIDIAN) + S_c) - 12)
    return omega

def calc_sunset_hour_angle(day):
    """Sunset hour angle (radians)."""
    delta = calc_delta_solar(day)
    cos_ws = -np.tan(LATITUDE) * np.tan(delta)
    # Clamp to [-1, 1] to avoid numerical issues
    cos_ws = max(-1.0, min(1.0, cos_ws))
    return np.arccos(cos_ws)

def calc_R_a_interval(t, day, interval=INTERVAL_HOURS):
    """Extraterrestrial radiation for sub-hourly period (MJ/m²/period)."""
    omega_mid = calc_omega(t, day)
    omega_1 = omega_mid - np.pi * interval / 24
    omega_2 = omega_mid + np.pi * interval / 24
    
    d_r = calc_d_r(day)
    delta = calc_delta_solar(day)
    omega_s = calc_sunset_hour_angle(day)
    
    # Clip to sunrise/sunset
    if omega_2 <= -omega_s or omega_1 >= omega_s:
        return 0.0
    
    omega_1 = max(omega_1, -omega_s)
    omega_2 = min(omega_2, omega_s)
    
    if omega_1 >= omega_2:
        return 0.0
    
    R_a = (12 * 60 / np.pi) * G_SC * d_r * (
        (omega_2 - omega_1) * np.sin(LATITUDE) * np.sin(delta) +
        np.cos(LATITUDE) * np.cos(delta) * (np.sin(omega_2) - np.sin(omega_1))
    )
    return max(R_a, 0)

def calc_R_a_daily(day):
    """Daily extraterrestrial radiation (MJ/m²/day)."""
    d_r = calc_d_r(day)
    delta = calc_delta_solar(day)
    omega_s = calc_sunset_hour_angle(day)
    
    R_a = (24 * 60 / np.pi) * G_SC * d_r * (
        omega_s * np.sin(LATITUDE) * np.sin(delta) +
        np.cos(LATITUDE) * np.cos(delta) * np.sin(omega_s)
    )
    return R_a

def calc_N(day):
    """Maximum sunshine hours."""
    omega_s = calc_sunset_hour_angle(day)
    return 24 / np.pi * omega_s

def calc_R_s(day, n):
    """Solar radiation from sunshine hours (MJ/m²/day)."""
    N = calc_N(day)
    R_a_val = calc_R_a_daily(day)
    if N > 0 and n > 0:
        return (0.25 + 0.50 * n/N) * R_a_val
    return 0

def calc_R_so(day):
    """Clear-sky solar radiation (MJ/m²/day)."""
    R_a_val = calc_R_a_daily(day)
    return (0.75 + 2e-5 * ELEVATION) * R_a_val

def calc_R_n(R_s, t, day, T, RH, alpha=0.20):
    """Net radiation for sub-hourly period (MJ/m²/period)."""
    from config import SIGMA, INTERVAL_HOURS
    from weather import e_sat
    
    # Convert measured solar from W/m² to MJ/m²/period
    R_s_MJ = R_s * INTERVAL_HOURS * 3600 / 1e6
    
    # Net shortwave
    R_ns = (1 - alpha) * R_s_MJ
    
    # Actual vapor pressure
    e_a = e_sat(T) * (RH / 100)
    
    # Clear-sky radiation for this period
    R_a_period = calc_R_a_interval(t, day, INTERVAL_HOURS)
    if R_a_period > 0:
        R_so_period = (0.75 + 2e-5 * ELEVATION) * R_a_period
    else:
        R_so_period = 0.001
    
    # Cloudiness factor
    if R_s_MJ > 0 and R_so_period > 0.001:
        R_s_R_so = min(R_s_MJ / R_so_period, 1.0)
        f_cd = 1.35 * R_s_R_so - 0.35
        f_cd = max(0.05, min(f_cd, 1.0))
    else:
        f_cd = 0.3  # Nighttime
    
    sigma_period = SIGMA * (INTERVAL_HOURS / 24)
    T_K = T + 273.16
    
    R_nl = sigma_period * T_K**4 * (0.34 - 0.14 * np.sqrt(max(e_a, 0.001))) * f_cd
    
    R_n = R_ns - R_nl
    return R_n

def calc_G(R_n, is_daytime):
    """Soil heat flux (MJ/m²/period)."""
    return R_n * (0.1 if is_daytime else 0.5)