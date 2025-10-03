# ============================================================
# ERCOT SPP Sensor Platform
# ============================================================
# Defines all sensor entities for the ERCOT integration
#
# This module creates Home Assistant sensor entities that display
# ERCOT pricing data in various formats for user convenience.
#
# Sensors created:
# 1. Price ($/MWh) - Raw ERCOT settlement point price
# 2. Price (¢/kWh) - Price converted to cents per kilowatt-hour
# 3. Last Updated - Timestamp of last price update
# 4. Sellback Rate ($/kWh) - Rate paid for exported energy
# 5. Sellback Rate (¢/kWh) - Same as above in cents
# 6. Sellback Earnings - Lifetime earnings from exports (optional)
#
# Architecture:
# - Base class (ERCOTBaseSensor) provides common functionality
# - Individual sensor classes inherit from base class
# - All sensors are grouped under one device in HA UI
# - Sensors automatically update when coordinator fetches new data
#
# For AI Agents:
# - To add a new sensor, create a class inheriting from ERCOTBaseSensor
# - Define unique_id, name, unit, state_class, and icon
# - Implement native_value property to return data from coordinator
# - Add sensor to list in async_setup_entry()
#
# Author: GrumpyTanker
# License: MIT
# Repository: https://github.com/GrumpyTanker/ERCOT-Settlement-Price-Point
# ============================================================

"""ERCOT SPP Sensor Platform.

This module defines all sensor entities for displaying ERCOT electricity
pricing data in Home Assistant. Sensors are created through the platform
setup function and automatically receive updates from the data coordinator.
"""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy, CURRENCY_DOLLAR
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MWH_TO_KWH, DOLLARS_TO_CENTS


# ============================================================
# Platform Setup
# ============================================================

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ERCOT SPP sensors from a config entry.
    
    This function is called automatically when the integration is loaded.
    It creates all sensor entities and adds them to Home Assistant.
    
    Args:
        hass: Home Assistant instance
        entry: Config entry containing user configuration
        async_add_entities: Callback to add entities to HA
    """
    # Get the data coordinator from hass.data
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Create list of sensor entities
    sensors = [
        ERCOTPriceSensor(coordinator, entry),           # $/MWh
        ERCOTTimestampSensor(coordinator, entry),       # Last Updated
        ERCOTPriceCentsKwhSensor(coordinator, entry),   # ¢/kWh
        ERCOTSellbackRateSensor(coordinator, entry),    # Sellback $/kWh
        ERCOTSellbackCentsSensor(coordinator, entry),   # Sellback ¢/kWh
    ]
    
    # Add earnings sensor only if user provided an export entity
    if coordinator.export_entity:
        sensors.append(ERCOTEarningsSensor(coordinator, entry))
    
    # Register all sensors with Home Assistant
    async_add_entities(sensors)


# ============================================================
# Base Sensor Class
# ============================================================

class ERCOTBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for all ERCOT sensors.
    
    This class provides common functionality:
    - Connection to the data coordinator
    - Device information (groups sensors under one device)
    - Automatic updates when coordinator fetches new data
    """
    
    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize the base sensor.
        
        Args:
            coordinator: Data coordinator that fetches ERCOT prices
            entry: Config entry with user settings
        """
        super().__init__(coordinator)
        self._entry = entry
        self._attr_has_entity_name = True  # Use device name + sensor name
        
        # Create device info - all sensors will be grouped under this device
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"ERCOT {coordinator.zone}",
            manufacturer="ERCOT",
            model=coordinator.zone,
            configuration_url="https://www.ercot.com/content/cdr/html/real_time_spp.html",
        )


# ============================================================
# Individual Sensor Definitions
# ============================================================

class ERCOTPriceSensor(ERCOTBaseSensor):
    """ERCOT Settlement Point Price in $/MWh.
    
    This is the raw price directly from ERCOT's real-time feed.
    Example: 14.72 means $14.72 per megawatt-hour.
    """
    
    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize price sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_price_mwh"
        self._attr_name = "Price"
        self._attr_native_unit_of_measurement = "$/MWh"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:currency-usd"
    
    @property
    def native_value(self):
        """Return the current price in $/MWh."""
        return self.coordinator.data.get("price_mwh")


class ERCOTTimestampSensor(ERCOTBaseSensor):
    """ERCOT Last Updated timestamp.
    
    Shows when ERCOT last updated the prices.
    Updates every 5 minutes with new price intervals.
    """
    
    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize timestamp sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_timestamp"
        self._attr_name = "Last Updated"
        self._attr_icon = "mdi:clock-outline"
    
    @property
    def native_value(self):
        """Return the last update timestamp."""
        return self.coordinator.data.get("timestamp")


class ERCOTPriceCentsKwhSensor(ERCOTBaseSensor):
    """ERCOT Price converted to cents per kilowatt-hour.
    
    This converts the $/MWh price to the more familiar ¢/kWh unit.
    Formula: ($/MWh ÷ 1000) × 100
    Example: $14.72/MWh = 1.472 ¢/kWh
    """
    
    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize cents/kWh sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_price_cents_kwh"
        self._attr_name = "Price (¢/kWh)"
        self._attr_native_unit_of_measurement = "¢/kWh"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:flash"
    
    @property
    def native_value(self):
        """Calculate and return price in cents/kWh.
        
        Conversion formula:
        $/MWh → $/kWh (divide by 1000) → ¢/kWh (multiply by 100)
        
        Example: $14.72/MWh = $0.01472/kWh = 1.472 ¢/kWh
        """
        price_mwh = self.coordinator.data.get("price_mwh", 0)
        # Convert: $/MWh → $/kWh → ¢/kWh
        return round((price_mwh / MWH_TO_KWH) * DOLLARS_TO_CENTS, 2)


class ERCOTSellbackRateSensor(ERCOTBaseSensor):
    """Sellback rate in $/kWh.
    
    This is the rate you're paid for exported energy.
    Calculated as: SPP × (sellback_percent / 100) ÷ 1000
    
    Example for Tesla Electric (90%):
    $14.72/MWh × 0.90 = $13.248/MWh = $0.013248/kWh
    """
    
    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize sellback rate sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_sellback_rate"
        self._attr_name = "Sellback Rate"
        self._attr_native_unit_of_measurement = "$/kWh"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:cash"
    
    @property
    def native_value(self):
        """Calculate sellback rate in $/kWh.
        
        Formula: (SPP_$/MWh ÷ 1000) × (sellback_percent ÷ 100)
        
        Example for Tesla Electric (90%):
        $14.72/MWh × 0.90 = $13.248/MWh = $0.013248/kWh
        """
        price_mwh = self.coordinator.data.get("price_mwh", 0)
        percent = self.coordinator.sellback_percent / DOLLARS_TO_CENTS
        # Convert MWh to kWh and apply percentage
        return round((price_mwh / MWH_TO_KWH) * percent, 5)


class ERCOTSellbackCentsSensor(ERCOTBaseSensor):
    """Sellback rate in cents per kWh.
    
    Same as sellback rate above, but in cents for readability.
    Example: $0.013248/kWh = 1.3248 ¢/kWh
    """
    
    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize sellback cents sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_sellback_cents"
        self._attr_name = "Sellback Rate (¢/kWh)"
        self._attr_native_unit_of_measurement = "¢/kWh"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:cash-multiple"
    
    @property
    def native_value(self):
        """Calculate sellback rate in ¢/kWh.
        
        Same calculation as sellback rate in $/kWh, but converted to cents.
        
        Formula: (SPP_$/MWh ÷ 1000) × (sellback_percent ÷ 100) × 100
        
        Example: $0.013248/kWh = 1.3248 ¢/kWh
        """
        price_mwh = self.coordinator.data.get("price_mwh", 0)
        percent = self.coordinator.sellback_percent / DOLLARS_TO_CENTS
        # Convert to cents per kWh
        return round((price_mwh / MWH_TO_KWH) * percent * DOLLARS_TO_CENTS, 2)


class ERCOTEarningsSensor(ERCOTBaseSensor):
    """Lifetime earnings from grid exports.
    
    Tracks total money earned from selling energy back to the grid.
    
    How it works:
    1. Monitors the configured export energy sensor
    2. When export increases, calculates: delta_kWh × current_sellback_rate
    3. Adds to lifetime total
    4. Handles counter resets (daily/weekly resets common in solar systems)
    
    This is a total_increasing sensor, so it only goes up and is preserved
    across Home Assistant restarts.
    """
    
    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize earnings sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_earnings"
        self._attr_name = "Sellback Earnings"
        self._attr_native_unit_of_measurement = CURRENCY_DOLLAR
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_icon = "mdi:cash-check"
        
        # Track last export value and total earnings
        self._last_export = 0
        self._total = 0
    
    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator.
        
        Called automatically whenever the coordinator fetches new ERCOT prices.
        This also checks the export sensor and calculates earnings.
        """
        # Get the configured export entity
        export_entity = self.coordinator.export_entity
        
        if export_entity:
            # Get current export value from Home Assistant
            export_state = self.hass.states.get(export_entity)
            
            if export_state and export_state.state not in ["unknown", "unavailable"]:
                current_export = float(export_state.state)
                
                # Calculate change since last update
                delta = current_export - self._last_export
                
                # Handle counter reset (delta will be negative)
                # This happens when export counter resets daily/weekly
                if delta < 0:
                    delta = current_export  # Use current value as delta
                
                # Calculate earnings for this delta
                # Formula: delta_kWh × (SPP_$/MWh ÷ 1000) × (sellback_% ÷ 100)
                price_kwh = self.coordinator.data.get("price_mwh", 0) / MWH_TO_KWH
                percent = self.coordinator.sellback_percent / DOLLARS_TO_CENTS
                rate = price_kwh * percent
                
                # Add to total earnings
                self._total += delta * rate
                self._last_export = current_export
        
        # Update the entity state in Home Assistant
        self.async_write_ha_state()
    

    @property
    def native_value(self):
        """Return total earnings."""
        return round(self._total, 2)