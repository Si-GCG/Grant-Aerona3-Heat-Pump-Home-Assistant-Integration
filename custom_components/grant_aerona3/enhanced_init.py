"""Enhanced Grant Aerona3 Heat Pump integration for Home Assistant."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Dict, Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady, ConfigEntryAuthFailed

from .const import DOMAIN
from .enhanced_coordinator import GrantAerona3EnhancedCoordinator
from .register_manager import GrantAerona3RegisterManager

_LOGGER = logging.getLogger(__name__)

# Define platforms based on configuration
PLATFORMS = [
    Platform.SENSOR,      # Always available
    Platform.BINARY_SENSOR, # Always available
    Platform.CLIMATE,     # Always available
    Platform.SWITCH,      # Always available
    Platform.NUMBER,      # Always available for setpoints
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Grant Aerona3 from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Validate and migrate configuration if needed
    config_data = await _validate_and_migrate_config(hass, entry)
    
    try:
        # Initialize enhanced coordinator
        coordinator = GrantAerona3EnhancedCoordinator(hass, entry)
        
        # Perform initial data refresh
        await coordinator.async_config_entry_first_refresh()
        
        # Setup weather compensation system
        await coordinator.async_setup_weather_compensation()
        
        # Store coordinator in hass data
        hass.data[DOMAIN][entry.entry_id] = coordinator
        
        # Get platforms to set up based on configuration
        platforms_to_setup = _get_platforms_for_config(config_data)
        
        # Set up platforms
        await hass.config_entries.async_forward_entry_setups(entry, platforms_to_setup)
        
        # Setup service handlers if needed
        await _setup_services(hass, coordinator)
        
        _LOGGER.info(
            "Grant Aerona3 integration setup completed. "
            "Template: %s, Platforms: %s, Enabled registers: %d",
            config_data.get("installation_template", "unknown"),
            ", ".join(platforms_to_setup),
            len(coordinator.register_manager._enabled_registers)
        )
        
        return True
        
    except Exception as err:
        _LOGGER.error("Failed to setup Grant Aerona3 integration: %s", err)
        raise ConfigEntryNotReady(f"Failed to setup integration: {err}") from err


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Get the platforms that were set up
    config_data = entry.data
    platforms_to_unload = _get_platforms_for_config(config_data)
    
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, platforms_to_unload)
    
    if unload_ok:
        # Clean up coordinator
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        
        # Clean up any additional resources if needed
        if hasattr(coordinator, 'async_cleanup'):
            await coordinator.async_cleanup()
            
        _LOGGER.info("Grant Aerona3 integration unloaded successfully")

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def _validate_and_migrate_config(hass: HomeAssistant, entry: ConfigEntry) -> Dict[str, Any]:
    """Validate and migrate configuration if needed."""
    config_data = dict(entry.data)
    config_version = config_data.get("config_version", 1)
    
    # Migration from version 1 to version 2
    if config_version < 2:
        _LOGGER.info("Migrating Grant Aerona3 configuration from v%d to v2", config_version)
        
        # Migrate to new structure
        migrated_config = _migrate_config_v1_to_v2(config_data)
        
        # Update config entry
        hass.config_entries.async_update_entry(
            entry,
            data=migrated_config
        )
        
        config_data = migrated_config
        _LOGGER.info("Configuration migrated successfully")
    
    # Validate current configuration
    validation_errors = _validate_config(config_data)
    if validation_errors:
        error_msg = "Configuration validation failed: " + ", ".join(validation_errors)
        _LOGGER.error(error_msg)
        raise ConfigEntryAuthFailed(error_msg)
    
    return config_data


def _migrate_config_v1_to_v2(old_config: Dict[str, Any]) -> Dict[str, Any]:
    """Migrate configuration from version 1 to version 2."""
    new_config = old_config.copy()
    
    # Set default template based on old configuration
    if not new_config.get("installation_template"):
        # Guess template based on existing config
        if old_config.get("dhw_cylinder", False):
            new_config["installation_template"] = "single_zone_dhw"
        else:
            new_config["installation_template"] = "single_zone_basic"
    
    # Set default zone configuration
    if "zones" not in new_config:
        new_config["zones"] = {
            "zone_1": {"enabled": True, "name": "Main Zone"},
            "zone_2": {"enabled": False, "name": "Second Zone"}
        }
    
    # Set default feature flags
    feature_defaults = {
        "dhw_cylinder": False,
        "backup_heater": False,
        "weather_compensation": True,
        "flow_rate_method": "fixed_rate",
        "flow_rate": 20,
        "advanced_features": False,
        "diagnostic_monitoring": False,
        "config_version": 2
    }
    
    for key, default_value in feature_defaults.items():
        if key not in new_config:
            new_config[key] = default_value
    
    return new_config


def _validate_config(config: Dict[str, Any]) -> list[str]:
    """Validate configuration and return list of errors."""
    errors = []
    
    # Required fields
    required_fields = ["host", "port", "slave_id"]
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required field: {field}")
    
    # Validate installation template
    valid_templates = [
        "single_zone_basic", "single_zone_dhw", 
        "dual_zone_system", "replacement_system"
    ]
    template = config.get("installation_template")
    if template and template not in valid_templates:
        errors.append(f"Invalid installation template: {template}")
    
    # Validate flow rate settings
    flow_method = config.get("flow_rate_method")
    if flow_method == "fixed_rate":
        flow_rate = config.get("flow_rate")
        if not flow_rate or not (10 <= flow_rate <= 50):
            errors.append("Flow rate must be between 10 and 50 L/min")
    
    # Validate zone configuration
    zones = config.get("zones", {})
    if not zones.get("zone_1", {}).get("enabled"):
        errors.append("Zone 1 must be enabled")
    
    return errors


def _get_platforms_for_config(config: Dict[str, Any]) -> list[str]:
    """Get list of platforms to set up based on configuration."""
    platforms = [
        Platform.SENSOR,        # Always needed
        Platform.BINARY_SENSOR, # Always needed  
        Platform.CLIMATE,       # Always needed for zone control
        Platform.SWITCH,        # Always needed for basic controls
    ]
    
    # Add number platform for setpoints (always needed)
    platforms.append(Platform.NUMBER)
    
    # Add additional platforms based on features
    if config.get("dhw_cylinder", False):
        # DHW adds additional sensors and controls
        pass  # Already included in base platforms
        
    if config.get("backup_heater", False):
        # Backup heater adds additional switches
        pass  # Already included in base platforms
    
    return platforms


async def _setup_services(hass: HomeAssistant, coordinator: GrantAerona3EnhancedCoordinator) -> None:
    """Set up additional services for the integration."""
    
    async def handle_refresh_data(call):
        """Handle refresh data service call."""
        await coordinator.async_request_refresh()
    
    async def handle_get_performance_stats(call):
        """Handle get performance stats service call."""
        stats = coordinator.get_performance_stats()
        _LOGGER.info("Performance stats: %s", stats)
        return stats
    
    # Register services
    hass.services.async_register(
        DOMAIN,
        "refresh_data",
        handle_refresh_data,
        schema=None
    )
    
    hass.services.async_register(
        DOMAIN,
        "get_performance_stats", 
        handle_get_performance_stats,
        schema=None
    )
    
    _LOGGER.debug("Grant Aerona3 services registered")


class GrantAerona3Integration:
    """Main integration class for managing the Grant Aerona3 integration."""
    
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize the integration."""
        self.hass = hass
        self.entry = entry
        self.coordinator: GrantAerona3EnhancedCoordinator = None
        self.platforms_loaded = []
        
    async def async_setup(self) -> bool:
        """Set up the integration."""
        try:
            # Validate configuration
            config_data = await _validate_and_migrate_config(self.hass, self.entry)
            
            # Initialize coordinator
            self.coordinator = GrantAerona3EnhancedCoordinator(self.hass, self.entry)
            await self.coordinator.async_config_entry_first_refresh()
            
            # Store in hass data
            self.hass.data[DOMAIN][self.entry.entry_id] = self.coordinator
            
            # Setup platforms
            platforms = _get_platforms_for_config(config_data)
            await self.hass.config_entries.async_forward_entry_setups(self.entry, platforms)
            self.platforms_loaded = platforms
            
            # Setup services
            await _setup_services(self.hass, self.coordinator)
            
            return True
            
        except Exception as err:
            _LOGGER.error("Failed to setup Grant Aerona3 integration: %s", err)
            raise ConfigEntryNotReady(f"Setup failed: {err}") from err
    
    async def async_unload(self) -> bool:
        """Unload the integration."""
        # Unload platforms
        unload_ok = await self.hass.config_entries.async_unload_platforms(
            self.entry, self.platforms_loaded
        )
        
        if unload_ok:
            # Clean up coordinator
            if self.coordinator:
                if hasattr(self.coordinator, 'async_cleanup'):
                    await self.coordinator.async_cleanup()
                    
            # Remove from hass data
            self.hass.data[DOMAIN].pop(self.entry.entry_id, None)
            
        return unload_ok
    
    async def async_reload(self) -> None:
        """Reload the integration."""
        await self.async_unload()
        await self.async_setup()


# Backward compatibility - keep the simple functions for existing installations
async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entries to new format."""
    if config_entry.version == 1:
        _LOGGER.info("Migrating Grant Aerona3 config entry from version 1 to 2")
        
        new_data = _migrate_config_v1_to_v2(dict(config_entry.data))
        
        hass.config_entries.async_update_entry(
            config_entry,
            data=new_data,
            version=2
        )
        
        _LOGGER.info("Migration completed successfully")
    
    return True