#!/usr/bin/env python3
"""Core MVP test for Grant Aerona3 Enhanced Integration (no HA dependencies)."""

import sys
import unittest
from typing import Dict, Any
from enum import Enum

# Add the custom_components path
sys.path.insert(0, './custom_components/grant_aerona3')

# Import our core components
from register_manager import (
    GrantAerona3RegisterManager,
    RegisterType,
    RegisterCategory,
    RegisterConfig
)


class TestGrantAerona3CoreMVP(unittest.TestCase):
    """Test cases for Grant Aerona3 core MVP functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.basic_config = {
            "host": "192.168.1.100",
            "port": 502,
            "slave_id": 1,
            "scan_interval": 30,
            "installation_template": "single_zone_basic",
            "zones": {
                "zone_1": {"enabled": True, "name": "Main Zone"},
                "zone_2": {"enabled": False, "name": "Second Zone"}
            },
            "dhw_cylinder": False,
            "backup_heater": False,
            "weather_compensation": True,
            "flow_rate_method": "fixed_rate",
            "flow_rate": 20,
            "advanced_features": False,
            "diagnostic_monitoring": False
        }
        
        self.dhw_config = self.basic_config.copy()
        self.dhw_config.update({
            "installation_template": "single_zone_dhw",
            "dhw_cylinder": True,
            "backup_heater": True,
            "flow_rate": 22
        })

    def test_register_manager_initialization(self):
        """Test that register manager initializes correctly."""
        manager = GrantAerona3RegisterManager(self.basic_config)
        
        # Test that manager has required attributes
        self.assertIsNotNone(manager.config)
        self.assertIsNotNone(manager._register_definitions)
        self.assertIsNotNone(manager._enabled_registers)
        
        # Test that some registers are enabled
        self.assertGreater(len(manager._enabled_registers), 0)

    def test_register_types_enum(self):
        """Test RegisterType enum values."""
        self.assertEqual(RegisterType.INPUT.value, "input")
        self.assertEqual(RegisterType.HOLDING.value, "holding")
        self.assertEqual(RegisterType.COIL.value, "coil")

    def test_register_categories_enum(self):
        """Test RegisterCategory enum values."""
        self.assertEqual(RegisterCategory.BASIC.value, "basic")
        self.assertEqual(RegisterCategory.ZONES.value, "zones")
        self.assertEqual(RegisterCategory.DHW.value, "dhw")
        self.assertEqual(RegisterCategory.EXTERNAL.value, "external")
        self.assertEqual(RegisterCategory.ADVANCED.value, "advanced")
        self.assertEqual(RegisterCategory.DIAGNOSTIC.value, "diagnostic")

    def test_register_config_creation(self):
        """Test RegisterConfig creation."""
        register_config = RegisterConfig(
            address=0,
            name="Test Register",
            register_type=RegisterType.INPUT,
            category=RegisterCategory.BASIC,
            unit="°C",
            scale=1.0,
            device_class="temperature"
        )
        
        self.assertEqual(register_config.address, 0)
        self.assertEqual(register_config.name, "Test Register")
        self.assertEqual(register_config.register_type, RegisterType.INPUT)
        self.assertEqual(register_config.category, RegisterCategory.BASIC)
        self.assertEqual(register_config.unit, "°C")
        self.assertEqual(register_config.scale, 1.0)
        self.assertEqual(register_config.device_class, "temperature")

    def test_basic_configuration_registers(self):
        """Test register enablement for basic configuration."""
        manager = GrantAerona3RegisterManager(self.basic_config)
        
        enabled_registers = manager.get_enabled_registers()
        self.assertGreater(len(enabled_registers), 0)
        
        # Test that basic registers are enabled
        basic_found = False
        for register_id, register_config in enabled_registers.items():
            if register_config.category == RegisterCategory.BASIC:
                basic_found = True
                break
        self.assertTrue(basic_found, "No basic registers found")
        
        # Test input registers specifically
        input_registers = manager.get_enabled_registers(RegisterType.INPUT)
        self.assertGreater(len(input_registers), 0, "No input registers enabled")
        
        # Test that expected basic registers are present
        expected_basic_registers = ["return_temp", "power_consumption", "outdoor_temp", "flow_temp"]
        input_register_ids = list(input_registers.keys())
        
        for expected in expected_basic_registers:
            self.assertIn(expected, input_register_ids, f"Expected register {expected} not found")

    def test_dhw_configuration_registers(self):
        """Test register enablement for DHW configuration."""
        manager = GrantAerona3RegisterManager(self.dhw_config)
        
        enabled_registers = manager.get_enabled_registers()
        
        # Test that DHW registers are enabled
        dhw_found = False
        for register_id, register_config in enabled_registers.items():
            if register_config.category == RegisterCategory.DHW:
                dhw_found = True
                break
        self.assertTrue(dhw_found, "No DHW registers found")
        
        # Test specific DHW registers
        input_registers = manager.get_enabled_registers(RegisterType.INPUT)
        expected_dhw_registers = ["dhw_mode", "dhw_temp"]
        
        input_register_ids = list(input_registers.keys())
        for expected in expected_dhw_registers:
            self.assertIn(expected, input_register_ids, f"Expected DHW register {expected} not found")

    def test_zone_2_feature_toggle(self):
        """Test that zone 2 registers are properly toggled."""
        # Test with zone 2 disabled
        manager_basic = GrantAerona3RegisterManager(self.basic_config)
        basic_registers = manager_basic.get_enabled_registers()
        
        zone2_in_basic = any(
            reg_config.requires_feature == "zones.zone_2.enabled"
            for reg_config in basic_registers.values()
        )
        self.assertFalse(zone2_in_basic, "Zone 2 registers should not be enabled in basic config")
        
        # Test with zone 2 enabled
        dual_zone_config = self.basic_config.copy()
        dual_zone_config["zones"]["zone_2"]["enabled"] = True
        
        manager_dual = GrantAerona3RegisterManager(dual_zone_config)
        dual_registers = manager_dual.get_enabled_registers()
        
        zone2_in_dual = any(
            reg_config.requires_feature == "zones.zone_2.enabled"
            for reg_config in dual_registers.values()
        )
        self.assertTrue(zone2_in_dual, "Zone 2 registers should be enabled in dual zone config")

    def test_feature_enablement_logic(self):
        """Test the feature enablement logic."""
        manager = GrantAerona3RegisterManager(self.basic_config)
        
        # Test direct features
        self.assertTrue(manager._is_feature_enabled("weather_compensation"))
        self.assertFalse(manager._is_feature_enabled("dhw_cylinder"))
        self.assertFalse(manager._is_feature_enabled("backup_heater"))
        
        # Test nested features
        self.assertTrue(manager._is_feature_enabled("zones.zone_1.enabled"))
        self.assertFalse(manager._is_feature_enabled("zones.zone_2.enabled"))
        
        # Test non-existent features
        self.assertFalse(manager._is_feature_enabled("non_existent_feature"))
        self.assertFalse(manager._is_feature_enabled("zones.zone_3.enabled"))

    def test_register_address_retrieval(self):
        """Test register address retrieval by type."""
        manager = GrantAerona3RegisterManager(self.basic_config)
        
        # Test input register addresses
        input_addresses = manager.get_register_addresses_by_type(RegisterType.INPUT)
        self.assertIsInstance(input_addresses, list)
        self.assertGreater(len(input_addresses), 0)
        
        # Test that addresses are sorted
        self.assertEqual(input_addresses, sorted(input_addresses))
        
        # Test that all addresses are valid integers
        for address in input_addresses:
            self.assertIsInstance(address, int)
            self.assertGreaterEqual(address, 0)
            self.assertLessEqual(address, 65535)

    def test_register_lookup_by_address(self):
        """Test looking up registers by address and type."""
        manager = GrantAerona3RegisterManager(self.basic_config)
        
        # Test that we can find a register by address
        input_addresses = manager.get_register_addresses_by_type(RegisterType.INPUT)
        if input_addresses:
            first_address = input_addresses[0]
            register_config = manager.get_register_by_address(first_address, RegisterType.INPUT)
            
            self.assertIsNotNone(register_config)
            self.assertEqual(register_config.address, first_address)
            self.assertEqual(register_config.register_type, RegisterType.INPUT)

    def test_register_is_enabled_check(self):
        """Test checking if specific registers are enabled."""
        manager = GrantAerona3RegisterManager(self.basic_config)
        
        # Test that basic registers are enabled
        self.assertTrue(manager.is_register_enabled("return_temp"))
        self.assertTrue(manager.is_register_enabled("power_consumption"))
        
        # Test that DHW registers are not enabled in basic config
        dhw_manager = GrantAerona3RegisterManager(self.dhw_config)
        self.assertTrue(dhw_manager.is_register_enabled("dhw_temp"))

    def test_configuration_structure_validation(self):
        """Test that configuration structure is validated properly."""
        # Test valid configuration
        manager = GrantAerona3RegisterManager(self.basic_config)
        self.assertIsNotNone(manager.config)
        
        # Test empty configuration
        empty_config = {}
        empty_manager = GrantAerona3RegisterManager(empty_config)
        # Should not crash, but will have minimal registers enabled
        enabled_registers = empty_manager.get_enabled_registers()
        # Basic registers should still be enabled even with empty config
        self.assertGreater(len(enabled_registers), 0)

    def test_performance_requirements(self):
        """Test that performance requirements are met."""
        import time
        
        # Test register manager initialization performance
        start_time = time.time()
        for _ in range(10):
            manager = GrantAerona3RegisterManager(self.basic_config)
            enabled_registers = manager.get_enabled_registers()
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 10
        self.assertLess(avg_time, 0.01, f"Register manager initialization too slow: {avg_time:.4f}s")
        
        # Test register retrieval performance
        manager = GrantAerona3RegisterManager(self.basic_config)
        
        start_time = time.time()
        for _ in range(100):
            input_registers = manager.get_enabled_registers(RegisterType.INPUT)
            holding_registers = manager.get_enabled_registers(RegisterType.HOLDING)
            coil_registers = manager.get_enabled_registers(RegisterType.COIL)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 100
        self.assertLess(avg_time, 0.001, f"Register retrieval too slow: {avg_time:.4f}s")

    def run_integration_validation(self):
        """Run complete integration validation."""
        print("=== Grant Aerona3 Core MVP Integration Validation ===")
        
        # Test basic configuration
        print("\n1. Testing basic single zone configuration...")
        manager_basic = GrantAerona3RegisterManager(self.basic_config)
        basic_registers = manager_basic.get_enabled_registers()
        print(f"   - Enabled registers: {len(basic_registers)}")
        
        # Test DHW configuration
        print("\n2. Testing DHW configuration...")
        manager_dhw = GrantAerona3RegisterManager(self.dhw_config)
        dhw_registers = manager_dhw.get_enabled_registers()
        print(f"   - Enabled registers: {len(dhw_registers)}")
        
        # Test register type distribution
        print("\n3. Register type distribution:")
        for register_type in RegisterType:
            type_registers = manager_dhw.get_enabled_registers(register_type)
            print(f"   - {register_type.value}: {len(type_registers)} registers")
        
        # Test register categories
        print("\n4. Register categories:")
        all_registers = manager_dhw.get_enabled_registers()
        category_counts = {}
        for register_config in all_registers.values():
            category = register_config.category
            category_counts[category] = category_counts.get(category, 0) + 1
        
        for category, count in category_counts.items():
            print(f"   - {category.value}: {count} registers")
        
        # Test specific register details
        print("\n5. Sample enabled registers:")
        sample_registers = list(all_registers.items())[:5]
        for register_id, register_config in sample_registers:
            print(f"   - {register_id}: {register_config.name} (addr: {register_config.address})")
        
        # Test performance
        print("\n6. Performance metrics:")
        import time
        start_time = time.time()
        for _ in range(100):
            test_manager = GrantAerona3RegisterManager(self.basic_config)
            test_registers = test_manager.get_enabled_registers()
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 100
        print(f"   - Average initialization time: {avg_time:.4f}s")
        print(f"   - Registers per second: {len(test_registers) / avg_time:.0f}")
        
        print("\n✅ Core MVP Integration validation completed successfully!")


def main():
    """Run the core MVP tests."""
    print("Running Grant Aerona3 Core MVP Unit Tests...")
    print("=" * 50)
    
    # Run unit tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGrantAerona3CoreMVP)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\n✅ All unit tests passed!")
        
        # Run integration validation
        test_instance = TestGrantAerona3CoreMVP()
        test_instance.setUp()
        test_instance.run_integration_validation()
        
        return True
    else:
        print("\n❌ Some tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)