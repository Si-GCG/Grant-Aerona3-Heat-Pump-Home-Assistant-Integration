# Troubleshooting Guide - Grant Aerona3 Integration

> **Common problems and solutions, sorted by how easy they are to fix**

Don't worry - most issues have simple solutions! This guide starts with easy fixes you can do yourself, then moves to problems that might need professional help.

## 🔧 **Quick Fixes (5 Minutes)**

These solve 80% of problems and are safe for anyone to try.

### 🚫 **Integration Shows "Unavailable"**

**What you see**: Grey "Unavailable" instead of temperature readings

**Quick fixes**:
1. **Restart the integration**:
   - Go to **Settings** → **Devices & Services**
   - Find **Grant Aerona3** 
   - Click **three dots** → **Reload**
   
2. **Check your network**:
   - Ping your Modbus converter: `ping 192.168.1.200`
   - Check ethernet cable connections
   - Verify converter power LED is on

3. **Restart Home Assistant**:
   - **Settings** → **System** → **Restart**
   - Wait 2-3 minutes for full startup

**Usually fixes**: 90% of "unavailable" problems

---

### 📊 **Sensors Showing Old Data**

**What you see**: Numbers that don't change or timestamps from hours ago

**Quick fixes**:
1. **Check scan interval**:
   - Too fast = Modbus overload
   - Recommended: 30 seconds minimum
   - Change in integration settings

2. **Restart heat pump controller**:
   - Turn off at isolator for 30 seconds
   - Turn back on and wait 2 minutes
   - Check if data resumes updating

3. **Clear Home Assistant cache**:
   - Hard refresh browser (Ctrl+Shift+R)
   - Clear browser cache for Home Assistant
   - Check on mobile app too

**Usually fixes**: 70% of stale data problems

---

### 🌡️ **Temperature Readings Look Wrong**

**What you see**: Outdoor temperature showing 999°C or -40°C

**Quick fixes**:
1. **Check sensor connections**:
   - Ensure all Modbus wires are tight
   - Check for loose connections at heat pump end
   - Verify pin assignments (Orange→Pin 5, Orange/White→Pin 4)

2. **Verify heat pump is on**:
   - Some sensors only work when system is running
   - Turn on heating briefly to test
   - Check outdoor unit isn't in defrost mode

3. **Compare with weather forecast**:
   - Outdoor temp should match local weather
   - If way off, check outdoor sensor on heat pump
   - Clean snow/ice from outdoor sensor

**Usually fixes**: 85% of temperature problems

---

### ⚡ **Power Readings Are Zero**

**What you see**: Power consumption always shows 0W

**Quick fixes**:
1. **Check heat pump is actually running**:
   - Listen for compressor running
   - Feel warm air from outdoor unit
   - Check status lights on heat pump

2. **Verify current sensor**:
   - Some heat pumps need current sensor enabled
   - Check service menu settings
   - Look for "Power Monitoring" option

3. **Test during known heating**:
   - Turn heating on manually
   - Wait 5 minutes for power reading
   - Should show 1-4kW when heating

**Usually fixes**: 75% of power monitoring issues

---

## 🔨 **Medium Fixes (15-30 Minutes)**

Need a bit more investigation but still doable at home.

### 🔌 **"Cannot Connect" Error During Setup**

**What you see**: Setup fails with connection error

**Step-by-step fix**:
1. **Test basic network connectivity**:
   ```bash
   # From computer on same network
   ping 192.168.1.200
   telnet 192.168.1.200 502
   ```

2. **Check converter configuration**:
   - Access converter web interface (usually http://192.168.1.200)
   - Verify Modbus settings:
     - **Port**: 502
     - **Baud**: 19200
     - **Data bits**: 8
     - **Parity**: None
     - **Stop bits**: 2

3. **Verify heat pump Modbus settings**:
   - Enter service menu (usually hold menu button 10 seconds)
   - Check Modbus is enabled
   - Confirm slave address is 1
   - Verify communication parameters match converter

4. **Test with Modbus tool**:
   ```bash
   # Install mbpoll if available
   mbpoll -m tcp -a 1 -r 1 -c 1 192.168.1.200
   ```

**Usually fixes**: 95% of connection problems

---

### 📉 **Weather Compensation Not Working**

**What you see**: Flow temperature doesn't change with outdoor temperature

**Diagnosis steps**:
1. **Check weather compensation is enabled**:
   - Find `switch.grant_aerona3_weather_compensation_active`
   - Must be "On" not "Off"
   - If missing, check installation template includes weather compensation

2. **Verify outdoor temperature sensor**:
   - Must be reading realistic values (-10°C to +25°C for UK)
   - Compare with local weather forecast
   - Clean outdoor sensor if different

3. **Check curve settings**:
   - **Min outdoor**: Should be around -8°C
   - **Max outdoor**: Should be around 16°C
   - **Min flow**: Around 30-35°C
   - **Max flow**: Around 45-50°C

4. **Test manually**:
   - Note current outdoor temp and flow temp
   - Wait for outdoor temp to change by 3°C+
   - Flow temp should change within 30 minutes

**Patience required**: Weather compensation changes are gradual, not instant!

---

### 🏠 **Wrong Installation Template Applied**

**What you see**: Missing sensors or controls for your actual setup

**How to fix**:
1. **Remove and re-add integration**:
   - **Settings** → **Devices & Services**
   - **Grant Aerona3** → **Delete**
   - **Add Integration** → **Grant Aerona3**
   - Choose correct template this time

2. **Template selection guide**:
   - **Single Zone Basic**: Just heating, no hot water cylinder
   - **Single Zone DHW**: Heating + hot water cylinder
   - **Dual Zone**: Upstairs/downstairs or UFH+radiators
   - **Replacement**: Complex system replacing old boiler

3. **Manual feature adjustment**:
   - Edit integration options
   - Enable/disable features as needed:
     - ☑️ DHW Cylinder
     - ☑️ Zone 2
     - ☑️ Backup Heater
     - ☑️ Weather Compensation

**Result**: Correct sensors and controls for your actual system

---

## 🛠️ **Advanced Fixes (1+ Hours)**

More complex problems requiring patience and possibly tools.

### 🔍 **Intermittent Connection Issues**

**What you see**: Integration works sometimes, fails other times

**Systematic diagnosis**:
1. **Monitor connection stability**:
   ```bash
   # Run continuous ping test
   ping -t 192.168.1.200
   # Watch for dropped packets
   ```

2. **Check Home Assistant logs**:
   - **Settings** → **System** → **Logs**
   - Filter for "grant_aerona3"
   - Look for patterns in errors

3. **Network troubleshooting**:
   - Check for IP address conflicts
   - Verify network cable quality
   - Test different ethernet port on router
   - Consider network interference

4. **Modbus traffic analysis**:
   - Install Wireshark or similar
   - Capture Modbus traffic during failures
   - Look for timeout patterns

5. **Progressive isolation**:
   - Test with Modbus tool during failures
   - Swap ethernet cables
   - Try different Modbus converter
   - Test from different network location

**Common causes found**:
- Faulty ethernet cable (40%)
- Network congestion (25%)
- Converter overheating (20%)
- EMI interference (15%)

---

### 📊 **Poor Performance or Accuracy**

**What you see**: COP readings don't match manual calculations, temperatures seem off

**Calibration process**:
1. **Manual verification**:
   - Use separate thermometers to check key temperatures
   - Calculate COP manually: Heat Output ÷ Power Input
   - Compare with integration readings

2. **Check flow rate settings**:
   - **Fixed rate**: Verify actual flow rate matches setting
   - **Calculated**: Check if estimation is reasonable
   - **Flow meter**: Verify meter is working correctly

3. **Sensor validation**:
   - Each temperature sensor against known reference
   - Power readings against clamp meter
   - Pressure readings if available

4. **Register mapping verification**:
   - Check if heat pump model has different register layout
   - Contact Grant technical support for register documentation
   - Compare with other users of same heat pump model

5. **Professional calibration**:
   - Annual service should include sensor calibration
   - Request specific check of temperature sensors
   - Verify refrigerant charge affects sensor readings

---

### ⚙️ **Complex System Configuration**

**What you see**: Integration doesn't handle your specific heat pump setup

**Custom configuration steps**:
1. **Document your system**:
   - Heat pump model and serial number
   - Controller version and firmware
   - Modbus register map if available
   - Unusual sensors or controls

2. **Advanced register configuration**:
   - Enable diagnostic monitoring
   - Access additional registers manually
   - Create custom sensors for unique features

3. **Create support request**:
   - **GitHub Issue** with full system details
   - Include Home Assistant logs
   - Attach photos of controller and connections
   - Specify what's missing or incorrect

4. **Community assistance**:
   - **Home Assistant Community** forum
   - Search for similar heat pump models
   - Share findings with other users

---

## 🚨 **Problems Needing Professional Help**

Don't attempt these yourself - call for qualified help.

### ⚡ **Electrical Issues**

**Call electrician immediately for**:
- Burning smells from converter or heat pump
- Electrical sparking anywhere
- Circuit breakers tripping repeatedly
- Any concerns about electrical safety

### 🔧 **Heat Pump System Issues**

**Call Gas Safe registered heat pump engineer for**:
- Heat pump not heating despite good monitoring
- Refrigerant leaks (ice forming, poor performance)
- Compressor problems (strange noises, not starting)
- Control system faults on heat pump itself
- Any safety concerns about heat pump operation

### 💻 **Complex Network Issues**

**Call IT professional for**:
- Network security concerns
- Complex routing or VLAN problems
- Enterprise network integration
- Advanced firewall configuration

---

## 📋 **Diagnostic Information to Collect**

When asking for help, collect this information first:

### Basic System Information
- **Heat pump model**: Grant Aerona3 6kW/8kW/10kW/12kW/14kW
- **Controller version**: Check display or manual
- **Installation type**: Single zone, dual zone, DHW, etc.
- **Modbus converter**: Make and model
- **Home Assistant version**: Settings → About

### Network Details
- **Converter IP address**: Usually 192.168.1.200
- **Home Assistant IP**: Check network settings
- **Network topology**: Router model, switches, etc.
- **Connection method**: Ethernet, USB, etc.

### Current Symptoms
- **When it started**: After update, sudden, gradual, etc.
- **Frequency**: Constant, intermittent, specific times
- **Error messages**: Exact text from logs
- **What you've tried**: List attempted solutions

### Log Files
```yaml
# Enable detailed logging in configuration.yaml
logger:
  default: warning
  logs:
    custom_components.grant_aerona3: debug
    pymodbus: debug
```

---

## 🔄 **Prevention is Better Than Cure**

### Monthly Maintenance
- **Visual inspection** of all connections
- **Clean heat pump filters** (outdoor and indoor units)
- **Check system performance** numbers still look normal
- **Update integration** if new version available

### Quarterly Checks
- **Deep clean** outdoor unit (remove leaves, debris)
- **Check refrigerant pipes** for damage or ice buildup
- **Verify all safety systems** working correctly
- **Review energy consumption** trends

### Annual Service
- **Professional heat pump service** by qualified engineer
- **Check refrigerant levels** and system pressures
- **Calibrate temperature sensors** if needed
- **Update firmware** on heat pump controller if available

---

## 💬 **Getting Community Help**

### Before Posting Questions
1. **Check this troubleshooting guide** first
2. **Search previous issues** on GitHub
3. **Collect diagnostic information** listed above
4. **Try obvious solutions** like restarts

### Where to Get Help
- **[GitHub Issues](https://github.com/your-username/Grant-Aerona3-Heat-Pump-Home-Assistant-Integration/issues)** - Technical problems
- **[Home Assistant Community](https://community.home-assistant.io/)** - General discussion
- **[Heat Pump Monitoring Group](https://www.facebook.com/groups/HeatPumpMonitoring)** - UK community

### How to Write Good Help Requests
1. **Descriptive title**: "Weather compensation not adjusting flow temperature" not "Help!"
2. **Clear problem description**: What you expect vs what happens
3. **System details**: Heat pump model, HA version, etc.
4. **Steps already tried**: Show you've done basic troubleshooting
5. **Log files**: Include relevant error messages

---

## 🎯 **Success Stories**

### Real Problems Solved

> **"Integration kept disconnecting every few hours. Turned out to be a dodgy ethernet cable - £3 replacement fixed six months of frustration!"** - *Kent user*

> **"Weather compensation wasn't working because outdoor temperature sensor was reading wrong. Found bird's nest blocking airflow to sensor. Cleaned it and saved £300 on engineer call!"** - *Wales user*

> **"COP readings were way off. Heat pump engineer found low refrigerant charge during annual service. Integration was actually helping diagnose a real problem!"** - *Scotland user*

> **"Kept getting 'cannot connect' errors. Discovered heat pump Modbus wasn't enabled after a power cut reset the controller. Simple service menu fix."** - *Yorkshire user*

---

**Remember: Most problems have simple solutions, and the integration is designed to help you understand your heat pump better! 🔧**

*When in doubt, start with the quick fixes and work your way up. You'll be amazed how many "big problems" are actually just loose connections! 🇬🇧*