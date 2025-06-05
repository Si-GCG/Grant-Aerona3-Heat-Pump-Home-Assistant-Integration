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
    """Load ALL 22 input register definitions (0-20, 32)."""
    return {
        # Register 0
        "return_temp": RegisterConfig(
            0, "Return Water Temperature", RegisterType.INPUT,
            RegisterCategory.BASIC, "°C", 0.1, "temperature",  # Fixed: was 1.0, now 0.1
            description="Return water temperature"
        ),
        
        # Register 1
        "compressor_frequency": RegisterConfig(
            1, "Compressor Operating Frequency", RegisterType.INPUT,
            RegisterCategory.BASIC, "Hz", 1.0, "frequency",
            description="Compressor operating frequency"
        ),
        
        # Register 2
        "discharge_temp": RegisterConfig(
            2, "Discharge Temperature", RegisterType.INPUT,
            RegisterCategory.BASIC, "°C", 0.1, "temperature",  # Fixed: was 1.0, now 0.1
            description="Discharge temperature"
        ),
        
        # Register 3
        "power_consumption": RegisterConfig(
            3, "Current Consumption Value", RegisterType.INPUT,
            RegisterCategory.BASIC, "W", 100.0, "power",  # Correct: divide by 100
            description="Current consumption value"
        ),
        
        # Register 4
        "fan_speed": RegisterConfig(
            4, "Fan Control Number Of Rotation", RegisterType.INPUT,
            RegisterCategory.BASIC, "rpm", 10.0, None,  # Correct: divide by 10
            description="Fan control number of rotation"
        ),
        
        # Register 5
        "defrost_temp": RegisterConfig(
            5, "Defrost Temperature", RegisterType.INPUT,
            RegisterCategory.BASIC, "°C", 0.1, "temperature",  # Fixed: was 1.0, now 0.1
            description="Defrost temperature"
        ),
        
        # Register 6
        "outdoor_temp": RegisterConfig(
            6, "Outdoor Air Temperature", RegisterType.INPUT,
            RegisterCategory.BASIC, "°C", 0.1, "temperature",  # Fixed: was 1.0, now 0.1
            description="Outdoor air temperature"
        ),
        
        # Register 7
        "pump_speed": RegisterConfig(
            7, "Water Pump Control Number Of Rotation", RegisterType.INPUT,
            RegisterCategory.BASIC, "rpm", 100.0, None,  # Correct: divide by 100
            description="Water pump control number of rotation"
        ),
        
        # Register 8
        "suction_temp": RegisterConfig(
            8, "Suction Temperature", RegisterType.INPUT,
            RegisterCategory.BASIC, "°C", 0.1, "temperature",  # Fixed: was 1.0, now 0.1
            description="Suction temperature"
        ),
        
        # Register 9
        "flow_temp": RegisterConfig(
            9, "Outgoing Water Temperature", RegisterType.INPUT,
            RegisterCategory.BASIC, "°C", 0.1, "temperature",  # Fixed: was 1.0, now 0.1
            description="Outgoing water temperature"
        ),
        
        # Register 10
        "operating_mode": RegisterConfig(
            10, "Selected Operating Mode", RegisterType.INPUT,
            RegisterCategory.BASIC, None, 1.0, None,
            description="Selected operating mode (0=Heating/Cooling OFF, 1=Heating, 2=Cooling)",
            enum_mapping={0: "Off", 1: "Heating", 2: "Cooling", 3: "DHW"}
        ),
        
        # Register 11
        "zone1_setpoint": RegisterConfig(
            11, "Room Air Set Temperature of Zone 1", RegisterType.INPUT,
            RegisterCategory.ZONES, "°C", 0.1, "temperature",  # Fixed: was 0.5, now 0.1
            description="Room air set temperature of Zone1(Master)"
        ),
        
        # Register 12
        "zone2_setpoint": RegisterConfig(
            12, "Room Air Set Temperature Of Zone 2", RegisterType.INPUT,
            RegisterCategory.ZONES, "°C", 0.1, "temperature",  # Fixed: was 0.5, now 0.1
            description="Room air set temperature of Zone2(Slave)",
            requires_feature="zones.zone_2.enabled"
        ),
        
        # Register 13
        "dhw_mode": RegisterConfig(
            13, "Selected DHW Operating Mode", RegisterType.INPUT,
            RegisterCategory.DHW, None, 1.0, None,
            description="Selected DHW operating mode (0=disable, 1=Comfort, 2=Economy, 3=Force)",
            requires_feature="dhw_cylinder",
            enum_mapping={0: "Disabled", 1: "Comfort", 2: "Economy", 3: "Force"}
        ),
        
        # Register 14
        "day_of_week": RegisterConfig(
            14, "Day", RegisterType.INPUT,
            RegisterCategory.BASIC, None, 1.0, None,
            description="Day (0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday)",
            enum_mapping={
                0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
                4: "Friday", 5: "Saturday", 6: "Sunday"
            }
        ),
        
        # Register 15
        "legionella_time": RegisterConfig(
            15, "Legionella Cycle Set Time", RegisterType.INPUT,
            RegisterCategory.DHW, "hours", 1.0, "duration",
            description="Legionella Cycle Set Time",
            requires_feature="dhw_cylinder"
        ),
        
        # Register 16
        "dhw_temp": RegisterConfig(
            16, "DHW Tank Temperature", RegisterType.INPUT,
            RegisterCategory.DHW, "°C", 0.1, "temperature",  # Fixed: was 0.5, now 0.1
            description="DHW tank temperature (Terminal 7-8)",
            requires_feature="dhw_cylinder"
        ),
        
        # Register 17
        "external_outdoor_temp": RegisterConfig(
            17, "Outdoor Air Temperature - Remote Sensor", RegisterType.INPUT,
            RegisterCategory.EXTERNAL, "°C", 0.1, "temperature",  # Fixed: was 0.5, now 0.1
            description="Outdoor air temperature (Terminal 9-10)",
            requires_feature="external_sensors.outdoor_temp"
        ),
        
        # Register 18
        "buffer_temp": RegisterConfig(
            18, "Buffer Tank Temperature", RegisterType.INPUT,
            RegisterCategory.BASIC, "°C", 0.1, "temperature",  # Fixed: was 0.5, now 0.1
            description="Buffer tank temperature (Terminal 11-12)"
        ),
        
        # Register 19
        "mix_water_temp": RegisterConfig(
            19, "Mix Water Temperature", RegisterType.INPUT,
            RegisterCategory.ZONES, "°C", 0.1, "temperature",  # Fixed: was 0.5, now 0.1
            description="Mix water temperature (Terminal 13-14)"
        ),
        
        # Register 20
        "humidity": RegisterConfig(
            20, "Humidity Sensor", RegisterType.INPUT,
            RegisterCategory.EXTERNAL, "%", 1.0, "humidity",
            description="Humidity sensor (Terminal 17-18)",
            requires_feature="external_sensors.humidity"
        ),
        
        # Register 32 (gap from 21-31 - these registers don't exist)
        "plate_hx_temp": RegisterConfig(
            32, "Plate Heat Exchanger Temperature", RegisterType.INPUT,
            RegisterCategory.ADVANCED, "°C", 0.1, "temperature",  # Fixed: was 1.0, now 0.1
            description="Plate heat exchanger temperature"
        ),
    }
        
 def _load_holding_registers(self) -> Dict[str, RegisterConfig]:
    """Load ALL 97 holding register definitions (2-96, 99-100)."""
    return {
        # Zone 1 Heating Controls (2-6)
        "zone1_fixed_flow": RegisterConfig(
            2, "Fixed Flow Temp Zone 1", RegisterType.HOLDING,
            RegisterCategory.ZONES, "°C", 0.1, "temperature", 23.0, 60.0,
            description="Heating Zone1, Fixed Outgoing water set point in Heating"
        ),
        "zone1_max_flow": RegisterConfig(
            3, "Max Flow Temp Zone1", RegisterType.HOLDING,
            RegisterCategory.ZONES, "°C", 0.1, "temperature", 23.0, 60.0,
            description="Max. Outgoing water temperature in Heating mode (Tm1) Zone1"
        ),
        "zone1_min_flow": RegisterConfig(
            4, "Min Flow Temp Zone1", RegisterType.HOLDING,
            RegisterCategory.ZONES, "°C", 0.1, "temperature", 23.0, 60.0,
            description="Min. Outgoing water temperature in Heating mode (Tm2) Zone1"
        ),
        "zone1_min_outdoor": RegisterConfig(
            5, "Min. Outdoor Air Temperature Zone1", RegisterType.HOLDING,
            RegisterCategory.ZONES, "°C", 0.1, "temperature", -20.0, 5.0,
            description="Min. Outdoor air temperature corresponding to max. Outgoing water temperature (Te1) Zone1"
        ),
        "zone1_max_outdoor": RegisterConfig(
            6, "Max. Outdoor Air Temperature Zone1", RegisterType.HOLDING,
            RegisterCategory.ZONES, "°C", 0.1, "temperature", 15.0, 25.0,
            description="Max. Outdoor air temperature corresponding to max. Outgoing water temperature (Te2) Zone1"
        ),
        
        # Zone 2 Heating Controls (7-11)
        "zone2_fixed_flow": RegisterConfig(
            7, "Fixed Flow Temp Zone 2", RegisterType.HOLDING,
            RegisterCategory.ZONES, "°C", 0.1, "temperature", 23.0, 60.0,
            description="Heating Zone2, Fixed Outgoing water set point in Heating",
            requires_feature="zones.zone_2.enabled"
        ),
        "zone2_max_flow": RegisterConfig(
            8, "Max Flow Temp Zone2", RegisterType.HOLDING,
            RegisterCategory.ZONES, "°C", 0.1, "temperature", 23.0, 60.0,
            description="Max. Outgoing water temperature in Heating mode (Tm1) Zone2",
            requires_feature="zones.zone_2.enabled"
        ),
        "zone2_min_flow": RegisterConfig(
            9, "Min Flow Temp Zone2", RegisterType.HOLDING,
            RegisterCategory.ZONES, "°C", 0.1, "temperature", 23.0, 60.0,
            description="Min. Outgoing water temperature in Heating mode (Tm2) Zone2",
            requires_feature="zones.zone_2.enabled"
        ),
        "zone2_min_outdoor": RegisterConfig(
            10, "Min. Outdoor Air Temperature Zone2", RegisterType.HOLDING,
            RegisterCategory.ZONES, "°C", 0.1, "temperature", -20.0, 5.0,
            description="Min. Outdoor air temperature corresponding to max. Outgoing water temperature (Te1) Zone2",
            requires_feature="zones.zone_2.enabled"
        ),
        "zone2_max_outdoor": RegisterConfig(
            11, "Max. Outdoor Air Temperature Zone2", RegisterType.HOLDING,
            RegisterCategory.ZONES, "°C", 0.1, "temperature", 15.0, 25.0,
            description="Max. Outdoor air temperature corresponding to max. Outgoing water temperature (Te2) Zone2",
            requires_feature="zones.zone_2.enabled"
        ),
        
        # Zone 1 Cooling Controls (12-16)
        "zone1_cooling_fixed": RegisterConfig(
            12, "Cooling Fixed Flow Temp Zone 1", RegisterType.HOLDING,
            RegisterCategory.ZONES, "°C", 0.1, "temperature", 5.0, 18.0,
            description="Cooling Zone1, Fixed Outgoing water set point in Cooling"
        ),
        "zone1_cooling_max": RegisterConfig(
            13, "Max. Flow Temperature In Cooling Mode", RegisterType.HOLDING,
            RegisterCategory.ZONES, "°C", 0.1, "temperature", 5.0, 18.0,
            description="Max. Outgoing water temperature in Cooling mode (Tm1) Zone1"
        ),
        "zone1_cooling_min": RegisterConfig(
            14, "Min. Flow Water Temperature In Cooling Mode", RegisterType.HOLDING,
            RegisterCategory.ZONES, "°C", 0.1, "temperature", 5.0, 18.0,
            description="Min. Outgoing water temperature in Cooling mode (Tm2) Zone1"
        ),
        "zone1_cooling_min_outdoor": RegisterConfig(
            15, "Min. Outdoor Air Temperature Cooling Zone1", RegisterType.HOLDING,
            RegisterCategory.ZONES, "°C", 0.1, "temperature", 15.0, 35.0,
            description="Min. Outdoor air temperature corresponding to max. Outgoing water temperature Cooling (Te1) Zone1"
        ),
        "zone1_cooling_max_outdoor": RegisterConfig(
            16, "Max. Outdoor Air Temperature Corresponding To M... 3", RegisterType.HOLDING,
            RegisterCategory.ZONES, "°C", 0.1, "temperature", 25.0, 45.0,
            description="Max. Outdoor air temperature corresponding to max. Outgoing water temperature Cooling (Te2) Zone1"
        ),
        
        # Zone 2 Cooling Controls (17-21)
        "zone2_cooling_fixed": RegisterConfig(
            17, "Cooling Fixed Flow Temp Zone2", RegisterType.HOLDING,
            RegisterCategory.ZONES, "°C", 0.1, "temperature", 5.0, 18.0,
            description="Cooling Zone2, Fixed Outgoing water set point in Cooling",
            requires_feature="zones.zone_2.enabled"
        ),
        "zone2_cooling_max": RegisterConfig(
            18, "Max Flow Temperature In Cooling Mode 2", RegisterType.HOLDING,
            RegisterCategory.ZONES, "°C", 0.1, "temperature", 5.0, 18.0,
            description="Max. Outgoing water temperature in Cooling mode (Tm1) Zone2",
            requires_feature="zones.zone_2.enabled"
        ),
        "zone2_cooling_min": RegisterConfig(
            19, "Min Flow Temperature In Cooling Mode 2", RegisterType.HOLDING,
            RegisterCategory.ZONES, "°C", 0.1, "temperature", 5.0, 18.0,
            description="Min. Outgoing water temperature in Cooling mode (Tm2) Zone2",
            requires_feature="zones.zone_2.enabled"
        ),
        "zone2_cooling_min_outdoor": RegisterConfig(
            20, "Min Outdoor Air Temperature Cooling Zone2", RegisterType.HOLDING,
            RegisterCategory.ZONES, "°C", 0.1, "temperature", 15.0, 35.0,
            description="Min. Outdoor air temperature corresponding to max. Outgoing water temperature (Te1) Zone2",
            requires_feature="zones.zone_2.enabled"
        ),
        "zone2_cooling_max_outdoor": RegisterConfig(
            21, "Max. Outdoor Air Temperature Cooling Zone2", RegisterType.HOLDING,
            RegisterCategory.ZONES, "°C", 0.1, "temperature", 25.0, 45.0,
            description="Max. Outdoor air temperature corresponding to max. Outgoing water temperature (Te2) Zone2",
            requires_feature="zones.zone_2.enabled"
        ),
        
        # System Hysteresis Controls (22-25)
        "heating_dhw_hysteresis": RegisterConfig(
            22, "Hysteresis Of Water Set Point In Heating And DHW", RegisterType.HOLDING,
            RegisterCategory.BASIC, "°C", 0.1, "temperature", 1.0, 5.0,
            description="Hysteresis of water set point in Heating and DHW"
        ),
        "cooling_hysteresis": RegisterConfig(
            23, "Hysteresis Of Water Set Point In Cooling", RegisterType.HOLDING,
            RegisterCategory.BASIC, "°C", 0.1, "temperature", 1.0, 5.0,
            description="Hysteresis of water set point in Cooling"
        ),
        "low_tariff_heating_diff": RegisterConfig(
            24, "Low Tariff Deferential Water Set Point For Heating", RegisterType.HOLDING,
            RegisterCategory.ADVANCED, "°C", 0.1, "temperature", 0.0, 10.0,
            description="Low tariff deferential water set point for Heating"
        ),
        "low_tariff_cooling_diff": RegisterConfig(
            25, "Low Tariff Deferential Water Set Point For Cooling", RegisterType.HOLDING,
            RegisterCategory.ADVANCED, "°C", 0.1, "temperature", 0.0, 10.0,
            description="Low tariff deferential water set point for Cooling"
        ),
        
        # DHW Controls (26-36)
        "dhw_priority": RegisterConfig(
            26, "DHW Production Priority Setting", RegisterType.HOLDING,
            RegisterCategory.DHW, None, 1.0, None, 0.0, 2.0,
            description="DHW production priority setting (0=DHW is unavailable, 1=DHW is available and priority DHW over space Heating, 2=DHW is available and priority space Heating over DHW)",
            requires_feature="dhw_cylinder",
            enum_mapping={0: "Unavailable", 1: "DHW Priority", 2: "Heating Priority"}
        ),
        "dhw_config_type": RegisterConfig(
            27, "Type Of Configuration To Heat The DHW", RegisterType.HOLDING,
            RegisterCategory.DHW, None, 1.0, None, 0.0, 2.0,
            description="Type of configuration to heat the DHW (0=Heat pump + Heater, 1=Heat pump only, 2=Heater only)",
            requires_feature="dhw_cylinder",
            enum_mapping={0: "Heat pump + Heater", 1: "Heat pump only", 2: "Heater only"}
        ),
        "dhw_comfort_temp": RegisterConfig(
            28, "DHW Comfort Set Temperature", RegisterType.HOLDING,
            RegisterCategory.DHW, "°C", 0.1, "temperature", 40.0, 65.0,
            description="DHW Comfort set temperature",
            requires_feature="dhw_cylinder"
        ),
        "dhw_economy_temp": RegisterConfig(
            29, "DHW Economy Set Temperature", RegisterType.HOLDING,
            RegisterCategory.DHW, "°C", 0.1, "temperature", 40.0, 60.0,
            description="DHW Economy set temperature",
            requires_feature="dhw_cylinder"
        ),
        "dhw_hysteresis": RegisterConfig(
            30, "DHW Set Point Hysteresis", RegisterType.HOLDING,
            RegisterCategory.DHW, "°C", 0.1, "temperature", 2.0, 10.0,
            description="DHW set point hysteresis",
            requires_feature="dhw_cylinder"
        ),
        "dhw_boost_temp": RegisterConfig(
            31, "DHW Over Boost Mode Set Point", RegisterType.HOLDING,
            RegisterCategory.DHW, "°C", 0.1, "temperature", 50.0, 70.0,
            description="DHW Over boost mode set point",
            requires_feature="dhw_cylinder"
        ),
        "dhw_max_time": RegisterConfig(
            32, "Max. Time For DHW Request", RegisterType.HOLDING,
            RegisterCategory.DHW, "min", 1.0, None, 10.0, 120.0,
            description="Max. time for DHW request",
            requires_feature="dhw_cylinder"
        ),
        "dhw_heater_delay": RegisterConfig(
            33, "Delay Time On DHW Heater From Off Compressor", RegisterType.HOLDING,
            RegisterCategory.DHW, "min", 1.0, None, 0.0, 30.0,
            description="Delay time on DHW heater from OFF compressor",
            requires_feature="dhw_cylinder"
        ),
        "dhw_heater_enable_temp": RegisterConfig(
            34, "Outdoor Air Temperature To Enable DHW Heaters", RegisterType.HOLDING,
            RegisterCategory.DHW, "°C", 0.1, "temperature", -15.0, 5.0,
            description="Outdoor air temperature to enable DHW heaters",
            requires_feature="dhw_cylinder"
        ),
        "dhw_heater_disable_temp": RegisterConfig(
            35, "Outdoor Air Temperature Hysteresis To Disable DHW Heaters", RegisterType.HOLDING,
            RegisterCategory.DHW, "°C", 0.1, "temperature", -10.0, 10.0,
            description="Outdoor air temperature hysteresis to disable DHW heaters",
            requires_feature="dhw_cylinder"
        ),
        "legionella_temp": RegisterConfig(
            36, "Anti-legionella Set Point", RegisterType.HOLDING,
            RegisterCategory.DHW, "°C", 0.1, "temperature", 60.0, 75.0,
            description="Anti-legionella set point",
            requires_feature="dhw_cylinder"
        ),
        
        # System Timing Controls (37-46)
        "night_mode_max_freq": RegisterConfig(
            37, "Max. Frequency Of Night Mode", RegisterType.HOLDING,
            RegisterCategory.ADVANCED, "Hz", 1.0, "frequency", 20.0, 100.0,
            description="Max. frequency of Night mode"
        ),
        "compressor_min_time": RegisterConfig(
            38, "Min. Time Compressor On/off Time", RegisterType.HOLDING,
            RegisterCategory.BASIC, "min", 1.0, None, 3.0, 10.0,
            description="Min. time compressor ON/OFF time"
        ),
        "pump_off_delay": RegisterConfig(
            39, "Delay Time Pump Off From Compressor Off", RegisterType.HOLDING,
            RegisterCategory.BASIC, "min", 1.0, None, 0.0, 10.0,
            description="Delay time pump OFF from compressor OFF"
        ),
        "compressor_on_delay": RegisterConfig(
            40, "Delay Time Compressor On From Pump On", RegisterType.HOLDING,
            RegisterCategory.BASIC, "min", 1.0, None, 1.0, 5.0,
            description="Delay time compressor ON from pump ON"
        ),
        "main_pump_config": RegisterConfig(
            41, "Type Of Configuration Of Main Water Pump", RegisterType.HOLDING,
            RegisterCategory.BASIC, None, 1.0, None, 0.0, 2.0,
            description="Type of configuration of Main water pump (0=always ON, 1=ON/OFF based on Buffertank temperature, 2=ON/OFF based on Sniffing cycles",
            enum_mapping={0: "Always ON", 1: "Buffer tank temp", 2: "Sniffing cycles"}
        ),
        "pump_sniffing_on_time": RegisterConfig(
            42, "Time On Main Water Pump For Sniffing Cycle", RegisterType.HOLDING,
            RegisterCategory.ADVANCED, "min", 1.0, None, 1.0, 10.0,
            description="Time ON Main water pump for Sniffing cycle"
        ),
        "pump_off_time": RegisterConfig(
            43, "Time Off Main Water Pump", RegisterType.HOLDING,
            RegisterCategory.ADVANCED, "min", 1.0, None, 5.0, 60.0,
            description="Time OFF Main water pump"
        ),
        "pump_delay_off_compressor": RegisterConfig(
            44, "Delay Time Off Main Water Pump From Off Compressor", RegisterType.HOLDING,
            RegisterCategory.BASIC, "min", 1.0, None, 0.0, 10.0,
            description="Delay time OFF Main water pump from OFF compressor"
        ),
        "pump_unlock_off_time": RegisterConfig(
            45, "Off Time For Unlock Pump Function Start", RegisterType.HOLDING,
            RegisterCategory.ADVANCED, "hours", 1.0, None, 12.0, 168.0,
            description="OFF time for Unlock pump function start"
        ),
        "main_pump_unlock_time": RegisterConfig(
            46, "Time On Main Water Pump For Unlock Pump Function", RegisterType.HOLDING,
            RegisterCategory.ADVANCED, "min", 1.0, None, 1.0, 10.0,
            description="Time ON Main water pump for Unlock pump function"
        ),
        
        # Additional Pump Controls (47-49)
        "pump1_unlock_time": RegisterConfig(
            47, "Time On Water Pump1 For Unlock Pump Function", RegisterType.HOLDING,
            RegisterCategory.ZONES, "min", 1.0, None, 1.0, 10.0,
            description="Time ON water pump1 for Unlock pump function"
        ),
        "pump2_unlock_time": RegisterConfig(
            48, "Time On Water Pump2 For Unlock Pump Function", RegisterType.HOLDING,
            RegisterCategory.ZONES, "min", 1.0, None, 1.0, 10.0,
            description="Time ON water pump2 for Unlock pump function",
            requires_feature="zones.zone_2.enabled"
        ),
        "additional_pump_operation": RegisterConfig(
            49, "Type Of Operation Of Additional Water Pump", RegisterType.HOLDING,
            RegisterCategory.EXTERNAL, None, 1.0, None, 0.0, 4.0,
            description="Type of operation of additional water pump (0=disable, 1=depending on Main water pump setting, 2=depending on Main water pump setting but always OFF when the DHW mode is activated, 3=always ON apart if any alarms are activated or if the HP unit is in OFF mode, 4=ON/OFF based on Room air temperature)",
            enum_mapping={0: "Disable", 1: "Follow main pump", 2: "Follow main (OFF in DHW)", 3: "Always ON", 4: "Room temp based"}
        ),
        
        # Frost Protection Controls (50-59)
        "frost_room_temp_start": RegisterConfig(
            50, "Start Temperature Of Frost Protection On Room Air Temp", RegisterType.HOLDING,
            RegisterCategory.BASIC, "°C", 0.1, "temperature", 5.0, 15.0,
            description="Start temperature of Frost protection on Room air temperature"
        ),
        "frost_room_temp_hysteresis": RegisterConfig(
            51, "Hysteresis Of Room Air Temperature Of Frost Protection", RegisterType.HOLDING,
            RegisterCategory.BASIC, "°C", 0.1, "temperature", 1.0, 5.0,
            description="Hysteresis of Room air temperature of Frost protection"
        ),
        "frost_water_temp": RegisterConfig(
            52, "Water Temperature Of Frost Protection", RegisterType.HOLDING,
            RegisterCategory.BASIC, "°C", 0.1, "temperature", 30.0, 50.0,
            description="Water temperature of Frost protection"
        ),
        "frost_pump_delay": RegisterConfig(
            53, "Delay Time Off Main Water Pump From Off", RegisterType.HOLDING,
            RegisterCategory.BASIC, "min", 1.0, None, 0.0, 10.0,
            description="Delay time OFF Main water pump from OFF Frost protection operation function"
        ),
        "frost_outdoor_temp_start": RegisterConfig(
            54, "Start Temperature Of Frost Protection On Outdoor Air Temp", RegisterType.HOLDING,
            RegisterCategory.BASIC, "°C", 0.1, "temperature", -10.0, 5.0,
            description="Start temperature of Frost protection on Outdoor air temperature"
        ),
        "frost_outdoor_temp_hysteresis": RegisterConfig(
            55, "Hysteresis Of Outdoor Air Temperature", RegisterType.HOLDING,
            RegisterCategory.BASIC, "°C", 0.1, "temperature", 1.0, 5.0,
            description="Hysteresis of Outdoor air temperature"
        ),
        "frost_backup_heater_temp": RegisterConfig(
            56, "Backup Heater Set Point During Frost Protection", RegisterType.HOLDING,
            RegisterCategory.EXTERNAL, "°C", 0.1, "temperature", 30.0, 50.0,
            description="Backup heater set point during Frost protection",
            requires_feature="backup_heater"
        ),
        "frost_outgoing_water_hysteresis": RegisterConfig(
            57, "Hysteresis Of Outgoing Water Temperature", RegisterType.HOLDING,
            RegisterCategory.BASIC, "°C", 0.1, "temperature", 1.0, 5.0,
            description="Hysteresis of Outgoing water temperature"
        ),
        "frost_dhw_tank_temp": RegisterConfig(
            58, "Start Temperature Of Frost Protection On DHW Tank Temp", RegisterType.HOLDING,
            RegisterCategory.DHW, "°C", 0.1, "temperature", 5.0, 15.0,
            description="Start temperature of Frost protection on DHW tank temperature",
            requires_feature="dhw_cylinder"
        ),
        "frost_dhw_tank_hysteresis": RegisterConfig(
            59, "Hysteresis Of DHW Tank Temperature", RegisterType.HOLDING,
            RegisterCategory.DHW, "°C", 0.1, "temperature", 1.0, 5.0,
            description="Hysteresis of DHW tank temperature",
            requires_feature="dhw_cylinder"
        ),
        
        # Humidity Controls (60-62)
        "room_humidity_value": RegisterConfig(
            60, "Room Relative Humidity Value", RegisterType.HOLDING,
            RegisterCategory.EXTERNAL, "%", 1.0, "humidity", 30.0, 70.0,
            description="Room relative humidity value",
            requires_feature="external_sensors.humidity"
        ),
        "humidity_flow_temp_start": RegisterConfig(
            61, "Room Relative Humidity Value To Start Increasing Flow Temp", RegisterType.HOLDING,
            RegisterCategory.EXTERNAL, "%", 1.0, "humidity", 60.0, 90.0,
            description="Room relative humidity value to start increasing Outgoing water temperature set",
            requires_feature="external_sensors.humidity"
        ),
        "humidity_flow_temp_hysteresis": RegisterConfig(
            62, "Max Flow Temp Hysteresis relative to Humidity", RegisterType.HOLDING,
            RegisterCategory.EXTERNAL, "°C", 0.1, "temperature", 2.0, 10.0,
            description="Max. Outgoing temperature hysteresis corresponding to 100% relative humidity",
            requires_feature="external_sensors.humidity"
        ),
        
        # Mixing Valve Controls (63-66)
        "mixing_valve_runtime": RegisterConfig(
            63, "Mixing Valve Runtime", RegisterType.HOLDING,
            RegisterCategory.EXTERNAL, "s", 1.0, None, 30.0, 300.0,
            description="Mixing valve runtime (from the fully closed to the fully open position)",
            requires_feature="mixing_valve"
        ),
        "mixing_valve_integral": RegisterConfig(
            64, "Mixing Valve Integral Factor", RegisterType.HOLDING,
            RegisterCategory.EXTERNAL, None, 1.0, None, 1.0, 100.0,
            description="Mixing valve integral factor",
            requires_feature="mixing_valve"
        ),
        "mixing_circuit_max_temp": RegisterConfig(
            65, "Max Water Temperature In Mixing Circuit", RegisterType.HOLDING,
            RegisterCategory.EXTERNAL, "°C", 1.0, "temperature", 30.0, 60.0,
            description="Max Water temperature in mixing circuit",
            requires_feature="mixing_valve"
        ),
        "three_way_valve_time": RegisterConfig(
            66, "3way Valve Change Over Time", RegisterType.HOLDING,
            RegisterCategory.EXTERNAL, "s", 1.0, None, 30.0, 300.0,
            description="3way valve change over time",
            requires_feature="three_way_valve"
        ),
        
        # Flow Switch and Alarm Controls (67-70)
        "flow_switch_startup_delay": RegisterConfig(
            67, "Flow Switch Alarm Delay Time At. Pump Start Up", RegisterType.HOLDING,
            RegisterCategory.BASIC, "s", 1.0, None, 10.0, 120.0,
            description="Flow switch alarm delay time at. Pump start up"
        ),
        "flow_switch_operation_delay": RegisterConfig(
            68, "Flow Switch Alarm Delay Time", RegisterType.HOLDING,
            RegisterCategory.BASIC, "s", 1.0, None, 5.0, 60.0,
            description="Flow switch alarm delay time in steady operation of the water pump"
        ),
        "alarm_retry_count": RegisterConfig(
            69, "The Number Of Retry Until Displaying Alarm", RegisterType.HOLDING,
            RegisterCategory.DIAGNOSTIC, None, 1.0, None, 1.0, 10.0,
            description="The number of retry until displaying alarm"
        ),
        "alarm_retry_time": RegisterConfig(
            70, "The Time Of Repeating Retry Until Displaying Alarm", RegisterType.HOLDING,
            RegisterCategory.DIAGNOSTIC, "min", 1.0, None, 1.0, 60.0,
            description="The time of repeating retry until displaying alarm"
        ),
        
        # Backup Heater Controls (71-83)
        "backup_heater_function": RegisterConfig(
            71, "Backup Heater Type Of Function", RegisterType.HOLDING,
            RegisterCategory.EXTERNAL, None, 1.0, None, 0.0, 3.0,
            description="Backup heater type of function (0=disable, 1=Replacement mode, 2=Emergency mode, 3=Supplementary mode)",
            requires_feature="backup_heater",
            enum_mapping={0: "Disable", 1: "Replacement", 2: "Emergency", 3: "Supplementary"}
        ),
        "manual_water_setpoint": RegisterConfig(
            72, "Manual Water Set Point", RegisterType.HOLDING,
            RegisterCategory.BASIC, "°C", 0.1, "temperature", 30.0, 60.0,
            description="Manual water set point"
        ),
        "manual_water_hysteresis": RegisterConfig(
            73, "Manual Water Temperature Hysteresis", RegisterType.HOLDING,
            RegisterCategory.BASIC, "°C", 0.1, "temperature", 1.0, 5.0,
            description="Manual water temperature hysteresis"
        ),
        "heater_flow_switch_delay": RegisterConfig(
            74, "Delay Time Of The Heater Off That Avoid Flow Switch Alarm", RegisterType.HOLDING,
            RegisterCategory.EXTERNAL, "s", 1.0, None, 0.0, 60.0,
            description="Delay time of the heater OFF that avoid flow switch alarm",
            requires_feature="backup_heater"
        ),
        "heater_activation_delay": RegisterConfig(
            75, "Heater Activation Delay Time", RegisterType.HOLDING,
            RegisterCategory.EXTERNAL, "min", 1.0, None, 0.0, 30.0,
            description="Heater activation delay time",
            requires_feature="backup_heater"
        ),
        "heater_integration_time": RegisterConfig(
            76, "Integration Time For Starting Heaters", RegisterType.HOLDING,
            RegisterCategory.EXTERNAL, "min", 1.0, None, 5.0, 60.0,
            description="Integration time for starting heaters",
            requires_feature="backup_heater"
        ),
        "backup_heater_enable_temp": RegisterConfig(
            77, "Outdoor Air Temperature To Enable Backup Heater", RegisterType.HOLDING,
            RegisterCategory.EXTERNAL, "°C", 0.1, "temperature", -20.0, 5.0,
            description="Outdoor air temperature to enable Backup heaters and disable compressor",
            requires_feature="backup_heater"
        ),
        "backup_heater_disable_temp": RegisterConfig(
            78, "Outdoor Air Temperature Hysteresis To Disable Backup Heaters and Enable Compressor", RegisterType.HOLDING,
            RegisterCategory.EXTERNAL, "°C", 0.1, "temperature", -15.0, 10.0,
            description="Outdoor air temperature hysteresis to disable Backup heaters and enable compressor",
            requires_feature="backup_heater"
        ),
        "backup_heater_supplementary_enable": RegisterConfig(
            79, "Outdoor Air Temperature To Enable Backup Heaters", RegisterType.HOLDING,
            RegisterCategory.EXTERNAL, "°C", 0.1, "temperature", -10.0, 5.0,
            description="Outdoor air temperature to enable Backup heaters (Supplementary mode)",
            requires_feature="backup_heater"
        ),
        "backup_heater_supplementary_disable": RegisterConfig(
            80, "Outdoor Air Temperature Hysteresis To Disable Backup Heaters (Supplementary Mode)", RegisterType.HOLDING,
            RegisterCategory.EXTERNAL, "°C", 0.1, "temperature", -5.0, 10.0,
            description="Outdoor air temperature hysteresis to disable Backup heaters (Supplementary mode)",
            requires_feature="backup_heater"
        ),
        "freeze_protection_functions": RegisterConfig(
            81, "Freeze Protection Functions", RegisterType.HOLDING,
            RegisterCategory.BASIC, None, 1.0, None, 0.0, 3.0,
            description="Freeze protection functions (0=disable, 1=enabled during Start-up, 2=enabled during Defrost, 3=enabled during Start-up and Defrost)",
            enum_mapping={0: "Disable", 1: "Start-up only", 2: "Defrost only", 3: "Start-up and Defrost"}
        ),
        "startup_outgoing_temp": RegisterConfig(
            82, "Outgoing Water Temperature Set Point During Start-up", RegisterType.HOLDING,
            RegisterCategory.BASIC, "°C", 0.1, "temperature", 30.0, 50.0,
            description="Outgoing water temperature set point during Start-up"
        ),
        "startup_temp_hysteresis": RegisterConfig(
            83, "Hysteresis Water Temperature Set Point During Start-up", RegisterType.HOLDING,
            RegisterCategory.BASIC, "°C", 0.1, "temperature", 1.0, 5.0,
            description="Hysteresis water temperature set point during Start-up"
        ),
        
        # EHS (External Heat Source) Controls (84-90)
        "ehs_function": RegisterConfig(
            84, "EHS Type Of Function", RegisterType.HOLDING,
            RegisterCategory.EXTERNAL, None, 1.0, None, 0.0, 2.0,
            description="EHS type of function (0=disable, 1=Replacement mode, 2=Supplementary mode)",
            requires_feature="external_heat_source",
            enum_mapping={0: "Disable", 1: "Replacement", 2: "Supplementary"}
        ),
        "ehs_enable_temp": RegisterConfig(
            85, "Outdoor Air Temperature To Enable EHS And Disable Compressor", RegisterType.HOLDING,
            RegisterCategory.EXTERNAL, "°C", 0.1, "temperature", -20.0, 5.0,
            description="Outdoor air temperature to enable EHS and disable compressor",
            requires_feature="external_heat_source"
        ),
        "ehs_disable_temp": RegisterConfig(
            86, "Outdoor Air Temperature Hysteresis To Disable Enable Compressor", RegisterType.HOLDING,
            RegisterCategory.EXTERNAL, "°C", 0.1, "temperature", -15.0, 10.0,
            description="Outdoor air temperature hysteresis to disable EHS and enable compressor",
            requires_feature="external_heat_source"
        ),
        "ehs_supplementary_enable": RegisterConfig(
            87, "Outdoor Air Temperature To Enable EHS", RegisterType.HOLDING,
            RegisterCategory.EXTERNAL, "°C", 0.1, "temperature", -10.0, 5.0,
            description="Outdoor air temperature to enable EHS (Supplementary mode)",
            requires_feature="external_heat_source"
        ),
        "ehs_supplementary_disable": RegisterConfig(
            88, "Outdoor Air Temperature Hysteresis To Disable EHS", RegisterType.HOLDING,
            RegisterCategory.EXTERNAL, "°C", 0.1, "temperature", -5.0, 10.0,
            description="Outdoor air temperature hysteresis to disable EHS (Supplementary mode)",
            requires_feature="external_heat_source"
        ),
        "ehs_activation_delay": RegisterConfig(
            89, "EHS Activation Delay Time", RegisterType.HOLDING,
            RegisterCategory.EXTERNAL, "min", 1.0, None, 0.0, 30.0,
            description="EHS activation delay time",
            requires_feature="external_heat_source"
        ),
        "ehs_integration_time": RegisterConfig(
            90, "Integration Time For Starting EHS", RegisterType.HOLDING,
            RegisterCategory.EXTERNAL, "min", 1.0, None, 5.0, 60.0,
            description="Integration time for starting EHS",
            requires_feature="external_heat_source"
        ),
        
        # Terminal Configuration Controls (91-96)
        "terminal_20_21_config": RegisterConfig(
            91, "Terminal 20-21 : On/off Remote Contact Or EHS Alarm", RegisterType.HOLDING,
            RegisterCategory.EXTERNAL, None, 1.0, None, 0.0, 2.0,
            description="Terminal 20-21 : ON/OFF remote contact or EHS Alarm input (0=disable (Remote controller only), 1=ON/OFF remote contact, 2=EHS Alarm input)",
            enum_mapping={0: "Disable", 1: "Remote contact", 2: "EHS Alarm"}
        ),
        "terminal_24_25_config": RegisterConfig(
            92, "Terminal 24-25 : Heating/cooling Mode Remote Contact", RegisterType.HOLDING,
            RegisterCategory.BASIC, None, 1.0, None, 0.0, 2.0,
            description="Terminal 24-25 : Heating/Cooling mode remote contact (0=disable (Remote controller only), 1=Cooling is CLOSE contact Heating is OPEN contact, 2=Cooling is OPEN contact Heating is CLOSE contact)",
            enum_mapping={0: "Disable", 1: "Cool=CLOSE Heat=OPEN", 2: "Cool=OPEN Heat=CLOSE"}
        ),
        "terminal_47_config": RegisterConfig(
            93, "Terminal 47 : Alarm", RegisterType.HOLDING,
            RegisterCategory.DIAGNOSTIC, None, 1.0, None, 0.0, 2.0,
            description="Terminal 47 : Alarm (Configurable output) (0=disable, 1=Alarm, 2=Ambient temperature reached)",
            enum_mapping={0: "Disable", 1: "Alarm", 2: "Temp reached"}
        ),
        "terminal_48_config": RegisterConfig(
            94, "Terminal 48 : Pump1", RegisterType.HOLDING,
            RegisterCategory.ZONES, None, 1.0, None, 0.0, 1.0,
            description="Terminal 48 : Pump1 (0=disable, 1=1st Additional water pump1 for Zone1)",
            enum_mapping={0: "Disable", 1: "Zone1 Pump"}
        ),
        "terminal_49_config": RegisterConfig(
            95, "Terminal 49 : Pump2", RegisterType.HOLDING,
            RegisterCategory.ZONES, None, 1.0, None, 0.0, 1.0,
            description="Terminal 49 : Pump2 (0=disable, 1=2nd Additional water pump2 for Zone2)",
            requires_feature="zones.zone_2.enabled",
            enum_mapping={0: "Disable", 1: "Zone2 Pump"}
        ),
        "terminal_50_52_config": RegisterConfig(
            96, "Terminal 50-51-52 : DHW 3way Valve", RegisterType.HOLDING,
            RegisterCategory.DHW, None, 1.0, None, 0.0, 1.0,
            description="Terminal 50-51-52 : DHW 3way valve (1=enable)",
            requires_feature="dhw_cylinder",
            enum_mapping={0: "Disable", 1: "Enable"}
        ),
        
        # Buffer Tank Controls (99-100) - Note: register 97-98 don't exist
        "buffer_heating_setpoint": RegisterConfig(
            99, "Buffer Tank Set Point For Heating", RegisterType.HOLDING,
            RegisterCategory.BASIC, "°C", 0.1, "temperature", 30.0, 60.0,
            description="Buffer tank set point for Heating"
        ),
        "buffer_cooling_setpoint": RegisterConfig(
            100, "Buffer Tank Set Point For Cooling", RegisterType.HOLDING,
            RegisterCategory.BASIC, "°C", 0.1, "temperature", 5.0, 18.0,
            description="Buffer tank set point for Cooling"
        ),
    }
        
def _load_coil_registers(self) -> Dict[str, RegisterConfig]:
    """Load ALL 32 coil register definitions (1-32)."""
    return {
        # Register 1
        "reboot_after_blackout": RegisterConfig(
            1, "Operation At The Time Of Reboot After Blackout", RegisterType.COIL,
            RegisterCategory.BASIC,
            description="Operation at the time of reboot after blackout 0 = disable 1 = enable"
        ),
        
        # Register 2
        "zone1_weather_comp": RegisterConfig(
            2, "Heating Weather Compensation Zone 1", RegisterType.COIL,
            RegisterCategory.ZONES,
            description="Heating Zone1, enable Outgoing water set point (0=Fixed set point, 1=Climatic curve)"
        ),
        
        # Register 3
        "zone2_weather_comp": RegisterConfig(
            3, "Heating Weather Compensation Zone 2", RegisterType.COIL,
            RegisterCategory.ZONES,
            description="Heating Zone2, enable Outgoing water set point (0=Fixed set point, 1=Climatic curve)",
            requires_feature="zones.zone_2.enabled"
        ),
        
        # Register 4
        "zone1_cooling_weather_comp": RegisterConfig(
            4, "Cooling Weather Compensation Zone 1", RegisterType.COIL,
            RegisterCategory.ZONES,
            description="Cooling Zone1, enable Outgoing water set point (0=Fixed set point, 1=Climatic curve)"
        ),
        
        # Register 5
        "zone2_cooling_weather_comp": RegisterConfig(
            5, "Cooling Weather Compensation Zone 2", RegisterType.COIL,
            RegisterCategory.ZONES,
            description="Cooling Zone2, enable Outgoing water set point (0=Fixed set point, 1=Climatic Curve)",
            requires_feature="zones.zone_2.enabled"
        ),
        
        # Register 6
        "anti_legionella": RegisterConfig(
            6, "Anti-legionella Function", RegisterType.COIL,
            RegisterCategory.DHW,
            description="Anti-legionella function (0=disable, 1=enable)",
            requires_feature="dhw_cylinder"
        ),
        
        # Register 7
        "control_mode": RegisterConfig(
            7, "The HP Unit Turns On/off Based On", RegisterType.COIL,
            RegisterCategory.BASIC,
            description="The HP unit turns ON/OFF based on (0=Room set point, 1=Water set point)"
        ),
        
        # Register 8
        "frost_protect_room": RegisterConfig(
            8, "Frost Protection Based On Room Temperature", RegisterType.COIL,
            RegisterCategory.BASIC,
            description="Frost Protection based on Room Temperature"
        ),
        
        # Register 9
        "frost_protect_outdoor": RegisterConfig(
            9, "Frost Protection Based On Outdoor Temperature", RegisterType.COIL,
            RegisterCategory.BASIC,
            description="Frost protection by outdoor temperature 0=disable 1 = enable"
        ),
        
        # Register 10
        "frost_protect_flow": RegisterConfig(
            10, "Frost Protection Based On Flow Temp", RegisterType.COIL,
            RegisterCategory.BASIC,
            description="Frost protection based on Outgoing water temperature 0=disable 1 = enable"
        ),
        
        # Register 11
        "dhw_frost_protection": RegisterConfig(
            11, "DHW Storage Frost Protection", RegisterType.COIL,
            RegisterCategory.DHW,
            description="DHW storage frost protection 0=disable 1 = enable",
            requires_feature="dhw_cylinder"
        ),
        
        # Register 12
        "secondary_frost_protection": RegisterConfig(
            12, "Secondary System Circuit Frost Protection", RegisterType.COIL,
            RegisterCategory.EXTERNAL,
            description="Secondary system circuit frost protection 0=disable 1 = enable"
        ),
        
        # Register 13
        "humidity_compensation": RegisterConfig(
            13, "Compensation For Room Humidity", RegisterType.COIL,
            RegisterCategory.EXTERNAL,
            description="Compensation for room humidity (0=disable, 1=enable)",
            requires_feature="external_sensors.humidity"
        ),
        
        # Register 14
        "backup_heater_conditions": RegisterConfig(
            14, "Conditions To Be Available Backup Heaters", RegisterType.COIL,
            RegisterCategory.EXTERNAL,
            description="Conditions to be available Backup heaters (0=always enabled, 1=depends on Outdoor Air temperature)",
            requires_feature="backup_heater"
        ),
        
        # Register 15 - Note: No register 15 in your const.py, but keeping sequence
        
        # Register 16
        "remote_controller": RegisterConfig(
            16, "Terminal 1-2-3 : Remote Controller", RegisterType.COIL,
            RegisterCategory.BASIC,
            description="Terminal 1-2-3 : Remote Controller (0=disable, 1=enable)"
        ),
        
        # Register 17
        "mixing_valve": RegisterConfig(
            17, "Terminal 4-5-6 : 3way Mixing Valve", RegisterType.COIL,
            RegisterCategory.EXTERNAL,
            description="Terminal 4-5-6 : 3way mixing valve (0=disable, 1=enable)",
            requires_feature="mixing_valve"
        ),
        
        # Register 18
        "dhw_tank_probe": RegisterConfig(
            18, "Terminal 7-8 : DHW Tank Temperature Probe", RegisterType.COIL,
            RegisterCategory.DHW,
            description="Terminal 7-8 : DHW tank temperature probe (0=disable, 1=enable)",
            requires_feature="dhw_cylinder"
        ),
        
        # Register 19
        "external_outdoor_probe": RegisterConfig(
            19, "Terminal 9-10 : Outdoor Air Temperature Probe", RegisterType.COIL,
            RegisterCategory.EXTERNAL,
            description="Terminal 9-10 : Outdoor air temperature probe (additional) (0=disable, 1=enable)",
            requires_feature="external_sensors.outdoor_temp"
        ),
        
        # Register 20
        "buffer_tank_probe": RegisterConfig(
            20, "Terminal 11-12 : Buffer Tank Temperature Probe", RegisterType.COIL,
            RegisterCategory.BASIC,
            description="Terminal 11-12 : Buffer tank temperature probe (0=disable, 1=enable)"
        ),
        
        # Register 21
        "mix_water_probe": RegisterConfig(
            21, "Terminal 13-14 : Mix Water Temperature Probe", RegisterType.COIL,
            RegisterCategory.ZONES,
            description="Terminal 13-14 : Mix Water temperature probe (0=disable, 1=enable)"
        ),
        
        # Register 22
        "modbus_enable": RegisterConfig(
            22, "Terminal 15-16-32 : Rs485 Mod Bus", RegisterType.COIL,
            RegisterCategory.BASIC,
            description="Terminal 15-16-32 : RS485 Mod Bus (0=disable, 1=enable)"
        ),
        
        # Register 23
        "humidity_sensor": RegisterConfig(
            23, "Terminal 17-18 : Humidity Sensor", RegisterType.COIL,
            RegisterCategory.EXTERNAL,
            description="Terminal 17-18 : Humidity sensor (0=disable, 1=enable)",
            requires_feature="external_sensors.humidity"
        ),
        
        # Register 24
        "dhw_remote_contact": RegisterConfig(
            24, "Terminal 19-18 : DHW Remote Contact", RegisterType.COIL,
            RegisterCategory.DHW,
            description="Terminal 19-18 : DHW remote contact (0=disable (Remote controller only), 1=enable)",
            requires_feature="dhw_cylinder"
        ),
        
        # Register 25
        "dual_setpoint_control": RegisterConfig(
            25, "Terminal 22-23 : Dual Set Point Control", RegisterType.COIL,
            RegisterCategory.ADVANCED,
            description="Terminal 22-23 : Dual set point control (0=disable, 1=enable)"
        ),
        
        # Register 26
        "flow_switch": RegisterConfig(
            26, "Terminal 26-27 : Flow Switch", RegisterType.COIL,
            RegisterCategory.BASIC,
            description="Terminal 26-27 : Flow switch (0=disable, 1=enable)"
        ),
        
        # Register 27
        "night_mode": RegisterConfig(
            27, "Terminal 28-29 : Night Mode", RegisterType.COIL,
            RegisterCategory.ADVANCED,
            description="Terminal 28-29 : Night mode (0=disable (Remote controller only), 1=enable)"
        ),
        
        # Register 28
        "low_tariff": RegisterConfig(
            28, "Terminal 30-31 : Low Tariff", RegisterType.COIL,
            RegisterCategory.ADVANCED,
            description="Terminal 30-31 : Low tariff (0=disable (Remote controller only), 1=enable)"
        ),
        
        # Register 29
        "external_heat_source": RegisterConfig(
            29, "Terminal 41-42 : EHS", RegisterType.COIL,
            RegisterCategory.EXTERNAL,
            description="Terminal 41-42 : EHS (External heat source for space heating) (0=disable, 1=enable)",
            requires_feature="external_heat_source"
        ),
        
        # Register 30
        "heating_cooling_mode_output": RegisterConfig(
            30, "Terminal 43-44 : Heating/cooling Mode Output", RegisterType.COIL,
            RegisterCategory.BASIC,
            description="Terminal 43-44 : Heating/Cooling mode output (0=disable, 1=Indication of Cooling mode (CLOSE=Cooling), 2=indication of Heating mode (CLOSE=Heating))"
        ),
        
        # Register 31
        "dehumidifier": RegisterConfig(
            31, "Terminal 45 : Dehumidifier", RegisterType.COIL,
            RegisterCategory.EXTERNAL,
            description="Terminal 45 : Dehumidifier (0=disable, 1=enable)",
            requires_feature="dehumidifier"
        ),
        
        # Register 32
        "terminal_46_config": RegisterConfig(
            32, "Terminal 46 : DHW Electric Heater Or Backup Heater", RegisterType.COIL,
            RegisterCategory.EXTERNAL,
            description="Terminal 46 : DHW Electric heater or Backup heater (0=DHW Electric heater, 1=Backup heater)",
            requires_feature="backup_heater"
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
