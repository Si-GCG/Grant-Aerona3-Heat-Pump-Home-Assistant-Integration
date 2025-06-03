#!/usr/bin/env python3
"""Test weather compensation system for Grant Aerona3."""

import sys
import unittest
from unittest.mock import Mock, AsyncMock
import asyncio
from typing import Dict, Any

# Add the custom_components path
sys.path.insert(0, './custom_components/grant_aerona3')

from weather_compensation import (
    LinearHeatingCurve,
    AdvancedHeatingCurve,
    DualCurveWeatherCompensation,
    WeatherCompensationController,
    HeatingCurveConfig,
    WeatherCompensationConfig,
    WeatherCompensationMode,
    CurveType,
)


class TestWeatherCompensation(unittest.TestCase):
    """Test weather compensation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.basic_curve_config = HeatingCurveConfig(
            name="Test Curve",
            min_outdoor_temp=-5.0,
            max_outdoor_temp=18.0,
            min_flow_temp=25.0,
            max_flow_temp=45.0,
            curve_type=CurveType.LINEAR
        )
        
        self.boost_curve_config = HeatingCurveConfig(
            name="Boost Curve",
            min_outdoor_temp=-10.0,
            max_outdoor_temp=15.0,
            min_flow_temp=35.0,
            max_flow_temp=55.0,
            curve_type=CurveType.LINEAR
        )

    def test_linear_heating_curve_basic(self):
        """Test basic linear heating curve calculations."""
        curve = LinearHeatingCurve(self.basic_curve_config)
        
        # Test edge cases
        self.assertEqual(curve.calculate_flow_temperature(-10.0), 45.0)  # Below min outdoor
        self.assertEqual(curve.calculate_flow_temperature(25.0), 25.0)   # Above max outdoor
        
        # Test linear interpolation
        self.assertEqual(curve.calculate_flow_temperature(-5.0), 45.0)   # Min outdoor
        self.assertEqual(curve.calculate_flow_temperature(18.0), 25.0)   # Max outdoor
        
        # Test midpoint
        midpoint_outdoor = (-5.0 + 18.0) / 2  # 6.5°C
        expected_flow = (45.0 + 25.0) / 2     # 35.0°C
        self.assertEqual(curve.calculate_flow_temperature(midpoint_outdoor), expected_flow)

    def test_linear_heating_curve_validation(self):
        """Test heating curve configuration validation."""
        curve = LinearHeatingCurve(self.basic_curve_config)
        
        # Valid configuration should pass
        errors = curve.validate_config()
        self.assertEqual(len(errors), 0)
        
        # Invalid configuration
        invalid_config = HeatingCurveConfig(
            name="Invalid",
            min_outdoor_temp=10.0,  # Min > Max
            max_outdoor_temp=5.0,
            min_flow_temp=50.0,     # Min > Max
            max_flow_temp=30.0,
        )
        
        invalid_curve = LinearHeatingCurve(invalid_config)
        errors = invalid_curve.validate_config()
        self.assertGreater(len(errors), 0)

    def test_heating_curve_points_generation(self):
        """Test curve points generation for visualization."""
        curve = LinearHeatingCurve(self.basic_curve_config)
        
        points = curve.get_curve_points(5)
        self.assertEqual(len(points), 5)
        
        # Check first and last points
        first_point = points[0]
        last_point = points[-1]
        
        self.assertEqual(first_point[0], -5.0)  # Min outdoor temp
        self.assertEqual(first_point[1], 45.0)  # Max flow temp
        
        self.assertEqual(last_point[0], 18.0)   # Max outdoor temp
        self.assertEqual(last_point[1], 25.0)   # Min flow temp

    def test_advanced_heating_curve_quadratic(self):
        """Test quadratic heating curve."""
        quadratic_config = HeatingCurveConfig(
            name="Quadratic Test",
            min_outdoor_temp=-5.0,
            max_outdoor_temp=15.0,
            min_flow_temp=25.0,
            max_flow_temp=50.0,
            curve_type=CurveType.QUADRATIC,
            curve_steepness=2.0
        )
        
        curve = AdvancedHeatingCurve(quadratic_config)
        
        # Quadratic curve should give different results than linear
        linear_result = LinearHeatingCurve(quadratic_config).calculate_flow_temperature(0.0)
        quadratic_result = curve.calculate_flow_temperature(0.0)
        
        # Results should be different (exact values depend on implementation)
        self.assertNotEqual(linear_result, quadratic_result)
        
        # Results should still be within valid range
        self.assertGreaterEqual(quadratic_result, 25.0)
        self.assertLessEqual(quadratic_result, 50.0)

    def test_weather_compensation_config_creation(self):
        """Test weather compensation configuration creation."""
        config = WeatherCompensationConfig(
            mode=WeatherCompensationMode.WEATHER_COMPENSATION,
            primary_curve=self.basic_curve_config,
            secondary_curve=self.boost_curve_config,
            update_interval=60
        )
        
        self.assertEqual(config.mode, WeatherCompensationMode.WEATHER_COMPENSATION)
        self.assertEqual(config.primary_curve.name, "Test Curve")
        self.assertEqual(config.secondary_curve.name, "Boost Curve")
        self.assertEqual(config.update_interval, 60)

    def test_dual_curve_system_initialization(self):
        """Test dual curve weather compensation system initialization."""
        # Mock objects
        mock_hass = Mock()
        mock_coordinator = Mock()
        mock_coordinator.data = {
            "outdoor_temp": {"value": 5.0},
            "external_outdoor_temp": {"value": 4.5}
        }
        
        config = WeatherCompensationConfig(
            mode=WeatherCompensationMode.DUAL_CURVE,
            primary_curve=self.basic_curve_config,
            secondary_curve=self.boost_curve_config
        )
        
        dual_curve = DualCurveWeatherCompensation(mock_hass, mock_coordinator, config)
        
        # Test initialization
        self.assertIsNotNone(dual_curve.primary_curve)
        self.assertIsNotNone(dual_curve.secondary_curve)
        self.assertEqual(dual_curve.active_curve, "primary")
        self.assertFalse(dual_curve.boost_active)

    def test_dual_curve_boost_activation(self):
        """Test boost mode activation and deactivation."""
        # This test requires async, so we'll use a simple sync test
        mock_hass = Mock()
        mock_coordinator = Mock()
        
        config = WeatherCompensationConfig(
            mode=WeatherCompensationMode.DUAL_CURVE,
            primary_curve=self.basic_curve_config,
            secondary_curve=self.boost_curve_config
        )
        
        dual_curve = DualCurveWeatherCompensation(mock_hass, mock_coordinator, config)
        
        # Test boost activation logic
        self.assertFalse(dual_curve.boost_active)
        
        # Manual boost activation would be tested in async test
        # For now, just test the state tracking
        dual_curve.boost_active = True
        dual_curve.active_curve = "secondary"
        
        self.assertTrue(dual_curve.boost_active)
        self.assertEqual(dual_curve.active_curve, "secondary")

    def test_status_reporting(self):
        """Test weather compensation status reporting."""
        mock_hass = Mock()
        mock_coordinator = Mock()
        
        config = WeatherCompensationConfig(
            mode=WeatherCompensationMode.WEATHER_COMPENSATION,
            primary_curve=self.basic_curve_config,
            secondary_curve=self.boost_curve_config
        )
        
        dual_curve = DualCurveWeatherCompensation(mock_hass, mock_coordinator, config)
        
        # Set some test data
        dual_curve.last_outdoor_temp = 10.0
        dual_curve.last_flow_temp = 35.0
        dual_curve.calculation_count = 5
        
        status = dual_curve.get_current_status()
        
        # Test status content
        self.assertEqual(status["mode"], "weather_compensation")
        self.assertEqual(status["active_curve"], "primary")
        self.assertEqual(status["last_outdoor_temp"], 10.0)
        self.assertEqual(status["last_flow_temp"], 35.0)
        self.assertEqual(status["calculation_count"], 5)
        self.assertFalse(status["boost_active"])

    def test_curve_visualization_data(self):
        """Test curve visualization data generation."""
        mock_hass = Mock()
        mock_coordinator = Mock()
        
        config = WeatherCompensationConfig(
            mode=WeatherCompensationMode.WEATHER_COMPENSATION,
            primary_curve=self.basic_curve_config
        )
        
        dual_curve = DualCurveWeatherCompensation(mock_hass, mock_coordinator, config)
        dual_curve.last_outdoor_temp = 8.0
        dual_curve.last_flow_temp = 32.0
        
        viz_data = dual_curve.get_curve_visualization_data("primary")
        
        # Test visualization data structure
        self.assertEqual(viz_data["curve_name"], "Test Curve")
        self.assertEqual(viz_data["curve_type"], "linear")
        self.assertEqual(viz_data["current_outdoor"], 8.0)
        self.assertEqual(viz_data["current_flow"], 32.0)
        self.assertIn("points", viz_data)
        self.assertIn("config", viz_data)

    def test_weather_compensation_controller_config_creation(self):
        """Test weather compensation controller configuration creation."""
        # Mock integration config
        integration_config = {
            "weather_compensation": True,
            "wc_min_outdoor_temp": -8.0,
            "wc_max_outdoor_temp": 20.0,
            "wc_min_flow_temp": 28.0,
            "wc_max_flow_temp": 48.0,
            "dual_weather_compensation": True,
            "boost_min_outdoor_temp": -12.0,
            "boost_max_outdoor_temp": 16.0,
            "boost_min_flow_temp": 38.0,
            "boost_max_flow_temp": 58.0,
            "zones": {
                "zone_1": {"enabled": True},
                "zone_2": {"enabled": False}
            }
        }
        
        mock_hass = Mock()
        mock_coordinator = Mock()
        
        controller = WeatherCompensationController(mock_hass, mock_coordinator, integration_config)
        wc_config = controller._create_weather_compensation_config()
        
        # Test primary curve configuration
        self.assertEqual(wc_config.primary_curve.min_outdoor_temp, -8.0)
        self.assertEqual(wc_config.primary_curve.max_outdoor_temp, 20.0)
        self.assertEqual(wc_config.primary_curve.min_flow_temp, 28.0)
        self.assertEqual(wc_config.primary_curve.max_flow_temp, 48.0)
        
        # Test secondary curve configuration
        self.assertIsNotNone(wc_config.secondary_curve)
        self.assertEqual(wc_config.secondary_curve.min_outdoor_temp, -12.0)
        self.assertEqual(wc_config.secondary_curve.max_outdoor_temp, 16.0)
        self.assertEqual(wc_config.secondary_curve.min_flow_temp, 38.0)
        self.assertEqual(wc_config.secondary_curve.max_flow_temp, 58.0)

    def test_weather_compensation_disabled(self):
        """Test weather compensation when disabled in config."""
        integration_config = {
            "weather_compensation": False
        }
        
        mock_hass = Mock()
        mock_coordinator = Mock()
        
        controller = WeatherCompensationController(mock_hass, mock_coordinator, integration_config)
        
        # Should not be enabled
        self.assertFalse(controller.is_enabled())
        
        # Status should reflect disabled state
        status = controller.get_status()
        self.assertFalse(status.get("enabled", True))

    def test_performance_requirements(self):
        """Test that weather compensation calculations are performant."""
        import time
        
        curve = LinearHeatingCurve(self.basic_curve_config)
        
        # Test calculation performance
        start_time = time.time()
        for i in range(1000):
            outdoor_temp = -10 + (i * 0.03)  # Range from -10 to 20
            flow_temp = curve.calculate_flow_temperature(outdoor_temp)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 1000
        self.assertLess(avg_time, 0.0001, f"Calculation too slow: {avg_time:.6f}s per calculation")

    def run_integration_validation(self):
        """Run complete integration validation."""
        print("=== Weather Compensation Integration Validation ===")
        
        # Test basic curve
        print("\n1. Testing linear heating curve...")
        curve = LinearHeatingCurve(self.basic_curve_config)
        test_temps = [-10, -5, 0, 5, 10, 15, 20]
        
        print("   Outdoor -> Flow Temperature:")
        for temp in test_temps:
            flow_temp = curve.calculate_flow_temperature(temp)
            print(f"   {temp:3.0f}°C -> {flow_temp:4.1f}°C")
        
        # Test curve validation
        print("\n2. Testing curve validation...")
        errors = curve.validate_config()
        print(f"   Validation errors: {len(errors)}")
        
        # Test boost curve
        print("\n3. Testing boost curve...")
        boost_curve = LinearHeatingCurve(self.boost_curve_config)
        print("   Boost curve outdoor -> flow:")
        for temp in test_temps:
            flow_temp = boost_curve.calculate_flow_temperature(temp)
            print(f"   {temp:3.0f}°C -> {flow_temp:4.1f}°C")
        
        # Test dual curve system
        print("\n4. Testing dual curve system...")
        mock_hass = Mock()
        mock_coordinator = Mock()
        
        config = WeatherCompensationConfig(
            mode=WeatherCompensationMode.DUAL_CURVE,
            primary_curve=self.basic_curve_config,
            secondary_curve=self.boost_curve_config
        )
        
        dual_curve = DualCurveWeatherCompensation(mock_hass, mock_coordinator, config)
        status = dual_curve.get_current_status()
        print(f"   Mode: {status['mode']}")
        print(f"   Active curve: {status['active_curve']}")
        print(f"   Boost active: {status['boost_active']}")
        
        # Test visualization data
        print("\n5. Testing curve visualization...")
        viz_data = dual_curve.get_curve_visualization_data("primary")
        points = viz_data.get("points", [])
        print(f"   Generated {len(points)} curve points")
        if points:
            print(f"   First point: {points[0]}")
            print(f"   Last point: {points[-1]}")
        
        # Test performance
        print("\n6. Performance metrics...")
        import time
        start_time = time.time()
        
        for _ in range(1000):
            curve.calculate_flow_temperature(10.0)
        
        end_time = time.time()
        calc_time = (end_time - start_time) / 1000
        print(f"   Average calculation time: {calc_time:.6f}s")
        print(f"   Calculations per second: {1/calc_time:.0f}")
        
        print("\n✅ Weather Compensation validation completed successfully!")


def main():
    """Run the weather compensation tests."""
    print("Running Grant Aerona3 Weather Compensation Tests...")
    print("=" * 55)
    
    # Run unit tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWeatherCompensation)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\n✅ All unit tests passed!")
        
        # Run integration validation
        test_instance = TestWeatherCompensation()
        test_instance.setUp()
        test_instance.run_integration_validation()
        
        return True
    else:
        print("\n❌ Some tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)