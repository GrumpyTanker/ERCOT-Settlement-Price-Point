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

from .const import DOMAIN


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
            await self.async_set_unique_id(user_input["zone"])
            self._abort_if_unique_id_configured()
            
            # Convert buyback provider selection to percentage
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