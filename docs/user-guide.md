# User Guide - Understanding Your Grant Aerona3 Integration

> **Everything you need to know about monitoring and controlling your heat pump through Home Assistant**

Welcome to your smart heat pump! This guide explains all the features in plain English, so you can get the most from your system and save money on your heating bills.

## 🎯 **What This Guide Covers**

- **Understanding the dashboard** - what all those numbers mean
- **Using weather compensation** - the biggest money-saver
- **Setting temperatures** - getting comfortable heating
- **Monitoring efficiency** - tracking your heat pump's performance
- **Spotting problems** - before they become expensive
- **Saving money** - tips and tricks for lower bills

---

## 📊 **Understanding Your Dashboard**

When you open Home Assistant, you'll see lots of information about your heat pump. Here's what it all means:

### 🌡️ **Temperature Readings**

#### **Outdoor Temperature**
- **What it is**: Temperature outside your home
- **Why it matters**: This drives weather compensation - colder outside means hotter water inside
- **Typical range**: -10°C to 25°C in the UK
- **💡 Tip**: Should match your local weather forecast

#### **Flow Temperature** 
- **What it is**: Temperature of water leaving your heat pump to heat your home
- **Why it matters**: Higher = more heating, but less efficient
- **Typical range**: 30°C to 50°C depending on your heating system
- **💡 Tip**: Underfloor heating uses lower temperatures (30-35°C), radiators use higher (40-50°C)

#### **Return Temperature**
- **What it is**: Temperature of water coming back from your heating system
- **Why it matters**: Difference between flow and return shows how much heat your home is using
- **Typical range**: 5-10°C cooler than flow temperature
- **💡 Tip**: Bigger difference = your heating system is working well

#### **Hot Water Temperature** (if you have a cylinder)
- **What it is**: Temperature in your hot water cylinder
- **Why it matters**: Should be hot enough for showers but not wastefully hot
- **Typical range**: 45°C to 60°C
- **💡 Tip**: 50°C is usually perfect for most homes

### ⚡ **Efficiency & Power**

#### **COP (Coefficient of Performance)**
- **What it is**: How efficiently your heat pump converts electricity into heat
- **What the numbers mean**:
  - **COP 2.5**: You get 2.5kW of heat for every 1kW of electricity (250% efficient)
  - **COP 3.5**: You get 3.5kW of heat for every 1kW of electricity (350% efficient)
  - **COP 4.5**: You get 4.5kW of heat for every 1kW of electricity (450% efficient)
- **Good performance**: 2.5+ in cold weather, 3.5+ in mild weather
- **💡 Tip**: Higher COP = lower bills. Weather compensation helps maintain high COP

#### **Power Consumption**
- **What it is**: How much electricity your heat pump is using right now
- **Typical range**: 1kW to 4kW depending on heat pump size and demand
- **Why it matters**: Helps you understand running costs
- **💡 Tip**: Multiply by your electricity rate to see cost per hour

#### **Energy Consumption**
- **What it is**: Total electricity used over time (daily, monthly)
- **Why it matters**: Tracks your heating costs
- **💡 Tip**: Compare with previous bills to see if you're saving money

### 🎛️ **System Status**

#### **Operating Mode**
- **Heating**: Heat pump is warming your home
- **Hot Water**: Heat pump is heating your cylinder (if you have one)
- **Standby**: Heat pump is waiting, ready to heat when needed
- **Defrost**: Heat pump is melting ice off the outdoor unit (normal in cold weather)

#### **Compressor Status**
- **Running**: The heart of your heat pump is working
- **Stopped**: Heat pump is idle
- **Frequency**: How hard the compressor is working (Hz)
  - Low frequency (20-40 Hz) = gentle heating
  - High frequency (60-120 Hz) = maximum heating

---

## 🌡️ **Weather Compensation - Your Money Saver**

Weather compensation is the cleverest feature of your heat pump. It automatically adjusts the water temperature based on how cold it is outside.

### How It Works
- **Cold outside (-5°C)**: Heat pump sends hot water (45°C) to your radiators
- **Mild outside (10°C)**: Heat pump sends cooler water (35°C) - still warm enough but more efficient
- **Warm outside (15°C)**: Heat pump sends just enough heat (30°C) to keep you comfortable

### Why It Saves Money
Without weather compensation, your heat pump sends the same temperature water regardless of outdoor conditions. This wastes energy on mild days.

**Example savings**:
- **Without weather compensation**: Always 45°C → COP 2.8 → £1,200/year
- **With weather compensation**: 30-45°C → COP 3.5 → £950/year
- **Annual saving**: £250! 💰

### Setting Up Weather Compensation

#### 1. Enable Weather Compensation
- **Find the switch**: `Weather Compensation Active`
- **Turn it on** ✅

#### 2. Configure Your Heating Curve
Your heating curve tells the heat pump what temperature to use at different outdoor temperatures.

**For Underfloor Heating**:
- **Min Outdoor**: -8°C (coldest you expect)
- **Max Outdoor**: 16°C (when heating stops)
- **Min Flow**: 30°C (mild weather)
- **Max Flow**: 40°C (cold weather)

**For Radiators**:
- **Min Outdoor**: -8°C
- **Max Outdoor**: 16°C  
- **Min Flow**: 35°C (mild weather)
- **Max Flow**: 50°C (cold weather)

#### 3. Test It's Working
- **Watch the flow temperature** change as outdoor temperature changes
- **Check the weather compensation status** shows "Active"
- **Monitor your COP** - should improve over the following days

### Boost Mode
Sometimes you need extra heat quickly:
- **Manual boost**: Turn on for 2 hours of extra heating
- **Automatic boost**: System activates when very cold
- **Party mode**: Higher temperatures for special occasions

---

## 🎛️ **Setting Temperatures**

### Zone 1 Temperature (Main Heating)
This controls your main heating system.

#### **Fixed Flow Temperature**
- **What it is**: Constant water temperature when not using weather compensation
- **When to use**: If you prefer manual control
- **Typical settings**: 40°C for radiators, 35°C for underfloor heating

#### **Max/Min Flow Temperature**
- **What it is**: Limits for weather compensation
- **Max temperature**: Hottest water allowed (usually 50°C)
- **Min temperature**: Coolest water used (usually 30°C)

### Zone 2 Temperature (Second Zone)
If you have upstairs/downstairs or separate areas:
- **Same controls as Zone 1**
- **Can be different temperatures** for different comfort levels
- **Useful for** heating bedrooms cooler than living areas

### Hot Water Temperature
For your cylinder (if you have one):
- **Target temperature**: Usually 50°C
- **Boost function**: Heat water quickly when needed
- **Legionella protection**: Weekly high-temperature cycle for safety

---

## 📈 **Monitoring Performance**

### Daily Checks (30 seconds)
**Quick glance at**:
- **COP reading** - should be 2.5+ most of the time
- **No error messages** in system health
- **Flow temperature** adjusting with outdoor temperature

### Weekly Checks (5 minutes)
**Look at**:
- **Energy consumption trends** - are bills going up or down?
- **Runtime hours** - how much is your heat pump working?
- **Average COP for the week** - tracking efficiency over time

### Monthly Analysis (15 minutes)
**Review**:
- **Total energy consumption** vs previous months
- **Cost analysis** compared to old heating system
- **Weather compensation performance** - is it saving money?
- **System health trends** - any developing issues?

### What Good Performance Looks Like

#### **Excellent Performance** 🟢
- **COP**: 3.5+ in mild weather, 2.8+ in cold weather  
- **Energy use**: Decreasing compared to old heating system
- **Comfort**: Home stays warm with consistent temperatures
- **Issues**: None or very rare

#### **Good Performance** 🟡
- **COP**: 3.0+ in mild weather, 2.5+ in cold weather
- **Energy use**: Similar to old system but more consistent heat
- **Comfort**: Generally warm with occasional adjustments needed
- **Issues**: Minor issues resolved quickly

#### **Needs Attention** 🔴
- **COP**: Below 2.5 consistently
- **Energy use**: Higher than expected
- **Comfort**: Home not reaching target temperatures
- **Issues**: Regular error messages or system shutdowns

---

## 🔍 **Spotting Problems Early**

Your integration monitors system health and can warn you about problems before they become expensive repairs.

### Warning Signs to Watch For

#### **Efficiency Problems**
- **Low COP** (below 2.0 for extended periods)
- **High power consumption** with little heating
- **Poor weather compensation** response

**Possible causes**: Dirty filters, low refrigerant, faulty sensors
**Action**: Check filters, call heating engineer if continues

#### **Temperature Issues**
- **Flow and return temperatures** too close together (less than 5°C difference)
- **Outdoor temperature** doesn't match weather forecast
- **Hot water** not reaching target temperature

**Possible causes**: Circulation problems, sensor faults, system imbalance
**Action**: Check pump speeds, bleed radiators, professional check

#### **System Faults**
- **Frequent defrost cycles** (more than once per hour in cold weather)
- **Compressor short cycling** (starting and stopping frequently)
- **Error codes** appearing in system health

**Possible causes**: Refrigerant issues, electrical problems, control faults
**Action**: Contact qualified heat pump engineer immediately

### Predictive Maintenance

Your integration tracks patterns that indicate when maintenance is needed:

#### **Filter Change Reminders**
- **Based on runtime hours** and airflow readings
- **Typical interval**: Every 3-6 months
- **DIY job**: Usually just vacuum or replace filter

#### **Annual Service Due**
- **Based on operating hours** and system performance
- **Professional job**: Gas Safe registered heat pump engineer
- **Typical cost**: £150-300 annually

#### **Performance Degradation**
- **Gradual COP decline** over months/years
- **Increasing power consumption** for same heating
- **May indicate**: Refrigerant loss, component wear, system fouling

---

## 💰 **Saving Money with Your Heat Pump**

### Immediate Savings (Start Today)

#### **Enable Weather Compensation**
- **Potential saving**: 10-15% on heating bills
- **How**: Turn on weather compensation switch
- **Time to benefit**: Immediate

#### **Optimise Temperatures** 
- **Lower flow temperatures** when possible
- **Hot water** to 50°C (not 60°C unless needed)
- **Zone 2** cooler than Zone 1 for bedrooms

#### **Time Your Hot Water**
- **Heat before peak electricity rates** if you have time-of-use tariffs
- **Use boost sparingly** - only when really needed
- **Consider** heating hot water when COP is highest (mild weather)

### Medium-term Optimisation (First Month)

#### **Learn Your Usage Patterns**
- **Track when you use most heating** and adjust setpoints
- **Identify wasteful habits** like heating when out
- **Optimise schedules** around your lifestyle

#### **Fine-tune Weather Compensation**
- **Adjust curves** based on comfort and efficiency
- **Lower maximum temperatures** if home stays warm enough
- **Extend heating hours** rather than higher temperatures

#### **Home Improvements**
- **Better insulation** = lower flow temperatures = higher COP
- **Radiator upgrades** to larger ones allow lower temperatures
- **Smart thermostats** for better zone control

### Long-term Benefits (6-12 Months)

#### **Seasonal Adjustments**
- **Summer setup** for hot water only
- **Winter optimisation** for maximum efficiency
- **Spring/autumn** weather compensation fine-tuning

#### **Compare with Previous Heating**
- **Annual energy comparison** vs old boiler
- **Cost analysis** including maintenance savings
- **Comfort improvements** quantified

#### **System Upgrades**
- **Buffer tank** addition for smoother operation
- **Flow meters** for more accurate monitoring
- **Smart controls** integration for automation

---

## 🏠 **Seasonal Operation Guide**

### Winter Operation (Dec-Feb)
- **Weather compensation** working hardest
- **Higher power consumption** but still efficient
- **Defrost cycles** normal in cold weather
- **Monitor COP** - aim for 2.5+ even in cold snaps

### Spring Operation (Mar-May)
- **Excellent COP** as weather warms
- **Reduced heating demand** 
- **Perfect time** to optimise weather compensation curves
- **Consider** hot water only periods on warm days

### Summer Operation (Jun-Aug)
- **Hot water only** if heating not needed
- **Highest COP** of the year for hot water
- **Maintenance period** - ideal time for annual service
- **System rest** - opportunity for any upgrades

### Autumn Operation (Sep-Nov)
- **Restart heating** gradually
- **Check all systems** after summer break
- **Optimise settings** for coming winter
- **Monitor performance** as temperatures drop

---

## 🚨 **When to Call for Help**

### DIY Fixes (Safe to Try)
- **Check and clean filters** (monthly)
- **Bleed radiators** if cold spots
- **Reset integration** if sensors not updating
- **Adjust temperature setpoints** for comfort

### Call a Heating Engineer
- **Error codes** appearing regularly
- **COP below 2.0** consistently  
- **No heating or hot water** 
- **Strange noises** from heat pump
- **Refrigerant leaks** (ice forming, poor performance)
- **Electrical issues** (tripping circuits, burnt smells)

### Emergency (Call Immediately)
- **Gas smell** (if hybrid system)
- **Water leaks** causing damage
- **Electrical sparking** or burning smells
- **Complete system failure** in freezing weather

---

## 📚 **Further Reading**

- **[Weather Compensation Guide](weather-compensation.md)** - Deep dive into efficiency optimisation
- **[Troubleshooting Guide](troubleshooting.md)** - Fixing common problems
- **[Technical Documentation](technical/README.md)** - For the technically minded

---

## 💬 **Community Tips**

### From Real Users

> **"Set my hot water to 48°C instead of 55°C - COP improved from 2.8 to 3.2 with no noticeable difference in shower temperature."** - *Somerset user*

> **"Weather compensation saved me £15/month immediately. Best feature of the whole system!"** - *Lancashire user*

> **"Lower flow temperatures in bedrooms to 40°C - kids sleep better and bills are lower."** - *Yorkshire family*

> **"Use boost mode only for guests. Regular daily patterns work much better for efficiency."** - *Devon user*

---

**Congratulations! You now understand your heat pump system better than most heating engineers! 🎓**

*Use this knowledge to save money, stay comfortable, and get the most from your brilliant Grant Aerona3 heat pump! 🇬🇧*