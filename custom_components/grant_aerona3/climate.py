"""Climate platform for Grant Aerona3 Heat Pump."""
import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL, OPERATING_MODES
from .coordinator import GrantAerona3Coordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Grant Aerona3 climate entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = [
        GrantAerona3Climate(coordinator, config_entry, 1),  # Zone 1
        GrantAerona3Climate(coordinator, config_entry, 2),  # Zone 2
    ]
    
    async_add_entities(entities)


class GrantAerona3Climate(CoordinatorEntity, ClimateEntity):
    """Grant Aerona3 Climate entity."""

    def __init__(
        self,
        coordinator: GrantAerona3Coordinator,
        config_entry: ConfigEntry,
        zone: int,
    ) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self._zone = zone
        self._attr_unique_id = f"{config_entry.entry_id}_climate_zone_{zone}"
        self._attr_name = f"Grant Aerona3 Zone {zone}"
        
        # Device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Grant Aerona3 Heat Pump",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "sw_version": "1.0.0",
        }

        # Climate capabilities
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.TURN_ON
            | ClimateEntityFeature.TURN_OFF
        )
        
        self._attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT, HVACMode.COOL]
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_target_temperature_step = 0.5
        self._attr_min_temp = 23.0
        self._attr_max_temp = 60.0

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        # Use outgoing water temperature as current temperature
        if "input_9" in self.coordinator.data:
            return self.coordinator.data["input_9"]["value"]
        return None

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature."""
        # Get the fixed flow temperature for this zone
        holding_key = f"holding_{2 if self._zone == 1 else 7}"
        if holding_key in self.coordinator.data:
            return self.coordinator.data[holding_key]["value"]
        return None

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        if "input_10" in self.coordinator.data:
            mode = self.coordinator.data["input_10"]["value"]
            if mode == 0:
                return HVACMode.OFF
            elif mode == 1:
                return HVACMode.HEAT
            elif mode == 2:
                return HVACMode.COOL
        return HVACMode.OFF

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        attrs = {}
        
        # Add zone-specific set temperature
        set_temp_key = f"input_{10 + self._zone}"
        if set_temp_key in self.coordinator.data:
            attrs["zone_set_temperature"] = self.coordinator.data[set_temp_key]["value"]
        
        # Add weather compensation status
        wc_key = f"coil_{1 + self._zone}"
        if wc_key in self.coordinator.data:
            attrs["weather_compensation"] = self.coordinator.data[wc_key]["value"]
        
        # Add outdoor temperature
        if "input_6" in self.coordinator.data:
            attrs["outdoor_temperature"] = self.coordinator.data["input_6"]["value"]
        
        # Add return water temperature
        if "input_0" in self.coordinator.data:
            attrs["return_water_temperature"] = self.coordinator.data["input_0"]["value"]
        
        # Add power consumption
        if "input_3" in self.coordinator.data:
            attrs["power_consumption"] = self.coordinator.data["input_3"]["value"]
        
        return attrs

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return

        # Convert temperature to raw value (multiply by 2 for 0.5°C resolution)
        raw_value = int(temperature * 2)
        
        # Determine the holding register address for this zone
        address = 2 if self._zone == 1 else 7
        
        # Write to the holding register
        success = await self.coordinator.async_write_holding_register(address, raw_value)
        
        if success:
            # Request immediate update
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set temperature for zone %s", self._zone)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new HVAC mode."""
        # Note: The Grant Aerona3 operating mode is typically controlled by the main controller
        # This would require writing to specific control registers if available
        # For now, we'll log the request
        _LOGGER.info("HVAC mode change requested for zone %s: %s", self._zone, hvac_mode)
        
        # In a full implementation, you would write to the appropriate control register
        # based on the heat pump's control protocol