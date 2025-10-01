# ============================================================
# Constants for ERCOT SPP Integration
# ============================================================
# This file contains all constant values used throughout the integration.
# Keeping constants in one place makes them easier to maintain and update.
#
# Author: GrumpyTanker
# License: MIT
# ============================================================

"""Constants for the ERCOT SPP integration."""

# --------------------------------------------------------
# Integration Domain
# --------------------------------------------------------
DOMAIN = "ercot_spp"

# --------------------------------------------------------
# ERCOT Pricing Zones
# --------------------------------------------------------
# These are the official zone identifiers used by ERCOT
# Load Zones (LZ) - Residential and small commercial typically use these
# Hub Zones (HB) - Wholesale markets and large commercial

ZONES = [
    # Load Zones
    "LZ_AEN",      # AEP Central Load Zone
    "LZ_CPS",      # CPS Energy Load Zone
    "LZ_HOUSTON",  # Houston Load Zone
    "LZ_LCRA",     # LCRA Load Zone
    "LZ_NORTH",    # North Load Zone (most common residential)
    "LZ_RAYBN",    # Rayburn Load Zone
    "LZ_SOUTH",    # South Load Zone
    "LZ_WEST",     # West Load Zone
    
    # Hub Zones
    "HB_BUSAVG",   # Hub Bus Average
    "HB_HOUSTON",  # Houston Hub
    "HB_HUBAVG",   # Hub Average
    "HB_NORTH",    # North Hub
    "HB_PAN",      # Panhandle Hub
    "HB_SOUTH",    # South Hub
    "HB_WEST",     # West Hub
]