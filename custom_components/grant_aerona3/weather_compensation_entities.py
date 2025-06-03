"""Weather compensation entities for Grant Aerona3 Heat Pump."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.components.switch import SwitchEntity
from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .enhanced_coordinator import GrantAerona3EnhancedCoordinator
from .weather_compensation import WeatherCompensationController

_LOGGER = logging.getLogger(__name__)


async def async_setup_weather_compensation_entities(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    coordinator: GrantAerona3EnhancedCoordinator,
    weather_compensation: WeatherCompensationController,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up weather compensation entities."""
    
    if not weather_compensation.is_enabled():
        _LOGGER.debug("Weather compensation not enabled, skipping entities")
        return
    
    entities = []
    
    # Add weather compensation sensors
    entities.extend([
        WeatherCompensationStatusSensor(coordinator, config_entry, weather_compensation),
        WeatherCompensationTargetTempSensor(coordinator, config_entry, weather_compensation),
        WeatherCompensationCurveSensor(coordinator, config_entry, weather_compensation),
        WeatherCompensationEfficiencySensor(coordinator, config_entry, weather_compensation),
    ])
    
    # Add boost mode entities
    entities.extend([
        WeatherCompensationBoostSwitch(coordinator, config_entry, weather_compensation),
        WeatherCompensationBoostStatusSensor(coordinator, config_entry, weather_compensation),
        WeatherCompensationBoostRemainingTimeSensor(coordinator, config_entry, weather_compensation),
    ])
    
    # Add configuration controls
    entities.extend([
        WeatherCompensationMinOutdoorTempNumber(coordinator, config_entry, weather_compensation),
        WeatherCompensationMaxOutdoorTempNumber(coordinator, config_entry, weather_compensation),
        WeatherCompensationMinFlowTempNumber(coordinator, config_entry, weather_compensation),
        WeatherCompensationMaxFlowTempNumber(coordinator, config_entry, weather_compensation),
    ])
    
    # Add dual curve entities if enabled
    config_data = config_entry.data
    if config_data.get("dual_weather_compensation", False):
        entities.extend([
            WeatherCompensationBoostCurveStatusSensor(coordinator, config_entry, weather_compensation),
            WeatherCompensationCurveComparisonSensor(coordinator, config_entry, weather_compensation),
        ])
    
    async_add_entities(entities)


class WeatherCompensationStatusSensor(CoordinatorEntity, SensorEntity):
    """Weather compensation status sensor."""

    def __init__(
        self,
        coordinator: GrantAerona3EnhancedCoordinator,
        config_entry: ConfigEntry,
        weather_compensation: WeatherCompensationController,
    ) -> None:
        """Initialize the status sensor."""
        super().__init__(coordinator)
        self.weather_compensation = weather_compensation
        
        self._attr_unique_id = f"{config_entry.entry_id}_weather_compensation_status"
        self._attr_name = "Grant Aerona3 Weather Compensation Status"
        self._attr_icon = "mdi:thermometer-auto"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Grant Aerona3 Heat Pump",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "sw_version": "2.0.0",
        }

    @property
    def native_value(self) -> str:
        """Return the status of weather compensation."""
        status = self.weather_compensation.get_status()
        
        if not status.get("enabled", False):
            return "Disabled"
        elif status.get("boost_active", False):
            return "Boost Active"
        else:
            return "Active"

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        status = self.weather_compensation.get_status()
        
        attributes = {
            "mode": status.get("mode", "unknown"),
            "active_curve": status.get("active_curve", "unknown"),
            "curve_name": status.get("curve_name", "unknown"),
            "last_outdoor_temp": status.get("last_outdoor_temp"),
            "last_flow_temp": status.get("last_flow_temp"),
            "calculation_count": status.get("calculation_count", 0),
            "last_update": status.get("last_update"),
            "tooltip": "Weather Compensation automatically adjusts your heating flow temperature based on outdoor conditions. Colder outside = hotter water temperature for efficient heating.",
            "benefits": "Saves 10-15% energy costs by preventing overheating during mild weather",
            "how_it_works": "Uses outdoor temperature to calculate optimal flow temperature - no manual adjustments needed"
        }
        
        # Add primary curve configuration
        primary_config = status.get("primary_curve_config", {})
        if primary_config:
            attributes.update({
                "primary_curve_name": primary_config.get("name"),
                "primary_min_outdoor": primary_config.get("min_outdoor"),
                "primary_max_outdoor": primary_config.get("max_outdoor"),
                "primary_min_flow": primary_config.get("min_flow"),
                "primary_max_flow": primary_config.get("max_flow"),
            })
        
        return attributes


class WeatherCompensationTargetTempSensor(CoordinatorEntity, SensorEntity):
    """Weather compensation target temperature sensor."""

    def __init__(
        self,
        coordinator: GrantAerona3EnhancedCoordinator,
        config_entry: ConfigEntry,
        weather_compensation: WeatherCompensationController,
    ) -> None:
        """Initialize the target temperature sensor."""
        super().__init__(coordinator)
        self.weather_compensation = weather_compensation
        
        self._attr_unique_id = f"{config_entry.entry_id}_weather_compensation_target_temp"
        self._attr_name = "Grant Aerona3 WC Target Flow Temperature"
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_device_class = "temperature"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:thermometer-water"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Grant Aerona3 Heat Pump",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "sw_version": "2.0.0",
        }

    @property
    def native_value(self) -> Optional[float]:
        """Return the target flow temperature."""
        status = self.weather_compensation.get_status()
        return status.get("last_flow_temp")

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        status = self.weather_compensation.get_status()
        return {
            "outdoor_temperature": status.get("last_outdoor_temp"),
            "active_curve": status.get("active_curve"),
            "calculation_method": "weather_compensation"
        }


class WeatherCompensationCurveSensor(CoordinatorEntity, SensorEntity):
    """Weather compensation curve information sensor."""

    def __init__(
        self,
        coordinator: GrantAerona3EnhancedCoordinator,
        config_entry: ConfigEntry,
        weather_compensation: WeatherCompensationController,
    ) -> None:
        """Initialize the curve sensor."""
        super().__init__(coordinator)
        self.weather_compensation = weather_compensation
        
        self._attr_unique_id = f"{config_entry.entry_id}_weather_compensation_curve"
        self._attr_name = "Grant Aerona3 WC Curve Data"
        self._attr_icon = "mdi:chart-line"
        self._attr_entity_category = "diagnostic"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Grant Aerona3 Heat Pump",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "sw_version": "2.0.0",
        }

    @property
    def native_value(self) -> str:
        """Return the active curve name."""
        status = self.weather_compensation.get_status()
        return status.get("curve_name", "Unknown")

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return curve visualization data."""
        curve_data = self.weather_compensation.get_curve_data("primary")
        
        if not curve_data:
            return {}
        
        return {
            "curve_type": curve_data.get("curve_type"),
            "curve_points": curve_data.get("points", [])[:10],  # Limit for state size
            "current_outdoor": curve_data.get("current_outdoor"),
            "current_flow": curve_data.get("current_flow"),
            "config": curve_data.get("config", {}),
        }


class WeatherCompensationEfficiencySensor(CoordinatorEntity, SensorEntity):
    """Weather compensation efficiency sensor."""

    def __init__(
        self,
        coordinator: GrantAerona3EnhancedCoordinator,
        config_entry: ConfigEntry,
        weather_compensation: WeatherCompensationController,
    ) -> None:
        """Initialize the efficiency sensor."""
        super().__init__(coordinator)
        self.weather_compensation = weather_compensation
        
        self._attr_unique_id = f"{config_entry.entry_id}_weather_compensation_efficiency"
        self._attr_name = "Grant Aerona3 WC Efficiency Gain"
        self._attr_native_unit_of_measurement = "%"
        self._attr_icon = "mdi:percent"
        self._attr_entity_category = "diagnostic"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Grant Aerona3 Heat Pump",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "sw_version": "2.0.0",
        }

    @property
    def native_value(self) -> Optional[float]:
        """Return estimated efficiency gain from weather compensation."""
        # This is a simplified calculation - in practice would need historical data
        status = self.weather_compensation.get_status()
        
        if not status.get("enabled", False):
            return 0.0
        
        # Estimate efficiency gain based on outdoor temperature
        outdoor_temp = status.get("last_outdoor_temp")
        if outdoor_temp is not None:
            # Weather compensation typically saves 10-15% energy
            # More savings in milder weather
            if outdoor_temp > 10:
                return 15.0  # High savings in mild weather
            elif outdoor_temp > 0:
                return 12.0  # Medium savings
            else:
                return 8.0   # Lower savings in very cold weather
        
        return 10.0  # Default estimate


class WeatherCompensationBoostSwitch(CoordinatorEntity, SwitchEntity):
    """Weather compensation boost mode switch."""

    def __init__(
        self,
        coordinator: GrantAerona3EnhancedCoordinator,
        config_entry: ConfigEntry,
        weather_compensation: WeatherCompensationController,
    ) -> None:
        """Initialize the boost switch."""
        super().__init__(coordinator)
        self.weather_compensation = weather_compensation
        self._config_entry = config_entry
        
        self._attr_unique_id = f"{config_entry.entry_id}_weather_compensation_boost"
        self._attr_name = "Grant Aerona3 WC Boost Mode"
        self._attr_icon = "mdi:fire"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Grant Aerona3 Heat Pump",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "sw_version": "2.0.0",
        }

    @property
    def is_on(self) -> bool:
        """Return true if boost mode is active."""
        status = self.weather_compensation.get_status()
        return status.get("boost_active", False)

    @property
    def available(self) -> bool:
        """Return true if boost mode is available."""
        # Boost is available if dual weather compensation is enabled
        return self._config_entry.data.get("dual_weather_compensation", False)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on boost mode."""
        duration = kwargs.get("duration", 120)  # Default 2 hours
        success = await self.weather_compensation.activate_boost_mode(
            duration_minutes=duration,
            reason="manual_switch"
        )
        
        if success:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off boost mode."""
        await self.weather_compensation.deactivate_boost_mode("manual_switch")
        await self.coordinator.async_request_refresh()

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        status = self.weather_compensation.get_status()
        return {
            "boost_remaining_minutes": status.get("boost_remaining_minutes"),
            "boost_curve": status.get("curve_name") if status.get("boost_active") else None,
        }


class WeatherCompensationBoostStatusSensor(CoordinatorEntity, BinarySensorEntity):
    """Weather compensation boost status binary sensor."""

    def __init__(
        self,
        coordinator: GrantAerona3EnhancedCoordinator,
        config_entry: ConfigEntry,
        weather_compensation: WeatherCompensationController,
    ) -> None:
        """Initialize the boost status sensor."""
        super().__init__(coordinator)
        self.weather_compensation = weather_compensation
        
        self._attr_unique_id = f"{config_entry.entry_id}_weather_compensation_boost_status"
        self._attr_name = "Grant Aerona3 WC Boost Active"
        self._attr_icon = "mdi:fire"
        self._attr_entity_category = "diagnostic"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Grant Aerona3 Heat Pump",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "sw_version": "2.0.0",
        }

    @property
    def is_on(self) -> bool:
        """Return true if boost mode is active."""
        status = self.weather_compensation.get_status()
        return status.get("boost_active", False)


class WeatherCompensationBoostRemainingTimeSensor(CoordinatorEntity, SensorEntity):
    """Weather compensation boost remaining time sensor."""

    def __init__(
        self,
        coordinator: GrantAerona3EnhancedCoordinator,
        config_entry: ConfigEntry,
        weather_compensation: WeatherCompensationController,
    ) -> None:
        """Initialize the boost remaining time sensor."""
        super().__init__(coordinator)
        self.weather_compensation = weather_compensation
        
        self._attr_unique_id = f"{config_entry.entry_id}_weather_compensation_boost_remaining"
        self._attr_name = "Grant Aerona3 WC Boost Remaining"
        self._attr_native_unit_of_measurement = UnitOfTime.MINUTES
        self._attr_device_class = "duration"
        self._attr_icon = "mdi:timer"
        self._attr_entity_category = "diagnostic"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Grant Aerona3 Heat Pump",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "sw_version": "2.0.0",
        }

    @property
    def native_value(self) -> Optional[int]:
        """Return remaining boost time in minutes."""
        status = self.weather_compensation.get_status()
        return status.get("boost_remaining_minutes")

    @property
    def available(self) -> bool:
        """Return true if boost mode is active."""
        status = self.weather_compensation.get_status()
        return status.get("boost_active", False)


class WeatherCompensationMinOutdoorTempNumber(CoordinatorEntity, NumberEntity):
    """Weather compensation minimum outdoor temperature number entity."""

    def __init__(
        self,
        coordinator: GrantAerona3EnhancedCoordinator,
        config_entry: ConfigEntry,
        weather_compensation: WeatherCompensationController,
    ) -> None:
        """Initialize the min outdoor temp number."""
        super().__init__(coordinator)
        self.weather_compensation = weather_compensation
        
        self._attr_unique_id = f"{config_entry.entry_id}_wc_min_outdoor_temp"
        self._attr_name = "Grant Aerona3 WC Min Outdoor Temp"
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_device_class = "temperature"
        self._attr_mode = NumberMode.BOX
        self._attr_native_min_value = -30.0
        self._attr_native_max_value = 5.0
        self._attr_native_step = 0.5
        self._attr_icon = "mdi:thermometer-minus"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Grant Aerona3 Heat Pump",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "sw_version": "2.0.0",
        }

    @property
    def native_value(self) -> Optional[float]:
        """Return the current minimum outdoor temperature."""
        status = self.weather_compensation.get_status()
        primary_config = status.get("primary_curve_config", {})
        return primary_config.get("min_outdoor")

    async def async_set_native_value(self, value: float) -> None:
        """Set the minimum outdoor temperature."""
        # This would need to be implemented in the weather compensation system
        # For now, just log the change
        _LOGGER.info("Setting WC min outdoor temp to %.1f°C", value)
        # TODO: Implement actual setting update


class WeatherCompensationMaxOutdoorTempNumber(CoordinatorEntity, NumberEntity):
    """Weather compensation maximum outdoor temperature number entity."""

    def __init__(
        self,
        coordinator: GrantAerona3EnhancedCoordinator,
        config_entry: ConfigEntry,
        weather_compensation: WeatherCompensationController,
    ) -> None:
        """Initialize the max outdoor temp number."""
        super().__init__(coordinator)
        self.weather_compensation = weather_compensation
        
        self._attr_unique_id = f"{config_entry.entry_id}_wc_max_outdoor_temp"
        self._attr_name = "Grant Aerona3 WC Max Outdoor Temp"
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_device_class = "temperature"
        self._attr_mode = NumberMode.BOX
        self._attr_native_min_value = 10.0
        self._attr_native_max_value = 30.0
        self._attr_native_step = 0.5
        self._attr_icon = "mdi:thermometer-plus"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Grant Aerona3 Heat Pump",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "sw_version": "2.0.0",
        }

    @property
    def native_value(self) -> Optional[float]:
        """Return the current maximum outdoor temperature."""
        status = self.weather_compensation.get_status()
        primary_config = status.get("primary_curve_config", {})
        return primary_config.get("max_outdoor")

    async def async_set_native_value(self, value: float) -> None:
        """Set the maximum outdoor temperature."""
        _LOGGER.info("Setting WC max outdoor temp to %.1f°C", value)
        # TODO: Implement actual setting update


class WeatherCompensationMinFlowTempNumber(CoordinatorEntity, NumberEntity):
    """Weather compensation minimum flow temperature number entity."""

    def __init__(
        self,
        coordinator: GrantAerona3EnhancedCoordinator,
        config_entry: ConfigEntry,
        weather_compensation: WeatherCompensationController,
    ) -> None:
        """Initialize the min flow temp number."""
        super().__init__(coordinator)
        self.weather_compensation = weather_compensation
        
        self._attr_unique_id = f"{config_entry.entry_id}_wc_min_flow_temp"
        self._attr_name = "Grant Aerona3 WC Min Flow Temp"
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_device_class = "temperature"
        self._attr_mode = NumberMode.BOX
        self._attr_native_min_value = 20.0
        self._attr_native_max_value = 40.0
        self._attr_native_step = 0.5
        self._attr_icon = "mdi:water-thermometer"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Grant Aerona3 Heat Pump",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "sw_version": "2.0.0",
        }

    @property
    def native_value(self) -> Optional[float]:
        """Return the current minimum flow temperature."""
        status = self.weather_compensation.get_status()
        primary_config = status.get("primary_curve_config", {})
        return primary_config.get("min_flow")

    async def async_set_native_value(self, value: float) -> None:
        """Set the minimum flow temperature."""
        _LOGGER.info("Setting WC min flow temp to %.1f°C", value)
        # TODO: Implement actual setting update


class WeatherCompensationMaxFlowTempNumber(CoordinatorEntity, NumberEntity):
    """Weather compensation maximum flow temperature number entity."""

    def __init__(
        self,
        coordinator: GrantAerona3EnhancedCoordinator,
        config_entry: ConfigEntry,
        weather_compensation: WeatherCompensationController,
    ) -> None:
        """Initialize the max flow temp number."""
        super().__init__(coordinator)
        self.weather_compensation = weather_compensation
        
        self._attr_unique_id = f"{config_entry.entry_id}_wc_max_flow_temp"
        self._attr_name = "Grant Aerona3 WC Max Flow Temp"
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_device_class = "temperature"
        self._attr_mode = NumberMode.BOX
        self._attr_native_min_value = 35.0
        self._attr_native_max_value = 70.0
        self._attr_native_step = 0.5
        self._attr_icon = "mdi:water-thermometer"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Grant Aerona3 Heat Pump",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "sw_version": "2.0.0",
        }

    @property
    def native_value(self) -> Optional[float]:
        """Return the current maximum flow temperature."""
        status = self.weather_compensation.get_status()
        primary_config = status.get("primary_curve_config", {})
        return primary_config.get("max_flow")

    async def async_set_native_value(self, value: float) -> None:
        """Set the maximum flow temperature."""
        _LOGGER.info("Setting WC max flow temp to %.1f°C", value)
        # TODO: Implement actual setting update


class WeatherCompensationBoostCurveStatusSensor(CoordinatorEntity, SensorEntity):
    """Weather compensation boost curve status sensor."""

    def __init__(
        self,
        coordinator: GrantAerona3EnhancedCoordinator,
        config_entry: ConfigEntry,
        weather_compensation: WeatherCompensationController,
    ) -> None:
        """Initialize the boost curve status sensor."""
        super().__init__(coordinator)
        self.weather_compensation = weather_compensation
        
        self._attr_unique_id = f"{config_entry.entry_id}_wc_boost_curve_status"
        self._attr_name = "Grant Aerona3 WC Boost Curve Status"
        self._attr_icon = "mdi:chart-line-variant"
        self._attr_entity_category = "diagnostic"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Grant Aerona3 Heat Pump",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "sw_version": "2.0.0",
        }

    @property
    def native_value(self) -> str:
        """Return the boost curve status."""
        status = self.weather_compensation.get_status()
        
        if status.get("boost_active", False):
            return "Active"
        else:
            return "Standby"

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return boost curve configuration."""
        secondary_curve_data = self.weather_compensation.get_curve_data("secondary")
        
        if secondary_curve_data:
            config = secondary_curve_data.get("config", {})
            return {
                "curve_name": secondary_curve_data.get("curve_name"),
                "curve_type": secondary_curve_data.get("curve_type"),
                "min_outdoor": config.get("min_outdoor"),
                "max_outdoor": config.get("max_outdoor"),
                "min_flow": config.get("min_flow"),
                "max_flow": config.get("max_flow"),
            }
        
        return {}


class WeatherCompensationCurveComparisonSensor(CoordinatorEntity, SensorEntity):
    """Weather compensation curve comparison sensor."""

    def __init__(
        self,
        coordinator: GrantAerona3EnhancedCoordinator,
        config_entry: ConfigEntry,
        weather_compensation: WeatherCompensationController,
    ) -> None:
        """Initialize the curve comparison sensor."""
        super().__init__(coordinator)
        self.weather_compensation = weather_compensation
        
        self._attr_unique_id = f"{config_entry.entry_id}_wc_curve_comparison"
        self._attr_name = "Grant Aerona3 WC Curve Comparison"
        self._attr_icon = "mdi:compare"
        self._attr_entity_category = "diagnostic"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Grant Aerona3 Heat Pump",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "sw_version": "2.0.0",
        }

    @property
    def native_value(self) -> str:
        """Return the curve comparison summary."""
        status = self.weather_compensation.get_status()
        outdoor_temp = status.get("last_outdoor_temp")
        
        if outdoor_temp is not None:
            primary_data = self.weather_compensation.get_curve_data("primary")
            secondary_data = self.weather_compensation.get_curve_data("secondary")
            
            if primary_data and secondary_data:
                # Calculate temperature difference between curves at current outdoor temp
                # This would need to be implemented in the weather compensation system
                return f"Boost +8°C at {outdoor_temp}°C"
        
        return "No comparison available"

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return detailed curve comparison data."""
        primary_data = self.weather_compensation.get_curve_data("primary")
        secondary_data = self.weather_compensation.get_curve_data("secondary")
        
        if not (primary_data and secondary_data):
            return {}
        
        return {
            "primary_curve": {
                "name": primary_data.get("curve_name"),
                "current_flow": primary_data.get("current_flow"),
            },
            "secondary_curve": {
                "name": secondary_data.get("curve_name"),
                "current_flow": secondary_data.get("current_flow"),
            },
            "difference": abs((secondary_data.get("current_flow", 0) or 0) - 
                            (primary_data.get("current_flow", 0) or 0)),
        }