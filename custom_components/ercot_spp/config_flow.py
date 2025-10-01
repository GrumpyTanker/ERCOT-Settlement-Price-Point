# ============================================================
# ERCOT SPP Configuration Flow
# ============================================================
# Handles the UI-based configuration of the ERCOT integration
#
# Features:
# - Initial setup wizard (async_step_user)
# - Options/reconfiguration flow (ERCOTOptionsFlow)
# - Input validation
# - Dropdown selectors for zone and buyback provider
#
# User Inputs:
# 1. ERCOT Pricing Zone (dropdown with labels)
# 2. Grid Export Energy Sensor (optional entity selector)
# 3. Buyback Rate Provider (Tesla Electric 90%, Full Rate 100%, or Custom)
# 4. Custom Percentage (only visible if Custom selected)
#
# Author: Your Name
# License: MIT
# ============================================================

"""Config flow for ERCOT SPP integration."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import DOMAIN, ZONES


# ============================================================
# Initial Configuration Flow
# ============================================================

class ERCOTConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ERCOT SPP.
    
    This class creates the initial setup wizard that appears when
    users add the integration via Settings → Devices & Services → Add Integration.
    """

    VERSION = 1  # Config flow version (increment if changing schema)

    async def async_step_user(self, user_input=None):
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler.
        
        This enables the "Configure" button in the UI after setup.
        
        Args:
            config_entry: The existing configuration entry
            
        Returns:
            ERCOTOptionsFlow: Options flow handler
        """
        return ERCOTOptionsFlow(config_entry)


# ============================================================
# Options Flow (Reconfiguration)
# ============================================================

class ERCOTOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for ERCOT SPP.
    
    This allows users to change settings after initial setup without
    removing and re-adding the integration. Accessed via the "Configure"
    button on the integration card.
    """

    def __init__(self, config_entry):
        """Initialize options flow.
        
        Args:
            config_entry: The existing configuration to modify
        """
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options.
        
        Args:
            user_input: Dictionary of user changes (None on first display)
            
        Returns:
            FlowResult: Either shows form or updates the config
        """
        if user_input is not None:
            # --------------------------------------------------------
            # Convert buyback provider to percentage (same logic as initial setup)
            # --------------------------------------------------------
            if user_input["buyback_provider"] == "Tesla Electric":
                user_input["sellback_percent"] = 90
            elif user_input["buyback_provider"] == "Custom":
                user_input["sellback_percent"] = user_input.get("custom_percent", 100)
            else:
                user_input["sellback_percent"] = 100
                
            # Update the configuration
            return self.async_create_entry(title="", data=user_input)

        # --------------------------------------------------------
        # Get current values from config
        # --------------------------------------------------------
        current_provider = self.config_entry.data.get("buyback_provider", "Tesla Electric")
        current_percent = self.config_entry.data.get("sellback_percent", 90)

        # --------------------------------------------------------
        # Define the options form (similar to initial setup but without zone)
        # Note: Zone cannot be changed after setup (would require new device)
        # --------------------------------------------------------
        data_schema = vol.Schema(
            {
                # Export Entity Selector
                vol.Optional(
                    "export_entity",
                    default=self.config_entry.data.get("export_entity"),
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        device_class="energy",
                    )
                ),
                
                # Buyback Provider
                vol.Required("buyback_provider", default=current_provider): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {"label": "Tesla Electric (90% of SPP)", "value": "Tesla Electric"},
                            {"label": "100% of SPP", "value": "Full Rate"},
                            {"label": "Custom Percentage", "value": "Custom"},
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                
                # Custom Percentage
                vol.Optional("custom_percent", default=current_percent): vol.All(
                    selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=100,
                            unit_of_measurement="%",
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    )
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)


# ============================================================
# Constants File
# ============================================================

# custom_components/ercot_spp/const.py
"""Constants for the ERCOT SPP integration.

This file contains all constant values used throughout the integration.
Keeping constants in one place makes them easier to maintain and update.
"""

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
]"""Handle the initial configuration step.
        
        Args:
            user_input: Dictionary of user selections (None on first display)
            
        Returns:
            FlowResult: Either shows the form or creates the config entry
        """
        errors = {}

        # If user has submitted the form
        if user_input is not None:
            # Ensure only one instance per zone
            await self.async_set_unique_id(user_input["zone"])
            self._abort_if_unique_id_configured()
            
            # --------------------------------------------------------
            # Convert buyback provider selection to percentage
            # --------------------------------------------------------
            if user_input["buyback_provider"] == "Tesla Electric":
                # Tesla Electric pays 90% of SPP
                user_input["sellback_percent"] = 90
            elif user_input["buyback_provider"] == "Custom":
                # Use custom percentage from input
                user_input["sellback_percent"] = user_input.get("custom_percent", 100)
            else:
                # Full Rate = 100% of SPP
                user_input["sellback_percent"] = 100
            
            # Create the config entry
            return self.async_create_entry(
                title=f"ERCOT {user_input['zone']}",
                data=user_input,
            )

        # --------------------------------------------------------
        # Define the configuration form schema
        # --------------------------------------------------------
        data_schema = vol.Schema(
            {
                # ERCOT Pricing Zone Selection
                vol.Required("zone", default="LZ_NORTH"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            # Load Zones (most common for residential)
                            {"label": "LZ North (Default)", "value": "LZ_NORTH"},
                            {"label": "LZ South", "value": "LZ_SOUTH"},
                            {"label": "LZ Houston", "value": "LZ_HOUSTON"},
                            {"label": "LZ West", "value": "LZ_WEST"},
                            {"label": "LZ AEN", "value": "LZ_AEN"},
                            {"label": "LZ CPS", "value": "LZ_CPS"},
                            {"label": "LZ LCRA", "value": "LZ_LCRA"},
                            {"label": "LZ Rayburn", "value": "LZ_RAYBN"},
                            # Hub Zones (typically for commercial/wholesale)
                            {"label": "Hub Bus Average", "value": "HB_BUSAVG"},
                            {"label": "Hub Houston", "value": "HB_HOUSTON"},
                            {"label": "Hub Average", "value": "HB_HUBAVG"},
                            {"label": "Hub North", "value": "HB_NORTH"},
                            {"label": "Hub Panhandle", "value": "HB_PAN"},
                            {"label": "Hub South", "value": "HB_SOUTH"},
                            {"label": "Hub West", "value": "HB_WEST"},
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                
                # Grid Export Energy Sensor (optional)
                # This is typically a sensor from your solar/battery system
                # that tracks kWh exported to the grid
                vol.Optional("export_entity"): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",  # Must be a sensor
                        device_class="energy",  # Must track energy
                    )
                ),
                
                # Buyback Rate Provider Selection
                vol.Required("buyback_provider", default="Tesla Electric"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {"label": "Tesla Electric (90% of SPP)", "value": "Tesla Electric"},
                            {"label": "100% of SPP", "value": "Full Rate"},
                            {"label": "Custom Percentage", "value": "Custom"},
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                
                # Custom Percentage Input (only relevant if Custom selected)
                vol.Optional("custom_percent", default=90): vol.All(
                    selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,    # Minimum 1%
                            max=100,  # Maximum 100%
                            unit_of_measurement="%",
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    )
                ),
            }
        )

        # Display the configuration form
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "zone_help": "Select your ERCOT pricing zone",
                "export_help": "Select the sensor that tracks your grid export energy (kWh)",
                "buyback_help": "Select your utility's buyback rate",
            }# custom_components/ercot_spp/config_flow.py
"""Config flow for ERCOT SPP integration."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import DOMAIN, ZONES

class ERCOTConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ERCOT SPP."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input["zone"])
            self._abort_if_unique_id_configured()
            
            # Set sellback percentage based on provider selection
            if user_input["buyback_provider"] == "Tesla Electric":
                user_input["sellback_percent"] = 90
            elif user_input["buyback_provider"] == "Custom":
                user_input["sellback_percent"] = user_input.get("custom_percent", 100)
            else:
                user_input["sellback_percent"] = 100
            
            return self.async_create_entry(
                title=f"ERCOT {user_input['zone']}",
                data=user_input,
            )

        data_schema = vol.Schema(
            {
                vol.Required("zone", default="LZ_NORTH"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {"label": "LZ North (Default)", "value": "LZ_NORTH"},
                            {"label": "LZ South", "value": "LZ_SOUTH"},
                            {"label": "LZ Houston", "value": "LZ_HOUSTON"},
                            {"label": "LZ West", "value": "LZ_WEST"},
                            {"label": "LZ AEN", "value": "LZ_AEN"},
                            {"label": "LZ CPS", "value": "LZ_CPS"},
                            {"label": "LZ LCRA", "value": "LZ_LCRA"},
                            {"label": "LZ Rayburn", "value": "LZ_RAYBN"},
                            {"label": "Hub Bus Average", "value": "HB_BUSAVG"},
                            {"label": "Hub Houston", "value": "HB_HOUSTON"},
                            {"label": "Hub Average", "value": "HB_HUBAVG"},
                            {"label": "Hub North", "value": "HB_NORTH"},
                            {"label": "Hub Panhandle", "value": "HB_PAN"},
                            {"label": "Hub South", "value": "HB_SOUTH"},
                            {"label": "Hub West", "value": "HB_WEST"},
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional("export_entity"): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        device_class="energy",
                    )
                ),
                vol.Required("buyback_provider", default="Tesla Electric"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {"label": "Tesla Electric (90% of SPP)", "value": "Tesla Electric"},
                            {"label": "100% of SPP", "value": "Full Rate"},
                            {"label": "Custom Percentage", "value": "Custom"},
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional("custom_percent", default=90): vol.All(
                    selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=100,
                            unit_of_measurement="%",
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "zone_help": "Select your ERCOT pricing zone",
                "export_help": "Select the sensor that tracks your grid export energy (kWh)",
                "buyback_help": "Select your utility's buyback rate",
            }
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return ERCOTOptionsFlow(config_entry)


class ERCOTOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for ERCOT SPP."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            # Update sellback percentage based on provider
            if user_input["buyback_provider"] == "Tesla Electric":
                user_input["sellback_percent"] = 90
            elif user_input["buyback_provider"] == "Custom":
                user_input["sellback_percent"] = user_input.get("custom_percent", 100)
            else:
                user_input["sellback_percent"] = 100
                
            return self.async_create_entry(title="", data=user_input)

        current_provider = self.config_entry.data.get("buyback_provider", "Tesla Electric")
        current_percent = self.config_entry.data.get("sellback_percent", 90)

        data_schema = vol.Schema(
            {
                vol.Optional(
                    "export_entity",
                    default=self.config_entry.data.get("export_entity"),
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        device_class="energy",
                    )
                ),
                vol.Required("buyback_provider", default=current_provider): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {"label": "Tesla Electric (90% of SPP)", "value": "Tesla Electric"},
                            {"label": "100% of SPP", "value": "Full Rate"},
                            {"label": "Custom Percentage", "value": "Custom"},
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional("custom_percent", default=current_percent): vol.All(
                    selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=100,
                            unit_of_measurement="%",
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    )
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)


# custom_components/ercot_spp/const.py
"""Constants for the ERCOT SPP integration."""

DOMAIN = "ercot_spp"

ZONES = [
    "HB_BUSAVG",
    "HB_HOUSTON",
    "HB_HUBAVG",
    "HB_NORTH",
    "HB_PAN",
    "HB_SOUTH",
    "HB_WEST",
    "LZ_AEN",
    "LZ_CPS",
    "LZ_HOUSTON",
    "LZ_LCRA",
    "LZ_NORTH",
    "LZ_RAYBN",
    "LZ_SOUTH",
    "LZ_WEST",
]