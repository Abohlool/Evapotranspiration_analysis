"""Configuration constants and crop parameters for pistachio orchard."""

import numpy as np

# Location parameters - Torbat-e Heydarieh
LATITUDE = np.radians(35.2875)  # radians
STANDARD_MERIDIAN = 52.5  # IRST meridian (E)
LOCAL_MERIDIAN = 59.2215  # Measurement site longitude (E)

# Measurement parameters
INTERVAL_HOURS = 10 / 60  # 10-minute interval
G_SC = 0.0820  # Solar constant (MJ/m²/min)

# Site characteristics
ELEVATION = 1500  # m above sea level
ALBEDO = 0.20  # Pistachio orchard albedo
SIGMA = 4.903e-9  # Stefan-Boltzmann constant (MJ/K⁴/m²/day)

# Soil parameters (typical loam for pistachio regions)
THETA_FC = 0.28  # Field capacity (m³/m³)
THETA_WP = 0.12  # Wilting point (m³/m³)
ZE = 0.10  # Evaporation layer depth (m)

# Pistachio crop parameters (FAO-56 Table 12)
KC_INI = 0.40  # Initial stage
KC_MID = 1.10  # Mid-season
KC_END = 0.70  # End-season
TREE_HEIGHT = 3.5  # m
ROOT_DEPTH_MAX = 1.5  # Maximum root depth (m)
P_DEPLETION = 0.40  # Depletion fraction

# Wind speed conversion constants
WIND_HEIGHT_MEASUREMENT = 2.0  # m
