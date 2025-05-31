"""Binary sensor platform for Grant Aerona3 Heat Pump."""
import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import GrantAerona3Coordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Grant Aerona3 binary sensor entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = [
        GrantAerona3StatusSensor(coordinator, config_entry, "heating", "Heating Active"),
        GrantAerona3StatusSensor(coordinator, config_entry, "cooling", "Cooling Active"),
        GrantAerona3StatusSensor(coordinator, config_entry, "dhw", "DHW Active"),
        GrantAerona3StatusSensor(coordinator, config_entry, "defrost", "Defrost Active"),
        GrantAerona3StatusSensor(coordinator, config_entry, "compressor", "Compressor Running"),
        GrantAerona3StatusSensor(coordinator, config_entry, "pump", "Water Pump Running"),
        GrantAerona3StatusSensor(coordinator, config_entry, "fan", "Fan Running"),
    ]
    
    async_add_entities(entities)


class GrantAerona3StatusSensor(CoordinatorEntity, BinarySensorEntity):
    """Grant Aerona3 status binary sensor."""

    def __init__(
        self,
        coordinator: GrantAerona3Coordinator,
        config_entry: ConfigEntry,
        sensor_type: str,
        name: str,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        
        self._attr_unique_id = f"{config_entry.entry_id}_binary_sensor_{sensor_type}"
        self._attr_name = f"Grant Aerona3 {name}"
        
        # Device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Grant Aerona3 Heat Pump",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "sw_version": "1.0.0",
        }
        
        # Set device class based on sensor type
        if sensor_type in ["heating", "cooling"]:
            self._attr_device_class = BinarySensorDeviceClass.HEAT
        elif sensor_type == "compressor":
            self._attr_device_class = BinarySensorDeviceClass.RUNNING
        elif sensor_type in ["pump", "fan"]:
            self._attr_device_class = BinarySensorDeviceClass.RUNNING
        else:
            self._attr_device_class = BinarySensorDeviceClass.RUNNING

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        if self._sensor_type == "heating":
            # Check if operating mode is heating (1)
            if "input_10" in self.coordinator.data:
                return self.coordinator.data["input_10"]["value"] == 1
                
        elif self._sensor_type == "cooling":
            # Check if operating mode is cooling (2)
            if "input_10" in self.coordinator.data:
                return self.coordinator.data["input_10"]["value"] == 2
                
        elif self._sensor_type == "dhw":
            # Check if DHW mode is active (not disabled)
            if "input_13" in self.coordinator.data:
                return self.coordinator.data["input_13"]["value"] > 0
                
        elif self._sensor_type == "defrost":
            # Check if defrost temperature is significantly different from outdoor temp
            if "input_5" in self.coordinator.data and "input_6" in self.coordinator.data:
                defrost_temp = self.coordinator.data["input_5"]["value"]
                outdoor_temp = self.coordinator.data["input_6"]["value"]
                # Simple heuristic: defrost active if defrost temp > outdoor temp + 5°C
                return defrost_temp > (outdoor_temp + 5)
                
        elif self._sensor_type == "compressor":
            # Check if compressor frequency > 0
            if "input_1" in self.coordinator.data:
                return self.coordinator.data["input_1"]["value"] > 0
                
        elif self._sensor_type == "pump":
            # Check if water pump speed > 0
            if "input_7" in self.coordinator.data:
                return self.coordinator.data["input_7"]["value"] > 0
                
        elif self._sensor_type == "fan":
            # Check if fan speed > 0
            if "input_4" in self.coordinator.data:
                return self.coordinator.data["input_4"]["value"] > 0
        
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        attrs = {"sensor_type": self._sensor_type}
        
        # Add relevant data based on sensor type
        if self._sensor_type == "compressor" and "input_1" in self.coordinator.data:
            attrs["frequency"] = self.coordinator.data["input_1"]["value"]
            
        elif self._sensor_type == "pump" and "input_7" in self.coordinator.data:
            attrs["speed"] = self.coordinator.data["input_7"]["value"]
            
        elif self._sensor_type == "fan" and "input_4" in self.coordinator.data:
            attrs["speed"] = self.coordinator.data["input_4"]["value"]
            
        elif self._sensor_type == "defrost":
            if "input_5" in self.coordinator.data:
                attrs["defrost_temperature"] = self.coordinator.data["input_5"]["value"]
            if "input_6" in self.coordinator.data:
                attrs["outdoor_temperature"] = self.coordinator.data["input_6"]["value"]
        
        return attrs