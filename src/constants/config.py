"""Physical constants and pistachio orchard parameters."""

import numpy as np

# ============================================================================
# LOCATION - Torbat-e Heydarieh, Razavi Khorasan, Iran
# ============================================================================

phi = np.radians(35.2875)       # Latitude (radians)
L_z = 52.5                      # Standard meridian for IRST (°E)
L_m = 59.2215                   # Longitude of measurement site (°E)
z_elev = 1500                   # Elevation (m above sea level)
t_0 = 10 / 60                   # Measurement interval (hours)

# ============================================================================
# PHYSICAL CONSTANTS
# ============================================================================

G_sc = 0.0820                   # Solar constant (MJ/m²/min)
sigma = 4.903e-9                # Stefan-Boltzmann constant (MJ/K⁴/m²/day)
alpha = 0.20                    # Albedo for pistachio orchard (0.20-0.22)
c_s = 1.2                       # Soil specific heat (MJ/m³/°C)

# ============================================================================
# PISTACHIO PARAMETERS (FAO-56 Table 12)
# ============================================================================

Kc_ini = 0.40                   # Initial stage Kc
Kc_mid = 1.10                   # Mid-season Kc
Kc_end = 0.70                   # End-season Kc
tree_height = 3.5               # Pistachio tree height (m)
root_depth_max = 1.5            # Maximum root depth (m)
p_depletion = 0.40              # Depletion fraction for pistachio

# ============================================================================
# SOIL PARAMETERS (typical loam for pistachio regions)
# ============================================================================

theta_FC = 0.28                 # Field capacity (m³/m³)
theta_WP = 0.12                 # Wilting point (m³/m³)
Ze = 0.10                       # Evaporation layer depth (m)