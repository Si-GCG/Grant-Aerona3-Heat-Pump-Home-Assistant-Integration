"""Register management for Grant Aerona3 Heat Pump integration."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set
from enum import Enum

_LOGGER = logging.getLogger(__name__)


class RegisterType(Enum):
    """Register types for Grant Aerona3."""
    INPUT = "input"
    HOLDING = "holding"
    COIL = "coil"


class RegisterCategory(Enum):
    """Register categories for organization."""
    BASIC = "basic"          # Always enabled
    ZONES = "zones"          # Zone-specific registers
    DHW = "dhw"             # Domestic hot water
    EXTERNAL = "external"    # External components
    ADVANCED = "advanced"    # Advanced features
    DIAGNOSTIC = "diagnostic"  # Error codes and diagnostics


class RegisterConfig:
    """Configuration for a single register."""
    
    def __init__(
        self,
        address: int,
        name: str,
        register_type: RegisterType,
        category: RegisterCategory = RegisterCategory.BASIC,
        unit: Optional[str] = None,
        scale: float = 1.0,
        device_class: Optional[str] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        description: Optional[str] = None,
        requires_feature: Optional[str] = None,
        enum_mapping: Optional[Dict[int, str]] = None,
    ):
        """Initialize register configuration."""
        self.address = address
        self.name = name
        self.register_type = register_type
        self.category = category
        self.unit = unit
        self.scale = scale
        self.device_class = device_class
        self.min_value = min_value
        self.max_value = max_value
        self.description = description
        self.requires_feature = requires_feature
        self.enum_mapping = enum_mapping or {}


class GrantAerona3RegisterManager:
    """Manages register mappings and feature-based enablement."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize register manager with configuration."""
        self.config = config
        self._register_definitions = self._load_register_definitions()
        self._enabled_registers = self._determine_enabled_registers()
        
    def _load_register_definitions(self) -> Dict[str, RegisterConfig]:
        """Load all register definitions."""
        registers = {}
        
        # Load input registers
        registers.update(self._load_input_registers())
        
        # Load holding registers
        registers.update(self._load_holding_registers())
        
        # Load coil registers
        registers.update(self._load_coil_registers())
        
        return registers
        
    def _load_input_registers(self) -> Dict[str, RegisterConfig]:
        """Load input register definitions."""
        return {
            # Basic monitoring registers (always enabled)
            "return_temp": RegisterConfig(
                0, "Return Water Temperature", RegisterType.INPUT,
                RegisterCategory.BASIC, "°C", 1.0, "temperature"
            ),
            "compressor_frequency": RegisterConfig(
                1, "Compressor Frequency", RegisterType.INPUT,
                RegisterCategory.BASIC, "Hz", 1.0, "frequency"
            ),
            "discharge_temp": RegisterConfig(
                2, "Discharge Temperature", RegisterType.INPUT,
                RegisterCategory.BASIC, "°C", 1.0, "temperature"
            ),
            "power_consumption": RegisterConfig(
                3, "Current Power Consumption", RegisterType.INPUT,
                RegisterCategory.BASIC, "W", 100.0, "power"
            ),
            "fan_speed": RegisterConfig(
                4, "Fan Speed", RegisterType.INPUT,
                RegisterCategory.BASIC, "rpm", 10.0
            ),
            "defrost_temp": RegisterConfig(
                5, "Defrost Temperature", RegisterType.INPUT,
                RegisterCategory.BASIC, "°C", 1.0, "temperature"
            ),
            "outdoor_temp": RegisterConfig(
                6, "Outdoor Air Temperature", RegisterType.INPUT,
                RegisterCategory.BASIC, "°C", 1.0, "temperature"
            ),
            "pump_speed": RegisterConfig(
                7, "Water Pump Speed", RegisterType.INPUT,
                RegisterCategory.BASIC, "rpm", 100.0
            ),
            "suction_temp": RegisterConfig(
                8, "Suction Temperature", RegisterType.INPUT,
                RegisterCategory.BASIC, "°C", 1.0, "temperature"
            ),
            "flow_temp": RegisterConfig(
                9, "Outgoing Water Temperature", RegisterType.INPUT,
                RegisterCategory.BASIC, "°C", 1.0, "temperature"
            ),
            "operating_mode": RegisterConfig(
                10, "Operating Mode", RegisterType.INPUT,
                RegisterCategory.BASIC, enum_mapping={
                    0: "Off", 1: "Heating", 2: "Cooling", 3: "DHW"
                }
            ),
            "zone1_setpoint": RegisterConfig(
                11, "Zone 1 Set Temperature", RegisterType.INPUT,
                RegisterCategory.ZONES, "°C", 0.1, "temperature"
            ),
            "zone2_setpoint": RegisterConfig(
                12, "Zone 2 Set Temperature", RegisterType.INPUT,
                RegisterCategory.ZONES, "°C", 0.1, "temperature",
                requires_feature="zones.zone_2.enabled"
            ),
            "dhw_mode": RegisterConfig(
                13, "DHW Operating Mode", RegisterType.INPUT,
                RegisterCategory.DHW, enum_mapping={
                    0: "Disabled", 1: "Comfort", 2: "Economy", 3: "Force"
                },
                requires_feature="dhw_cylinder"
            ),
            "legionella_day": RegisterConfig(
                14, "Day for Legionella Cycle", RegisterType.INPUT,
                RegisterCategory.DHW, enum_mapping={
                    0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
                    4: "Friday", 5: "Saturday", 6: "Sunday"
                },
                requires_feature="dhw_cylinder"
            ),
            "legionella_time": RegisterConfig(
                15, "Legionella Cycle Start Time", RegisterType.INPUT,
                RegisterCategory.DHW,
                requires_feature="dhw_cylinder"
            ),
            "dhw_temp": RegisterConfig(
                16, "DHW Tank Temperature", RegisterType.INPUT,
                RegisterCategory.DHW, "°C", 0.1, "temperature",
                requires_feature="dhw_cylinder"
            ),
            "external_outdoor_temp": RegisterConfig(
                17, "External Outdoor Temperature", RegisterType.INPUT,
                RegisterCategory.EXTERNAL, "°C", 0.1, "temperature",
                requires_feature="external_sensors.outdoor_temp"
            ),
            "buffer_temp": RegisterConfig(
                18, "Buffer Tank Temperature", RegisterType.INPUT,
                RegisterCategory.BASIC, "°C", 0.1, "temperature"
            ),
            
            # Extended registers (19-33) - previously missing
            "mix_water_temp": RegisterConfig(
                19, "Mix Water Temperature", RegisterType.INPUT,
                RegisterCategory.ZONES, "°C", 0.1, "temperature"
            ),
            "humidity": RegisterConfig(
                20, "Humidity Sensor", RegisterType.INPUT,
                RegisterCategory.EXTERNAL, "%", 1.0, "humidity",
                requires_feature="external_sensors.humidity"
            ),
            "error_code_1": RegisterConfig(
                21, "Error Code 1", RegisterType.INPUT,
                RegisterCategory.DIAGNOSTIC
            ),
            "error_code_2": RegisterConfig(
                22, "Error Code 2", RegisterType.INPUT,
                RegisterCategory.DIAGNOSTIC
            ),
            "system_runtime": RegisterConfig(
                23, "System Runtime Hours", RegisterType.INPUT,
                RegisterCategory.DIAGNOSTIC, "h", 1.0
            ),
            "compressor_runtime": RegisterConfig(
                24, "Compressor Runtime Hours", RegisterType.INPUT,
                RegisterCategory.DIAGNOSTIC, "h", 1.0
            ),
            "defrost_count": RegisterConfig(
                25, "Defrost Cycle Count", RegisterType.INPUT,
                RegisterCategory.DIAGNOSTIC
            ),
            "backup_heater_runtime": RegisterConfig(
                26, "Backup Heater Runtime", RegisterType.INPUT,
                RegisterCategory.EXTERNAL, "h", 1.0,
                requires_feature="backup_heater"
            ),
            "flow_rate": RegisterConfig(
                27, "Flow Rate", RegisterType.INPUT,
                RegisterCategory.ADVANCED, "L/min", 0.1,
                requires_feature="flow_metering"
            ),
            "dhw_flow_rate": RegisterConfig(
                28, "DHW Flow Rate", RegisterType.INPUT,
                RegisterCategory.DHW, "L/min", 0.1,
                requires_feature="dhw_cylinder"
            ),
            "plate_hx_temp": RegisterConfig(
                32, "Plate Heat Exchanger Temperature", RegisterType.INPUT,
                RegisterCategory.ADVANCED, "°C", 0.1, "temperature"
            ),
        }
        
    def _load_holding_registers(self) -> Dict[str, RegisterConfig]:
        """Load holding register definitions."""
        return {
            # Zone 1 temperature controls
            "zone1_fixed_flow": RegisterConfig(
                2, "Zone 1 Fixed Flow Temperature", RegisterType.HOLDING,
                RegisterCategory.ZONES, "°C", 0.1, "temperature", 23, 60
            ),
            "zone1_max_flow": RegisterConfig(
                3, "Zone 1 Max Flow Temperature", RegisterType.HOLDING,
                RegisterCategory.ZONES, "°C", 0.1, "temperature", 23, 60
            ),
            "zone1_min_flow": RegisterConfig(
                4, "Zone 1 Min Flow Temperature", RegisterType.HOLDING,
                RegisterCategory.ZONES, "°C", 0.1, "temperature", 23, 60
            ),
            
            # Zone 2 temperature controls
            "zone2_fixed_flow": RegisterConfig(
                7, "Zone 2 Fixed Flow Temperature", RegisterType.HOLDING,
                RegisterCategory.ZONES, "°C", 0.1, "temperature", 23, 60,
                requires_feature="zones.zone_2.enabled"
            ),
            "zone2_max_flow": RegisterConfig(
                8, "Zone 2 Max Flow Temperature", RegisterType.HOLDING,
                RegisterCategory.ZONES, "°C", 0.1, "temperature", 23, 60,
                requires_feature="zones.zone_2.enabled"
            ),
            "zone2_min_flow": RegisterConfig(
                9, "Zone 2 Min Flow Temperature", RegisterType.HOLDING,
                RegisterCategory.ZONES, "°C", 0.1, "temperature", 23, 60,
                requires_feature="zones.zone_2.enabled"
            ),
            
            # DHW controls
            "dhw_setpoint": RegisterConfig(
                26, "DHW Target Temperature", RegisterType.HOLDING,
                RegisterCategory.DHW, "°C", 0.1, "temperature", 40, 65,
                requires_feature="dhw_cylinder"
            ),
            "dhw_hysteresis": RegisterConfig(
                27, "DHW Hysteresis", RegisterType.HOLDING,
                RegisterCategory.DHW, "°C", 0.1, "temperature", 2, 10,
                requires_feature="dhw_cylinder"
            ),
            
            # Weather compensation outdoor temperature ranges
            "wc_min_outdoor": RegisterConfig(
                40, "Weather Comp Min Outdoor Temp", RegisterType.HOLDING,
                RegisterCategory.ADVANCED, "°C", 0.1, "temperature", -20, 5
            ),
            "wc_max_outdoor": RegisterConfig(
                41, "Weather Comp Max Outdoor Temp", RegisterType.HOLDING,
                RegisterCategory.ADVANCED, "°C", 0.1, "temperature", 15, 25
            ),
            
            # Backup heater controls
            "backup_heater_setpoint": RegisterConfig(
                50, "Backup Heater Activation Temperature", RegisterType.HOLDING,
                RegisterCategory.EXTERNAL, "°C", 0.1, "temperature", -15, 5,
                requires_feature="backup_heater"
            ),
        }
        
    def _load_coil_registers(self) -> Dict[str, RegisterConfig]:
        """Load coil register definitions."""
        return {
            # Weather compensation controls
            "zone1_weather_comp": RegisterConfig(
                2, "Zone 1 Weather Compensation", RegisterType.COIL,
                RegisterCategory.ZONES,
                description="Enable weather compensation for Zone 1"
            ),
            "zone2_weather_comp": RegisterConfig(
                3, "Zone 2 Weather Compensation", RegisterType.COIL,
                RegisterCategory.ZONES,
                description="Enable weather compensation for Zone 2",
                requires_feature="zones.zone_2.enabled"
            ),
            
            # DHW controls
            "dhw_enable": RegisterConfig(
                6, "DHW Enable", RegisterType.COIL,
                RegisterCategory.DHW,
                description="Enable DHW heating",
                requires_feature="dhw_cylinder"
            ),
            "dhw_boost": RegisterConfig(
                20, "DHW Boost Mode", RegisterType.COIL,
                RegisterCategory.DHW,
                description="Activate DHW boost mode",
                requires_feature="dhw_cylinder"
            ),
            "dhw_remote_relay": RegisterConfig(
                21, "DHW Remote Relay", RegisterType.COIL,
                RegisterCategory.DHW,
                description="DHW remote relay control",
                requires_feature="dhw_cylinder"
            ),
            
            # System controls
            "anti_legionella": RegisterConfig(
                6, "Anti-Legionella Function", RegisterType.COIL,
                RegisterCategory.DHW,
                description="Enable anti-legionella function",
                requires_feature="dhw_cylinder"
            ),
            "control_mode": RegisterConfig(
                7, "Control Mode", RegisterType.COIL,
                RegisterCategory.BASIC,
                description="HP control mode (0=Room setpoint, 1=Water setpoint)"
            ),
            
            # Frost protection
            "frost_protect_room": RegisterConfig(
                8, "Frost Protection Room", RegisterType.COIL,
                RegisterCategory.BASIC,
                description="Frost protection based on room temperature"
            ),
            "frost_protect_outdoor": RegisterConfig(
                9, "Frost Protection Outdoor", RegisterType.COIL,
                RegisterCategory.BASIC,
                description="Frost protection based on outdoor temperature"
            ),
            "frost_protect_water": RegisterConfig(
                10, "Frost Protection Water", RegisterType.COIL,
                RegisterCategory.BASIC,
                description="Frost protection based on water temperature"
            ),
            
            # External component controls
            "backup_heater_enable": RegisterConfig(
                15, "Backup Heater Enable", RegisterType.COIL,
                RegisterCategory.EXTERNAL,
                description="Enable backup heater operation",
                requires_feature="backup_heater"
            ),
            "circulation_pump": RegisterConfig(
                16, "Circulation Pump", RegisterType.COIL,
                RegisterCategory.EXTERNAL,
                description="Enable circulation pump",
                requires_feature="circulation_pump"
            ),
        }
        
    def _determine_enabled_registers(self) -> Set[str]:
        """Determine which registers should be enabled based on configuration."""
        enabled = set()
        
        for register_id, register_config in self._register_definitions.items():
            # Always enable basic category registers
            if register_config.category == RegisterCategory.BASIC:
                enabled.add(register_id)
                continue
                
            # Check if feature requirement is met
            if register_config.requires_feature:
                if self._is_feature_enabled(register_config.requires_feature):
                    enabled.add(register_id)
            else:
                # No feature requirement, enable by category
                if self._is_category_enabled(register_config.category):
                    enabled.add(register_id)
                    
        return enabled
        
    def _is_feature_enabled(self, feature_path: str) -> bool:
        """Check if a specific feature is enabled in configuration."""
        parts = feature_path.split(".")
        current = self.config
        
        try:
            for part in parts:
                current = current[part]
            return bool(current)
        except (KeyError, TypeError):
            return False
            
    def _is_category_enabled(self, category: RegisterCategory) -> bool:
        """Check if a register category should be enabled."""
        category_mapping = {
            RegisterCategory.ZONES: True,  # Always enable zone registers
            RegisterCategory.DHW: self.config.get("dhw_cylinder", False),
            RegisterCategory.EXTERNAL: True,  # Enable if any external components
            RegisterCategory.ADVANCED: self.config.get("advanced_features", False),
            RegisterCategory.DIAGNOSTIC: self.config.get("diagnostic_monitoring", False),
        }
        
        return category_mapping.get(category, False)
        
    def get_enabled_registers(self, register_type: Optional[RegisterType] = None) -> Dict[str, RegisterConfig]:
        """Get enabled registers, optionally filtered by type."""
        enabled_registers = {}
        
        for register_id in self._enabled_registers:
            register_config = self._register_definitions[register_id]
            
            if register_type is None or register_config.register_type == register_type:
                enabled_registers[register_id] = register_config
                
        return enabled_registers
        
    def get_register_by_address(self, address: int, register_type: RegisterType) -> Optional[RegisterConfig]:
        """Get register configuration by address and type."""
        for register_config in self._register_definitions.values():
            if (register_config.address == address and 
                register_config.register_type == register_type):
                return register_config
        return None
        
    def is_register_enabled(self, register_id: str) -> bool:
        """Check if a specific register is enabled."""
        return register_id in self._enabled_registers
        
    def get_register_addresses_by_type(self, register_type: RegisterType) -> List[int]:
        """Get list of enabled register addresses for a specific type."""
        addresses = []
        enabled_registers = self.get_enabled_registers(register_type)
        
        for register_config in enabled_registers.values():
            addresses.append(register_config.address)
            
        return sorted(addresses)
    
    def get_enabled_registers_by_category(self, category: RegisterCategory) -> Dict[str, RegisterConfig]:
        """Get enabled registers filtered by category."""
        category_registers = {}
        
        for register_id in self._enabled_registers:
            register_config = self._register_definitions.get(register_id)
            if register_config and register_config.category == category:
                category_registers[register_id] = register_config
                
        return category_registers
    
    def validate_register_address(self, address: int, register_type: RegisterType) -> bool:
        """Validate register address against allowed ranges for security."""
        # Define safe address ranges for Grant Aerona3 heat pump
        valid_ranges = {
            RegisterType.INPUT: (0, 100),      # Input registers: 0-100
            RegisterType.HOLDING: (0, 100),    # Holding registers: 0-100  
            RegisterType.COIL: (0, 50)         # Coil registers: 0-50
        }
        
        min_addr, max_addr = valid_ranges.get(register_type, (0, 0))
        if not (min_addr <= address <= max_addr):
            _LOGGER.error(
                "Invalid register address %d for type %s. Valid range: %d-%d",
                address, register_type.value, min_addr, max_addr
            )
            return False
            
        return True
    
    def validate_register_write_permission(self, register_id: str) -> bool:
        """Validate if register can be safely written to."""
        register_config = self._register_definitions.get(register_id)
        if not register_config:
            _LOGGER.error("Unknown register ID: %s", register_id)
            return False
            
        # Only allow writes to holding registers and coils
        if register_config.register_type == RegisterType.INPUT:
            _LOGGER.error("Cannot write to input register: %s", register_id)
            return False
            
        # Additional safety checks for critical registers
        critical_registers = {
            'zone1_fixed_flow', 'zone2_fixed_flow', 'dhw_setpoint', 
            'backup_heater_enable', 'operating_mode'
        }
        
        if register_id in critical_registers:
            _LOGGER.warning("Writing to critical register: %s", register_id)
            # In production, add additional permission checks here
            
        return True