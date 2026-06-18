"""Atmospheric functions: vapor pressure, psychrometric constant, etc."""

import numpy as np


def e_sat(T: float) -> float:
    """Saturated vapor pressure (kPa) - FAO-56 Eq. 11"""
    return 0.6108 * np.exp((17.27 * T) / (T + 237.3))


def calc_e_s(T_max: float, T_min: float) -> float:
    """Mean saturated vapor pressure (kPa) - FAO-56 Eq. 12"""
    return (e_sat(T_max) + e_sat(T_min)) / 2


def calc_e_a(T_min: float, T_max: float, RH_min: float, RH_max: float) -> float:
    """Actual vapor pressure (kPa) - FAO-56 Eq. 17"""
    return (e_sat(T_min) * RH_max / 100 + e_sat(T_max) * RH_min / 100) / 2


def calc_Delta(T: float) -> float:
    """Slope of saturation vapor pressure curve (kPa/°C) - FAO-56 Eq. 13"""
    es = e_sat(T)
    return 4098 * es / ((T + 237.3) ** 2)


def calc_gamma(P: float) -> float:
    """Psychrometric constant (kPa/°C) - FAO-56 Eq. 8"""
    a_psy = 1.013e-3 / 0.622 / 2.45
    return a_psy * P