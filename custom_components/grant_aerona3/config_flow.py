"""Unified config flow for Grant Aerona3 Heat Pump integration with installation type selection."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from pymodbus.client import ModbusTcpClient

from .const import (
    CONF_SCAN_INTERVAL,
    CONF_SLAVE_ID,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SLAVE_ID,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

# Installation type selection schema
STEP_INSTALL_TYPE_SCHEMA = vol.Schema({
    vol.Required("install_type", default="basic"): vol.In({
        "basic": "Basic Setup - Quick and simple configuration",
        "enhanced": "Enhanced Setup - Advanced features with installation templates"
    })
})

# Basic setup schema
STEP_BASIC_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): str,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
    vol.Optional(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): int,
    vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
})

# Enhanced setup - connection details
STEP_ENHANCED_CONNECTION_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): str,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
    vol.Optional(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): int,
})

# Enhanced setup - installation template selection
STEP_ENHANCED_TEMPLATE_SCHEMA = vol.Schema({
    vol.Required("installation_template", default="single_zone"): vol.In({
        "single_zone": "Single Zone Heating (Most Common - 65%)",
        "dual_zone": "Dual Zone Heating (Upstairs/Downstairs - 20%)",
        "dhw_only": "Hot Water Only (Cylinder heating - 8%)",
        "replacement": "Boiler Replacement (Full system - 5%)",
        "custom": "Custom Configuration (Advanced users - 2%)"
    })
})

# Enhanced setup - advanced options
STEP_ENHANCED_ADVANCED_SCHEMA = vol.Schema({
    vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
    vol.Optional("weather_compensation", default=True): bool,
    vol.Optional("advanced_monitoring", default=True): bool,
    vol.Optional("energy_tracking", default=True): bool,
})


async def validate_connection(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    
    def _test_connection():
        """Test connection to the Modbus device."""
        client = ModbusTcpClient(
            host=data[CONF_HOST],
            port=data[CONF_PORT],
            timeout=10
        )

        try:
            if not client.connect():
                raise CannotConnect("Failed to connect to Modbus device")

            # Try to read a register to verify communication
            result = client.read_input_registers(
                address=0,
                count=1,
                slave=data[CONF_SLAVE_ID]
            )

            if result.isError():
                raise CannotConnect("Failed to read from Modbus device")

            return True

        finally:
            client.close()

    # Test connection in executor to avoid blocking
    await hass.async_add_executor_job(_test_connection)

    # Return info that you want to store in the config entry
    return {"title": f"Grant Aerona3 ({data[CONF_HOST]})"}


class GrantAerona3ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Grant Aerona3 Heat Pump."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self.install_type = None
        self.connection_data = {}
        self.template_data = {}
        self.advanced_data = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - installation type selection."""
        if user_input is not None:
            self.install_type = user_input["install_type"]
            
            if self.install_type == "basic":
                return await self.async_step_basic()
            else:
                return await self.async_step_enhanced_connection()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_INSTALL_TYPE_SCHEMA,
            description_placeholders={
                "basic_desc": "Quick setup with default settings. Perfect for most users.",
                "enhanced_desc": "Advanced setup with installation templates, weather compensation, and detailed monitoring options."
            }
        )

    async def async_step_basic(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle basic installation setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_connection(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception as err:
                _LOGGER.exception("Unexpected exception during basic setup")
                errors["base"] = "unknown"
            else:
                # Check if already configured
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()

                # Add installation type to data
                final_data = {**user_input, "install_type": "basic"}
                
                return self.async_create_entry(
                    title=info["title"], 
                    data=final_data
                )

        return self.async_show_form(
            step_id="basic",
            data_schema=STEP_BASIC_SCHEMA,
            errors=errors,
            description_placeholders={
                "setup_type": "Basic Setup",
                "description": "Enter your heat pump's network details. Default settings work for most installations."
            }
        )

    async def async_step_enhanced_connection(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle enhanced installation - connection step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Test connection with default scan interval for validation
                test_data = {**user_input, CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL}
                await validate_connection(self.hass, test_data)
                
                # Store connection data and move to template selection
                self.connection_data = user_input
                return await self.async_step_enhanced_template()
                
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception as err:
                _LOGGER.exception("Unexpected exception during enhanced connection setup")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="enhanced_connection",
            data_schema=STEP_ENHANCED_CONNECTION_SCHEMA,
            errors=errors,
            description_placeholders={
                "setup_type": "Enhanced Setup - Step 1 of 3",
                "description": "Enter your heat pump's network details."
            }
        )

    async def async_step_enhanced_template(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle enhanced installation - template selection."""
        if user_input is not None:
            self.template_data = user_input
            return await self.async_step_enhanced_advanced()

        return self.async_show_form(
            step_id="enhanced_template",
            data_schema=STEP_ENHANCED_TEMPLATE_SCHEMA,
            description_placeholders={
                "setup_type": "Enhanced Setup - Step 2 of 3",
                "description": "Choose your installation type. This will configure optimal settings for your setup."
            }
        )

    async def async_step_enhanced_advanced(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle enhanced installation - advanced options."""
        if user_input is not None:
            self.advanced_data = user_input
            
            # Check if already configured
            await self.async_set_unique_id(self.connection_data[CONF_HOST])
            self._abort_if_unique_id_configured()

            # Combine all data
            final_data = {
                **self.connection_data,
                **self.template_data,
                **self.advanced_data,
                "install_type": "enhanced"
            }

            title = f"Grant Aerona3 ({self.connection_data[CONF_HOST]})"
            
            return self.async_create_entry(
                title=title,
                data=final_data
            )

        return self.async_show_form(
            step_id="enhanced_advanced",
            data_schema=STEP_ENHANCED_ADVANCED_SCHEMA,
            description_placeholders={
                "setup_type": "Enhanced Setup - Step 3 of 3",
                "description": "Configure advanced features and monitoring options."
            }
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
