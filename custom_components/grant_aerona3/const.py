"""Constants for the Grant Aerona3 Heat Pump integration."""

DOMAIN = "grant_aerona3"

# Configuration keys
CONF_HOST = "host"
CONF_PORT = "port"
CONF_SLAVE_ID = "slave_id"
CONF_SCAN_INTERVAL = "scan_interval"

# Default values
DEFAULT_PORT = 502
DEFAULT_SLAVE_ID = 1
DEFAULT_SCAN_INTERVAL = 30

# Device information
MANUFACTURER = "Grant Engineering"
MODEL = "Aerona3"

# Register types
INPUT_REGISTERS = "input"
HOLDING_REGISTERS = "holding"
COIL_REGISTERS = "coil"

# Input register addresses and their properties
INPUT_REGISTER_MAP = {
    0: {"name": "Return Water Temperature", "unit": "°C", "scale": 1.0, "device_class": "temperature"},
    1: {"name": "Compressor Frequency", "unit": "Hz", "scale": 1.0, "device_class": "frequency"},
    2: {"name": "Discharge Temperature", "unit": "°C", "scale": 1.0, "device_class": "temperature"},
    3: {"name": "Current Power Consumption", "unit": "W", "scale": 100.0, "device_class": "power"},
    4: {"name": "Fan Speed", "unit": "rpm", "scale": 10.0, "device_class": None},
    5: {"name": "Defrost Temperature", "unit": "°C", "scale": 1.0, "device_class": "temperature"},
    6: {"name": "Outdoor Air Temperature", "unit": "°C", "scale": 1.0, "device_class": "temperature"},
    7: {"name": "Water Pump Speed", "unit": "rpm", "scale": 100.0, "device_class": None},
    8: {"name": "Suction Temperature", "unit": "°C", "scale": 1.0, "device_class": "temperature"},
    9: {"name": "Outgoing Water Temperature", "unit": "°C", "scale": 1.0, "device_class": "temperature"},
    10: {"name": "Operating Mode", "unit": None, "scale": 1.0, "device_class": None},
    11: {"name": "Zone 1 Set Temperature", "unit": "°C", "scale": 0.1, "device_class": "temperature"},
    12: {"name": "Zone 2 Set Temperature", "unit": "°C", "scale": 0.1, "device_class": "temperature"},
    13: {"name": "DHW Operating Mode", "unit": None, "scale": 1.0, "device_class": None},
    14: {"name": "Day of Week", "unit": None, "scale": 1.0, "device_class": None},
    15: {"name": "Clock", "unit": None, "scale": 1.0, "device_class": None},
    16: {"name": "DHW Tank Temperature", "unit": "°C", "scale": 0.1, "device_class": "temperature"},
    17: {"name": "External Outdoor Temperature", "unit": "°C", "scale": 0.1, "device_class": "temperature"},
    18: {"name": "Buffer Tank Temperature", "unit": "°C", "scale": 0.1, "device_class": "temperature"},
}

# Holding register addresses for temperature setpoints
HOLDING_REGISTER_MAP = {
    2: {"name": "Zone 1 Fixed Flow Temperature", "unit": "°C", "scale": 0.1, "min": 23, "max": 60},
    3: {"name": "Zone 1 Max Flow Temperature", "unit": "°C", "scale": 0.1, "min": 23, "max": 60},
    4: {"name": "Zone 1 Min Flow Temperature", "unit": "°C", "scale": 0.1, "min": 23, "max": 60},
    7: {"name": "Zone 2 Fixed Flow Temperature", "unit": "°C", "scale": 0.1, "min": 23, "max": 60},
    8: {"name": "Zone 2 Max Flow Temperature", "unit": "°C", "scale": 0.1, "min": 23, "max": 60},
    9: {"name": "Zone 2 Min Flow Temperature", "unit": "°C", "scale": 0.1, "min": 23, "max": 60},
}

# Coil register addresses for switches
COIL_REGISTER_MAP = {
    2: {"name": "Zone 1 Weather Compensation", "description": "Enable weather compensation for Zone 1"},
    3: {"name": "Zone 2 Weather Compensation", "description": "Enable weather compensation for Zone 2"},
    4: {"name": "Zone 1 Cooling Weather Compensation", "description": "Enable cooling weather compensation for Zone 1"},
    5: {"name": "Zone 2 Cooling Weather Compensation", "description": "Enable cooling weather compensation for Zone 2"},
    6: {"name": "Anti-Legionella Function", "description": "Enable anti-legionella function"},
    7: {"name": "Control Mode", "description": "HP control mode (0=Room setpoint, 1=Water setpoint)"},
    8: {"name": "Frost Protection Room", "description": "Frost protection based on room temperature"},
    9: {"name": "Frost Protection Outdoor", "description": "Frost protection based on outdoor temperature"},
    10: {"name": "Frost Protection Water", "description": "Frost protection based on water temperature"},
    11: {"name": "DHW Frost Protection", "description": "DHW storage frost protection"},
}

# Operating modes
OPERATING_MODES = {
    0: "Off",
    1: "Heating",
    2: "Cooling"
}

# DHW operating modes
DHW_MODES = {
    0: "Disabled",
    1: "Comfort",
    2: "Economy",
    3: "Force"
}

# Days of week
DAYS_OF_WEEK = {
    0: "Monday",
    1: "Tuesday", 
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday"
}
