#!/usr/bin/env python3
"""Test enhanced Grant Aerona3 integration functionality."""

import sys
import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from typing import Dict, Any

# Add the custom_components path for testing
sys.path.insert(0, './custom_components/grant_aerona3')

# Core imports for testing
from register_manager import (
    GrantAerona3RegisterManager,
    RegisterType,
    RegisterCategory,
    RegisterConfig
)

# Weather compensation imports
from test_weather_compensation_core import (
    LinearHeatingCurve,
    HeatingCurveConfig,
    CurveType
)


class TestEnhancedIntegration(unittest.TestCase):
    """Test the enhanced Grant Aerona3 integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.basic_config = {
            "host": "192.168.1.100",
            "port": 502,
            "slave_id": 1,
            "installation_template": "single_zone_dhw",
            "zones": {
                "zone_1": {"enabled": True, "name": "Main Zone"},
                "zone_2": {"enabled": False, "name": "Second Zone"}
            },
            "dhw_cylinder": True,
            "backup_heater": False,
            "weather_compensation": True,
            "dual_weather_compensation": True,
            "flow_rate_method": "fixed_rate",
            "flow_rate": 20,
            "advanced_features": True,
            "diagnostic_monitoring": True,
            "wc_min_outdoor_temp": -8.0,
            "wc_max_outdoor_temp": 20.0,
            "wc_min_flow_temp": 28.0,
            "wc_max_flow_temp": 48.0,
            "boost_min_outdoor_temp": -12.0,
            "boost_max_outdoor_temp": 16.0,
            "boost_min_flow_temp": 38.0,
            "boost_max_flow_temp": 58.0,
        }
        
        # Initialize register manager for testing
        self.register_manager = GrantAerona3RegisterManager(self.basic_config)
        
        # Initialize weather compensation components
        self.wc_primary_config = HeatingCurveConfig(
            name="Primary Curve",
            min_outdoor_temp=-8.0,
            max_outdoor_temp=20.0,
            min_flow_temp=28.0,
            max_flow_temp=48.0,
            curve_type=CurveType.LINEAR
        )
        
        self.wc_boost_config = HeatingCurveConfig(
            name="Boost Curve",
            min_outdoor_temp=-12.0,
            max_outdoor_temp=16.0,
            min_flow_temp=38.0,
            max_flow_temp=58.0,
            curve_type=CurveType.LINEAR
        )

    def test_register_manager_enhanced_features(self):
        """Test register manager with enhanced features enabled."""
        # Should have significantly more registers enabled
        enabled_registers = len(self.register_manager._enabled_registers)
        self.assertGreater(enabled_registers, 30, 
                          f"Should have >30 registers enabled, got {enabled_registers}")
        
        # Check that DHW registers are enabled
        dhw_registers = self.register_manager.get_enabled_registers_by_category(
            RegisterCategory.DHW
        )
        self.assertGreater(len(dhw_registers), 8, 
                          "Should have multiple DHW registers enabled")
        
        # Check that we have all register types
        input_regs = self.register_manager.get_enabled_registers(RegisterType.INPUT)
        holding_regs = self.register_manager.get_enabled_registers(RegisterType.HOLDING)
        coil_regs = self.register_manager.get_enabled_registers(RegisterType.COIL)
        
        self.assertGreater(len(input_regs), 15, "Should have 15+ input registers")
        self.assertGreater(len(holding_regs), 5, "Should have 5+ holding registers")
        self.assertGreater(len(coil_regs), 8, "Should have 8+ coil registers")

    def test_weather_compensation_curves_integration(self):
        """Test weather compensation curves work correctly."""
        primary_curve = LinearHeatingCurve(self.wc_primary_config)
        boost_curve = LinearHeatingCurve(self.wc_boost_config)
        
        # Test at various outdoor temperatures
        test_temperatures = [-10, -5, 0, 5, 10, 15]
        
        for outdoor_temp in test_temperatures:
            primary_flow = primary_curve.calculate_flow_temperature(outdoor_temp)
            boost_flow = boost_curve.calculate_flow_temperature(outdoor_temp)
            
            # Boost should generally give higher flow temperatures
            if -8 <= outdoor_temp <= 16:  # Within both curve operating ranges
                self.assertGreaterEqual(
                    boost_flow, primary_flow,
                    f"Boost should give higher flow temp at {outdoor_temp}°C: "
                    f"primary={primary_flow}°C, boost={boost_flow}°C"
                )
            
            # All temperatures should be reasonable
            self.assertTrue(20 <= primary_flow <= 60, 
                          f"Primary flow temp {primary_flow}°C out of range")
            self.assertTrue(20 <= boost_flow <= 70, 
                          f"Boost flow temp {boost_flow}°C out of range")

    def test_enhanced_register_categorization(self):
        """Test enhanced register categorization."""
        # Test all categories are represented
        categories = [
            RegisterCategory.BASIC,
            RegisterCategory.DHW,
            RegisterCategory.ZONES,
            RegisterCategory.EXTERNAL,
            RegisterCategory.DIAGNOSTIC
        ]
        
        for category in categories:
            category_registers = self.register_manager.get_enabled_registers_by_category(category)
            
            if category == RegisterCategory.BASIC:
                self.assertGreater(len(category_registers), 10, 
                                 f"Should have 10+ {category.value} registers")
            elif category == RegisterCategory.DHW:
                # DHW should be enabled in our config
                self.assertGreater(len(category_registers), 5, 
                                 f"Should have 5+ {category.value} registers")
            elif category == RegisterCategory.ZONES:
                # Zone 1 enabled, zone 2 disabled
                self.assertGreater(len(category_registers), 2, 
                                 f"Should have 2+ {category.value} registers")

    def test_register_addresses_are_valid(self):
        """Test that all register addresses are within valid Modbus ranges."""
        all_registers = self.register_manager._register_definitions
        
        for register_id, register_config in all_registers.items():
            # Modbus addresses should be reasonable
            self.assertTrue(0 <= register_config.address <= 65535, 
                          f"Register {register_id} address {register_config.address} out of range")
            
            # Check scaling factors are reasonable
            self.assertTrue(0.01 <= register_config.scale <= 100, 
                          f"Register {register_id} scale {register_config.scale} seems unreasonable")

    def test_feature_toggle_consistency(self):
        """Test that feature toggles work consistently."""
        # Test with DHW disabled
        config_no_dhw = self.basic_config.copy()
        config_no_dhw["dhw_cylinder"] = False
        
        manager_no_dhw = GrantAerona3RegisterManager(config_no_dhw)
        dhw_registers_disabled = manager_no_dhw.get_enabled_registers_by_category(
            RegisterCategory.DHW
        )
        
        # Should have significantly fewer DHW registers
        dhw_registers_enabled = self.register_manager.get_enabled_registers_by_category(
            RegisterCategory.DHW
        )
        
        self.assertLess(len(dhw_registers_disabled), len(dhw_registers_enabled),
                       "Disabling DHW should reduce number of DHW registers")

    def test_installation_template_register_mapping(self):
        """Test that installation templates correctly map to register sets."""
        templates_to_test = [
            ("single_zone_basic", False, False),  # DHW, backup
            ("single_zone_dhw", True, False),
            ("dual_zone_system", True, True),
        ]
        
        for template, should_have_dhw, should_have_zones in templates_to_test:
            config = self.basic_config.copy()
            config["installation_template"] = template
            config["dhw_cylinder"] = should_have_dhw
            
            # Enable zone 2 for dual zone
            if should_have_zones:
                config["zones"]["zone_2"]["enabled"] = True
            
            manager = GrantAerona3RegisterManager(config)
            
            dhw_count = len(manager.get_enabled_registers_by_category(RegisterCategory.DHW))
            zone_count = len(manager.get_enabled_registers_by_category(RegisterCategory.ZONES))
            
            if should_have_dhw:
                self.assertGreater(dhw_count, 5, 
                                 f"Template {template} should have DHW registers")
            
            if should_have_zones:
                self.assertGreater(zone_count, 4, 
                                 f"Template {template} should have zone registers")

    def test_performance_requirements_met(self):
        """Test that performance requirements are met."""
        import time
        
        # Test register manager initialization performance
        start_time = time.time()
        for _ in range(100):
            manager = GrantAerona3RegisterManager(self.basic_config)
        end_time = time.time()
        
        avg_init_time = (end_time - start_time) / 100
        self.assertLess(avg_init_time, 0.01, 
                       f"Register manager init too slow: {avg_init_time:.4f}s")
        
        # Test weather compensation calculation performance
        primary_curve = LinearHeatingCurve(self.wc_primary_config)
        
        start_time = time.time()
        for i in range(10000):
            temp = -10 + (i * 0.003)  # Range from -10 to 20
            flow_temp = primary_curve.calculate_flow_temperature(temp)
        end_time = time.time()
        
        calc_time = (end_time - start_time) / 10000
        self.assertLess(calc_time, 0.00005, 
                       f"WC calculation too slow: {calc_time:.8f}s")

    def test_data_validation_boundaries(self):
        """Test data validation boundaries."""
        # Test temperature boundary validation
        primary_curve = LinearHeatingCurve(self.wc_primary_config)
        
        # Extreme temperatures should be clamped
        very_cold = primary_curve.calculate_flow_temperature(-50)
        very_hot = primary_curve.calculate_flow_temperature(50)
        
        self.assertEqual(very_cold, self.wc_primary_config.max_flow_temp, 
                        "Very cold outdoor temp should clamp to max flow temp")
        self.assertEqual(very_hot, self.wc_primary_config.min_flow_temp, 
                        "Very hot outdoor temp should clamp to min flow temp")

    def test_curve_validation_logic(self):
        """Test weather compensation curve validation."""
        # Valid configuration should pass
        errors = LinearHeatingCurve(self.wc_primary_config).validate_config()
        self.assertEqual(len(errors), 0, f"Valid config should have no errors: {errors}")
        
        # Invalid configuration should fail
        invalid_config = HeatingCurveConfig(
            name="Invalid",
            min_outdoor_temp=10.0,  # Min > Max (invalid)
            max_outdoor_temp=5.0,
            min_flow_temp=50.0,     # Min > Max (invalid)
            max_flow_temp=30.0,
        )
        
        errors = LinearHeatingCurve(invalid_config).validate_config()
        self.assertGreater(len(errors), 0, "Invalid config should have errors")

    def test_register_enum_mappings(self):
        """Test that register enum mappings work correctly."""
        # Find a register with enum mapping
        all_registers = self.register_manager._register_definitions
        
        enum_register = None
        for register_id, register_config in all_registers.items():
            if register_config.enum_mapping:
                enum_register = register_config
                break
        
        if enum_register:
            # Test that enum mapping values are strings
            for key, value in enum_register.enum_mapping.items():
                self.assertIsInstance(key, int, "Enum keys should be integers")
                self.assertIsInstance(value, str, "Enum values should be strings")

    def run_integration_validation(self):
        """Run comprehensive integration validation."""
        print("=== Enhanced Grant Aerona3 Integration Validation ===")
        
        # 1. Register Management Validation
        print(f"\n1. Register Management:")
        enabled_count = len(self.register_manager._enabled_registers)
        total_count = len(self.register_manager._register_definitions)
        print(f"   - Enabled registers: {enabled_count}/{total_count}")
        
        # Register type breakdown
        type_counts = {}
        for reg_type in RegisterType:
            count = len(self.register_manager.get_enabled_registers(reg_type))
            type_counts[reg_type.value] = count
            print(f"   - {reg_type.value}: {count} registers")
        
        # Category breakdown
        print("\n2. Register Categories:")
        for category in RegisterCategory:
            count = len(self.register_manager.get_enabled_registers_by_category(category))
            print(f"   - {category.value}: {count} registers")
        
        # 3. Weather Compensation Validation
        print("\n3. Weather Compensation:")
        primary_curve = LinearHeatingCurve(self.wc_primary_config)
        boost_curve = LinearHeatingCurve(self.wc_boost_config)
        
        test_temps = [-8, -3, 0, 5, 10, 16, 20]
        print("   Outdoor °C -> Primary °C | Boost °C | Difference")
        for temp in test_temps:
            primary_flow = primary_curve.calculate_flow_temperature(temp)
            boost_flow = boost_curve.calculate_flow_temperature(temp)
            diff = boost_flow - primary_flow
            print(f"   {temp:8.0f} -> {primary_flow:8.1f} | {boost_flow:6.1f} | {diff:+5.1f}")
        
        # 4. Performance Metrics
        print("\n4. Performance Metrics:")
        import time
        
        # Register manager performance
        start_time = time.time()
        for _ in range(1000):
            manager = GrantAerona3RegisterManager(self.basic_config)
        reg_time = (time.time() - start_time) / 1000
        print(f"   - Register manager init: {reg_time:.6f}s avg")
        
        # Weather compensation performance
        start_time = time.time()
        for _ in range(10000):
            primary_curve.calculate_flow_temperature(10.0)
        wc_time = (time.time() - start_time) / 10000
        print(f"   - WC calculation: {wc_time:.8f}s avg")
        print(f"   - WC calculations/sec: {1/wc_time:,.0f}")
        
        # 5. Configuration Validation
        print("\n5. Configuration Features:")
        features = [
            ("DHW Cylinder", self.basic_config.get("dhw_cylinder")),
            ("Weather Compensation", self.basic_config.get("weather_compensation")),
            ("Dual WC Curves", self.basic_config.get("dual_weather_compensation")),
            ("Advanced Features", self.basic_config.get("advanced_features")),
            ("Diagnostic Monitoring", self.basic_config.get("diagnostic_monitoring")),
        ]
        
        for feature_name, enabled in features:
            status = "✓ Enabled" if enabled else "✗ Disabled"
            print(f"   - {feature_name}: {status}")
        
        print("\n✅ Enhanced Integration validation completed successfully!")


def main():
    """Run the enhanced integration tests."""
    print("Running Grant Aerona3 Enhanced Integration Tests...")
    print("=" * 60)
    
    # Run unit tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEnhancedIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\n✅ All unit tests passed!")
        
        # Run integration validation
        test_instance = TestEnhancedIntegration()
        test_instance.setUp()
        test_instance.run_integration_validation()
        
        return True
    else:
        print("\n❌ Some tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)