# Contributing to Grant Aerona3 Heat Pump Integration

> **Help make this integration even better for the British heat pump community!**

We warmly welcome contributions from everyone - whether you're a seasoned developer, heating engineer, or heat pump owner with great ideas. This guide explains how to contribute effectively.

## 🤝 **Ways to Contribute**

### 🐛 **Report Bugs**
Found something that's not working? Help us fix it!

#### **Before Reporting**
1. **Check existing issues** - someone might have reported it already
2. **Try basic troubleshooting** - see our [Troubleshooting Guide](docs/troubleshooting.md)
3. **Test with latest version** - update the integration first

#### **What to Include**
- **Clear title**: "Weather compensation not working with 8kW model" not "It's broken"
- **System details**: Heat pump model, Home Assistant version, integration version
- **Steps to reproduce**: What you did before the problem occurred
- **Expected vs actual**: What should happen vs what actually happens
- **Log files**: Enable debug logging and include relevant errors
- **Screenshots**: If UI-related, show what you see

### 💡 **Suggest Features**
Got an idea to make the integration better?

#### **Great Feature Ideas**
- **New heat pump models** - expand compatibility
- **Additional sensors** - more monitoring capabilities  
- **Dashboard improvements** - better visualisation
- **Automation examples** - smart heating scenarios
- **Documentation enhancements** - clearer explanations

#### **How to Suggest**
1. **Open a GitHub issue** with "Feature Request" label
2. **Describe the benefit** - how would this help users?
3. **Provide context** - your heat pump model, use case, etc.
4. **Include examples** - mockups, similar features, etc.

### 📖 **Improve Documentation**
Help make the integration more accessible!

#### **Documentation Needs**
- **Additional heat pump models** - specific setup instructions
- **More troubleshooting scenarios** - real problems and solutions
- **Better examples** - automation scripts, dashboard configs
- **Video guides** - visual installation walkthroughs
- **Translations** - guides in other languages

### 🔧 **Contribute Code**
Ready to dive into the technical side?

#### **Good First Contributions**
- **Add new register definitions** for additional heat pump models
- **Improve error handling** and user feedback
- **Add unit tests** for existing functionality
- **Optimise performance** in data processing
- **Enhance entity descriptions** and tooltips

---

## 🚀 **Development Setup**

### **Prerequisites**
- **Python 3.10+** (same as Home Assistant requirement)
- **Git** for version control
- **Text editor/IDE** (VS Code recommended)
- **Grant Aerona3 heat pump** (for testing) or access to test data

### **Local Development Environment**

#### **1. Fork and Clone**
```bash
# Fork the repository on GitHub first, then:
git clone https://github.com/YOUR-USERNAME/Grant-Aerona3-Heat-Pump-Home-Assistant-Integration.git
cd Grant-Aerona3-Heat-Pump-Home-Assistant-Integration
```

#### **2. Set Up Development Environment**
```bash
# Create virtual environment
python -m venv venv

# Activate it (Linux/Mac)
source venv/bin/activate
# Or on Windows
venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt
```

#### **3. Install Pre-commit Hooks**
```bash
# Install pre-commit hooks for code quality
pre-commit install
```

#### **4. Run Tests**
```bash
# Run all tests
python -m pytest

# Run specific test files
python test_core_mvp.py
python test_weather_compensation_core.py
python test_enhanced_integration.py

# Run with coverage
python -m pytest --cov=custom_components.grant_aerona3
```

### **Development in Home Assistant**

#### **Option 1: Development Container (Recommended)**
```bash
# Open in VS Code with Dev Containers extension
code .
# Command palette: "Dev Containers: Open in Container"
```

#### **Option 2: Local Home Assistant**
```bash
# Copy integration to your HA config
cp -r custom_components/grant_aerona3 /path/to/homeassistant/config/custom_components/

# Restart Home Assistant
# Add integration via UI for testing
```

---

## 📝 **Coding Standards**

### **Code Style**
We follow **Python PEP 8** with some Home Assistant-specific conventions:

```python
# Good
class GrantAerona3Sensor(CoordinatorEntity, SensorEntity):
    """Temperature sensor for Grant Aerona3 heat pump."""
    
    def __init__(self, coordinator: GrantAerona3Coordinator, config: dict) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config = config
        
    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""
        return self.coordinator.data.get("temperature")
```

#### **Key Conventions**
- **Type hints** on all function parameters and returns
- **Docstrings** for all classes and public methods
- **Error handling** with specific exception types
- **Logging** with appropriate levels (debug, info, warning, error)
- **Constants** in UPPER_CASE in const.py

### **Security Requirements**
- **Input validation** on all user inputs
- **Sanitise data** before logging or display
- **No hardcoded credentials** or sensitive data
- **Secure defaults** for all configuration options

### **Performance Guidelines**
- **Async operations** for all I/O (network, file operations)
- **Efficient data structures** (avoid nested loops where possible)
- **Memory management** (bounded collections, cleanup methods)
- **Minimal blocking** operations in the main thread

---

## 🧪 **Testing Requirements**

### **Test Coverage**
All new code should include appropriate tests:

#### **Unit Tests** (Required)
```python
def test_register_manager_initialization():
    """Test register manager initializes correctly."""
    config = {"dhw_cylinder": True, "zones": {"zone_1": {"enabled": True}}}
    manager = GrantAerona3RegisterManager(config)
    
    assert len(manager._enabled_registers) > 20
    assert "dhw_temp" in manager._enabled_registers
```

#### **Integration Tests** (Recommended)
```python
async def test_coordinator_data_update():
    """Test coordinator fetches and processes data correctly."""
    with patch("pymodbus.client.ModbusTcpClient") as mock_client:
        # Set up mock responses
        coordinator = GrantAerona3EnhancedCoordinator(hass, config_entry)
        await coordinator.async_config_entry_first_refresh()
        
        assert coordinator.data["outdoor_temp"]["value"] is not None
```

#### **Performance Tests** (For Core Features)
```python
def test_weather_compensation_performance():
    """Test weather compensation calculations are fast enough."""
    curve = LinearHeatingCurve(test_config)
    
    start_time = time.time()
    for _ in range(10000):
        curve.calculate_flow_temperature(random.uniform(-10, 20))
    duration = time.time() - start_time
    
    assert duration < 0.1  # Should complete in <100ms
```

### **Running Tests Locally**
```bash
# Run all tests with output
python -m pytest -v

# Run specific test file
python -m pytest test_weather_compensation_core.py -v

# Run with coverage report
python -m pytest --cov=custom_components.grant_aerona3 --cov-report=html

# Run performance tests
python -m pytest -k "performance" -v
```

---

## 📋 **Pull Request Process**

### **Before Submitting**

#### **1. Create Feature Branch**
```bash
# Create descriptive branch name
git checkout -b feature/weather-compensation-boost-mode
# or
git checkout -b fix/sensor-unavailable-at-startup
# or  
git checkout -b docs/installation-guide-improvements
```

#### **2. Make Changes**
- **Follow coding standards** outlined above
- **Add appropriate tests** for new functionality
- **Update documentation** if behaviour changes
- **Test thoroughly** with real heat pump if possible

#### **3. Pre-submission Checklist**
- [ ] **All tests pass** locally
- [ ] **Code follows style guidelines**
- [ ] **Documentation updated** if needed
- [ ] **Security considerations** reviewed
- [ ] **Performance impact** considered
- [ ] **Backwards compatibility** maintained (unless major version)

### **Submitting Pull Request**

#### **1. Update Your Branch**
```bash
# Get latest changes from main
git fetch upstream
git rebase upstream/main

# Resolve any conflicts
# Run tests again after rebase
```

#### **2. Push and Create PR**
```bash
# Push your branch
git push origin feature/your-feature-name

# Create pull request on GitHub
# Use the PR template provided
```

#### **3. PR Description Template**
```markdown
## Description
Brief description of what this PR does and why.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)  
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing completed with real heat pump
- [ ] Performance impact assessed

## Heat Pump Models Tested
- [ ] Grant Aerona3 6kW
- [ ] Grant Aerona3 8kW  
- [ ] Grant Aerona3 10kW
- [ ] Grant Aerona3 12kW
- [ ] Grant Aerona3 14kW
- [ ] Other (specify): ___________

## Documentation
- [ ] README updated if needed
- [ ] User guide updated if needed
- [ ] API documentation updated if needed
- [ ] CHANGELOG.md updated

## Screenshots (if applicable)
Include screenshots of any UI changes.
```

### **Review Process**

#### **What Reviewers Look For**
1. **Functionality** - Does it work as intended?
2. **Code quality** - Is it maintainable and well-structured?
3. **Security** - Are there any security implications?
4. **Performance** - Will it impact system performance?
5. **Documentation** - Is it clear how to use new features?
6. **Testing** - Is there adequate test coverage?

#### **Responding to Feedback**
- **Be responsive** - reply to comments within a few days
- **Be open** to suggestions and constructive criticism
- **Ask questions** if feedback isn't clear
- **Make requested changes** in separate commits for easy review
- **Update tests** if functionality changes during review

---

## 🎯 **Specific Contribution Areas**

### **Heat Pump Model Support**
Help expand compatibility to more Grant models:

#### **What We Need**
- **Register maps** for different Grant Aerona3 variants
- **Test data** from real installations
- **Model-specific quirks** and configuration differences
- **Installation templates** for different system types

#### **How to Contribute**
1. **Document your heat pump model** completely
2. **Capture register data** using Modbus tools
3. **Test integration** with your specific model
4. **Submit register definitions** via pull request
5. **Help test** others' contributions with your model

### **Weather Compensation Improvements**
Enhance the money-saving weather compensation features:

#### **Enhancement Ideas**
- **Advanced curves** (quadratic, custom curves)
- **Zone-specific** weather compensation
- **Predictive algorithms** using weather forecasts
- **Learning systems** that adapt to house characteristics
- **Integration with** smart thermostats

### **Dashboard and UI Enhancements**
Make the integration more user-friendly:

#### **UI Improvement Areas**
- **Better visualisations** of weather compensation curves
- **Energy flow diagrams** showing heat pump operation
- **Historical analysis** tools for efficiency trends
- **Mobile-friendly** dashboard layouts
- **Accessibility** improvements for screen readers

### **Documentation and Education**
Help make heat pump technology accessible:

#### **Documentation Needs**
- **Video tutorials** for installation and setup
- **Case studies** from real homes showing savings
- **Automation examples** for different scenarios
- **Troubleshooting guides** for specific problems
- **Best practices** guides for different home types

---

## 🏆 **Recognition**

### **Contributor Hall of Fame**
We recognise significant contributions in our README and release notes:

- **Code contributors** - GitHub profile links and contribution descriptions
- **Documentation contributors** - Credit in relevant guides
- **Community helpers** - Recognition for support and testing
- **Feature sponsors** - Credit for funding development work

### **How to Get Recognised**
- **Quality over quantity** - well-tested, documented contributions
- **Community involvement** - helping others in issues and discussions
- **Long-term commitment** - ongoing contributions and maintenance
- **Knowledge sharing** - blog posts, videos, conference talks about the integration

---

## 💬 **Community Guidelines**

### **Be Respectful**
- **Welcome newcomers** - everyone was a beginner once
- **Be patient** with questions - not everyone has technical background
- **Constructive feedback** - focus on code/ideas, not people
- **Inclusive language** - avoid assumptions about gender, experience level, etc.

### **Be Helpful**
- **Share knowledge** - explain concepts clearly
- **Link to resources** - point people to relevant documentation
- **Test others' contributions** - help with community testing
- **Report issues clearly** - help maintainers understand problems

### **Be Professional**
- **Keep discussions** focused on the project
- **Avoid political** or controversial topics
- **Respect maintainers'** time and decisions
- **Follow** the Code of Conduct

---

## 📞 **Getting Help**

### **Where to Ask Questions**
1. **GitHub Discussions** - General questions about contributing
2. **GitHub Issues** - Specific bugs or feature requests
3. **Home Assistant Community** - Integration usage questions
4. **Discord/Slack** - Real-time chat with community (links in README)

### **Maintainer Response Times**
- **Bug reports**: Within 48 hours for acknowledgment
- **Feature requests**: Within 1 week for initial response
- **Pull requests**: Within 1 week for first review
- **Security issues**: Within 24 hours (use security contact)

---

**Thank you for considering contributing to this project! Your help makes the British heat pump community stronger and more efficient! 🇬🇧💚**

*Remember: Every contribution, no matter how small, helps other heat pump owners save money and reduce their carbon footprint. That's pretty brilliant! 🌱*