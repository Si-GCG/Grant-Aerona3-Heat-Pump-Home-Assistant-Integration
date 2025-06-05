"""Constants for Grant Aerona3 Heat Pump integration."""
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfPower,
    UnitOfFrequency,
    PERCENTAGE,
)

# Domain
DOMAIN = "grant_aerona3"

# Configuration constants
CONF_SCAN_INTERVAL = "scan_interval"
CONF_SLAVE_ID = "slave_id"

# Default values
DEFAULT_PORT = 502
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_SLAVE_ID = 1

# Input Registers (Read-only monitoring data)
INPUT_REGISTER_MAP = {
    0: {
        "name": "Return water temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "scale": 1,
        "offset": 0,
        "description": "Return water temperature"
    },
    1: {
        "name": "Compressor operating frequency",
        "unit": UnitOfFrequency.HERTZ,
        "device_class": SensorDeviceClass.FREQUENCY,
        "state_class": SensorStateClass.MEASUREMENT,
        "scale": 1,
        "offset": 0,
        "description": "Compressor operating frequency"
    },
    2: {
        "name": "Discharge temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "scale": 1,
        "offset": 0,
        "description": "Discharge temperature"
    },
    3: {
        "name": "Current consumption value",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.CURRENT,
        "state_class": SensorStateClass.MEASUREMENT,
        "scale": 100,
        "offset": 0,
        "description": "Current consumption value"
    },
    4: {
        "name": "Fan control number of rotation",
        "unit": "rpm",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "scale": 10,
        "offset": 0,
        "description": "Fan control number of rotation"
    },
    5: {
        "name": "Defrost temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "scale": 1,
        "offset": 0,
        "description": "Defrost temperature"
    },
    6: {
        "name": "Outdoor air temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "scale": 1,
        "offset": 0,
        "description": "Outdoor air temperature"
    },
    7: {
        "name": "Water pump control number of rotation",
        "unit": "rpm",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "scale": 100,
        "offset": 0,
        "description": "Water pump control number of rotation"
    },
    8: {
        "name": "Suction temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "scale": 1,
        "offset": 0,
        "description": "Suction temperature"
    },
    9: {
        "name": "Outgoing water temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "scale": 1,
        "offset": 0,
        "description": "Outgoing water temperature"
    },
    10: {
        "name": "\"Selected operating mode (0=Heating/Cooling OFF",
        "unit": "0",
        "device_class": None,
        "state_class": None,
        "scale": 1,
        "offset": 0,
        "description": "\"Selected operating mode (0=Heating/Cooling OFF"
    },
    11: {
        "name": "Room air set temperature of Zone1(Master)",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "scale": 0.5,
        "offset": 0,
        "description": "Room air set temperature of Zone1(Master)"
    },
    12: {
        "name": "Room air set temperature of Zone2(Slave)",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "scale": 0.5,
        "offset": 0,
        "description": "Room air set temperature of Zone2(Slave)"
    },
    13: {
        "name": "\"Selected DHW operating mode (0=disable",
        "unit": "0",
        "device_class": None,
        "state_class": None,
        "scale": 1,
        "offset": 0,
        "description": "\"Selected DHW operating mode (0=disable"
    },
    14: {
        "name": "\"Day (0=Monday",
        "unit": "4=Friday",
        "device_class": None,
        "state_class": None,
        "scale": 1,
        "offset": 0,
        "description": "\"Day (0=Monday"
    },
    15: {
        "name": "Legionella Cycle Set Time",
        "unit": "1min",
        "device_class": SensorDeviceClass.DURATION,
        "state_class": None,
        "scale": 1,
        "offset": 0,
        "description": "Legionella Cycle Set Time"
    },
    16: {
        "name": "DHW tank temperature (Terminal 7-8)",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "scale": 0.5,
        "offset": 0,
        "description": "DHW tank temperature (Terminal 7-8)"
    },
    17: {
        "name": "Outdoor air temperature (Terminal 9-10)",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "scale": 0.5,
        "offset": 0,
        "description": "Outdoor air temperature (Terminal 9-10)"
    },
    18: {
        "name": "Buffer tank temperature (Terminal 11-12)",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "scale": 0.5,
        "offset": 0,
        "description": "Buffer tank temperature (Terminal 11-12)"
    },
    19: {
        "name": "Mix water temperature (Terminal 13-14)",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "scale": 0.5,
        "offset": 0,
        "description": "Mix water temperature (Terminal 13-14)"
    },
    20: {
        "name": "Humidity sensor (Terminal 17-18)",
        "unit": "1%",
        "device_class": None,
        "state_class": None,
        "scale": 1,
        "offset": 0,
        "description": "Humidity sensor (Terminal 17-18)"
    },
    21: {
        "name": "?Current error code",
        "unit": None,
        "device_class": SensorDeviceClass.CURRENT,
        "state_class": SensorStateClass.MEASUREMENT,
        "scale": 1,
        "offset": 0,
        "description": "?Current error code"
    },
    22: {
        "name": "?Error code once before",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "scale": 1,
        "offset": 0,
        "description": "?Error code once before"
    },
    23: {
        "name": "?Error code twice before",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "scale": 1,
        "offset": 0,
        "description": "?Error code twice before"
    },
    24: {
        "name": "?Error code three times before",
        "unit": None,
        "device_class": SensorDeviceClass.DURATION,
        "state_class": None,
        "scale": 1,
        "offset": 0,
        "description": "?Error code three times before"
    },
    25: {
        "name": "?Error code four times before",
        "unit": None,
        "device_class": SensorDeviceClass.DURATION,
        "state_class": None,
        "scale": 1,
        "offset": 0,
        "description": "?Error code four times before"
    },
    26: {
        "name": "?Error code five times before",
        "unit": None,
        "device_class": SensorDeviceClass.DURATION,
        "state_class": None,
        "scale": 1,
        "offset": 0,
        "description": "?Error code five times before"
    },
    27: {
        "name": "?Error code six times before",
        "unit": None,
        "device_class": SensorDeviceClass.DURATION,
        "state_class": None,
        "scale": 1,
        "offset": 0,
        "description": "?Error code six times before"
    },
    28: {
        "name": "?Error code seven times before",
        "unit": None,
        "device_class": SensorDeviceClass.DURATION,
        "state_class": None,
        "scale": 1,
        "offset": 0,
        "description": "?Error code seven times before"
    },
    29: {
        "name": "?Error code eight times before",
        "unit": None,
        "device_class": SensorDeviceClass.DURATION,
        "state_class": None,
        "scale": 1,
        "offset": 0,
        "description": "?Error code eight times before"
    },
    30: {
        "name": "?Error code nine times before",
        "unit": None,
        "device_class": SensorDeviceClass.DURATION,
        "state_class": None,
        "scale": 1,
        "offset": 0,
        "description": "?Error code nine times before"
    },
    31: {
        "name": "?Error code ten times before",
        "unit": None,
        "device_class": SensorDeviceClass.DURATION,
        "state_class": None,
        "scale": 1,
        "offset": 0,
        "description": "?Error code ten times before"
    },
    32: {
        "name": "Plate heat exchanger temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "scale": 1,
        "offset": 0,
        "description": "Plate heat exchanger temperature"
    },
}

# Holding Registers (Read/Write configuration settings)
HOLDING_REGISTER_MAP = {
    2: {
        "name": "\"Heating Zone1",
        "unit": "60",
        "device_class": None,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "\"Heating Zone1"
    },
    3: {
        "name": "Max. Outgoing water temperature in Heating mode (Tm1) Zone1",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Max. Outgoing water temperature in Heating mode (Tm1) Zone1"
    },
    4: {
        "name": "Min. Outgoing water temperature in Heating mode (Tm2) Zone1",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Min. Outgoing water temperature in Heating mode (Tm2) Zone1"
    },
    5: {
        "name": "Min. Outdoor air temperature corresponding to max. Outgoing water temperature (Te1) Zone1",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Min. Outdoor air temperature corresponding to max. Outgoing water temperature (Te1) Zone1"
    },
    6: {
        "name": "Max. Outdoor air temperature corresponding to max. Outgoing water temperature (Te2) Zone1",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Max. Outdoor air temperature corresponding to max. Outgoing water temperature (Te2) Zone1"
    },
    7: {
        "name": "\"Heating Zone2",
        "unit": "60",
        "device_class": None,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "\"Heating Zone2"
    },
    8: {
        "name": "Max. Outgoing water temperature in Heating mode (Tm1) Zone2",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Max. Outgoing water temperature in Heating mode (Tm1) Zone2"
    },
    9: {
        "name": "Min. Outgoing water temperature in Heating mode (Tm2) Zone2",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Min. Outgoing water temperature in Heating mode (Tm2) Zone2"
    },
    10: {
        "name": "Min. Outdoor air temperature corresponding to max. Outgoing water temperature (Te1) Zone2",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Min. Outdoor air temperature corresponding to max. Outgoing water temperature (Te1) Zone2"
    },
    11: {
        "name": "Max. Outdoor air temperature corresponding to max. Outgoing water temperature (Te2) Zone2",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Max. Outdoor air temperature corresponding to max. Outgoing water temperature (Te2) Zone2"
    },
    12: {
        "name": "\"Cooling Zone1",
        "unit": "23",
        "device_class": None,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "\"Cooling Zone1"
    },
    13: {
        "name": "Max. Outgoing water temperature in Cooling mode (Tm1) Zone1",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Max. Outgoing water temperature in Cooling mode (Tm1) Zone1"
    },
    14: {
        "name": "Min. Outgoing water temperature in Cooling mode (Tm2) Zone1",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Min. Outgoing water temperature in Cooling mode (Tm2) Zone1"
    },
    15: {
        "name": "Min. Outdoor air temperature corresponding to max. Outgoing water temperature (Te1) Zone1",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Min. Outdoor air temperature corresponding to max. Outgoing water temperature (Te1) Zone1"
    },
    16: {
        "name": "Max. Outdoor air temperature corresponding to max. Outgoing water temperature (Te2) Zone1",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Max. Outdoor air temperature corresponding to max. Outgoing water temperature (Te2) Zone1"
    },
    17: {
        "name": "\"Cooling Zone2",
        "unit": "23",
        "device_class": None,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "\"Cooling Zone2"
    },
    18: {
        "name": "Max. Outgoing water temperature in Cooling mode (Tm1) Zone2",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Max. Outgoing water temperature in Cooling mode (Tm1) Zone2"
    },
    19: {
        "name": "Min. Outgoing water temperature in Cooling mode (Tm2) Zone2",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Min. Outgoing water temperature in Cooling mode (Tm2) Zone2"
    },
    20: {
        "name": "Min. Outdoor air temperature corresponding to max. Outgoing water temperature (Te1) Zone2",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Min. Outdoor air temperature corresponding to max. Outgoing water temperature (Te1) Zone2"
    },
    21: {
        "name": "Max. Outdoor air temperature corresponding to max. Outgoing water temperature (Te2) Zone2",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Max. Outdoor air temperature corresponding to max. Outgoing water temperature (Te2) Zone2"
    },
    22: {
        "name": "Hysteresis of water set point in Heating and DHW",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": None,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Hysteresis of water set point in Heating and DHW"
    },
    23: {
        "name": "Hysteresis of water set point in Cooling",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": None,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Hysteresis of water set point in Cooling"
    },
    24: {
        "name": "Low tariff deferential water set point for Heating",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": None,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Low tariff deferential water set point for Heating"
    },
    25: {
        "name": "Low tariff deferential water set point for Cooling",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": None,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Low tariff deferential water set point for Cooling"
    },
    26: {
        "name": "\"DHW production priority setting (0=DHW is unavailable",
        "unit": "0",
        "device_class": None,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "\"DHW production priority setting (0=DHW is unavailable"
    },
    27: {
        "name": "\"Type of configuration to heat the DHW (0=Heat pump + Heater",
        "unit": "0",
        "device_class": None,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "\"Type of configuration to heat the DHW (0=Heat pump + Heater"
    },
    28: {
        "name": "DHW Comfort set temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "DHW Comfort set temperature"
    },
    29: {
        "name": "DHW Economy set temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "DHW Economy set temperature"
    },
    30: {
        "name": "DHW set point hysteresis",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": None,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "DHW set point hysteresis"
    },
    31: {
        "name": "DHW Over boost mode set point",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": None,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "DHW Over boost mode set point"
    },
    32: {
        "name": "Max. time for DHW request",
        "unit": "1min",
        "device_class": SensorDeviceClass.DURATION,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "Max. time for DHW request"
    },
    33: {
        "name": "Delay time on DHW heater from OFF compressor",
        "unit": "1min",
        "device_class": SensorDeviceClass.DURATION,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "Delay time on DHW heater from OFF compressor"
    },
    34: {
        "name": "Outdoor air temperature to enable DHW heaters",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Outdoor air temperature to enable DHW heaters"
    },
    35: {
        "name": "Outdoor air temperature hysteresis to disable DHW heaters",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Outdoor air temperature hysteresis to disable DHW heaters"
    },
    36: {
        "name": "Anti-legionella set point",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": None,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Anti-legionella set point"
    },
    37: {
        "name": "Max. frequency of Night mode",
        "unit": "5%",
        "device_class": SensorDeviceClass.FREQUENCY,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "Max. frequency of Night mode"
    },
    38: {
        "name": "Min. time compressor ON/OFF time",
        "unit": "1sec",
        "device_class": SensorDeviceClass.DURATION,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "Min. time compressor ON/OFF time"
    },
    39: {
        "name": "Delay time pump OFF from compressor OFF",
        "unit": "1sec",
        "device_class": SensorDeviceClass.DURATION,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "Delay time pump OFF from compressor OFF"
    },
    40: {
        "name": "Delay time compressor ON from pump ON",
        "unit": "1sec",
        "device_class": SensorDeviceClass.DURATION,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "Delay time compressor ON from pump ON"
    },
    41: {
        "name": "\"Type of configuration of Main water pump (0=always ON",
        "unit": "0",
        "device_class": None,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "\"Type of configuration of Main water pump (0=always ON"
    },
    42: {
        "name": "Time ON Main water pump for Sniffing cycle",
        "unit": "1min",
        "device_class": SensorDeviceClass.DURATION,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "Time ON Main water pump for Sniffing cycle"
    },
    43: {
        "name": "Time OFF Main water pump",
        "unit": "1min",
        "device_class": SensorDeviceClass.DURATION,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "Time OFF Main water pump"
    },
    44: {
        "name": "Delay time OFF Main water pump from OFF compressor",
        "unit": "1min",
        "device_class": SensorDeviceClass.DURATION,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "Delay time OFF Main water pump from OFF compressor"
    },
    45: {
        "name": "OFF time for Unlock pump function start",
        "unit": "1Hr",
        "device_class": SensorDeviceClass.DURATION,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "OFF time for Unlock pump function start"
    },
    46: {
        "name": "Time ON Main water pump for Unlock pump function",
        "unit": "1sec",
        "device_class": SensorDeviceClass.DURATION,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "Time ON Main water pump for Unlock pump function"
    },
    47: {
        "name": "Time ON water pump1 for Unlock pump function",
        "unit": "1sec",
        "device_class": SensorDeviceClass.DURATION,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "Time ON water pump1 for Unlock pump function"
    },
    48: {
        "name": "Time ON water pump2 for Unlock pump function",
        "unit": "1sec",
        "device_class": SensorDeviceClass.DURATION,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "Time ON water pump2 for Unlock pump function"
    },
    49: {
        "name": "\"Type of operation of additional water pump (0=disable",
        "unit": "4=ON/OFF based on Room air temperature)"",
        "device_class": None,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "\"Type of operation of additional water pump (0=disable"
    },
    50: {
        "name": "Start temperature of Frost protection on Room air temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Start temperature of Frost protection on Room air temperature"
    },
    51: {
        "name": "Hysteresis of Room air temperature of Frost protection",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Hysteresis of Room air temperature of Frost protection"
    },
    52: {
        "name": "Water temperature of Frost protection",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Water temperature of Frost protection"
    },
    53: {
        "name": "Delay time OFF Main water pump from OFF Frost protection operation function",
        "unit": "1sec",
        "device_class": SensorDeviceClass.DURATION,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "Delay time OFF Main water pump from OFF Frost protection operation function"
    },
    54: {
        "name": "Start temperature of Frost protection on Outdoor air temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Start temperature of Frost protection on Outdoor air temperature"
    },
    55: {
        "name": "Hysteresis of Outdoor air temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Hysteresis of Outdoor air temperature"
    },
    56: {
        "name": "Backup heater set point during Frost protection",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": None,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Backup heater set point during Frost protection"
    },
    57: {
        "name": "Hysteresis of Outgoing water temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Hysteresis of Outgoing water temperature"
    },
    58: {
        "name": "Start temperature of Frost protection on DHW tank temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Start temperature of Frost protection on DHW tank temperature"
    },
    59: {
        "name": "Hysteresis of DHW tank temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Hysteresis of DHW tank temperature"
    },
    60: {
        "name": "Room relative humidity value",
        "unit": "1%",
        "device_class": None,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "Room relative humidity value"
    },
    61: {
        "name": "Room relative humidity value to start increasing Outgoing water temperature set point",
        "unit": "1%",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "Room relative humidity value to start increasing Outgoing water temperature set point"
    },
    62: {
        "name": "Max. Outgoing temperature hysteresis corresponding to 100% relative humidity",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Max. Outgoing temperature hysteresis corresponding to 100% relative humidity"
    },
    63: {
        "name": "Mixing valve runtime (from the fully closed to the fully open position)",
        "unit": "10sec",
        "device_class": SensorDeviceClass.DURATION,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "Mixing valve runtime (from the fully closed to the fully open position)"
    },
    64: {
        "name": "Mixing valve integral factor",
        "unit": None,
        "device_class": None,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "Mixing valve integral factor"
    },
    65: {
        "name": "Max Water temperature in mixing circuit",
        "unit": None,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "Max Water temperature in mixing circuit"
    },
    66: {
        "name": "3way valve change over time",
        "unit": "1sec",
        "device_class": SensorDeviceClass.DURATION,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "3way valve change over time"
    },
    67: {
        "name": "Flow switch alarm delay time at. Pump start up",
        "unit": None,
        "device_class": SensorDeviceClass.DURATION,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "Flow switch alarm delay time at. Pump start up"
    },
    68: {
        "name": "Flow switch alarm delay time in steady operation of the water pump",
        "unit": None,
        "device_class": SensorDeviceClass.DURATION,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "Flow switch alarm delay time in steady operation of the water pump"
    },
    69: {
        "name": "The number of retry until displaying alarm",
        "unit": None,
        "device_class": None,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "The number of retry until displaying alarm"
    },
    70: {
        "name": "The time of repeating retry until displaying alarm",
        "unit": None,
        "device_class": SensorDeviceClass.DURATION,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "The time of repeating retry until displaying alarm"
    },
    71: {
        "name": "\"Backup heater type of function (0=disable",
        "unit": "0",
        "device_class": None,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "\"Backup heater type of function (0=disable"
    },
    72: {
        "name": "Manual water set point",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": None,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Manual water set point"
    },
    73: {
        "name": "Manual water temperature hysteresis",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Manual water temperature hysteresis"
    },
    74: {
        "name": "Delay time of the heater OFF that avoid flow switch alarm",
        "unit": "1 sec",
        "device_class": SensorDeviceClass.DURATION,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "Delay time of the heater OFF that avoid flow switch alarm"
    },
    75: {
        "name": "Heater activation delay time",
        "unit": "1min",
        "device_class": SensorDeviceClass.DURATION,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "Heater activation delay time"
    },
    76: {
        "name": "Integration time for starting heaters",
        "unit": "0C*sec",
        "device_class": SensorDeviceClass.DURATION,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "Integration time for starting heaters"
    },
    77: {
        "name": "Outdoor air temperature to enable Backup heaters and disable compressor",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Outdoor air temperature to enable Backup heaters and disable compressor"
    },
    78: {
        "name": "Outdoor air temperature hysteresis to disable Backup heaters and enable compressor",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Outdoor air temperature hysteresis to disable Backup heaters and enable compressor"
    },
    79: {
        "name": "Outdoor air temperature to enable Backup heaters (Supplementary mode)",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Outdoor air temperature to enable Backup heaters (Supplementary mode)"
    },
    80: {
        "name": "Outdoor air temperature hysteresis to disable Backup heaters (Supplementary mode)",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Outdoor air temperature hysteresis to disable Backup heaters (Supplementary mode)"
    },
    81: {
        "name": "\"Freeze protection functions (0=disable",
        "unit": "0",
        "device_class": None,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "\"Freeze protection functions (0=disable"
    },
    82: {
        "name": "Outgoing water temperature set point during Start-up",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Outgoing water temperature set point during Start-up"
    },
    83: {
        "name": "Hysteresis water temperature set point during Start-up",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Hysteresis water temperature set point during Start-up"
    },
    84: {
        "name": "\"EHS type of function (0=disable",
        "unit": "0",
        "device_class": None,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "\"EHS type of function (0=disable"
    },
    85: {
        "name": "Outdoor air temperature to enable EHS and disable compressor",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Outdoor air temperature to enable EHS and disable compressor"
    },
    86: {
        "name": "Outdoor air temperature hysteresis to disable EHS and enable compressor",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Outdoor air temperature hysteresis to disable EHS and enable compressor"
    },
    87: {
        "name": "Outdoor air temperature to enable EHS (Supplementary mode)",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Outdoor air temperature to enable EHS (Supplementary mode)"
    },
    88: {
        "name": "Outdoor air temperature hysteresis to disable EHS (Supplementary mode)",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Outdoor air temperature hysteresis to disable EHS (Supplementary mode)"
    },
    89: {
        "name": "EHS activation delay time",
        "unit": "1min",
        "device_class": SensorDeviceClass.DURATION,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "EHS activation delay time"
    },
    90: {
        "name": "Integration time for starting EHS",
        "unit": "0C*sec",
        "device_class": SensorDeviceClass.DURATION,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "Integration time for starting EHS"
    },
    91: {
        "name": "\"Terminal 20-21 : ON/OFF remote contact or EHS Alarm input (0=disable (Remote controller only)",
        "unit": "0",
        "device_class": None,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "\"Terminal 20-21 : ON/OFF remote contact or EHS Alarm input (0=disable (Remote controller only)"
    },
    92: {
        "name": "\"Terminal 24-25 : Heating/Cooling mode remote contact (0=disable (Remote controller only)",
        "unit": "0",
        "device_class": None,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "\"Terminal 24-25 : Heating/Cooling mode remote contact (0=disable (Remote controller only)"
    },
    93: {
        "name": "\"Terminal 47 : Alarm (Configurable output) (0=disable",
        "unit": "0",
        "device_class": None,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "\"Terminal 47 : Alarm (Configurable output) (0=disable"
    },
    94: {
        "name": "\"Terminal 48 : Pump1 (0=disable",
        "unit": "1",
        "device_class": None,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "\"Terminal 48 : Pump1 (0=disable"
    },
    95: {
        "name": "\"Terminal 49 : Pump2 (0=disable",
        "unit": "1",
        "device_class": None,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "\"Terminal 49 : Pump2 (0=disable"
    },
    96: {
        "name": "Terminal 50-51-52 : DHW 3way valve (1=enable)",
        "unit": None,
        "device_class": None,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "Terminal 50-51-52 : DHW 3way valve (1=enable)"
    },
    97: {
        "name": "Room set point target Master C?",
        "unit": None,
        "device_class": None,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "Room set point target Master C?"
    },
    98: {
        "name": "Room set point target Slave C?",
        "unit": None,
        "device_class": None,
        "scale": 1,
        "offset": 0,
        "writable": True,
        "description": "Room set point target Slave C?"
    },
    99: {
        "name": "Buffer tank set point for Heating",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": None,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Buffer tank set point for Heating"
    },
    100: {
        "name": "Buffer tank set point for Cooling",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": None,
        "scale": 0.5,
        "offset": 0,
        "writable": True,
        "description": "Buffer tank set point for Cooling"
    },
}

# Coil Registers (Read/Write boolean controls)
COIL_REGISTER_MAP = {
    2: {
        "name": "\"Heating Zone1",
        "device_class": None,
        "description": "\"Heating Zone1"
    },
    3: {
        "name": "\"Heating Zone2",
        "device_class": None,
        "description": "\"Heating Zone2"
    },
    4: {
        "name": "\"Cooling Zone1",
        "device_class": None,
        "description": "\"Cooling Zone1"
    },
    5: {
        "name": "\"Cooling Zone2",
        "device_class": None,
        "description": "\"Cooling Zone2"
    },
    6: {
        "name": "\"Anti-legionella function (0=disable",
        "device_class": None,
        "description": "\"Anti-legionella function (0=disable"
    },
    7: {
        "name": "\"The HP unit turns ON/OFF based on (0=Room set point",
        "device_class": None,
        "description": "\"The HP unit turns ON/OFF based on (0=Room set point"
    },
    8: {
        "name": "Frost Protection based on Room Temperature",
        "device_class": None,
        "description": "Frost Protection based on Room Temperature"
    },
    13: {
        "name": "\"Compensation for room humidity (0=disable",
        "device_class": None,
        "description": "\"Compensation for room humidity (0=disable"
    },
    14: {
        "name": "\"Conditions to be available Backup heaters (0=always enabled",
        "device_class": None,
        "description": "\"Conditions to be available Backup heaters (0=always enabled"
    },
    16: {
        "name": "Terminal 1-2-3 : Remote Controller (1=enable)",
        "device_class": None,
        "description": "Terminal 1-2-3 : Remote Controller (1=enable)"
    },
    17: {
        "name": "\"Terminal 4-5-6 : 3way mixing valve (0=disable",
        "device_class": None,
        "description": "\"Terminal 4-5-6 : 3way mixing valve (0=disable"
    },
    18: {
        "name": "\"Terminal 7-8 : DHW tank temperature probe (0=disable",
        "device_class": None,
        "description": "\"Terminal 7-8 : DHW tank temperature probe (0=disable"
    },
    19: {
        "name": "\"Terminal 9-10 : Outdoor air temperature probe (additional) (0=disable",
        "device_class": None,
        "description": "\"Terminal 9-10 : Outdoor air temperature probe (additional) (0=disable"
    },
    20: {
        "name": "\"Terminal 11-12 : Buffer tank temperature probe (0=disable",
        "device_class": None,
        "description": "\"Terminal 11-12 : Buffer tank temperature probe (0=disable"
    },
    21: {
        "name": "\"Terminal 13-14 : Mix Water temperature probe (0=disable",
        "device_class": None,
        "description": "\"Terminal 13-14 : Mix Water temperature probe (0=disable"
    },
    22: {
        "name": "\"Terminal 15-16-32 : RS485 Mod Bus (0=disable",
        "device_class": None,
        "description": "\"Terminal 15-16-32 : RS485 Mod Bus (0=disable"
    },
    23: {
        "name": "\"Terminal 17-18 : Humidity sensor (0=disable",
        "device_class": None,
        "description": "\"Terminal 17-18 : Humidity sensor (0=disable"
    },
    24: {
        "name": "\"Terminal 19-18 : DHW remote contact (0=disable (Remote controller only)",
        "device_class": None,
        "description": "\"Terminal 19-18 : DHW remote contact (0=disable (Remote controller only)"
    },
    25: {
        "name": "\"Terminal 22-23 : Dual set point control (0=disable",
        "device_class": None,
        "description": "\"Terminal 22-23 : Dual set point control (0=disable"
    },
    26: {
        "name": "\"Terminal 26-27 : Flow switch (0=disable",
        "device_class": None,
        "description": "\"Terminal 26-27 : Flow switch (0=disable"
    },
    27: {
        "name": "\"Terminal 28-29 : Night mode (0=disable (Remote controller only)",
        "device_class": None,
        "description": "\"Terminal 28-29 : Night mode (0=disable (Remote controller only)"
    },
    28: {
        "name": "\"Terminal 30-31 : Low tariff (0=disable (Remote controller only)",
        "device_class": None,
        "description": "\"Terminal 30-31 : Low tariff (0=disable (Remote controller only)"
    },
    29: {
        "name": "\"Terminal 41-42 : EHS (External heat source for space heating) (0=disable",
        "device_class": None,
        "description": "\"Terminal 41-42 : EHS (External heat source for space heating) (0=disable"
    },
    30: {
        "name": "\"Terminal 43-44 : Heating/Cooling mode output (0=disable",
        "device_class": None,
        "description": "\"Terminal 43-44 : Heating/Cooling mode output (0=disable"
    },
    31: {
        "name": "\"Terminal 45 : Dehumidifier (0=disable",
        "device_class": None,
        "description": "\"Terminal 45 : Dehumidifier (0=disable"
    },
    32: {
        "name": "\"Terminal 46 : DHW Electric heater or Backup heater (0=DHW Electric heater",
        "device_class": None,
        "description": "\"Terminal 46 : DHW Electric heater or Backup heater (0=DHW Electric heater"
    },
}

# Installation Templates
INSTALLATION_TEMPLATES = {
    "single_zone": {
        "name": "Single Zone Heating",
        "description": "Most common setup with one heating zone",
        "percentage": "65%",
        "enabled_registers": {
            "input": list(range(0, 33)),
            "holding": [2, 3, 4, 5, 6],
            "coil": [1, 2, 6]
        }
    },
    "dual_zone": {
        "name": "Dual Zone Heating",
        "description": "Upstairs/downstairs or separate zones", 
        "percentage": "20%",
        "enabled_registers": {
            "input": list(range(0, 33)),
            "holding": [2, 3, 4, 5, 6, 7, 8],
            "coil": [1, 2, 3, 6]
        }
    },
    "dhw_only": {
        "name": "Hot Water Only",
        "description": "Cylinder heating only",
        "percentage": "8%",
        "enabled_registers": {
            "input": [0, 1, 2, 3, 6, 11, 21, 22, 26],
            "holding": [],
            "coil": [1, 6]
        }
    },
    "replacement": {
        "name": "Boiler Replacement", 
        "description": "Full system replacement",
        "percentage": "5%",
        "enabled_registers": {
            "input": list(range(0, 33)),
            "holding": list(range(2, 20)),
            "coil": list(range(1, 10))
        }
    },
    "custom": {
        "name": "Custom Configuration",
        "description": "Advanced users - all registers",
        "percentage": "2%",
        "enabled_registers": {
            "input": list(range(0, 33)),
            "holding": list(range(2, 100)),
            "coil": list(range(1, 44))
        }
    }
}
