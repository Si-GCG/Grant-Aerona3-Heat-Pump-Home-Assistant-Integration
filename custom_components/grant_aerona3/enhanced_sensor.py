"""Enhanced sensor platform for Grant Aerona3 Heat Pump."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .enhanced_coordinator import GrantAerona3EnhancedCoordinator
from .register_manager import RegisterType, RegisterCategory
from .weather_compensation_entities import async_setup_weather_compensation_entities

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Grant Aerona3 enhanced sensor entities."""
    coordinator: GrantAerona3EnhancedCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = []
    
    # Create sensors for all enabled input registers
    input_registers = coordinator.register_manager.get_enabled_registers(RegisterType.INPUT)
    for register_id, register_config in input_registers.items():
        entities.append(
            GrantAerona3EnhancedSensor(coordinator, config_entry, register_id, register_config)
        )
    
    # Create sensors for enabled holding registers (read-only display)
    holding_registers = coordinator.register_manager.get_enabled_registers(RegisterType.HOLDING)
    for register_id, register_config in holding_registers.items():
        entities.append(
            GrantAerona3HoldingRegisterSensor(coordinator, config_entry, register_id, register_config)
        )
    
    # Add enhanced calculated sensors
    entities.extend([
        GrantAerona3EnhancedPowerSensor(coordinator, config_entry),
        GrantAerona3EnhancedEnergySensor(coordinator, config_entry),
        GrantAerona3EnhancedCOPSensor(coordinator, config_entry),
        GrantAerona3SystemRuntimeSensor(coordinator, config_entry),
        GrantAerona3EfficiencySensor(coordinator, config_entry),
    ])
    
    # Add diagnostic sensors if enabled
    if config_entry.data.get("diagnostic_monitoring", False):
        entities.extend([
            GrantAerona3SystemHealthSensor(coordinator, config_entry),
            GrantAerona3ErrorStatusSensor(coordinator, config_entry),
            GrantAerona3PerformanceMetricsSensor(coordinator, config_entry),
        ])
    
    # Setup weather compensation entities
    await async_setup_weather_compensation_entities(
        hass, config_entry, coordinator, coordinator.weather_compensation, async_add_entities
    )
    
    async_add_entities(entities)


class GrantAerona3EnhancedSensor(CoordinatorEntity, SensorEntity):
    """Enhanced Grant Aerona3 sensor entity using register manager."""

    def __init__(
        self,
        coordinator: GrantAerona3EnhancedCoordinator,
        config_entry: ConfigEntry,
        register_id: str,
        register_config,
    ) -> None:
        """Initialize the enhanced sensor."""
        super().__init__(coordinator)
        self._register_id = register_id
        self._register_config = register_config
        
        self._attr_unique_id = f"{config_entry.entry_id}_sensor_{register_id}"
        self._attr_name = f"Grant Aerona3 {register_config.name}"
        
        # Device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Grant Aerona3 Heat Pump",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "sw_version": "2.0.0",
        }
        
        # Set sensor properties
        self._attr_native_unit_of_measurement = register_config.unit
        self._attr_device_class = register_config.device_class
        
        # Set state class for numeric sensors
        if register_config.device_class in [
            SensorDeviceClass.TEMPERATURE,
            SensorDeviceClass.POWER,
            SensorDeviceClass.FREQUENCY,
            SensorDeviceClass.HUMIDITY,
        ]:
            self._attr_state_class = SensorStateClass.MEASUREMENT
        
        # Set entity category based on register category
        if register_config.category == RegisterCategory.DIAGNOSTIC:
            self._attr_entity_category = "diagnostic"

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if self._register_id not in self.coordinator.data:
            return None
            
        data = self.coordinator.data[self._register_id]
        
        # Use display_value if available (for enum mappings)
        if "display_value" in data:
            return data["display_value"]
            
        return data.get("value")

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        if self._register_id not in self.coordinator.data:
            return {}
            
        data = self.coordinator.data[self._register_id]
        
        attributes = {
            "register_id": self._register_id,
            "register_address": self._register_config.address,
            "register_category": self._register_config.category.value,
            "raw_value": data.get("raw_value"),
            "timestamp": data.get("timestamp"),
        }
        
        # Add user-friendly explanations for technical terms
        if self._register_config.description:
            attributes["description"] = self._register_config.description
            
        # Add helpful tooltips based on register type
        if "cop" in self._register_id.lower():
            attributes["tooltip"] = "COP (Coefficient of Performance) measures heat pump efficiency - higher numbers mean more efficient heating"
        elif "dhw" in self._register_id.lower():
            attributes["tooltip"] = "DHW (Domestic Hot Water) refers to your home's hot water system"
        elif "weather_compensation" in self._register_id.lower() or "wc" in self._register_id.lower():
            attributes["tooltip"] = "Weather Compensation automatically adjusts heating temperature based on outdoor conditions to save energy"
        elif "flow_temp" in self._register_id.lower():
            attributes["tooltip"] = "Flow temperature is the water temperature leaving the heat pump to heat your home"
        elif "return_temp" in self._register_id.lower():
            attributes["tooltip"] = "Return temperature is the cooled water coming back from your heating system"
        elif "compressor" in self._register_id.lower():
            attributes["tooltip"] = "The compressor is the heart of your heat pump that creates the heating effect"
        elif "defrost" in self._register_id.lower():
            attributes["tooltip"] = "Defrost mode removes ice from the outdoor unit during cold weather"
        
        # Add cached data indicator
        if data.get("cached", False):
            attributes["data_source"] = "cached"
            attributes["cache_age"] = data.get("cache_age", "unknown")
        else:
            attributes["data_source"] = "live"
            
        return attributes

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success and
            self._register_id in self.coordinator.data
        )


class GrantAerona3HoldingRegisterSensor(GrantAerona3EnhancedSensor):
    """Sensor for holding register values (read-only display)."""

    def __init__(
        self,
        coordinator: GrantAerona3EnhancedCoordinator,
        config_entry: ConfigEntry,
        register_id: str,
        register_config,
    ) -> None:
        """Initialize the holding register sensor."""
        super().__init__(coordinator, config_entry, register_id, register_config)
        
        # Override unique ID and name for holding registers
        self._attr_unique_id = f"{config_entry.entry_id}_holding_{register_id}"
        self._attr_name = f"Grant Aerona3 {register_config.name} (Current)"
        
        # Mark as diagnostic since these are configuration values
        self._attr_entity_category = "diagnostic"


class GrantAerona3EnhancedPowerSensor(CoordinatorEntity, SensorEntity):
    """Enhanced power consumption sensor with advanced features."""

    def __init__(
        self,
        coordinator: GrantAerona3EnhancedCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the enhanced power sensor."""
        super().__init__(coordinator)
        
        self._attr_unique_id = f"{config_entry.entry_id}_power_consumption_enhanced"
        self._attr_name = "Grant Aerona3 Power Consumption"
        self._attr_native_unit_of_measurement = UnitOfPower.WATT
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Grant Aerona3 Heat Pump",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "sw_version": "2.0.0",
        }
        
        # Power tracking for statistics
        self._power_history = []
        self._max_window_size = 100

    @property
    def native_value(self) -> Optional[float]:
        """Return the power consumption in watts."""
        if "power_consumption" in self.coordinator.data:
            power = self.coordinator.data["power_consumption"]["value"]
            
            # Track power history for statistics
            if len(self._power_history) >= self._max_window_size:
                self._power_history.pop(0)
            self._power_history.append(power)
            
            return power
        return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional power statistics."""
        if not self._power_history:
            return {}
            
        return {
            "average_power_1h": round(sum(self._power_history) / len(self._power_history), 1),
            "max_power_1h": round(max(self._power_history), 1),
            "min_power_1h": round(min(self._power_history), 1),
            "power_readings_count": len(self._power_history),
            "data_source": "calculated"
        }


class GrantAerona3EnhancedCOPSensor(CoordinatorEntity, SensorEntity):
    """Enhanced COP sensor with proper flow rate calculation."""

    def __init__(
        self,
        coordinator: GrantAerona3EnhancedCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the enhanced COP sensor."""
        super().__init__(coordinator)
        
        self._attr_unique_id = f"{config_entry.entry_id}_cop_enhanced"
        self._attr_name = "Grant Aerona3 COP"
        self._attr_native_unit_of_measurement = None
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:thermometer-chevron-up"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Grant Aerona3 Heat Pump",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "sw_version": "2.0.0",
        }
        
        self._config = config_entry.data

    @property
    def native_value(self) -> Optional[float]:
        """Return the calculated COP."""
        # Get required data
        power = self._get_sensor_value("power_consumption")
        flow_temp = self._get_sensor_value("flow_temp")
        return_temp = self._get_sensor_value("return_temp")
        
        if not all([power, flow_temp, return_temp]) or power <= 0:
            return None
        
        # Calculate temperature difference
        temp_diff = abs(flow_temp - return_temp)
        if temp_diff <= 0:
            return None
        
        # Get flow rate
        flow_rate = self._get_flow_rate()
        if not flow_rate:
            # Fallback to simplified calculation
            return self._calculate_simplified_cop(power, temp_diff)
        
        # Calculate heat output (Q = m * Cp * ΔT)
        # Where m = mass flow rate, Cp = specific heat capacity of water
        water_specific_heat = 4.18  # kJ/kg·K
        water_density = 1.0  # kg/L (approximate)
        
        # Convert flow rate to kg/s
        mass_flow_rate = (flow_rate * water_density) / 60  # kg/s
        
        # Calculate heat output in kW
        heat_output = (mass_flow_rate * water_specific_heat * temp_diff) / 1000
        
        # Calculate COP
        power_kw = power / 1000
        if power_kw > 0:
            cop = heat_output / power_kw
            return round(cop, 2)
        
        return None

    def _get_sensor_value(self, sensor_id: str) -> Optional[float]:
        """Get sensor value from coordinator data."""
        if sensor_id in self.coordinator.data:
            return self.coordinator.data[sensor_id].get("value")
        return None

    def _get_flow_rate(self) -> Optional[float]:
        """Get flow rate from configuration or sensor."""
        flow_method = self._config.get("flow_rate_method", "fixed_rate")
        
        if flow_method == "fixed_rate":
            return self._config.get("flow_rate", 20)
        elif flow_method == "flow_meter":
            return self._get_sensor_value("flow_rate")
        elif flow_method == "calculated_rate":
            # Use pump speed to estimate flow rate
            pump_speed = self._get_sensor_value("pump_speed")
            if pump_speed:
                # Simplified calculation - adjust based on system characteristics
                return pump_speed / 100 * 25  # Rough estimation
        
        return None

    def _calculate_simplified_cop(self, power: float, temp_diff: float) -> Optional[float]:
        """Calculate simplified COP without flow rate."""
        # Very rough estimation for display purposes
        if temp_diff > 0:
            estimated_efficiency = 3.0 + (temp_diff / 10)  # Base efficiency + temp factor
            return round(min(estimated_efficiency, 6.0), 2)  # Cap at 6.0
        return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional COP calculation details."""
        flow_method = self._config.get("flow_rate_method", "fixed_rate")
        flow_rate = self._get_flow_rate()
        
        attributes = {
            "calculation_method": "enhanced" if flow_rate else "simplified",
            "flow_rate_method": flow_method,
            "flow_rate": flow_rate,
            "tooltip": "COP (Coefficient of Performance) measures how efficiently your heat pump converts electricity into heat. A COP of 3.0 means you get 3kW of heat for every 1kW of electricity used.",
            "explanation": "Higher COP values mean better efficiency and lower running costs. Typical values: 2.5-4.0 for air source heat pumps.",
            "factors_affecting_cop": "Outdoor temperature, flow temperature, system age, and maintenance all affect COP performance."
        }
        
        if flow_rate:
            attributes["note"] = "COP calculated using actual flow rate and temperature differential"
        else:
            attributes["note"] = "Simplified COP calculation - install flow meter for accuracy"
            
        return attributes


class GrantAerona3SystemRuntimeSensor(CoordinatorEntity, SensorEntity):
    """System runtime sensor."""

    def __init__(
        self,
        coordinator: GrantAerona3EnhancedCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the runtime sensor."""
        super().__init__(coordinator)
        
        self._attr_unique_id = f"{config_entry.entry_id}_system_runtime"
        self._attr_name = "Grant Aerona3 System Runtime"
        self._attr_native_unit_of_measurement = UnitOfTime.HOURS
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
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
        """Return the system runtime hours."""
        if "system_runtime" in self.coordinator.data:
            return self.coordinator.data["system_runtime"]["value"]
        return None


class GrantAerona3EfficiencySensor(CoordinatorEntity, SensorEntity):
    """System efficiency sensor."""

    def __init__(
        self,
        coordinator: GrantAerona3EnhancedCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the efficiency sensor."""
        super().__init__(coordinator)
        
        self._attr_unique_id = f"{config_entry.entry_id}_system_efficiency"
        self._attr_name = "Grant Aerona3 System Efficiency"
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_icon = "mdi:gauge"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Grant Aerona3 Heat Pump",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "sw_version": "2.0.0",
        }

    @property
    def native_value(self) -> Optional[float]:
        """Return the system efficiency percentage."""
        # Get COP and convert to efficiency percentage
        if "cop_enhanced" in self.coordinator.data:
            cop = self.coordinator.data["cop_enhanced"]["value"]
            if cop and cop > 0:
                # Efficiency = (COP - 1) / COP * 100
                # This represents the percentage of energy that comes from the environment
                efficiency = ((cop - 1) / cop) * 100
                return round(efficiency, 1)
        return None


class GrantAerona3SystemHealthSensor(CoordinatorEntity, SensorEntity):
    """System health sensor."""

    def __init__(
        self,
        coordinator: GrantAerona3EnhancedCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the system health sensor."""
        super().__init__(coordinator)
        
        self._attr_unique_id = f"{config_entry.entry_id}_system_health"
        self._attr_name = "Grant Aerona3 System Health"
        self._attr_icon = "mdi:heart-pulse"
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
        """Return the system health status."""
        # Check various system parameters to determine health
        errors = []
        
        # Check for error codes
        if "error_code_1" in self.coordinator.data:
            error1 = self.coordinator.data["error_code_1"]["value"]
            if error1 != 0:
                errors.append(f"Error Code 1: {error1}")
                
        if "error_code_2" in self.coordinator.data:
            error2 = self.coordinator.data["error_code_2"]["value"]
            if error2 != 0:
                errors.append(f"Error Code 2: {error2}")
        
        # Check operating parameters
        warnings = []
        
        # Check compressor frequency
        if "compressor_frequency" in self.coordinator.data:
            freq = self.coordinator.data["compressor_frequency"]["value"]
            if freq > 120:  # High frequency might indicate stress
                warnings.append("High compressor frequency")
        
        # Determine overall health
        if errors:
            return "Error"
        elif warnings:
            return "Warning"
        else:
            return "Good"

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return health details."""
        return {
            "last_check": datetime.now().isoformat(),
            "coordinator_errors": self.coordinator._connection_errors,
            "data_freshness": "fresh" if self.coordinator.last_update_success else "stale"
        }


class GrantAerona3ErrorStatusSensor(CoordinatorEntity, SensorEntity):
    """Error status sensor."""

    def __init__(
        self,
        coordinator: GrantAerona3EnhancedCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the error status sensor."""
        super().__init__(coordinator)
        
        self._attr_unique_id = f"{config_entry.entry_id}_error_status"
        self._attr_name = "Grant Aerona3 Error Status"
        self._attr_icon = "mdi:alert-circle"
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
        """Return the current error status."""
        error_codes = []
        
        if "error_code_1" in self.coordinator.data:
            error1 = self.coordinator.data["error_code_1"]["value"]
            if error1 != 0:
                error_codes.append(f"E1:{error1}")
                
        if "error_code_2" in self.coordinator.data:
            error2 = self.coordinator.data["error_code_2"]["value"]
            if error2 != 0:
                error_codes.append(f"E2:{error2}")
        
        if error_codes:
            return ", ".join(error_codes)
        else:
            return "No Errors"


class GrantAerona3PerformanceMetricsSensor(CoordinatorEntity, SensorEntity):
    """Performance metrics sensor."""

    def __init__(
        self,
        coordinator: GrantAerona3EnhancedCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the performance metrics sensor."""
        super().__init__(coordinator)
        
        self._attr_unique_id = f"{config_entry.entry_id}_performance_metrics"
        self._attr_name = "Grant Aerona3 Performance Metrics"
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
        """Return the performance summary."""
        return "Active"

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return performance statistics."""
        stats = self.coordinator.get_performance_stats()
        
        return {
            "enabled_registers": stats.get("total_enabled_registers", 0),
            "connection_errors": stats.get("connection_errors", 0),
            "average_read_time": self._get_average_read_time(stats),
            "last_update": datetime.now().isoformat()
        }

    def _get_average_read_time(self, stats: Dict[str, Any]) -> Optional[float]:
        """Calculate average read time across all registers."""
        performance_data = stats.get("register_performance", {})
        if not performance_data:
            return None
            
        total_avg = sum(
            data.get("avg_read_time", 0) 
            for data in performance_data.values()
        )
        
        return round(total_avg / len(performance_data), 4) if performance_data else None


class GrantAerona3EnhancedEnergySensor(CoordinatorEntity, SensorEntity):
    """Enhanced energy consumption sensor."""

    def __init__(
        self,
        coordinator: GrantAerona3EnhancedCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the enhanced energy sensor."""
        super().__init__(coordinator)
        
        self._attr_unique_id = f"{config_entry.entry_id}_energy_consumption_enhanced"
        self._attr_name = "Grant Aerona3 Energy Consumption"
        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Grant Aerona3 Heat Pump",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "sw_version": "2.0.0",
        }
        
        self._last_power = None
        self._last_update = None
        self._total_energy = 0.0

    @property
    def native_value(self) -> float:
        """Return the total energy consumption in kWh."""
        if "power_consumption" in self.coordinator.data:
            current_power = self.coordinator.data["power_consumption"]["value"]
            current_time = datetime.now()
            
            if (self._last_power is not None and 
                self._last_update is not None and 
                current_power > 0):
                
                # Calculate time delta in hours
                time_delta = (current_time - self._last_update).total_seconds() / 3600
                
                # Calculate energy using average power over time period
                avg_power = (current_power + self._last_power) / 2
                energy_delta = (avg_power / 1000) * time_delta
                self._total_energy += energy_delta
            
            self._last_power = current_power
            self._last_update = current_time
        
        return round(self._total_energy, 3)

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional energy attributes."""
        return {
            "last_power": self._last_power,
            "calculation_method": "integration",
            "note": "Energy calculated by integrating power consumption over time"
        }