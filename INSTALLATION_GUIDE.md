# Grant Aerona3 Heat Pump Integration - Installation Guide

## Quick Start Checklist

- [ ] Hardware setup complete (Modbus converter connected)
- [ ] Home Assistant custom integration installed
- [ ] HACS frontend components installed
- [ ] Integration configured and entities created
- [ ] Dashboard imported and working
- [ ] Helper entities added
- [ ] Automations configured (optional)

## Step-by-Step Installation

### 1. Hardware Setup

#### Required Hardware
- **Waveshare RS485 to Ethernet Converter** (POE version recommended)
- **Shielded CAT7 cable** (for outdoor run to heat pump)
- **DIN rail enclosure** (for Modbus converter protection)

#### Wiring Configuration
```
Grant Aerona3 RJ45 Connection:
Pin 4: RS485- (Orange/White)
Pin 5: RS485+ (Orange)
Pin 8: GND (Ground)

Waveshare Converter Settings:
- Device Port: 502
- Work Mode: TCP Server
- IP Mode: Static (192.168.1.200)
- Baud Rate: 19200
- Data Bits: 8
- Parity: None
- Stop Bits: 2
- Protocol: Modbus TCP to RTU
```

#### Heat Pump Configuration
Access the service menu on your Grant Aerona3 and verify:
- Modbus is enabled
- Address: 1
- Baud rate: 19200
- Parity: None
- Stop bits: 2

### 2. Home Assistant Integration Setup

#### Install via HACS (Recommended)
```bash
# 1. Open HACS → Integrations
# 2. Three dots menu → Custom repositories
# 3. Add: https://github.com/Si-GCG/Grant-Aerona3-modbus
# 4. Category: Integration
# 5. Install "Grant Aerona3 Heat Pump"
# 6. Restart Home Assistant
```

#### Manual Installation
```bash
# Copy the custom_components folder to your HA config directory
cp -r custom_components/grant_aerona3 /config/custom_components/
```

### 3. Configure Integration

1. **Add Integration**:
   - Settings → Devices & Services
   - Add Integration → "Grant Aerona3 Heat Pump"

2. **Configuration Parameters**:
   ```yaml
   Host: 192.168.1.200        # Your Modbus converter IP
   Port: 502                  # Standard Modbus TCP port
   Slave ID: 1               # Heat pump Modbus address
   Scan Interval: 30         # Update frequency (seconds)
   ```

3. **Verify Connection**:
   - Check that entities are created
   - Verify data is updating
   - Test a simple control (like a switch)

### 4. Install Required Frontend Components

Install these HACS frontend components for the dashboard:

```yaml
Required Components:
- mushroom                 # Modern card designs
- apexcharts-card         # Advanced charts
- mini-graph-card         # Compact graphs  
- card-mod                # Card styling
- energy-flow-card-plus   # Energy visualization
```

Installation steps for each:
1. HACS → Frontend
2. Search for component name
3. Install
4. Add to Lovelace resources (if not automatic)

### 5. Add Helper Entities

Add to `configuration.yaml`:

```yaml
input_boolean:
  show_ashp_setpoints:
    name: Show ASHP Setpoints
    initial: false
    icon: mdi:tune

# Optional: Energy tracking helpers
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
  grant_aerona3_yearly_energy:
    source: sensor.grant_aerona3_energy_kwh
    cycle: yearly
```

### 6. Import Dashboard

#### Option A: Complete Dashboard
1. Settings → Dashboards → Add Dashboard
2. "New dashboard from scratch"
3. Name: "Grant Aerona3 Heat Pump"
4. Switch to YAML mode
5. Copy contents from `lovelace_dashboard.yaml`
6. Save

#### Option B: Single Card
1. Edit existing dashboard
2. Add card → Manual
3. Copy contents from `enhanced_ashp_card.yaml`
4. Save

### 7. Test Everything

#### Basic Functionality Test
- [ ] Temperature sensors showing values
- [ ] Climate entities responding to setpoint changes
- [ ] Switches toggling correctly
- [ ] Charts displaying data
- [ ] No error messages in logs

#### Advanced Testing
```yaml
# Test automation (temporary)
automation:
  - alias: "Test ASHP Control"
    trigger:
      - platform: state
        entity_id: input_boolean.test_ashp
        to: 'on'
    action:
      - service: number.set_value
        entity_id: number.grant_aerona3_zone_1_fixed_flow_temperature
        data:
          value: 45
      - delay: '00:00:05'
      - service: switch.toggle
        entity_id: switch.grant_aerona3_zone_1_weather_compensation
```

## Troubleshooting Common Issues

### Connection Problems

#### "Cannot connect to Modbus device"
```bash
# Test network connectivity
ping 192.168.1.200

# Test Modbus connection with mbpoll
mbpoll -t3 -r0 -c10 192.168.1.200

# Check Waveshare settings via web interface
# Navigate to http://192.168.1.200
```

#### "No data from heat pump"
1. Verify heat pump Modbus is enabled
2. Check wiring connections
3. Confirm Modbus settings match
4. Test with different scan interval

### Entity Issues

#### "Entities not created"
1. Check integration logs for errors
2. Verify Modbus communication
3. Restart integration
4. Check entity registry

#### "Values not updating"
1. Increase scan interval
2. Check network stability
3. Verify heat pump is responding
4. Review Home Assistant logs

### Dashboard Problems

#### "Cards not displaying correctly"
1. Install missing HACS components
2. Clear browser cache
3. Check for JavaScript errors
4. Verify entity names match

#### "Charts not working"
1. Ensure ApexCharts is installed
2. Check entity history is available
3. Verify time zone settings
4. Test with simple entities first

## Performance Optimization

### Network Optimization
```yaml
# Adjust scan interval based on network performance
# Fast network: 15-30 seconds
# Slow network: 60-120 seconds
scan_interval: 30
```

### Memory Usage
```yaml
# Limit history for high-frequency sensors
recorder:
  include:
    entities:
      - sensor.grant_aerona3_outdoor_air_temperature
      - sensor.grant_aerona3_power_consumption
  exclude:
    entities:
      - sensor.grant_aerona3_compressor_frequency  # High frequency
```

### Database Optimization
```yaml
# Configure retention for energy data
recorder:
  purge_keep_days: 365
  auto_purge: true
  commit_interval: 30
```

## Security Considerations

### Network Security
- Use VLAN isolation for IoT devices
- Configure firewall rules
- Regular firmware updates for Modbus converter
- Monitor for unusual network activity

### Home Assistant Security
- Regular backups of configuration
- Secure access to HA instance
- Monitor integration logs
- Keep integrations updated

## Maintenance

### Regular Tasks
- [ ] Check Modbus connection monthly
- [ ] Review error logs weekly
- [ ] Update integration when available
- [ ] Backup configuration before changes
- [ ] Monitor energy consumption trends

### Seasonal Adjustments
```yaml
# Winter optimization
automation:
  - alias: "Winter ASHP Settings"
    trigger:
      - platform: numeric_state
        entity_id: sensor.outdoor_temperature
        below: 5
    action:
      - service: switch.turn_on
        entity_id: switch.grant_aerona3_frost_protection_outdoor

# Summer optimization  
automation:
  - alias: "Summer ASHP Settings"
    trigger:
      - platform: numeric_state
        entity_id: sensor.outdoor_temperature
        above: 20
    action:
      - service: switch.turn_off
        entity_id: switch.grant_aerona3_frost_protection_outdoor
```

## Getting Help

### Log Collection
```bash
# Enable debug logging
logger:
  default: info
  logs:
    custom_components.grant_aerona3: debug
    pymodbus: debug

# Collect logs
grep "grant_aerona3\|modbus" home-assistant.log > ashp_debug.log
```

### Support Channels
1. **GitHub Issues**: Bug reports and feature requests
2. **Home Assistant Community**: General questions
3. **Renewable Heating Hub**: Heat pump specific discussions
4. **Documentation**: This guide and code comments

### Before Asking for Help
- [ ] Check this troubleshooting guide
- [ ] Review Home Assistant logs
- [ ] Test basic Modbus connectivity
- [ ] Verify hardware connections
- [ ] Include relevant log excerpts in support requests

## Next Steps

After successful installation:
1. **Explore Automations**: Set up efficiency monitoring
2. **Energy Dashboard**: Add to HA energy dashboard
3. **Mobile Access**: Configure HA mobile app
4. **Backup Strategy**: Regular configuration backups
5. **Community**: Share your experience and improvements

---

**Need help?** Check the main README.md for detailed entity documentation and advanced configuration options.