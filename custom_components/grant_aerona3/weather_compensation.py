"""Weather compensation system for Grant Aerona3 Heat Pump."""
from __future__ import annotations

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

_LOGGER = logging.getLogger(__name__)


class WeatherCompensationMode(Enum):
    """Weather compensation operating modes."""
    DISABLED = "disabled"
    FIXED_FLOW = "fixed_flow"
    WEATHER_COMPENSATION = "weather_compensation"
    DUAL_CURVE = "dual_curve"


class CurveType(Enum):
    """Heating curve types."""
    LINEAR = "linear"
    QUADRATIC = "quadratic"
    CUSTOM = "custom"


@dataclass
class HeatingCurveConfig:
    """Configuration for a heating curve."""
    name: str
    min_outdoor_temp: float
    max_outdoor_temp: float
    min_flow_temp: float
    max_flow_temp: float
    curve_type: CurveType = CurveType.LINEAR
    curve_steepness: float = 1.0
    enabled: bool = True


@dataclass
class WeatherCompensationConfig:
    """Configuration for weather compensation system."""
    mode: WeatherCompensationMode
    primary_curve: HeatingCurveConfig
    secondary_curve: Optional[HeatingCurveConfig] = None
    zone_settings: Dict[str, Dict[str, Any]] = None
    update_interval: int = 60  # seconds
    boost_settings: Dict[str, Any] = None


class LinearHeatingCurve:
    """Linear heating curve calculator."""
    
    def __init__(self, config: HeatingCurveConfig):
        """Initialize the heating curve."""
        self.config = config
        self.name = config.name
        self.min_outdoor_temp = config.min_outdoor_temp
        self.max_outdoor_temp = config.max_outdoor_temp
        self.min_flow_temp = config.min_flow_temp
        self.max_flow_temp = config.max_flow_temp
        
    def calculate_flow_temperature(self, outdoor_temp: float) -> float:
        """Calculate target flow temperature based on outdoor temperature."""
        
        # Clamp outdoor temperature to configured range
        outdoor_temp = max(self.min_outdoor_temp, 
                          min(self.max_outdoor_temp, outdoor_temp))
        
        # Handle edge cases
        if outdoor_temp <= self.min_outdoor_temp:
            return self.max_flow_temp
        elif outdoor_temp >= self.max_outdoor_temp:
            return self.min_flow_temp
        
        # Linear interpolation
        temp_range = self.max_outdoor_temp - self.min_outdoor_temp
        flow_range = self.max_flow_temp - self.min_flow_temp
        
        outdoor_ratio = (outdoor_temp - self.min_outdoor_temp) / temp_range
        target_flow = self.max_flow_temp - (outdoor_ratio * flow_range)
        
        return round(target_flow, 1)
    
    def get_curve_points(self, num_points: int = 10) -> list[Tuple[float, float]]:
        """Get points along the curve for visualization."""
        points = []
        
        for i in range(num_points):
            outdoor_temp = self.min_outdoor_temp + (
                (self.max_outdoor_temp - self.min_outdoor_temp) * i / (num_points - 1)
            )
            flow_temp = self.calculate_flow_temperature(outdoor_temp)
            points.append((outdoor_temp, flow_temp))
            
        return points
    
    def validate_config(self) -> list[str]:
        """Validate heating curve configuration."""
        errors = []
        
        if self.min_outdoor_temp >= self.max_outdoor_temp:
            errors.append("Minimum outdoor temperature must be less than maximum")
            
        if self.min_flow_temp >= self.max_flow_temp:
            errors.append("Minimum flow temperature must be less than maximum")
            
        if not (-30 <= self.min_outdoor_temp <= 20):
            errors.append("Minimum outdoor temperature must be between -30°C and 20°C")
            
        if not (15 <= self.max_outdoor_temp <= 30):
            errors.append("Maximum outdoor temperature must be between 15°C and 30°C")
            
        if not (20 <= self.min_flow_temp <= 40):
            errors.append("Minimum flow temperature must be between 20°C and 40°C")
            
        if not (35 <= self.max_flow_temp <= 70):
            errors.append("Maximum flow temperature must be between 35°C and 70°C")
            
        return errors


class AdvancedHeatingCurve(LinearHeatingCurve):
    """Advanced heating curve with quadratic and custom options."""
    
    def __init__(self, config: HeatingCurveConfig):
        """Initialize the advanced heating curve."""
        super().__init__(config)
        self.curve_type = config.curve_type
        self.curve_steepness = config.curve_steepness
        
    def calculate_flow_temperature(self, outdoor_temp: float) -> float:
        """Calculate flow temperature using selected curve type."""
        
        if self.curve_type == CurveType.LINEAR:
            return super().calculate_flow_temperature(outdoor_temp)
        elif self.curve_type == CurveType.QUADRATIC:
            return self._quadratic_curve(outdoor_temp)
        elif self.curve_type == CurveType.CUSTOM:
            return self._custom_curve(outdoor_temp)
        else:
            return super().calculate_flow_temperature(outdoor_temp)
            
    def _quadratic_curve(self, outdoor_temp: float) -> float:
        """Quadratic curve for more aggressive response at low temperatures."""
        # Clamp outdoor temperature
        outdoor_temp = max(self.min_outdoor_temp, 
                          min(self.max_outdoor_temp, outdoor_temp))
        
        # Normalize outdoor temperature to 0-1 range
        normalized = (outdoor_temp - self.min_outdoor_temp) / \
                    (self.max_outdoor_temp - self.min_outdoor_temp)
        
        # Apply quadratic transformation
        quadratic_factor = 1 - (normalized ** self.curve_steepness)
        
        # Calculate flow temperature
        flow_range = self.max_flow_temp - self.min_flow_temp
        target_flow = self.min_flow_temp + (quadratic_factor * flow_range)
        
        return round(target_flow, 1)
        
    def _custom_curve(self, outdoor_temp: float) -> float:
        """Custom curve with user-defined characteristics."""
        # For now, implement as enhanced linear with adjustable steepness
        linear_result = super().calculate_flow_temperature(outdoor_temp)
        
        # Apply steepness adjustment
        if outdoor_temp <= 0:  # Cold weather - increase aggressiveness
            adjustment = (self.curve_steepness - 1.0) * 5.0
            return round(min(self.max_flow_temp, linear_result + adjustment), 1)
        else:
            return linear_result


class DualCurveWeatherCompensation:
    """Dual curve weather compensation system."""
    
    def __init__(self, hass: HomeAssistant, coordinator, config: WeatherCompensationConfig):
        """Initialize dual curve system."""
        self.hass = hass
        self.coordinator = coordinator
        self.config = config
        
        # Initialize curves
        self.primary_curve = AdvancedHeatingCurve(config.primary_curve)
        self.secondary_curve = None
        if config.secondary_curve:
            self.secondary_curve = AdvancedHeatingCurve(config.secondary_curve)
        
        # Current state
        self.active_curve = "primary"
        self.boost_active = False
        self.boost_end_time: Optional[datetime] = None
        self.last_outdoor_temp: Optional[float] = None
        self.last_flow_temp: Optional[float] = None
        
        # Performance tracking
        self.calculation_count = 0
        self.last_update = datetime.now()
        
    async def async_setup(self):
        """Initialize weather compensation system."""
        # Validate configuration
        validation_errors = self._validate_configuration()
        if validation_errors:
            _LOGGER.error("Weather compensation configuration errors: %s", validation_errors)
            return False
            
        # Start update loop
        self._start_update_loop()
        
        _LOGGER.info(
            "Weather compensation system initialized. Mode: %s, Primary curve: %s",
            self.config.mode.value,
            self.primary_curve.name
        )
        
        return True
        
    def _validate_configuration(self) -> list[str]:
        """Validate weather compensation configuration."""
        errors = []
        
        # Validate primary curve
        primary_errors = self.primary_curve.validate_config()
        if primary_errors:
            errors.extend([f"Primary curve: {error}" for error in primary_errors])
            
        # Validate secondary curve if present
        if self.secondary_curve:
            secondary_errors = self.secondary_curve.validate_config()
            if secondary_errors:
                errors.extend([f"Secondary curve: {error}" for error in secondary_errors])
                
        return errors
        
    def _start_update_loop(self):
        """Start the weather compensation update loop."""
        async def update_weather_compensation(now):
            """Update weather compensation calculations."""
            await self._async_update_weather_compensation()
            
        # Schedule regular updates
        async_track_time_interval(
            self.hass,
            update_weather_compensation,
            timedelta(seconds=self.config.update_interval)
        )
        
    async def _async_update_weather_compensation(self):
        """Update weather compensation calculations."""
        try:
            # Get current outdoor temperature
            outdoor_temp = await self._get_outdoor_temperature()
            if outdoor_temp is None:
                _LOGGER.warning("Could not get outdoor temperature for weather compensation")
                return
                
            # Calculate target flow temperature
            target_flow_temp = await self._calculate_target_flow_temperature(outdoor_temp)
            
            # Apply zone-specific adjustments if configured
            zone_adjustments = self._calculate_zone_adjustments(target_flow_temp)
            
            # Update heat pump setpoints
            await self._apply_flow_temperature_setpoints(zone_adjustments)
            
            # Update tracking variables
            self.last_outdoor_temp = outdoor_temp
            self.last_flow_temp = target_flow_temp
            self.calculation_count += 1
            self.last_update = datetime.now()
            
            _LOGGER.debug(
                "Weather compensation updated: outdoor=%.1f°C, target_flow=%.1f°C, curve=%s",
                outdoor_temp, target_flow_temp, self.active_curve
            )
            
        except Exception as err:
            _LOGGER.error("Error updating weather compensation: %s", err)
            
    async def _get_outdoor_temperature(self) -> Optional[float]:
        """Get current outdoor temperature from coordinator."""
        # Try external outdoor temperature sensor first
        if "external_outdoor_temp" in self.coordinator.data:
            return self.coordinator.data["external_outdoor_temp"]["value"]
            
        # Fallback to main outdoor temperature sensor
        if "outdoor_temp" in self.coordinator.data:
            return self.coordinator.data["outdoor_temp"]["value"]
            
        return None
        
    async def _calculate_target_flow_temperature(self, outdoor_temp: float) -> float:
        """Calculate target flow temperature using active curve."""
        
        # Check if boost mode is active
        if self.boost_active and self.secondary_curve:
            # Check if boost has expired
            if self.boost_end_time and datetime.now() > self.boost_end_time:
                await self.deactivate_boost_mode("timeout")
            else:
                return self.secondary_curve.calculate_flow_temperature(outdoor_temp)
        
        # Use primary curve
        return self.primary_curve.calculate_flow_temperature(outdoor_temp)
        
    def _calculate_zone_adjustments(self, base_flow_temp: float) -> Dict[str, float]:
        """Calculate zone-specific flow temperature adjustments."""
        zone_adjustments = {}
        
        # Zone 1 always gets base temperature
        zone_adjustments["zone_1"] = base_flow_temp
        
        # Zone 2 adjustments if configured
        if (self.config.zone_settings and 
            "zone_2" in self.config.zone_settings and
            self.config.zone_settings["zone_2"].get("enabled", False)):
            
            zone_2_settings = self.config.zone_settings["zone_2"]
            zone_2_factor = zone_2_settings.get("compensation_factor", 1.0)
            zone_2_offset = zone_2_settings.get("temperature_offset", 0.0)
            
            zone_2_temp = (base_flow_temp * zone_2_factor) + zone_2_offset
            
            # Apply zone 2 limits
            min_temp = zone_2_settings.get("min_flow_temp", 20.0)
            max_temp = zone_2_settings.get("max_flow_temp", 60.0)
            zone_2_temp = max(min_temp, min(max_temp, zone_2_temp))
            
            zone_adjustments["zone_2"] = zone_2_temp
            
        return zone_adjustments
        
    async def _apply_flow_temperature_setpoints(self, zone_adjustments: Dict[str, float]):
        """Apply calculated flow temperatures to heat pump zones."""
        
        for zone_id, target_temp in zone_adjustments.items():
            # Determine the appropriate register based on zone
            if zone_id == "zone_1":
                register_id = "zone1_fixed_flow"
            elif zone_id == "zone_2":
                register_id = "zone2_fixed_flow"
            else:
                continue
                
            # Write to holding register
            success = await self.coordinator.async_write_holding_register_enhanced(
                register_id, target_temp
            )
            
            if not success:
                _LOGGER.warning("Failed to write flow temperature for %s", zone_id)
                
    async def activate_boost_mode(self, duration_minutes: int = 120, reason: str = "manual"):
        """Activate boost mode using secondary curve."""
        if not self.secondary_curve:
            _LOGGER.warning("Cannot activate boost mode: no secondary curve configured")
            return False
            
        self.boost_active = True
        self.boost_end_time = datetime.now() + timedelta(minutes=duration_minutes)
        self.active_curve = "secondary"
        
        # Trigger immediate update
        await self._async_update_weather_compensation()
        
        # Fire event
        self.hass.bus.async_fire("grant_aerona3_weather_compensation_boost_activated", {
            "reason": reason,
            "duration_minutes": duration_minutes,
            "curve_name": self.secondary_curve.name
        })
        
        _LOGGER.info("Weather compensation boost activated for %d minutes. Reason: %s", 
                    duration_minutes, reason)
        
        return True
        
    async def deactivate_boost_mode(self, reason: str = "manual"):
        """Deactivate boost mode and return to primary curve."""
        if not self.boost_active:
            return
            
        self.boost_active = False
        self.boost_end_time = None
        self.active_curve = "primary"
        
        # Trigger immediate update
        await self._async_update_weather_compensation()
        
        # Fire event
        self.hass.bus.async_fire("grant_aerona3_weather_compensation_boost_deactivated", {
            "reason": reason,
            "curve_name": self.primary_curve.name
        })
        
        _LOGGER.info("Weather compensation boost deactivated. Reason: %s", reason)
        
    def get_current_status(self) -> Dict[str, Any]:
        """Get current weather compensation status."""
        return {
            "mode": self.config.mode.value,
            "active_curve": self.active_curve,
            "curve_name": (self.secondary_curve.name if self.boost_active and self.secondary_curve 
                          else self.primary_curve.name),
            "boost_active": self.boost_active,
            "boost_remaining_minutes": self._get_boost_remaining_minutes(),
            "last_outdoor_temp": self.last_outdoor_temp,
            "last_flow_temp": self.last_flow_temp,
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "calculation_count": self.calculation_count,
            "primary_curve_config": {
                "name": self.primary_curve.name,
                "min_outdoor": self.primary_curve.min_outdoor_temp,
                "max_outdoor": self.primary_curve.max_outdoor_temp,
                "min_flow": self.primary_curve.min_flow_temp,
                "max_flow": self.primary_curve.max_flow_temp,
            }
        }
        
    def _get_boost_remaining_minutes(self) -> Optional[int]:
        """Get remaining boost time in minutes."""
        if not self.boost_active or not self.boost_end_time:
            return None
            
        remaining = (self.boost_end_time - datetime.now()).total_seconds()
        return max(0, int(remaining / 60))
        
    def get_curve_visualization_data(self, curve_name: str = "primary") -> Dict[str, Any]:
        """Get data for curve visualization."""
        curve = self.primary_curve if curve_name == "primary" else self.secondary_curve
        
        if not curve:
            return {}
            
        points = curve.get_curve_points(20)  # 20 points for smooth curve
        
        return {
            "curve_name": curve.name,
            "curve_type": curve.curve_type.value,
            "points": points,
            "current_outdoor": self.last_outdoor_temp,
            "current_flow": self.last_flow_temp,
            "config": {
                "min_outdoor": curve.min_outdoor_temp,
                "max_outdoor": curve.max_outdoor_temp,
                "min_flow": curve.min_flow_temp,
                "max_flow": curve.max_flow_temp,
            }
        }


class WeatherCompensationController:
    """Main controller for weather compensation system."""
    
    def __init__(self, hass: HomeAssistant, coordinator, config: Dict[str, Any]):
        """Initialize weather compensation controller."""
        self.hass = hass
        self.coordinator = coordinator
        self.config = config
        self.weather_compensation: Optional[DualCurveWeatherCompensation] = None
        
    async def async_setup(self) -> bool:
        """Setup weather compensation system."""
        # Check if weather compensation is enabled
        if not self.config.get("weather_compensation", False):
            _LOGGER.info("Weather compensation disabled in configuration")
            return True
            
        # Create weather compensation configuration
        wc_config = self._create_weather_compensation_config()
        
        # Initialize weather compensation system
        self.weather_compensation = DualCurveWeatherCompensation(
            self.hass, self.coordinator, wc_config
        )
        
        # Setup the system
        success = await self.weather_compensation.async_setup()
        
        if success:
            _LOGGER.info("Weather compensation controller initialized successfully")
        else:
            _LOGGER.error("Failed to initialize weather compensation controller")
            
        return success
        
    def _create_weather_compensation_config(self) -> WeatherCompensationConfig:
        """Create weather compensation configuration from integration config."""
        
        # Primary curve configuration
        primary_curve = HeatingCurveConfig(
            name="Standard Efficiency",
            min_outdoor_temp=self.config.get("wc_min_outdoor_temp", -5.0),
            max_outdoor_temp=self.config.get("wc_max_outdoor_temp", 18.0),
            min_flow_temp=self.config.get("wc_min_flow_temp", 25.0),
            max_flow_temp=self.config.get("wc_max_flow_temp", 45.0),
            curve_type=CurveType.LINEAR
        )
        
        # Secondary curve (boost mode) if dual curve is enabled
        secondary_curve = None
        if self.config.get("dual_weather_compensation", False):
            secondary_curve = HeatingCurveConfig(
                name="Boost/Adverse Weather",
                min_outdoor_temp=self.config.get("boost_min_outdoor_temp", -10.0),
                max_outdoor_temp=self.config.get("boost_max_outdoor_temp", 15.0),
                min_flow_temp=self.config.get("boost_min_flow_temp", 35.0),
                max_flow_temp=self.config.get("boost_max_flow_temp", 55.0),
                curve_type=CurveType.LINEAR
            )
        
        # Zone settings
        zone_settings = {}
        zones_config = self.config.get("zones", {})
        
        for zone_id, zone_config in zones_config.items():
            if zone_config.get("enabled", False):
                zone_settings[zone_id] = {
                    "enabled": True,
                    "compensation_factor": zone_config.get("compensation_factor", 1.0),
                    "temperature_offset": zone_config.get("temperature_offset", 0.0),
                    "min_flow_temp": zone_config.get("min_flow_temp", 20.0),
                    "max_flow_temp": zone_config.get("max_flow_temp", 60.0),
                }
        
        return WeatherCompensationConfig(
            mode=WeatherCompensationMode.WEATHER_COMPENSATION,
            primary_curve=primary_curve,
            secondary_curve=secondary_curve,
            zone_settings=zone_settings,
            update_interval=self.config.get("wc_update_interval", 60)
        )
        
    async def activate_boost_mode(self, duration_minutes: int = 120, reason: str = "manual") -> bool:
        """Activate boost mode."""
        if self.weather_compensation:
            return await self.weather_compensation.activate_boost_mode(duration_minutes, reason)
        return False
        
    async def deactivate_boost_mode(self, reason: str = "manual"):
        """Deactivate boost mode."""
        if self.weather_compensation:
            await self.weather_compensation.deactivate_boost_mode(reason)
            
    def get_status(self) -> Dict[str, Any]:
        """Get current weather compensation status."""
        if self.weather_compensation:
            return self.weather_compensation.get_current_status()
        return {"enabled": False}
        
    def get_curve_data(self, curve_name: str = "primary") -> Dict[str, Any]:
        """Get curve visualization data."""
        if self.weather_compensation:
            return self.weather_compensation.get_curve_visualization_data(curve_name)
        return {}
        
    def is_enabled(self) -> bool:
        """Check if weather compensation is enabled."""
        return self.weather_compensation is not None