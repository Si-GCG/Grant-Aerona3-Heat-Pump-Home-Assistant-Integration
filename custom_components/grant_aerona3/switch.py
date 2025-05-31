"""Switch platform for Grant Aerona3 Heat Pump."""
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import COIL_REGISTER_MAP, DOMAIN, MANUFACTURER, MODEL
from .coordinator import GrantAerona3Coordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Grant Aerona3 switch entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = []
    
    # Create switches for all coil registers
    for addr, config in COIL_REGISTER_MAP.items():
        entities.append(
            GrantAerona3Switch(coordinator, config_entry, addr, config)
        )
    
    async_add_entities(entities)


class GrantAerona3Switch(CoordinatorEntity, SwitchEntity):
    """Grant Aerona3 switch entity."""

    def __init__(
        self,
        coordinator: GrantAerona3Coordinator,
        config_entry: ConfigEntry,
        register_addr: int,
        register_config: dict[str, Any],
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._register_addr = register_addr
        self._register_config = register_config
        
        self._attr_unique_id = f"{config_entry.entry_id}_switch_{register_addr}"
        self._attr_name = f"Grant Aerona3 {register_config['name']}"
        
        # Device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Grant Aerona3 Heat Pump",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "sw_version": "1.0.0",
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if switch is on."""
        data_key = f"coil_{self._register_addr}"
        if data_key in self.coordinator.data:
            return self.coordinator.data[data_key]["value"]
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        return {
            "description": self._register_config["description"],
            "register_address": self._register_addr,
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        success = await self.coordinator.async_write_coil(self._register_addr, True)
        
        if success:
            # Request immediate update
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to turn on switch %s", self._attr_name)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        success = await self.coordinator.async_write_coil(self._register_addr, False)
        
        if success:
            # Request immediate update
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to turn off switch %s", self._attr_name)