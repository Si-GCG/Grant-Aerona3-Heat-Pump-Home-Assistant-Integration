#!/usr/bin/env python3
"""Core weather compensation test (no HA dependencies)."""

import sys
import unittest
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Tuple

# Minimal implementations to test core logic without HA dependencies

class CurveType(Enum):
    """Heating curve types."""
    LINEAR = "linear"
    QUADRATIC = "quadratic"
    CUSTOM = "custom"


@dataclass
class HeatingCurveConfig:
    """Configuration for a heating curve."""
    name: str
    min_outdoor_temp: float
    max_outdoor_temp: float
    min_flow_temp: float
    max_flow_temp: float
    curve_type: CurveType = CurveType.LINEAR
    curve_steepness: float = 1.0
    enabled: bool = True


class LinearHeatingCurve:
    """Linear heating curve calculator."""
    
    def __init__(self, config: HeatingCurveConfig):
        """Initialize the heating curve."""
        self.config = config
        self.name = config.name
        self.min_outdoor_temp = config.min_outdoor_temp
        self.max_outdoor_temp = config.max_outdoor_temp
        self.min_flow_temp = config.min_flow_temp
        self.max_flow_temp = config.max_flow_temp
        
    def calculate_flow_temperature(self, outdoor_temp: float) -> float:
        """Calculate target flow temperature based on outdoor temperature."""
        
        # Clamp outdoor temperature to configured range
        outdoor_temp = max(self.min_outdoor_temp, 
                          min(self.max_outdoor_temp, outdoor_temp))
        
        # Handle edge cases
        if outdoor_temp <= self.min_outdoor_temp:
            return self.max_flow_temp
        elif outdoor_temp >= self.max_outdoor_temp:
            return self.min_flow_temp
        
        # Linear interpolation
        temp_range = self.max_outdoor_temp - self.min_outdoor_temp
        flow_range = self.max_flow_temp - self.min_flow_temp
        
        outdoor_ratio = (outdoor_temp - self.min_outdoor_temp) / temp_range
        target_flow = self.max_flow_temp - (outdoor_ratio * flow_range)
        
        return round(target_flow, 1)
    
    def get_curve_points(self, num_points: int = 10) -> list[Tuple[float, float]]:
        """Get points along the curve for visualization."""
        points = []
        
        for i in range(num_points):
            outdoor_temp = self.min_outdoor_temp + (
                (self.max_outdoor_temp - self.min_outdoor_temp) * i / (num_points - 1)
            )
            flow_temp = self.calculate_flow_temperature(outdoor_temp)
            points.append((outdoor_temp, flow_temp))
            
        return points
    
    def validate_config(self) -> list[str]:
        """Validate heating curve configuration."""
        errors = []
        
        if self.min_outdoor_temp >= self.max_outdoor_temp:
            errors.append("Minimum outdoor temperature must be less than maximum")
            
        if self.min_flow_temp >= self.max_flow_temp:
            errors.append("Minimum flow temperature must be less than maximum")
            
        if not (-30 <= self.min_outdoor_temp <= 20):
            errors.append("Minimum outdoor temperature must be between -30°C and 20°C")
            
        if not (15 <= self.max_outdoor_temp <= 30):
            errors.append("Maximum outdoor temperature must be between 15°C and 30°C")
            
        if not (20 <= self.min_flow_temp <= 40):
            errors.append("Minimum flow temperature must be between 20°C and 40°C")
            
        if not (35 <= self.max_flow_temp <= 70):
            errors.append("Maximum flow temperature must be between 35°C and 70°C")
            
        return errors


class TestWeatherCompensationCore(unittest.TestCase):
    """Test core weather compensation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.basic_curve_config = HeatingCurveConfig(
            name="Standard Curve",
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

    def test_linear_curve_basic_calculations(self):
        """Test basic linear heating curve calculations."""
        curve = LinearHeatingCurve(self.basic_curve_config)
        
        # Test edge cases
        self.assertEqual(curve.calculate_flow_temperature(-10.0), 45.0)  # Below min outdoor
        self.assertEqual(curve.calculate_flow_temperature(25.0), 25.0)   # Above max outdoor
        
        # Test exact boundaries
        self.assertEqual(curve.calculate_flow_temperature(-5.0), 45.0)   # Min outdoor
        self.assertEqual(curve.calculate_flow_temperature(18.0), 25.0)   # Max outdoor
        
        # Test linear interpolation at midpoint
        midpoint_outdoor = (-5.0 + 18.0) / 2  # 6.5°C
        expected_flow = (45.0 + 25.0) / 2     # 35.0°C
        self.assertEqual(curve.calculate_flow_temperature(midpoint_outdoor), expected_flow)

    def test_linear_curve_interpolation_accuracy(self):
        """Test accuracy of linear interpolation."""
        curve = LinearHeatingCurve(self.basic_curve_config)
        
        # Test quarter points
        quarter_outdoor = -5.0 + (18.0 - (-5.0)) * 0.25  # 0.75°C
        quarter_flow = 45.0 - (45.0 - 25.0) * 0.25       # 40.0°C
        self.assertEqual(curve.calculate_flow_temperature(quarter_outdoor), quarter_flow)
        
        # Test three-quarter point
        three_quarter_outdoor = -5.0 + (18.0 - (-5.0)) * 0.75  # 12.25°C
        three_quarter_flow = 45.0 - (45.0 - 25.0) * 0.75       # 30.0°C
        self.assertEqual(curve.calculate_flow_temperature(three_quarter_outdoor), three_quarter_flow)

    def test_curve_validation_valid_config(self):
        """Test curve validation with valid configuration."""
        curve = LinearHeatingCurve(self.basic_curve_config)
        errors = curve.validate_config()
        self.assertEqual(len(errors), 0, f"Valid config should have no errors: {errors}")

    def test_curve_validation_invalid_configs(self):
        """Test curve validation with various invalid configurations."""
        
        # Test temperature range inversions
        invalid_outdoor_config = HeatingCurveConfig(
            name="Invalid Outdoor",
            min_outdoor_temp=10.0,  # Min > Max
            max_outdoor_temp=5.0,
            min_flow_temp=25.0,
            max_flow_temp=45.0,
        )
        curve = LinearHeatingCurve(invalid_outdoor_config)
        errors = curve.validate_config()
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("outdoor temperature" in error for error in errors))
        
        # Test flow temperature range inversion
        invalid_flow_config = HeatingCurveConfig(
            name="Invalid Flow",
            min_outdoor_temp=-5.0,
            max_outdoor_temp=18.0,
            min_flow_temp=50.0,     # Min > Max
            max_flow_temp=30.0,
        )
        curve = LinearHeatingCurve(invalid_flow_config)
        errors = curve.validate_config()
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("flow temperature" in error for error in errors))
        
        # Test extreme values
        extreme_config = HeatingCurveConfig(
            name="Extreme Values",
            min_outdoor_temp=-50.0,  # Too low
            max_outdoor_temp=50.0,   # Too high
            min_flow_temp=10.0,      # Too low
            max_flow_temp=100.0,     # Too high
        )
        curve = LinearHeatingCurve(extreme_config)
        errors = curve.validate_config()
        self.assertGreater(len(errors), 0)

    def test_curve_points_generation(self):
        """Test generation of curve points for visualization."""
        curve = LinearHeatingCurve(self.basic_curve_config)
        
        # Test different numbers of points
        for num_points in [3, 5, 10, 20]:
            points = curve.get_curve_points(num_points)
            self.assertEqual(len(points), num_points)
            
            # Check first and last points
            first_point = points[0]
            last_point = points[-1]
            
            self.assertEqual(first_point[0], -5.0)  # Min outdoor temp
            self.assertEqual(first_point[1], 45.0)  # Max flow temp
            
            self.assertEqual(last_point[0], 18.0)   # Max outdoor temp
            self.assertEqual(last_point[1], 25.0)   # Min flow temp
            
            # Check that points are ordered by outdoor temperature
            outdoor_temps = [point[0] for point in points]
            self.assertEqual(outdoor_temps, sorted(outdoor_temps))

    def test_boost_curve_vs_standard_curve(self):
        """Test comparison between standard and boost curves."""
        standard_curve = LinearHeatingCurve(self.basic_curve_config)
        boost_curve = LinearHeatingCurve(self.boost_curve_config)
        
        # Test at various outdoor temperatures
        test_temperatures = [-8, -5, 0, 5, 10, 15]
        
        for outdoor_temp in test_temperatures:
            standard_flow = standard_curve.calculate_flow_temperature(outdoor_temp)
            boost_flow = boost_curve.calculate_flow_temperature(outdoor_temp)
            
            # Boost curve should generally provide higher flow temperatures
            # (except at extreme ends where clamping occurs)
            if -5 <= outdoor_temp <= 15:  # Within both curve ranges
                self.assertGreaterEqual(
                    boost_flow, standard_flow,
                    f"Boost curve should give higher flow temp at {outdoor_temp}°C"
                )

    def test_performance_requirements(self):
        """Test that curve calculations meet performance requirements."""
        curve = LinearHeatingCurve(self.basic_curve_config)
        
        # Test calculation speed
        num_calculations = 10000
        start_time = time.time()
        
        for i in range(num_calculations):
            outdoor_temp = -15 + (i * 0.004)  # Range from -15 to 25
            flow_temp = curve.calculate_flow_temperature(outdoor_temp)
            
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / num_calculations
        
        # Should calculate very quickly
        self.assertLess(avg_time, 0.00001, f"Calculation too slow: {avg_time:.8f}s per calculation")
        
        # Should handle at least 100k calculations per second
        calculations_per_second = 1 / avg_time
        self.assertGreater(calculations_per_second, 100000)

    def test_rounding_consistency(self):
        """Test that rounding is consistent across calculations."""
        curve = LinearHeatingCurve(self.basic_curve_config)
        
        # Test same temperature multiple times
        outdoor_temp = 7.333333
        results = []
        
        for _ in range(100):
            result = curve.calculate_flow_temperature(outdoor_temp)
            results.append(result)
            
        # All results should be identical
        self.assertTrue(all(r == results[0] for r in results))
        
        # Result should be properly rounded
        self.assertEqual(results[0], round(results[0], 1))

    def test_curve_config_immutability(self):
        """Test that curve configuration doesn't change during calculations."""
        original_config = HeatingCurveConfig(
            name="Immutable Test",
            min_outdoor_temp=-5.0,
            max_outdoor_temp=18.0,
            min_flow_temp=25.0,
            max_flow_temp=45.0,
        )
        
        curve = LinearHeatingCurve(original_config)
        
        # Store original values
        original_min_outdoor = curve.min_outdoor_temp
        original_max_outdoor = curve.max_outdoor_temp
        original_min_flow = curve.min_flow_temp
        original_max_flow = curve.max_flow_temp
        
        # Perform many calculations
        for i in range(1000):
            curve.calculate_flow_temperature(i * 0.1)
            
        # Values should be unchanged
        self.assertEqual(curve.min_outdoor_temp, original_min_outdoor)
        self.assertEqual(curve.max_outdoor_temp, original_max_outdoor)
        self.assertEqual(curve.min_flow_temp, original_min_flow)
        self.assertEqual(curve.max_flow_temp, original_max_flow)

    def test_real_world_scenarios(self):
        """Test realistic weather compensation scenarios."""
        # UK climate typical curve
        uk_curve = LinearHeatingCurve(HeatingCurveConfig(
            name="UK Climate",
            min_outdoor_temp=-3.0,   # UK design temp
            max_outdoor_temp=16.0,   # Mild weather
            min_flow_temp=30.0,      # UFH suitable
            max_flow_temp=45.0,      # Cold weather
        ))
        
        # Calculate expected values for UK weather scenarios
        # Using the UK curve: -3°C to 16°C outdoor, 45°C to 30°C flow
        def calc_expected_uk_flow(outdoor_temp):
            # Clamp to range
            if outdoor_temp <= -3.0:
                return 45.0
            elif outdoor_temp >= 16.0:
                return 30.0
            else:
                # Linear interpolation
                temp_range = 16.0 - (-3.0)  # 19°C
                flow_range = 45.0 - 30.0    # 15°C
                ratio = (outdoor_temp - (-3.0)) / temp_range
                return round(45.0 - (ratio * flow_range), 1)
        
        # Test typical UK weather scenarios with calculated values
        scenarios = [
            (-3.0, calc_expected_uk_flow(-3.0), "Design cold day"),
            (0.0, calc_expected_uk_flow(0.0), "Freezing day"),
            (5.0, calc_expected_uk_flow(5.0), "Cool day"),
            (10.0, calc_expected_uk_flow(10.0), "Mild day"),
            (16.0, calc_expected_uk_flow(16.0), "Warm day"),
        ]
        
        for outdoor_temp, expected_flow, description in scenarios:
            actual_flow = uk_curve.calculate_flow_temperature(outdoor_temp)
            self.assertAlmostEqual(
                actual_flow, expected_flow, places=1,
                msg=f"UK scenario '{description}': expected {expected_flow}°C, got {actual_flow}°C"
            )

    def run_integration_validation(self):
        """Run comprehensive integration validation."""
        print("=== Weather Compensation Core Integration Validation ===")
        
        # Test basic curve functionality
        print("\n1. Testing standard heating curve...")
        standard_curve = LinearHeatingCurve(self.basic_curve_config)
        test_temps = [-10, -5, 0, 5, 10, 15, 20]
        
        print("   Outdoor Temp -> Flow Temp:")
        for temp in test_temps:
            flow_temp = standard_curve.calculate_flow_temperature(temp)
            print(f"   {temp:3.0f}°C -> {flow_temp:4.1f}°C")
        
        # Test boost curve
        print("\n2. Testing boost curve...")
        boost_curve = LinearHeatingCurve(self.boost_curve_config)
        print("   Outdoor Temp -> Boost Flow Temp:")
        for temp in test_temps:
            flow_temp = boost_curve.calculate_flow_temperature(temp)
            print(f"   {temp:3.0f}°C -> {flow_temp:4.1f}°C")
        
        # Test validation
        print("\n3. Testing curve validation...")
        errors = standard_curve.validate_config()
        print(f"   Standard curve validation errors: {len(errors)}")
        
        errors = boost_curve.validate_config()
        print(f"   Boost curve validation errors: {len(errors)}")
        
        # Test visualization points
        print("\n4. Testing curve visualization...")
        points = standard_curve.get_curve_points(10)
        print(f"   Generated {len(points)} curve points")
        print(f"   First point: {points[0][0]:.1f}°C -> {points[0][1]:.1f}°C")
        print(f"   Last point: {points[-1][0]:.1f}°C -> {points[-1][1]:.1f}°C")
        
        # Test performance
        print("\n5. Performance testing...")
        start_time = time.time()
        for _ in range(10000):
            standard_curve.calculate_flow_temperature(10.0)
        end_time = time.time()
        
        calc_time = (end_time - start_time) / 10000
        calc_per_sec = 1 / calc_time
        print(f"   Average calculation time: {calc_time:.8f}s")
        print(f"   Calculations per second: {calc_per_sec:,.0f}")
        
        # Test real-world scenario
        print("\n6. Real-world scenario validation...")
        uk_curve = LinearHeatingCurve(HeatingCurveConfig(
            name="UK Climate",
            min_outdoor_temp=-3.0,
            max_outdoor_temp=16.0,
            min_flow_temp=30.0,
            max_flow_temp=45.0,
        ))
        
        print("   UK Weather Compensation Curve:")
        uk_scenarios = [
            (-3, "Design cold day"),
            (0, "Freezing day"),
            (5, "Cool day"),
            (10, "Mild day"),
            (16, "Warm day")
        ]
        
        for temp, description in uk_scenarios:
            flow_temp = uk_curve.calculate_flow_temperature(temp)
            print(f"   {temp:3.0f}°C ({description:15s}) -> {flow_temp:4.1f}°C")
        
        print("\n✅ Weather Compensation Core validation completed successfully!")


def main():
    """Run the core weather compensation tests."""
    print("Running Grant Aerona3 Weather Compensation Core Tests...")
    print("=" * 60)
    
    # Run unit tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWeatherCompensationCore)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\n✅ All unit tests passed!")
        
        # Run integration validation
        test_instance = TestWeatherCompensationCore()
        test_instance.setUp()
        test_instance.run_integration_validation()
        
        return True
    else:
        print("\n❌ Some tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)