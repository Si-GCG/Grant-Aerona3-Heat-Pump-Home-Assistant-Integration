"""Sensor platform for Grant Aerona3 Heat Pump."""
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DAYS_OF_WEEK,
    DHW_MODES,
    DOMAIN,
    INPUT_REGISTER_MAP,
    MANUFACTURER,
    MODEL,
    OPERATING_MODES,
)
from .coordinator import GrantAerona3Coordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Grant Aerona3 sensor entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = []
    
    # Create sensors for all input registers
    for addr, config in INPUT_REGISTER_MAP.items():
        entities.append(
            GrantAerona3Sensor(coordinator, config_entry, addr, config)
        )
    
    # Add calculated sensors
    entities.extend([
        GrantAerona3PowerSensor(coordinator, config_entry),
        GrantAerona3EnergySensor(coordinator, config_entry),
        GrantAerona3COPSensor(coordinator, config_entry),
    ])
    
    async_add_entities(entities)


class GrantAerona3Sensor(CoordinatorEntity, SensorEntity):
    """Grant Aerona3 sensor entity."""

    def __init__(
        self,
        coordinator: GrantAerona3Coordinator,
        config_entry: ConfigEntry,
        register_addr: int,
        register_config: dict[str, Any],
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._register_addr = register_addr
        self._register_config = register_config
        
        self._attr_unique_id = f"{config_entry.entry_id}_sensor_{register_addr}"
        self._attr_name = f"Grant Aerona3 {register_config['name']}"
        
        # Device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Grant Aerona3 Heat Pump",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "sw_version": "1.0.0",
        }
        
        # Set sensor properties based on register config
        self._attr_native_unit_of_measurement = register_config.get("unit")
        self._attr_device_class = register_config.get("device_class")
        
        # Set state class for numeric sensors
        if register_config.get("device_class") in [
            SensorDeviceClass.TEMPERATURE,
            SensorDeviceClass.POWER,
            SensorDeviceClass.FREQUENCY,
        ]:
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        data_key = f"input_{self._register_addr}"
        if data_key not in self.coordinator.data:
            return None
            
        value = self.coordinator.data[data_key]["value"]
        
        # Handle special cases for enum values
        if self._register_addr == 10:  # Operating mode
            return OPERATING_MODES.get(value, f"Unknown ({value})")
        elif self._register_addr == 13:  # DHW mode
            return DHW_MODES.get(value, f"Unknown ({value})")
        elif self._register_addr == 14:  # Day of week
            return DAYS_OF_WEEK.get(value, f"Unknown ({value})")
        elif self._register_addr == 15:  # Clock
            # Convert minutes since midnight to HH:MM format
            hours = value // 60
            minutes = value % 60
            return f"{hours:02d}:{minutes:02d}"
        
        return value

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        data_key = f"input_{self._register_addr}"
        if data_key not in self.coordinator.data:
            return {}
            
        return {
            "raw_value": self.coordinator.data[data_key]["raw_value"],
            "register_address": self._register_addr,
        }


class GrantAerona3PowerSensor(CoordinatorEntity, SensorEntity):
    """Grant Aerona3 power consumption sensor with proper scaling."""

    def __init__(
        self,
        coordinator: GrantAerona3Coordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the power sensor."""
        super().__init__(coordinator)
        
        self._attr_unique_id = f"{config_entry.entry_id}_power_consumption"
        self._attr_name = "Grant Aerona3 Power Consumption"
        self._attr_native_unit_of_measurement = UnitOfPower.WATT
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT
        
        # Device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Grant Aerona3 Heat Pump",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "sw_version": "1.0.0",
        }

    @property
    def native_value(self) -> float | None:
        """Return the power consumption in watts."""
        if "input_3" in self.coordinator.data:
            return self.coordinator.data["input_3"]["value"]
        return None


class GrantAerona3EnergySensor(CoordinatorEntity, SensorEntity):
    """Grant Aerona3 energy consumption sensor."""

    def __init__(
        self,
        coordinator: GrantAerona3Coordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the energy sensor."""
        super().__init__(coordinator)
        
        self._attr_unique_id = f"{config_entry.entry_id}_energy_consumption"
        self._attr_name = "Grant Aerona3 Energy Consumption"
        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        
        # Device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Grant Aerona3 Heat Pump",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "sw_version": "1.0.0",
        }
        
        self._last_power = None
        self._total_energy = 0.0

    @property
    def native_value(self) -> float:
        """Return the total energy consumption in kWh."""
        # This is a simplified energy calculation
        # In a real implementation, you might want to use the integration sensor
        # or store energy data persistently
        if "input_3" in self.coordinator.data:
            current_power = self.coordinator.data["input_3"]["value"]
            
            if self._last_power is not None and current_power > 0:
                # Estimate energy based on power and time interval
                # This is a rough calculation - for accurate energy monitoring,
                # consider using Home Assistant's integration sensor
                time_delta_hours = 30 / 3600  # 30 seconds in hours
                energy_delta = (current_power / 1000) * time_delta_hours
                self._total_energy += energy_delta
            
            self._last_power = current_power
        
        return round(self._total_energy, 3)


class GrantAerona3COPSensor(CoordinatorEntity, SensorEntity):
    """Grant Aerona3 Coefficient of Performance sensor."""

    def __init__(
        self,
        coordinator: GrantAerona3Coordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the COP sensor."""
        super().__init__(coordinator)
        
        self._attr_unique_id = f"{config_entry.entry_id}_cop"
        self._attr_name = "Grant Aerona3 COP"
        self._attr_native_unit_of_measurement = None
        self._attr_state_class = SensorStateClass.MEASUREMENT
        
        # Device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Grant Aerona3 Heat Pump",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "sw_version": "1.0.0",
        }

    @property
    def native_value(self) -> float | None:
        """Return the calculated COP."""
        # COP calculation requires heat output and electrical input
        # This is a simplified calculation - for accurate COP,
        # you would need flow rate and temperature differential
        
        if "input_3" not in self.coordinator.data:
            return None
            
        power_consumption = self.coordinator.data["input_3"]["value"]
        
        if power_consumption <= 0:
            return None
        
        # Get temperature data for rough heat output estimation
        flow_temp = None
        return_temp = None
        
        if "input_9" in self.coordinator.data:
            flow_temp = self.coordinator.data["input_9"]["value"]
        if "input_0" in self.coordinator.data:
            return_temp = self.coordinator.data["input_0"]["value"]
        
        if flow_temp is None or return_temp is None:
            return None
        
        # Simplified COP calculation (this is not accurate without flow rate)
        # This is just an example - real COP requires proper heat measurement
        temp_diff = abs(flow_temp - return_temp)
        if temp_diff > 0:
            # Very rough estimation - not scientifically accurate
            estimated_heat_output = power_consumption * (1 + temp_diff / 10)
            cop = estimated_heat_output / power_consumption
            return round(cop, 2)
        
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        return {
            "note": "This is a simplified COP calculation. For accurate COP measurement, use external heat and power meters."
        }