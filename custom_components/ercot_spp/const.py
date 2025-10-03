# ============================================================
# Constants for ERCOT SPP Integration
# ============================================================
# This file contains all constant values used throughout the integration.
# Keeping constants in one place makes them easier to maintain and update.
#
# Purpose:
# - Define integration domain name for Home Assistant registration
# - List all supported ERCOT pricing zones with descriptions
# - Provide zone mapping for data extraction
#
# For AI Agents:
# - Add new zones here and update zone_map in __init__.py
# - Zone identifiers must match ERCOT's official naming
# - Maintain alphabetical order within Load and Hub sections
#
# Author: GrumpyTanker
# License: MIT
# Repository: https://github.com/GrumpyTanker/ERCOT-Settlement-Price-Point
# ============================================================

"""Constants for the ERCOT SPP integration.

This module defines all constant values used across the integration,
including the domain identifier and supported ERCOT pricing zones.
"""

# --------------------------------------------------------
# Integration Domain
# --------------------------------------------------------
# This unique identifier registers the integration with Home Assistant
# and is used for entity_id prefixes and internal data storage
DOMAIN = "ercot_spp"

# --------------------------------------------------------
# ERCOT Pricing Zones
# --------------------------------------------------------
# These are the official zone identifiers used by ERCOT for
# Settlement Point Prices (SPP) in the Texas electricity market.
#
# Load Zones (LZ):
#   Represent geographical areas where electricity is delivered to
#   end consumers. Residential and small commercial users typically
#   reference these zones for pricing.
#
# Hub Zones (HB):
#   Represent wholesale market hubs used for commercial trading
#   and large-scale electricity transactions.
#
# Geographic Coverage:
#   ERCOT serves ~90% of Texas electric load, excluding
#   El Paso, upper Panhandle, and parts of East Texas.

ZONES = [
    # --------------------------------------------------------
    # Load Zones (8 zones)
    # --------------------------------------------------------
    "LZ_AEN",      # AEP Central Load Zone (Central/East Texas)
    "LZ_CPS",      # CPS Energy Load Zone (San Antonio area)
    "LZ_HOUSTON",  # Houston Load Zone (Greater Houston metropolitan)
    "LZ_LCRA",     # LCRA Load Zone (Austin/Colorado River area)
    "LZ_NORTH",    # North Load Zone (DFW, Waco, Abilene) - Most common
    "LZ_RAYBN",    # Rayburn Load Zone (Rayburn Country Electric)
    "LZ_SOUTH",    # South Load Zone (Corpus Christi, Laredo)
    "LZ_WEST",     # West Load Zone (Midland, Odessa)
    
    # --------------------------------------------------------
    # Hub Zones (7 zones)
    # --------------------------------------------------------
    "HB_BUSAVG",   # Hub Bus Average (Average of all hub prices)
    "HB_HOUSTON",  # Houston Hub (Wholesale Houston trading hub)
    "HB_HUBAVG",   # Hub Average (Average of major hubs)
    "HB_NORTH",    # North Hub (Wholesale North Texas trading hub)
    "HB_PAN",      # Panhandle Hub (Panhandle wind generation hub)
    "HB_SOUTH",    # South Hub (South Texas trading hub)
    "HB_WEST",     # West Hub (West Texas trading hub)
]

# --------------------------------------------------------
# Configuration Defaults
# --------------------------------------------------------
# Default values used during initial integration setup
DEFAULT_ZONE = "LZ_NORTH"           # Most common residential zone
DEFAULT_UPDATE_INTERVAL = 5         # Minutes between ERCOT data fetches
DEFAULT_SELLBACK_PERCENT = 90       # Tesla Electric default (90% of SPP)

# --------------------------------------------------------
# Data Source Configuration
# --------------------------------------------------------
# ERCOT's public real-time Settlement Point Price page
ERCOT_DATA_URL = "https://www.ercot.com/content/cdr/html/real_time_spp.html"

# Data update frequency on ERCOT website
# ERCOT publishes 15-minute interval prices updated approximately every 5 minutes
ERCOT_UPDATE_FREQUENCY = "5 minutes"

# --------------------------------------------------------
# Sensor Configuration
# --------------------------------------------------------
# Unit conversions for price sensors
MWH_TO_KWH = 1000.0                # 1 MWh = 1000 kWh
DOLLARS_TO_CENTS = 100.0            # $1 = 100 cents