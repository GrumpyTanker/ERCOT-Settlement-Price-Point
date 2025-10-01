# ============================================================
# ERCOT Real-Time Settlement Point Prices Integration
# ============================================================
# Main integration initialization file
#
# This file handles:
# - Integration setup and teardown
# - Data coordinator initialization
# - Platform loading (sensors)
# - Web scraping logic for ERCOT price data
#
# Author: GrumpyTanker
# License: MIT
# ============================================================

"""ERCOT Real-Time Settlement Point Prices Integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN

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
            update_interval=timedelta(minutes=5),  # Update every 5 minutes
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
        
        # ERCOT's real-time SPP page URL
        url = "https://www.ercot.com/content/cdr/html/real_time_spp.html"
        
        # Fetch the HTML page
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()
        
        # --------------------------------------------------------
        # Extract timestamp (e.g., "Oct 01, 2025 10:17")
        # --------------------------------------------------------
        timestamp_match = re.search(r'Last Updated: ([^<\n]+)', html)
        timestamp = timestamp_match.group(1) if timestamp_match else None
        
        # --------------------------------------------------------
        # Extract all table cells from the HTML
        # Pattern matches: <td>VALUE</td>
        # --------------------------------------------------------
        cells = re.findall(r'<td[^>]*>([^<]+)</td>', html, re.IGNORECASE)
        
        if len(cells) < 17:
            raise Exception("Not enough data cells found in ERCOT table")
        
        # --------------------------------------------------------
        # Get the last 17 cells (the most recent price row)
        # Each row has 17 columns: date, time, and 15 price zones
        # --------------------------------------------------------
        last_row = cells[-17:]
        
        # --------------------------------------------------------
        # Map zone names to column positions (0-indexed)
        # Position 0 = Date, Position 1 = Time
        # Prices start at position 2
        # --------------------------------------------------------
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
            "LZ_NORTH": 13,    # North Load Zone (most common)
            "LZ_RAYBN": 14,    # Rayburn Load Zone
            "LZ_SOUTH": 15,    # South Load Zone
            "LZ_WEST": 16,     # West Load Zone
        }
        
        # Get the column index for the configured zone
        col_idx = zone_map.get(self.zone, 13)  # Default to LZ_NORTH
        
        # Extract and convert price to float
        price = float(last_row[col_idx])
        
        # Return parsed data for sensors to use
        return {
            "price_mwh": price,           # Price in $/MWh
            "timestamp": timestamp,       # Last update time
            "date": last_row[0],         # Date (MM/DD/YYYY)
            "time": last_row[1],         # Time (HHMM)
        }