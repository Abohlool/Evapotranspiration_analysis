"""FAO-56 Penman-Monteith ETo and crop coefficient functions."""

import numpy as np
from config import alpha, sigma, t_0, z_elev, Kc_ini, Kc_mid, Kc_end, tree_height
from atmosphere import e_sat, calc_Delta, calc_gamma
from solar_geometry import calc_R_a_interval


def calc_R_n(R_s: float, t: float, day: int, T: float, RH: float) -> float:
    """Net radiation for sub-hourly period (MJ/m²/period) - FAO-56 Eq. 40"""
    R_s_MJ = R_s * t_0 * 3600 / 1e6
    R_ns = (1 - alpha) * R_s_MJ

    e_a = e_sat(T) * (RH / 100)

    R_a_period = calc_R_a_interval(t, day, t_0)
    if R_a_period > 0:
        R_so_period = (0.75 + 2e-5 * z_elev) * R_a_period
    else:
        R_so_period = 0.001

    if R_s_MJ > 0 and R_so_period > 0.001:
        R_s_R_so = min(R_s_MJ / R_so_period, 1.0)
        f_cd = 1.35 * R_s_R_so - 0.35
        f_cd = max(0.05, min(f_cd, 1.0))
    else:
        f_cd = 0.3

    sigma_period = sigma * (t_0 / 24)
    T_K = T + 273.16

    R_nl = sigma_period * T_K ** 4 * (0.34 - 0.14 * np.sqrt(max(e_a, 0.001))) * f_cd
    R_n = R_ns - R_nl

    return R_n


def calc_G(R_n: float, is_daytime: bool) -> float:
    """Soil heat flux (MJ/m²/period) - FAO-56 Eqs. 45-46"""
    return R_n * (0.1 if is_daytime else 0.5)


def calc_ETo_interval(R_n: float, G: float, T: float, u2: float,
                      e_s: float, e_a: float, P: float,
                      interval_hours: float = t_0) -> float:
    """FAO-56 Penman-Monteith ETo for sub-hourly period (mm/period) - FAO-56 Eq. 53"""
    Delta = calc_Delta(T)
    gamma = calc_gamma(P)
    vpd = e_s - e_a

    Cn = 37 * interval_hours
    Cd = 0.24

    numerator = (0.408 * Delta * (R_n - G) +
                 gamma * (Cn / (T + 273.16)) * u2 * vpd)
    denominator = Delta + gamma * (1 + Cd * u2)

    ETo = numerator / denominator
    return max(ETo, 0)


def get_Kc(stage: str = 'mid', u2: float = 2.0, RHmin: float = 45) -> float:
    """Get climate-adjusted Kc for pistachio - FAO-56 Eq. 62"""
    Kc_table = {'ini': Kc_ini, 'mid': Kc_mid, 'end': Kc_end}
    Kc = Kc_table.get(stage, Kc_mid)

    if stage in ['mid', 'end']:
        Kc = Kc + (0.04 * (u2 - 2) - 0.004 * (RHmin - 45)) * (tree_height / 3) ** 0.3

    return Kc