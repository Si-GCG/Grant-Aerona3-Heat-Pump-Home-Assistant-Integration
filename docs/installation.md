# Installation Guide - Grant Aerona3 Heat Pump Integration

> **Step-by-step guide to get your Grant Aerona3 talking to Home Assistant**

This guide is written for everyone, whether you're comfortable with technology or prefer simple instructions. We'll get your heat pump connected in about 15 minutes!

## 🏁 **Before You Start**

### What You'll Need
- **Grant Aerona3 heat pump** (any model - 6kW, 8kW, 10kW, 12kW, or 14kW)
- **Home Assistant** running on any device (Raspberry Pi, NUC, Synology NAS, etc.)
- **Modbus converter** to connect your heat pump to your network
- **Basic tools** (screwdriver, network cable)

### Check Your Home Assistant Version
1. Go to **Settings** → **System** → **General**
2. Look for **Core** version - you need **2023.4** or newer
3. If you're older, update Home Assistant first

---

## 🔌 **Step 1: Connect Your Heat Pump to Your Network**

### Option A: Waveshare Ethernet Converter (Recommended)

This is the easiest method - plug and play!

#### What to Buy
- **Waveshare RS485 to POE ETH (B)** converter
- Available from Amazon, eBay, or electronics suppliers
- Cost: Around £30-40

#### Wiring Instructions
1. **Turn off your heat pump** at the isolator switch
2. **Remove the front panel** of your Grant Aerona3 controller
3. **Locate the Modbus terminals** (usually at the bottom, labelled)
4. **Connect the wires**:
   - **Orange wire** → Pin 15 (RS485+)
   - **Orange/White wire** → Pin 16 (RS485-)
   - **Blue wire** → Pin 32 (GND)
5. **Connect ethernet cable** from converter to your router
6. **Power up** the converter and heat pump

#### Network Setup
1. **Find the converter's IP address** (usually 192.168.1.200)
2. **Test connection** by pinging it from your computer:
   ```
   ping 192.168.1.200
   ```
3. If it doesn't respond, check the converter manual for default settings

### Option B: USB RS485 Converter

Use this if you prefer a direct USB connection to your Home Assistant device.

#### What to Buy
- **USB to RS485 converter** 
- Available from Amazon/eBay for around £15-20

#### Setup
1. **Connect USB converter** to your Home Assistant device
2. **Wire to heat pump** same as above (Orange → A+, Orange/White → B-, Blue → GND)
3. **Configure Home Assistant** to use the USB serial port

---

## 🏠 **Step 2: Enable Modbus on Your Heat Pump**

Your Grant Aerona3 needs to be told to accept Modbus connections.

### Accessing the Service Menu
1. **Turn on your heat pump** controller
2. **Press and hold** the menu button for 10 seconds
3. **Enter service code** (usually 1234 or check your manual)
4. **Navigate to** "Communications" or "Modbus" settings
5. **Enable Modbus** and set:
   - **Baud Rate**: 19200
   - **Data Bits**: 8
   - **Parity**: None
   - **Stop Bits**: 2
   - **Slave Address**: 1

### Can't Find the Service Menu?
- Check your Grant Aerona3 manual (page varies by model)
- Contact Grant technical support for your specific model
- Some older models may need a firmware update

---

## 📱 **Step 3: Install the Integration in Home Assistant**

### Method 1: HACS (Recommended)

HACS makes installation and updates much easier.

#### Install HACS First (if you haven't already)
1. **Follow the HACS installation guide**: https://hacs.xyz/docs/setup/download
2. **Restart Home Assistant**
3. **Go to HACS** in the sidebar

#### Install Grant Aerona3 Integration
1. **Open HACS** → **Integrations**
2. **Click the three dots** (⋮) → **Custom repositories**
3. **Add repository**:
   - **URL**: `https://github.com/your-username/Grant-Aerona3-Heat-Pump-Home-Assistant-Integration`
   - **Category**: Integration
4. **Click "Add"**
5. **Search for "Grant Aerona3"** in HACS
6. **Click "Download"**
7. **Restart Home Assistant**

### Method 2: Manual Installation

If you prefer to do it manually or don't use HACS.

#### Download and Install
1. **Download the latest release** from GitHub
2. **Extract the zip file**
3. **Copy the folder** `custom_components/grant_aerona3` 
4. **Paste it** into your Home Assistant `config/custom_components/` folder
5. **Restart Home Assistant**

---

## ⚙️ **Step 4: Add and Configure the Integration**

### Adding the Integration
1. **Go to Settings** → **Devices & Services**
2. **Click "Add Integration"** (+ button)
3. **Search for "Grant Aerona3"**
4. **Click on it** to start setup

### Setup Wizard

The integration will guide you through setup with a friendly wizard:

#### Connection Settings
- **Host**: IP address of your Modbus converter (e.g., 192.168.1.200)
- **Port**: 502 (this is the standard Modbus port)
- **Slave ID**: 1 (unless you changed it)
- **Scan Interval**: 30 seconds (how often to check your heat pump)

#### Installation Type
Choose what best describes your home:

- **🏠 Single Zone Basic (35%)**: One heating zone, no hot water cylinder
- **🚿 Single Zone + Hot Water (50%)**: One heating zone with hot water cylinder  
- **🏘️ Dual Zone System (10%)**: Two heating zones (upstairs/downstairs)
- **🔄 Replacement System (5%)**: Replacing an old boiler system

#### Feature Selection
The wizard will ask about your specific setup:
- **Hot water cylinder**: Yes/No
- **Backup heater**: Yes/No (electric immersion or gas backup)
- **Zone 2**: Yes/No (second heating zone)
- **Flow meter**: Yes/No (if you have flow rate monitoring)

### Testing the Connection
1. **Click "Test Connection"** - this checks if Home Assistant can talk to your heat pump
2. **If successful**: You'll see a green tick ✅
3. **If failed**: Check your wiring and network connection

---

## 🎉 **Step 5: Your First Look**

### What You'll See
After successful setup, you'll have:

#### New Devices & Services Entry
- **Grant Aerona3 Heat Pump** device with all sensors and controls

#### Key Entities Created
- **🌡️ Temperature sensors**: Outdoor, flow, return, hot water
- **⚡ Power monitoring**: Consumption, efficiency (COP)
- **🎛️ Controls**: Temperature setpoints, weather compensation
- **📊 Status sensors**: System health, operating mode

#### Automatic Dashboard
The integration creates a basic dashboard automatically, or you can add cards to your existing dashboards.

---

## 🎛️ **Step 6: Basic Configuration**

### Setting Up Weather Compensation

Weather compensation is the biggest money-saver! It automatically adjusts your heating based on outdoor temperature.

#### Enable Weather Compensation
1. **Find the switch**: `switch.grant_aerona3_weather_compensation_active`
2. **Turn it on** ✅
3. **Check it's working**: Look for the weather compensation status sensor

#### Understanding the Settings
- **Min Outdoor Temp**: Coldest temperature you expect (-8°C for most of UK)
- **Max Outdoor Temp**: When heating isn't needed (16°C typical)
- **Min Flow Temp**: Lowest water temperature (30°C for UFH, 35°C for radiators)
- **Max Flow Temp**: Highest water temperature (45°C typical)

### Setting Temperature Setpoints
1. **Zone 1 Temperature**: Set your main heating temperature
2. **Hot Water Temperature**: Set DHW cylinder temperature (if you have one)
3. **Zone 2 Temperature**: Set second zone temperature (if you have one)

---

## 🔍 **Step 7: Verify Everything is Working**

### Quick Health Check
1. **Check temperature readings** - do they look realistic?
2. **Watch the COP (efficiency)** - should be between 2.5-4.5
3. **Monitor power consumption** - should match your expectations
4. **Test weather compensation** - flow temperature should change with outdoor temperature

### Common Things to Check
- **Outdoor temperature** matches weather forecast
- **Flow and return temperatures** have a difference (usually 5-10°C)
- **Power consumption** changes when heating starts/stops
- **No error messages** in the system health sensor

---

## 🚨 **Common Installation Issues**

### "Cannot Connect" Error
**Cause**: Network connectivity issues
**Fix**: 
1. Check ethernet cable connections
2. Verify IP address is correct
3. Test ping to converter: `ping 192.168.1.200`
4. Check converter power LED is on

### "No Response from Heat Pump"
**Cause**: Modbus not enabled or wrong settings
**Fix**:
1. Double-check Modbus is enabled in heat pump service menu
2. Verify baud rate is 19200
3. Check wiring connections are tight
4. Ensure slave address is 1

### "Integration Not Found"
**Cause**: Installation not complete
**Fix**:
1. Restart Home Assistant after installation
2. Check `custom_components/grant_aerona3` folder exists
3. Check Home Assistant logs for errors

### Sensors Show "Unknown" or "Unavailable"
**Cause**: Communication working but data not readable
**Fix**:
1. Check scan interval isn't too fast (minimum 30 seconds)
2. Verify heat pump is powered on
3. Some sensors only work when heating is active

---

## 🎯 **Next Steps**

### Congratulations! 🎉
Your Grant Aerona3 is now connected to Home Assistant!

### What to Do Next
1. **📱 Explore the dashboard** - see what information is available
2. **📖 Read the User Guide** - understand all the features
3. **🌡️ Set up weather compensation** - start saving money
4. **📊 Create automations** - make your system even smarter
5. **💬 Join the community** - share your experience and get tips

### Recommended Reading
- **[User Manual](user-guide.md)** - Understanding your system
- **[Weather Compensation Guide](weather-compensation.md)** - Optimising efficiency  
- **[Troubleshooting Guide](troubleshooting.md)** - Solving common problems

---

## 💬 **Need Help?**

### Community Support
- **[GitHub Issues](https://github.com/your-username/Grant-Aerona3-Heat-Pump-Home-Assistant-Integration/issues)** - Technical problems
- **[Home Assistant Community](https://community.home-assistant.io/)** - General discussion
- **[Heat Pump Monitoring Facebook Group](https://www.facebook.com/groups/HeatPumpMonitoring)** - UK heat pump community

### Professional Support
- **Grant UK Technical**: 0800 999 2733
- **Local heating engineer** familiar with Grant heat pumps

---

**Well done! Your heat pump is now smart and ready to save you money! 🏠💰**

*Remember: weather compensation alone can save 10-15% on your heating bills. You've just made a brilliant investment in your home's efficiency! 🇬🇧*
