"""Enhanced config flow for Grant Aerona3 Heat Pump integration."""
from __future__ import annotations

import logging
import re
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


class InstallationTemplate:
    """Installation template for Grant Aerona3 configurations."""
    
    def __init__(
        self,
        template_id: str,
        name: str,
        description: str,
        percentage: str,
        common: bool,
        default_config: Dict[str, Any]
    ):
        """Initialize installation template."""
        self.template_id = template_id
        self.name = name
        self.description = description
        self.percentage = percentage
        self.common = common
        self.default_config = default_config


# Installation templates based on Grant Aerona3 common configurations
INSTALLATION_TEMPLATES = {
    "single_zone_basic": InstallationTemplate(
        template_id="single_zone_basic",
        name="Basic Single Zone",
        description="One heating zone, no hot water cylinder",
        percentage="35%",
        common=True,
        default_config={
            "zones": {
                "zone_1": {"enabled": True, "name": "Main Zone"},
                "zone_2": {"enabled": False, "name": "Second Zone"}
            },
            "dhw_cylinder": False,
            "backup_heater": False,
            "weather_compensation": True,
            "flow_rate_method": "fixed_rate",
            "flow_rate": 20,
            "advanced_features": False,
            "diagnostic_monitoring": False
        }
    ),
    "single_zone_dhw": InstallationTemplate(
        template_id="single_zone_dhw",
        name="Single Zone + Hot Water",
        description="One heating zone with hot water cylinder",
        percentage="50%",
        common=True,
        default_config={
            "zones": {
                "zone_1": {"enabled": True, "name": "Main Zone"},
                "zone_2": {"enabled": False, "name": "Second Zone"}
            },
            "dhw_cylinder": True,
            "backup_heater": True,
            "weather_compensation": True,
            "flow_rate_method": "fixed_rate",
            "flow_rate": 22,
            "advanced_features": False,
            "diagnostic_monitoring": False
        }
    ),
    "dual_zone_system": InstallationTemplate(
        template_id="dual_zone_system",
        name="Two Zone System",
        description="Separate upstairs/downstairs or UFH/radiators",
        percentage="10%",
        common=False,
        default_config={
            "zones": {
                "zone_1": {"enabled": True, "name": "Downstairs"},
                "zone_2": {"enabled": True, "name": "Upstairs"}
            },
            "dhw_cylinder": True,
            "backup_heater": True,
            "weather_compensation": True,
            "dual_weather_compensation": True,
            "flow_rate_method": "fixed_rate",
            "flow_rate": 25,
            "advanced_features": True,
            "diagnostic_monitoring": False
        }
    ),
    "replacement_system": InstallationTemplate(
        template_id="replacement_system",
        name="Boiler Replacement",
        description="Replacing existing boiler, keeping radiators",
        percentage="15%",
        common=True,
        default_config={
            "zones": {
                "zone_1": {"enabled": True, "name": "Main Zone"},
                "zone_2": {"enabled": False, "name": "Second Zone"}
            },
            "dhw_cylinder": True,
            "backup_heater": False,
            "weather_compensation": True,
            "existing_radiators": True,
            "flow_rate_method": "fixed_rate",
            "flow_rate": 20,
            "advanced_features": False,
            "diagnostic_monitoring": False
        }
    )
}


async def validate_connection(hass: HomeAssistant, data: Dict[str, Any]) -> Dict[str, Any]:
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
    
    # Return info that you want to store in the config entry.
    return {"title": f"Grant Aerona3 ({data[CONF_HOST]})"}


class GrantAerona3EnhancedConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle enhanced config flow for Grant Aerona3 Heat Pump."""

    VERSION = 2  # Increment version for enhanced flow

    def __init__(self):
        """Initialize config flow."""
        self._config_data = {}
        self._selected_template = None
    
    def _sanitize_user_input(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize user input to prevent injection attacks."""
        sanitized = {}
        
        for key, value in user_input.items():
            if isinstance(value, str):
                # Remove potentially dangerous characters for security
                sanitized_value = re.sub(r'[<>"\';\\]', '', value.strip())
                # Additional validation for specific fields
                if key == CONF_HOST:
                    # Validate IP address format
                    if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', sanitized_value):
                        raise ValueError(f"Invalid IP address format: {sanitized_value}")
                elif key == CONF_PORT:
                    # Port should be numeric
                    if not isinstance(value, int) or not (1 <= value <= 65535):
                        raise ValueError(f"Invalid port number: {value}")
                elif key == CONF_SLAVE_ID:
                    # Slave ID should be between 1-247
                    if not isinstance(value, int) or not (1 <= value <= 247):
                        raise ValueError(f"Invalid Slave ID: {value}")
                sanitized[key] = sanitized_value
            elif isinstance(value, (int, float, bool)):
                # Numeric and boolean values are generally safe
                sanitized[key] = value
            elif isinstance(value, dict):
                # Recursively sanitize nested dictionaries
                sanitized[key] = self._sanitize_user_input(value)
            else:
                # For other types, convert to string and sanitize
                sanitized[key] = re.sub(r'[<>"\';\\]', '', str(value))
                
        return sanitized

    async def async_step_user(
        self, user_input: Dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - installation type selection."""
        errors: Dict[str, str] = {}
        
        if user_input is not None:
            try:
                # Sanitize user input for security
                sanitized_input = self._sanitize_user_input(user_input)
                template_id = sanitized_input.get("installation_type")
                if template_id in INSTALLATION_TEMPLATES:
                    self._selected_template = INSTALLATION_TEMPLATES[template_id]
                    return await self.async_step_connection()
                else:
                    errors["base"] = "invalid_template"
            except ValueError as err:
                _LOGGER.error("Input validation error: %s", err)
                errors["base"] = "invalid_input"

        # Create schema for installation type selection
        installation_options = {}
        for template_id, template in INSTALLATION_TEMPLATES.items():
            label = f"{template.name} ({template.percentage}) - {template.description}"
            installation_options[template_id] = label

        schema = vol.Schema({
            vol.Required("installation_type"): vol.In(installation_options)
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "common_setups": "Most common Grant Aerona3 installations",
                "basic_info": "Choose the configuration that matches your installed system"
            }
        )

    async def async_step_connection(
        self, user_input: Dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle connection configuration."""
        errors: Dict[str, str] = {}
        
        if user_input is not None:
            try:
                # Sanitize user input for security
                sanitized_input = self._sanitize_user_input(user_input)
                
                # Validate connection
                await validate_connection(self.hass, sanitized_input)
                
                # Store connection data
                self._config_data.update(sanitized_input)
                
                # Check if already configured
                await self.async_set_unique_id(sanitized_input[CONF_HOST])
                self._abort_if_unique_id_configured()
                
                return await self.async_step_system_verification()
                
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception during connection test")
                errors["base"] = "unknown"

        schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
            vol.Optional(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): int,
            vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
        })

        return self.async_show_form(
            step_id="connection",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "template_name": self._selected_template.name,
                "template_description": self._selected_template.description
            }
        )

    async def async_step_system_verification(
        self, user_input: Dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle system component verification."""
        errors: Dict[str, str] = {}
        
        if user_input is not None:
            # Update config with verified components
            self._config_data.update(user_input)
            
            # Move to flow rate configuration
            return await self.async_step_flow_rate()

        # Create schema based on selected template
        template_config = self._selected_template.default_config
        
        schema_dict = {}
        
        # Always include zone configuration
        schema_dict[vol.Optional("zone_1_name", default="Main Zone")] = str
        
        if template_config.get("zones", {}).get("zone_2", {}).get("enabled", False):
            schema_dict[vol.Optional("zone_2_enabled", default=True)] = bool
            schema_dict[vol.Optional("zone_2_name", default="Second Zone")] = str
        else:
            schema_dict[vol.Optional("zone_2_enabled", default=False)] = bool
            schema_dict[vol.Optional("zone_2_name", default="Second Zone")] = str
        
        # DHW configuration
        schema_dict[vol.Optional("dhw_cylinder", default=template_config.get("dhw_cylinder", False))] = bool
        
        if template_config.get("dhw_cylinder", False):
            schema_dict[vol.Optional("dhw_cylinder_size", default="250L")] = vol.In([
                "180L", "210L", "250L", "300L", "Custom"
            ])
            
        # Backup heater
        schema_dict[vol.Optional("backup_heater", default=template_config.get("backup_heater", False))] = bool
        
        schema = vol.Schema(schema_dict)

        return self.async_show_form(
            step_id="system_verification",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "template_name": self._selected_template.name,
                "verification_info": "Confirm the components installed in your system"
            }
        )

    async def async_step_flow_rate(
        self, user_input: Dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle flow rate configuration."""
        errors: Dict[str, str] = {}
        
        if user_input is not None:
            # Update config with flow rate settings
            self._config_data.update(user_input)
            
            # Create final configuration
            final_config = self._create_final_config()
            
            return self.async_create_entry(
                title=f"Grant Aerona3 ({self._config_data[CONF_HOST]})",
                data=final_config
            )

        # Flow rate configuration
        template_flow_rate = self._selected_template.default_config.get("flow_rate", 20)
        
        schema = vol.Schema({
            vol.Required("flow_rate_method", default="fixed_rate"): vol.In({
                "fixed_rate": "Fixed Flow Rate (most common)",
                "calculated_rate": "Calculate from System",
                "flow_meter": "External Flow Meter"
            }),
            vol.Optional("flow_rate", default=template_flow_rate): vol.Range(min=10, max=50),
        })

        return self.async_show_form(
            step_id="flow_rate",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "flow_rate_info": "Configure how flow rate is determined",
                "typical_range": "Typical range 15-25 L/min for residential systems"
            }
        )

    def _create_final_config(self) -> Dict[str, Any]:
        """Create final configuration from collected data."""
        # Start with template defaults
        final_config = self._selected_template.default_config.copy()
        
        # Update with connection settings
        final_config.update({
            CONF_HOST: self._config_data[CONF_HOST],
            CONF_PORT: self._config_data[CONF_PORT],
            CONF_SLAVE_ID: self._config_data[CONF_SLAVE_ID],
            CONF_SCAN_INTERVAL: self._config_data[CONF_SCAN_INTERVAL],
        })
        
        # Update zones configuration
        if "zone_1_name" in self._config_data:
            final_config["zones"]["zone_1"]["name"] = self._config_data["zone_1_name"]
            
        if "zone_2_enabled" in self._config_data:
            final_config["zones"]["zone_2"]["enabled"] = self._config_data["zone_2_enabled"]
            
        if "zone_2_name" in self._config_data:
            final_config["zones"]["zone_2"]["name"] = self._config_data["zone_2_name"]
        
        # Update DHW configuration
        if "dhw_cylinder" in self._config_data:
            final_config["dhw_cylinder"] = self._config_data["dhw_cylinder"]
            
        if "dhw_cylinder_size" in self._config_data:
            final_config["dhw_cylinder_size"] = self._config_data["dhw_cylinder_size"]
            
        # Update backup heater
        if "backup_heater" in self._config_data:
            final_config["backup_heater"] = self._config_data["backup_heater"]
            
        # Update flow rate settings
        if "flow_rate_method" in self._config_data:
            final_config["flow_rate_method"] = self._config_data["flow_rate_method"]
            
        if "flow_rate" in self._config_data:
            final_config["flow_rate"] = self._config_data["flow_rate"]
            
        # Add metadata
        final_config.update({
            "installation_template": self._selected_template.template_id,
            "config_version": 2,
            "setup_date": self.hass.helpers.utcnow().isoformat()
        })
        
        return final_config

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get options flow handler."""
        return GrantAerona3OptionsFlow(config_entry)


class GrantAerona3OptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Grant Aerona3."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: Dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: Dict[str, str] = {}
        
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_config = self.config_entry.data
        
        # Create options schema
        schema = vol.Schema({
            vol.Optional(
                "advanced_features",
                default=current_config.get("advanced_features", False)
            ): bool,
            vol.Optional(
                "diagnostic_monitoring",
                default=current_config.get("diagnostic_monitoring", False)
            ): bool,
            vol.Optional(
                "weather_compensation",
                default=current_config.get("weather_compensation", True)
            ): bool,
            vol.Optional(
                "dual_weather_compensation",
                default=current_config.get("dual_weather_compensation", False)
            ): bool,
        })

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "options_info": "Configure advanced features and monitoring options"
            }
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""