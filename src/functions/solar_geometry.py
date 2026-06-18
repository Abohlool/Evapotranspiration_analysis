"""Solar geometry functions: declination, equation of time, hour angles."""

import numpy as np
from config import phi, L_z, L_m, G_sc, z_elev, t_0


def calc_delta_solar(day: int) -> float:
    """Solar declination (radians) - FAO-56 Eq. 24"""
    return 0.409 * np.sin(2 * np.pi * day / 365 - 1.39)


def calc_d_r(day: int) -> float:
    """Inverse relative Earth-Sun distance - FAO-56 Eq. 23"""
    return 1 + 0.033 * np.cos(2 * np.pi * day / 365)


def calc_S_c(day: int) -> float:
    """Seasonal correction for solar time (hours) - FAO-56 Eqs. 32-33"""
    b = 2 * np.pi / 364 * (day - 81)
    S_c = 0.1645 * np.sin(2 * b) - 0.1255 * np.cos(b) - 0.025 * np.sin(b)
    return S_c


def calc_omega(t: float, day: int) -> float:
    """Solar time angle at midpoint (radians) - FAO-56 Eq. 31"""
    S_c = calc_S_c(day)
    omega = np.pi / 12 * ((t + 0.06667 * (L_z - L_m) + S_c) - 12)
    return omega


def calc_sunset_hour_angle(day: int) -> float:
    """Sunset hour angle (radians) - FAO-56 Eq. 25"""
    delta = calc_delta_solar(day)
    return np.arccos(-np.tan(phi) * np.tan(delta))


def calc_R_a_interval(t: float, day: int, interval: float = t_0) -> float:
    """Extraterrestrial radiation for sub-hourly period (MJ/m²/period) - FAO-56 Eq. 28"""
    omega_mid = calc_omega(t, day)
    omega_1 = omega_mid - np.pi * interval / 24
    omega_2 = omega_mid + np.pi * interval / 24

    d_r = calc_d_r(day)
    delta = calc_delta_solar(day)
    omega_s = calc_sunset_hour_angle(day)

    if omega_2 <= -omega_s or omega_1 >= omega_s:
        return 0.0

    omega_1 = max(omega_1, -omega_s)
    omega_2 = min(omega_2, omega_s)

    if omega_1 >= omega_2:
        return 0.0

    R_a = (12 * 60 / np.pi) * G_sc * d_r * (
        (omega_2 - omega_1) * np.sin(phi) * np.sin(delta) +
        np.cos(phi) * np.cos(delta) * (np.sin(omega_2) - np.sin(omega_1))
    )

    return max(R_a, 0)


def calc_R_a_daily(day: int) -> float:
    """Daily extraterrestrial radiation (MJ/m²/day) - FAO-56 Eq. 21"""
    d_r = calc_d_r(day)
    delta = calc_delta_solar(day)
    omega_s = calc_sunset_hour_angle(day)

    R_a = (24 * 60 / np.pi) * G_sc * d_r * (
        omega_s * np.sin(phi) * np.sin(delta) +
        np.cos(phi) * np.cos(delta) * np.sin(omega_s)
    )
    return R_a


def calc_N(day: int) -> float:
    """Maximum sunshine hours - FAO-56 Eq. 34"""
    omega_s = calc_sunset_hour_angle(day)
    return 24 / np.pi * omega_s