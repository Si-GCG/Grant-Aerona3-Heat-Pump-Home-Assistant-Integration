
# This is currently in beta
# Unofficial Grant Aerona3 Heat Pump Home Assistant Integration

A comprehensive Home Assistant custom integration for controlling and monitoring Grant Aerona3 Air Source Heat Pumps via Modbus communication.

## Features

### 🌡️ Climate Control
- **Dual Zone Support**: Independent control for Zone 1 and Zone 2
- **Temperature Setpoints**: Adjustable flow temperature setpoints
- **Weather Compensation**: Enable/disable weather compensation per zone
- **HVAC Mode Control**: Heat, Cool, and Off modes

### 📊 Comprehensive Monitoring
- **Temperature Sensors**: Outdoor, flow, return, discharge, suction, defrost, DHW tank, and buffer tank temperatures
- **Performance Metrics**: Power consumption, COP calculation, compressor frequency
- **System Status**: Compressor, pump, and fan operation status
- **Energy Tracking**: Total energy consumption monitoring

### 🔧 Advanced Controls
- **Protection Systems**: Frost protection controls for room, outdoor, and water
- **Anti-Legionella**: Configurable anti-legionella function
- **Control Modes**: Switch between room and water setpoint control
- **DHW Management**: Domestic hot water mode monitoring

### 🎨 Beautiful Dashboard
- **Modern UI**: Clean, responsive Lovelace dashboard
- **Real-time Charts**: Temperature trends and performance monitoring
- **Quick Controls**: Easy access to common settings
- **Status Indicators**: Visual system status with color coding

## Hardware Requirements

### Modbus Communication
- **Waveshare RS485 to Ethernet Converter** (recommended)
  - Model: RS232/485/422 to POE ETH (B)
  - IP: 192.168.1.200 (default)
  - Port: 502
- **Alternative**: USB to RS485 converter
- **Wiring**: Connect to Grant Aerona3 Modbus terminals
  - RS485+ (orange) → Pin 5
  - RS485- (orange/white) → Pin 4
  - GND → Pin 8

### Heat Pump Configuration
- **Modbus Settings**: 19200 bps, 8 data bits, no parity, 2 stop bits
- **Slave Address**: 1 (default)
- **Enable Modbus**: Ensure Modbus is enabled in service menu

## Installation

### 1. Install the Custom Integration

#### Method 1: HACS (Recommended)
1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots menu → "Custom repositories"
4. Add repository URL: `https://github.com/Si-GCG/Grant-Aerona3-modbus`
5. Category: "Integration"
6. Click "Add"
7. Find "Grant Aerona3 Heat Pump" and install
8. Restart Home Assistant

#### Method 2: Manual Installation
1. Download the `custom_components/grant_aerona3` folder
2. Copy to your Home Assistant `custom_components` directory
3. Restart Home Assistant

### 2. Configure the Integration

1. Go to **Settings** → **Devices & Services**
2. Click **"+ Add Integration"**
3. Search for **"Grant Aerona3 Heat Pump"**
4. Enter your configuration:
   - **Host**: IP address of your Modbus converter (e.g., 192.168.1.200)
   - **Port**: 502 (default)
   - **Slave ID**: 1 (default)
   - **Scan Interval**: 30 seconds (recommended)
5. Click **"Submit"**

### 3. Install Required HACS Frontend Components

For the dashboard to work properly, install these HACS frontend components:

```yaml
# Required HACS Frontend Components
- mushroom          # Modern card designs
- apexcharts-card   # Advanced charting
- mini-graph-card   # Compact graphs
- card-mod          # Card styling
- energy-flow-card-plus  # Energy flow visualization
```

### 4. Add Helper Entities

Add this to your `configuration.yaml`:

```yaml
input_boolean:
  show_ashp_setpoints:
    name: Show ASHP Setpoints
    initial: false
    icon: mdi:tune
```

## Dashboard Setup

### Option 1: Complete Dashboard
Copy the contents of `lovelace_dashboard.yaml` to create a dedicated heat pump dashboard:

1. Go to **Settings** → **Dashboards**
2. Click **"+ Add Dashboard"**
3. Choose **"New dashboard from scratch"**
4. Name it "Grant Aerona3 Heat Pump"
5. Switch to **YAML mode**
6. Paste the contents of `lovelace_dashboard.yaml`
7. Save

### Option 2: Single Card
Add the enhanced card to an existing dashboard:

1. Edit your dashboard
2. Add a new card
3. Choose **"Manual"** card type
4. Paste the contents of `enhanced_ashp_card.yaml`
5. Save

## Configuration Examples

### Basic Modbus Configuration
```yaml
# This is handled automatically by the integration
# No manual modbus configuration needed
```

### Energy Dashboard Integration
```yaml
# Add to configuration.yaml for energy dashboard
sensor:
  - platform: integration
    source: sensor.grant_aerona3_power_consumption
    name: grant_aerona3_energy_kwh
    unit_prefix: k
    round: 2
    method: trapezoidal

utility_meter:
  grant_aerona3_daily_energy:
    source: sensor.grant_aerona3_energy_kwh
    cycle: daily
  grant_aerona3_monthly_energy:
    source: sensor.grant_aerona3_energy_kwh
    cycle: monthly
```

### Automation Examples

#### Frost Protection
```yaml
automation:
  - alias: "ASHP Frost Protection"
    trigger:
      - platform: numeric_state
        entity_id: sensor.grant_aerona3_outdoor_air_temperature
        below: 0
    action:
      - service: switch.turn_on
        entity_id: switch.grant_aerona3_frost_protection_outdoor
```

#### Energy Efficiency Alert
```yaml
automation:
  - alias: "ASHP Low COP Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.grant_aerona3_cop
        below: 2.0
        for:
          minutes: 30
    action:
      - service: notify.mobile_app_your_phone
        data:
          message: "Heat pump COP is low ({{ states('sensor.grant_aerona3_cop') }}). Check system."
```

#### Weather Compensation Auto-Enable
```yaml
automation:
  - alias: "Enable Weather Compensation in Winter"
    trigger:
      - platform: numeric_state
        entity_id: sensor.grant_aerona3_outdoor_air_temperature
        below: 10
    action:
      - service: switch.turn_on
        entity_id: 
          - switch.grant_aerona3_zone_1_weather_compensation
          - switch.grant_aerona3_zone_2_weather_compensation
```

## Available Entities

### Climate Entities
- `climate.grant_aerona3_zone_1` - Zone 1 climate control
- `climate.grant_aerona3_zone_2` - Zone 2 climate control

### Temperature Sensors
- `sensor.grant_aerona3_outdoor_air_temperature`
- `sensor.grant_aerona3_outgoing_water_temperature`
- `sensor.grant_aerona3_return_water_temperature`
- `sensor.grant_aerona3_discharge_temperature`
- `sensor.grant_aerona3_suction_temperature`
- `sensor.grant_aerona3_defrost_temperature`
- `sensor.grant_aerona3_dhw_tank_temperature`
- `sensor.grant_aerona3_buffer_tank_temperature`

### Performance Sensors
- `sensor.grant_aerona3_power_consumption`
- `sensor.grant_aerona3_energy_consumption`
- `sensor.grant_aerona3_cop`
- `sensor.grant_aerona3_compressor_frequency`
- `sensor.grant_aerona3_fan_speed`
- `sensor.grant_aerona3_water_pump_speed`

### Status Sensors
- `binary_sensor.grant_aerona3_compressor_running`
- `binary_sensor.grant_aerona3_water_pump_running`
- `binary_sensor.grant_aerona3_fan_running`
- `binary_sensor.grant_aerona3_heating_active`
- `binary_sensor.grant_aerona3_cooling_active`
- `binary_sensor.grant_aerona3_dhw_active`
- `binary_sensor.grant_aerona3_defrost_active`

### Control Switches
- `switch.grant_aerona3_zone_1_weather_compensation`
- `switch.grant_aerona3_zone_2_weather_compensation`
- `switch.grant_aerona3_anti_legionella_function`
- `switch.grant_aerona3_control_mode`
- `switch.grant_aerona3_frost_protection_room`
- `switch.grant_aerona3_frost_protection_outdoor`
- `switch.grant_aerona3_frost_protection_water`

### Temperature Setpoints
- `number.grant_aerona3_zone_1_fixed_flow_temperature`
- `number.grant_aerona3_zone_1_max_flow_temperature`
- `number.grant_aerona3_zone_1_min_flow_temperature`
- `number.grant_aerona3_zone_2_fixed_flow_temperature`
- `number.grant_aerona3_zone_2_max_flow_temperature`
- `number.grant_aerona3_zone_2_min_flow_temperature`

## Troubleshooting

### Connection Issues
1. **Check Network Connectivity**: Ensure Home Assistant can reach the Modbus converter IP
2. **Verify Modbus Settings**: Confirm baud rate, parity, and stop bits match heat pump settings
3. **Check Wiring**: Verify RS485 connections are correct and secure
4. **Test with Modbus Tool**: Use `mbpoll` or similar to test basic connectivity

### Entity Not Updating
1. **Check Scan Interval**: Increase if network is slow
2. **Review Logs**: Check Home Assistant logs for Modbus errors
3. **Restart Integration**: Reload the integration from Devices & Services

### Dashboard Issues
1. **Install HACS Components**: Ensure all required frontend components are installed
2. **Clear Browser Cache**: Force refresh the dashboard
3. **Check Entity Names**: Verify entity IDs match your configuration

## Support and Contributing

### Getting Help
- **GitHub Issues**: Report bugs and request features
- **Home Assistant Community**: Ask questions in the forum
- **Documentation**: Check this README and inline code comments

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Credits and Acknowledgments

This integration builds upon the excellent work of:
- **Si-GCG**: Original Grant Aerona3 Modbus research and implementation
- **aerona-chofu-ashp**: Community Modbus mapping project
- **Renewable Heating Hub**: Community support and documentation
- **Open Energy Monitor**: Technical guidance and tools

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This integration is not officially supported by Grant Engineering. Use at your own risk. Always ensure proper safety measures when working with heating systems.
