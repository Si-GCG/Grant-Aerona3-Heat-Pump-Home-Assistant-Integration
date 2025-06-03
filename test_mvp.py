#!/usr/bin/env python3
"""Basic MVP test for Grant Aerona3 Enhanced Integration."""

import sys
import unittest
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any

# Add the custom_components path
sys.path.insert(0, './custom_components/grant_aerona3')

from register_manager import (
    GrantAerona3RegisterManager,
    RegisterType,
    RegisterCategory,
    RegisterConfig
)
from enhanced_config_flow import INSTALLATION_TEMPLATES


class TestGrantAerona3MVP(unittest.TestCase):
    """Test cases for Grant Aerona3 MVP functionality."""
    
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
        
        self.dhw_config = {
            "host": "192.168.1.100",
            "port": 502,
            "slave_id": 1,
            "scan_interval": 30,
            "installation_template": "single_zone_dhw",
            "zones": {
                "zone_1": {"enabled": True, "name": "Main Zone"},
                "zone_2": {"enabled": False, "name": "Second Zone"}
            },
            "dhw_cylinder": True,
            "backup_heater": True,
            "weather_compensation": True,
            "flow_rate_method": "fixed_rate",
            "flow_rate": 22,
            "advanced_features": False,
            "diagnostic_monitoring": False
        }

    def test_installation_templates_available(self):
        """Test that installation templates are properly defined."""
        self.assertIn("single_zone_basic", INSTALLATION_TEMPLATES)
        self.assertIn("single_zone_dhw", INSTALLATION_TEMPLATES)
        self.assertIn("dual_zone_system", INSTALLATION_TEMPLATES)
        self.assertIn("replacement_system", INSTALLATION_TEMPLATES)
        
        # Test template structure
        template = INSTALLATION_TEMPLATES["single_zone_basic"]
        self.assertEqual(template.name, "Basic Single Zone")
        self.assertTrue(template.common)
        self.assertIn("zones", template.default_config)

    def test_register_manager_basic_config(self):
        """Test register manager with basic single zone configuration."""
        manager = GrantAerona3RegisterManager(self.basic_config)
        
        # Test that basic registers are enabled
        enabled_registers = manager.get_enabled_registers()
        self.assertGreater(len(enabled_registers), 0)
        
        # Test that basic category registers are always enabled
        basic_registers = manager.get_enabled_registers(RegisterType.INPUT)
        basic_register_found = False
        for register_id, register_config in basic_registers.items():
            if register_config.category == RegisterCategory.BASIC:
                basic_register_found = True
                break
        self.assertTrue(basic_register_found, "No basic registers found")
        
        # Test that DHW registers are NOT enabled for basic config
        dhw_registers = [
            reg_id for reg_id, reg_config in enabled_registers.items()
            if reg_config.category == RegisterCategory.DHW
        ]
        self.assertEqual(len(dhw_registers), 0, "DHW registers should not be enabled for basic config")

    def test_register_manager_dhw_config(self):
        """Test register manager with DHW configuration."""
        manager = GrantAerona3RegisterManager(self.dhw_config)
        
        enabled_registers = manager.get_enabled_registers()
        
        # Test that DHW registers ARE enabled for DHW config
        dhw_registers = [
            reg_id for reg_id, reg_config in enabled_registers.items()
            if reg_config.category == RegisterCategory.DHW
        ]
        self.assertGreater(len(dhw_registers), 0, "DHW registers should be enabled for DHW config")
        
        # Test specific DHW registers
        input_registers = manager.get_enabled_registers(RegisterType.INPUT)
        dhw_register_ids = [reg_id for reg_id in input_registers.keys()]
        
        # Should include DHW-related registers
        expected_dhw_registers = ["dhw_mode", "dhw_temp"]
        for expected in expected_dhw_registers:
            self.assertIn(expected, dhw_register_ids, f"Expected DHW register {expected} not found")

    def test_register_manager_zone_2_disabled(self):
        """Test that zone 2 registers are disabled when zone 2 is disabled."""
        manager = GrantAerona3RegisterManager(self.basic_config)
        
        enabled_registers = manager.get_enabled_registers()
        
        # Zone 2 registers should not be enabled
        zone2_registers = [
            reg_id for reg_id, reg_config in enabled_registers.items()
            if reg_config.requires_feature == "zones.zone_2.enabled"
        ]
        self.assertEqual(len(zone2_registers), 0, "Zone 2 registers should not be enabled")

    def test_register_manager_zone_2_enabled(self):
        """Test that zone 2 registers are enabled when zone 2 is enabled."""
        dual_zone_config = self.basic_config.copy()
        dual_zone_config["zones"]["zone_2"]["enabled"] = True
        
        manager = GrantAerona3RegisterManager(dual_zone_config)
        enabled_registers = manager.get_enabled_registers()
        
        # Zone 2 registers should be enabled
        zone2_registers = [
            reg_id for reg_id, reg_config in enabled_registers.items()
            if reg_config.requires_feature == "zones.zone_2.enabled"
        ]
        self.assertGreater(len(zone2_registers), 0, "Zone 2 registers should be enabled")

    def test_register_config_validation(self):
        """Test register configuration validation."""
        manager = GrantAerona3RegisterManager(self.basic_config)
        
        # Test basic register properties
        enabled_registers = manager.get_enabled_registers(RegisterType.INPUT)
        
        for register_id, register_config in enabled_registers.items():
            # Test required properties
            self.assertIsInstance(register_config.address, int)
            self.assertIsInstance(register_config.name, str)
            self.assertIsInstance(register_config.register_type, RegisterType)
            self.assertIsInstance(register_config.category, RegisterCategory)
            
            # Test address ranges
            self.assertGreaterEqual(register_config.address, 0)
            self.assertLessEqual(register_config.address, 65535)

    def test_register_address_uniqueness(self):
        """Test that register addresses are unique within each type."""
        manager = GrantAerona3RegisterManager(self.basic_config)
        
        for register_type in RegisterType:
            registers = manager.get_enabled_registers(register_type)
            addresses = [reg_config.address for reg_config in registers.values()]
            
            # Check for duplicates
            unique_addresses = set(addresses)
            self.assertEqual(
                len(addresses), 
                len(unique_addresses),
                f"Duplicate addresses found in {register_type.value} registers"
            )

    def test_feature_enablement_logic(self):
        """Test the feature enablement logic."""
        manager = GrantAerona3RegisterManager(self.basic_config)
        
        # Test basic features
        self.assertTrue(manager._is_feature_enabled("weather_compensation"))
        self.assertFalse(manager._is_feature_enabled("dhw_cylinder"))
        self.assertFalse(manager._is_feature_enabled("backup_heater"))
        
        # Test nested features
        self.assertTrue(manager._is_feature_enabled("zones.zone_1.enabled"))
        self.assertFalse(manager._is_feature_enabled("zones.zone_2.enabled"))

    def test_register_type_separation(self):
        """Test that different register types are properly separated."""
        manager = GrantAerona3RegisterManager(self.basic_config)
        
        input_registers = manager.get_enabled_registers(RegisterType.INPUT)
        holding_registers = manager.get_enabled_registers(RegisterType.HOLDING)
        coil_registers = manager.get_enabled_registers(RegisterType.COIL)
        
        # All should be non-empty for basic config
        self.assertGreater(len(input_registers), 0, "No input registers enabled")
        self.assertGreater(len(holding_registers), 0, "No holding registers enabled")
        self.assertGreater(len(coil_registers), 0, "No coil registers enabled")
        
        # Check that register IDs don't overlap between types
        all_register_ids = set()
        for registers in [input_registers, holding_registers, coil_registers]:
            register_ids = set(registers.keys())
            overlap = all_register_ids.intersection(register_ids)
            self.assertEqual(len(overlap), 0, f"Register ID overlap found: {overlap}")
            all_register_ids.update(register_ids)

    def test_config_migration_logic(self):
        """Test configuration migration from v1 to v2."""
        # Import the migration function
        from enhanced_init import _migrate_config_v1_to_v2
        
        # Create old v1 config
        old_config = {
            "host": "192.168.1.100",
            "port": 502,
            "slave_id": 1,
            "scan_interval": 30
        }
        
        # Migrate to v2
        new_config = _migrate_config_v1_to_v2(old_config)
        
        # Test that required v2 fields are added
        self.assertIn("installation_template", new_config)
        self.assertIn("zones", new_config)
        self.assertIn("config_version", new_config)
        self.assertEqual(new_config["config_version"], 2)
        
        # Test zone structure
        self.assertIn("zone_1", new_config["zones"])
        self.assertTrue(new_config["zones"]["zone_1"]["enabled"])

    def test_performance_requirements(self):
        """Test that performance requirements are met."""
        manager = GrantAerona3RegisterManager(self.basic_config)
        
        # Test that register manager initialization is fast
        import time
        start_time = time.time()
        
        for _ in range(10):
            test_manager = GrantAerona3RegisterManager(self.basic_config)
            enabled_registers = test_manager.get_enabled_registers()
        
        end_time = time.time()
        avg_time = (end_time - start_time) / 10
        
        # Should initialize in under 10ms
        self.assertLess(avg_time, 0.01, f"Register manager initialization too slow: {avg_time:.4f}s")

    def run_integration_validation(self):
        """Run complete integration validation."""
        print("=== Grant Aerona3 MVP Integration Validation ===")
        
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
        
        print("\n5. Installation templates:")
        for template_id, template in INSTALLATION_TEMPLATES.items():
            print(f"   - {template_id}: {template.name} ({template.percentage})")
        
        print("\n✅ MVP Integration validation completed successfully!")


def main():
    """Run the MVP tests."""
    # Run unit tests
    print("Running Grant Aerona3 MVP Unit Tests...")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGrantAerona3MVP)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\n✅ All unit tests passed!")
        
        # Run integration validation
        test_instance = TestGrantAerona3MVP()
        test_instance.setUp()
        test_instance.run_integration_validation()
        
        return True
    else:
        print("\n❌ Some tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)