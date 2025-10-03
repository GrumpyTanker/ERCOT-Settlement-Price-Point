# ============================================================
# ERCOT SPP Configuration Flow
# ============================================================
# Handles the UI-based configuration of the ERCOT integration
#
# This module creates the setup wizard and options dialog that users
# interact with in the Home Assistant UI.
#
# Configuration Flow (ERCOTConfigFlow):
# - Initial setup wizard shown when adding integration
# - Collects: zone, export sensor, buyback provider, custom percentage
# - Creates unique config entry per zone
# - Cannot add same zone twice (unique_id = zone)
#
# Options Flow (ERCOTOptionsFlow):
# - Allows reconfiguring export sensor and buyback percentage
# - Cannot change zone (must remove and re-add integration)
# - Accessed via "Configure" button in Integrations UI
#
# Features:
# - Dropdown selectors for zone and buyback provider
# - Entity selector for export sensor (filters to energy sensors)
# - Number input for custom percentage (1-100%)
# - Automatic conversion of provider selection to percentage
#
# User Inputs:
# 1. ERCOT Pricing Zone (required, 15 options)
# 2. Grid Export Energy Sensor (optional, entity selector)
# 3. Buyback Rate Provider (required, 3 options)
# 4. Custom Percentage (optional, only if Custom provider selected)
#
# Data Validation:
# - Zone must be one of 15 valid ERCOT zones
# - Export entity must have device_class: energy
# - Custom percentage must be 1-100
# - Duplicate zones prevented via unique_id check
#
# For AI Agents:
# - Provider selection is UI-friendly, stored as sellback_percent integer
# - Zone list must match const.py ZONES and __init__.py zone_map
# - To add zones: update dropdown options, const.py, and __init__.py
#
# Author: GrumpyTanker
# License: MIT
# Repository: https://github.com/GrumpyTanker/ERCOT-Settlement-Price-Point
# ============================================================

"""Config flow for ERCOT SPP integration.

This module handles user interaction for configuring the ERCOT integration
through the Home Assistant UI, including both initial setup and reconfiguration.
"""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import DOMAIN, DEFAULT_ZONE, DEFAULT_SELLBACK_PERCENT


# ============================================================
# Initial Configuration Flow
# ============================================================

class ERCOTConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ERCOT SPP.
    
    This class creates the initial setup wizard that appears when
    users add the integration via Settings → Devices & Services → Add Integration.
    """

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial configuration step.
        
        Args:
            user_input: Dictionary of user selections (None on first display)
            
        Returns:
            FlowResult: Either shows the form or creates the config entry
        """
        errors = {}

        if user_input is not None:
            # Use zone as unique_id to prevent duplicate configurations
            # This ensures users can only add each zone once
            await self.async_set_unique_id(user_input["zone"])
            self._abort_if_unique_id_configured()
            
            # Convert user-friendly provider selection to percentage value
            # This allows for easy UI selection while storing practical numeric value
            if user_input["buyback_provider"] == "Tesla Electric":
                user_input["sellback_percent"] = 90  # Tesla Electric pays 90% of SPP
            elif user_input["buyback_provider"] == "Custom":
                user_input["sellback_percent"] = user_input.get("custom_percent", 100)
            else:  # "Full Rate"
                user_input["sellback_percent"] = 100  # 100% of SPP
            
            # Create the config entry - this will trigger async_setup_entry in __init__.py
            return self.async_create_entry(
                title=f"ERCOT {user_input['zone']}",
                data=user_input,
            )

        # Build the configuration form schema
        # Using Home Assistant's selector system for modern UI components
        data_schema = vol.Schema(
            {
                vol.Required("zone", default=DEFAULT_ZONE): selector.SelectSelector(
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
                vol.Optional("custom_percent", default=DEFAULT_SELLBACK_PERCENT): vol.All(
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
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return ERCOTOptionsFlow(config_entry)


# ============================================================
# Options Flow (Reconfiguration)
# ============================================================

class ERCOTOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for ERCOT SPP."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        super().__init__()
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
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