# ============================================================
# ERCOT Real-Time Settlement Point Prices Integration
# ============================================================
# Main integration initialization file
#
# This file handles:
# - Integration setup and teardown (async_setup_entry, async_unload_entry)
# - Data coordinator initialization (ERCOTDataUpdateCoordinator)
# - Platform loading (sensors)
# - Web scraping logic for ERCOT price data
#
# Data Flow:
# 1. Config entry created via config_flow.py
# 2. async_setup_entry() creates coordinator
# 3. Coordinator fetches data every 5 minutes from ERCOT website
# 4. Sensors (sensor.py) display data from coordinator
#
# Web Scraping Details:
# - Target URL: https://www.ercot.com/content/cdr/html/real_time_spp.html
# - Method: HTML table parsing using regex
# - Update frequency: Every 5 minutes
# - Data format: Last 17 cells = [date, time, 15 price zones]
#
# For AI Agents:
# - All data fetching logic is in ERCOTDataUpdateCoordinator._async_update_data()
# - Zone mapping is in zone_map dictionary (line ~179)
# - To add zones: update zone_map, const.py, and config_flow.py
# - Error handling uses Home Assistant's coordinator pattern
#
# Author: GrumpyTanker
# License: MIT
# Repository: https://github.com/GrumpyTanker/ERCOT-Settlement-Price-Point
# ============================================================

"""ERCOT Real-Time Settlement Point Prices Integration.

This integration provides real-time electricity pricing data from ERCOT
(Electric Reliability Council of Texas) for Home Assistant users.

The integration scrapes ERCOT's public Settlement Point Price (SPP) data
and creates sensors for price tracking and solar/battery sellback calculations.
"""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, ERCOT_DATA_URL, DEFAULT_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

# Define which platforms this integration provides
PLATFORMS: list[Platform] = [Platform.SENSOR]


# ============================================================
# Integration Setup
# ============================================================

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ERCOT SPP from a config entry.
    
    This is called when the integration is added via the UI.
    
    Args:
        hass: Home Assistant instance
        entry: Configuration entry containing user selections
        
    Returns:
        bool: True if setup was successful
    """
    
    # Create the data coordinator that will fetch ERCOT prices
    coordinator = ERCOTDataUpdateCoordinator(
        hass,
        zone=entry.data["zone"],
        export_entity=entry.data.get("export_entity"),
        sellback_percent=entry.data.get("sellback_percent", 90),
    )
    
    # Perform initial data fetch
    await coordinator.async_config_entry_first_refresh()
    
    # Store coordinator in hass.data for access by platforms
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Set up all platforms (currently just sensors)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry.
    
    Called when the integration is removed via the UI.
    
    Args:
        hass: Home Assistant instance
        entry: Configuration entry being removed
        
    Returns:
        bool: True if unload was successful
    """
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok


# ============================================================
# Data Update Coordinator
# ============================================================

class ERCOTDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching ERCOT price data.
    
    This coordinator handles:
    - Periodic polling of ERCOT website (every 5 minutes)
    - HTML parsing to extract price data
    - Error handling and retries
    - Data distribution to all sensors
    """
    
    def __init__(
        self,
        hass: HomeAssistant,
        zone: str,
        export_entity: str | None,
        sellback_percent: int,
    ) -> None:
        """Initialize the coordinator.
        
        Args:
            hass: Home Assistant instance
            zone: ERCOT pricing zone (e.g., "LZ_NORTH")
            export_entity: Entity ID of grid export sensor (optional)
            sellback_percent: Percentage of SPP paid for exports (e.g., 90)
        """
        self.zone = zone
        self.export_entity = export_entity
        self.sellback_percent = sellback_percent
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            # Update every 5 minutes to match ERCOT's data publication frequency
            update_interval=timedelta(minutes=DEFAULT_UPDATE_INTERVAL),
        )
    
    async def _async_update_data(self):
        """Fetch data from ERCOT.
        
        This method is called automatically every 5 minutes by the coordinator.
        
        Returns:
            dict: Parsed data containing price, timestamp, etc.
            
        Raises:
            Exception: If data cannot be fetched or parsed
        """
        import aiohttp
        import re
        
        # --------------------------------------------------------
        # Fetch HTML from ERCOT website
        # --------------------------------------------------------
        # ERCOT publishes real-time Settlement Point Prices (SPP) as an HTML table
        # Updated approximately every 5 minutes with 15-minute interval prices
        async with aiohttp.ClientSession() as session:
            async with session.get(ERCOT_DATA_URL) as response:
                html = await response.text()
        
        # --------------------------------------------------------
        # Extract timestamp (e.g., "Oct 01, 2025 10:17")
        # --------------------------------------------------------
        # The ERCOT page includes a "Last Updated:" text followed by timestamp
        # Regex pattern: Look for text after "Last Updated: " until < or newline
        timestamp_match = re.search(r'Last Updated: ([^<\n]+)', html)
        timestamp = timestamp_match.group(1) if timestamp_match else None
        
        # --------------------------------------------------------
        # Extract all table cells from the HTML
        # --------------------------------------------------------
        # Regex pattern breakdown:
        # - <td[^>]*>  : Matches opening <td> tag with any attributes
        # - ([^<]+)    : Captures text content (anything except <)
        # - </td>      : Matches closing tag
        # - re.IGNORECASE : Case-insensitive matching
        #
        # This extracts all cell values from the HTML table.
        # The table contains multiple rows of historical prices.
        cells = re.findall(r'<td[^>]*>([^<]+)</td>', html, re.IGNORECASE)
        
        # Validate we have enough data
        # Minimum 17 cells needed: 1 date + 1 time + 15 price zones
        if len(cells) < 17:
            raise Exception("Not enough data cells found in ERCOT table")
        
        # --------------------------------------------------------
        # Get the last 17 cells (the most recent price row)
        # Each row has 17 columns: date, time, and 15 price zones
        # --------------------------------------------------------
        last_row = cells[-17:]
        
        # --------------------------------------------------------
        # Map zone names to column positions (0-indexed)
        # --------------------------------------------------------
        # Each row in the ERCOT table has 17 columns:
        # [0] = Date (MM/DD/YYYY)
        # [1] = Time (HHMM format, e.g., "1015" = 10:15 AM)
        # [2-16] = Price zones (15 total)
        #
        # Column order matches ERCOT's official table structure.
        # IMPORTANT: This mapping must match the actual column order on ERCOT website.
        # If ERCOT changes their table structure, this map needs updating.
        #
        # For AI Agents: When adding new zones, update this map, const.py ZONES list,
        # and config_flow.py dropdown options.
        zone_map = {
            "HB_BUSAVG": 2,    # Hub Bus Average
            "HB_HOUSTON": 3,   # Houston Hub
            "HB_HUBAVG": 4,    # Hub Average
            "HB_NORTH": 5,     # North Hub
            "HB_PAN": 6,       # Panhandle Hub
            "HB_SOUTH": 7,     # South Hub
            "HB_WEST": 8,      # West Hub
            "LZ_AEN": 9,       # AEP Central Load Zone
            "LZ_CPS": 10,      # CPS Energy Load Zone
            "LZ_HOUSTON": 11,  # Houston Load Zone
            "LZ_LCRA": 12,     # LCRA Load Zone
            "LZ_NORTH": 13,    # North Load Zone (most common residential)
            "LZ_RAYBN": 14,    # Rayburn Load Zone
            "LZ_SOUTH": 15,    # South Load Zone
            "LZ_WEST": 16,     # West Load Zone
        }
        
        # Get the column index for the configured zone
        # Falls back to LZ_NORTH (column 13) if zone not found
        col_idx = zone_map.get(self.zone, 13)
        
        # Extract and convert price to float
        price = float(last_row[col_idx])
        
        # Return parsed data for sensors to use
        return {
            "price_mwh": price,           # Price in $/MWh
            "timestamp": timestamp,       # Last update time
            "date": last_row[0],         # Date (MM/DD/YYYY)
            "time": last_row[1],         # Time (HHMM)
        }