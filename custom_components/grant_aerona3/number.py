"""Number platform for Grant Aerona3 Heat Pump."""
import logging
from typing import Any

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, HOLDING_REGISTER_MAP, MANUFACTURER, MODEL
from .coordinator import GrantAerona3Coordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Grant Aerona3 number entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = []
    
    # Create number entities for all holding registers
    for addr, config in HOLDING_REGISTER_MAP.items():
        entities.append(
            GrantAerona3Number(coordinator, config_entry, addr, config)
        )
    
    async_add_entities(entities)


class GrantAerona3Number(CoordinatorEntity, NumberEntity):
    """Grant Aerona3 number entity for temperature setpoints."""

    def __init__(
        self,
        coordinator: GrantAerona3Coordinator,
        config_entry: ConfigEntry,
        register_addr: int,
        register_config: dict[str, Any],
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._register_addr = register_addr
        self._register_config = register_config
        
        self._attr_unique_id = f"{config_entry.entry_id}_number_{register_addr}"
        self._attr_name = f"Grant Aerona3 {register_config['name']}"
        
        # Device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Grant Aerona3 Heat Pump",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "sw_version": "1.0.0",
        }
        
        # Set number properties
        self._attr_native_min_value = register_config["min"]
        self._attr_native_max_value = register_config["max"]
        self._attr_native_step = 0.5  # 0.5°C steps
        self._attr_native_unit_of_measurement = register_config["unit"]
        self._attr_mode = "box"  # Allow direct input

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        data_key = f"holding_{self._register_addr}"
        if data_key in self.coordinator.data:
            return self.coordinator.data[data_key]["value"]
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        data_key = f"holding_{self._register_addr}"
        if data_key not in self.coordinator.data:
            return {}
            
        return {
            "raw_value": self.coordinator.data[data_key]["raw_value"],
            "register_address": self._register_addr,
            "min_value": self._register_config["min"],
            "max_value": self._register_config["max"],
        }

    async def async_set_native_value(self, value: float) -> None:
        """Set the temperature setpoint."""
        # Convert temperature to raw value (multiply by 2 for 0.5°C resolution)
        raw_value = int(value * 2)
        
        # Ensure value is within bounds
        if value < self._attr_native_min_value or value > self._attr_native_max_value:
            _LOGGER.error(
                "Temperature %s is out of bounds (%s-%s) for %s",
                value,
                self._attr_native_min_value,
                self._attr_native_max_value,
                self._attr_name,
            )
            return
        
        # Write to the holding register
        success = await self.coordinator.async_write_holding_register(
            self._register_addr, raw_value
        )
        
        if success:
            # Request immediate update
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set value for %s", self._attr_name)