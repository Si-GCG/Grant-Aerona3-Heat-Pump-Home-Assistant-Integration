"""Enhanced data update coordinator for Grant Aerona3 Heat Pump."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from collections import defaultdict, deque

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

from .const import (
    CONF_SCAN_INTERVAL,
    CONF_SLAVE_ID,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .register_manager import (
    GrantAerona3RegisterManager,
    RegisterType,
    RegisterCategory,
)
from .weather_compensation import WeatherCompensationController

_LOGGER = logging.getLogger(__name__)


class GrantAerona3EnhancedCoordinator(DataUpdateCoordinator):
    """Enhanced Grant Aerona3 data update coordinator with register management."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the enhanced coordinator."""
        self.entry = entry
        self.host = entry.data[CONF_HOST]
        self.port = entry.data[CONF_PORT]
        self.slave_id = entry.data[CONF_SLAVE_ID]
        
        scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

        # Initialize register manager
        self.register_manager = GrantAerona3RegisterManager(entry.data)
        
        # Initialize weather compensation controller
        self.weather_compensation = WeatherCompensationController(hass, self, entry.data)
        
        # Modbus client
        self._client = ModbusTcpClient(
            host=self.host,
            port=self.port,
            timeout=10
        )
        
        # Performance tracking with memory management
        self._read_performance = defaultdict(lambda: deque(maxlen=100))  # Limited to 100 entries
        self._error_counts = defaultdict(int)
        self._last_successful_read = {}
        self._max_error_count = 1000  # Prevent unbounded growth
        
        # Connection management
        self._connection_errors = 0
        self._max_connection_errors = 5
        
        # Data validation
        self._data_validator = DataValidator()
        
        # Weather compensation setup flag
        self._weather_compensation_initialized = False
        
    async def async_setup_weather_compensation(self):
        """Setup weather compensation after coordinator is initialized."""
        if not self._weather_compensation_initialized:
            try:
                success = await self.weather_compensation.async_setup()
                self._weather_compensation_initialized = success
                if success:
                    _LOGGER.info("Weather compensation system initialized successfully")
                else:
                    _LOGGER.warning("Weather compensation system initialization failed")
            except Exception as err:
                _LOGGER.error("Error setting up weather compensation: %s", err)
                self._weather_compensation_initialized = False
        
    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from the heat pump."""
        try:
            return await self.hass.async_add_executor_job(self._fetch_data)
        except Exception as err:
            self._connection_errors += 1
            if self._connection_errors >= self._max_connection_errors:
                _LOGGER.error(
                    "Too many connection errors (%d), will retry in %d seconds",
                    self._connection_errors,
                    self.update_interval.total_seconds()
                )
            raise UpdateFailed(f"Error communicating with heat pump: {err}") from err

    def _fetch_data(self) -> Dict[str, Any]:
        """Fetch data from the heat pump (runs in executor)."""
        data = {}
        start_time = datetime.now()
        
        try:
            if not self._client.connect():
                raise ModbusException("Failed to connect to Modbus device")

            # Read input registers
            input_data = self._read_input_registers_enhanced()
            data.update(input_data)

            # Read holding registers
            holding_data = self._read_holding_registers_enhanced()
            data.update(holding_data)

            # Read coil registers
            coil_data = self._read_coil_registers_enhanced()
            data.update(coil_data)
            
            # Add metadata
            data["_metadata"] = {
                "fetch_duration": (datetime.now() - start_time).total_seconds(),
                "timestamp": datetime.now().isoformat(),
                "enabled_registers": len(self.register_manager._enabled_registers),
                "connection_errors": self._connection_errors
            }
            
            # Reset connection error count on successful read
            self._connection_errors = 0

        finally:
            self._client.close()

        return data

    def _read_input_registers_enhanced(self) -> Dict[str, Any]:
        """Read input registers using register manager."""
        data = {}
        enabled_registers = self.register_manager.get_enabled_registers(RegisterType.INPUT)
        
        if not enabled_registers:
            return data
            
        # Group registers by contiguous blocks for efficient reading
        register_blocks = self._group_registers_into_blocks(enabled_registers)
        
        for start_addr, count in register_blocks:
            try:
                read_start = datetime.now()
                result = self._client.read_input_registers(
                    address=start_addr,
                    count=count,
                    slave=self.slave_id
                )
                read_duration = (datetime.now() - read_start).total_seconds()
                
                if result.isError():
                    _LOGGER.error("Error reading input registers %d-%d: %s", 
                                start_addr, start_addr + count - 1, result)
                    self._error_counts[f"input_{start_addr}"] += 1
                    continue
                    
                # Process each register in the block
                for register_id, register_config in enabled_registers.items():
                    if start_addr <= register_config.address < start_addr + count:
                        offset = register_config.address - start_addr
                        raw_value = result.registers[offset]
                        
                        # Process the register value
                        processed_data = self._process_register_value(
                            register_config, raw_value
                        )
                        
                        if processed_data:
                            data[register_id] = processed_data
                            
                        # Track performance
                        self._read_performance[register_id].append(read_duration)
                        
                # Store successful read for fallback
                self._last_successful_read[f"input_{start_addr}"] = result.registers
                        
            except Exception as err:
                _LOGGER.error("Error reading input register block %d-%d: %s", 
                            start_addr, start_addr + count - 1, err)
                self._error_counts[f"input_{start_addr}"] += 1
                
                # Use cached data if available
                cached_data = self._get_cached_data_for_block(
                    start_addr, count, enabled_registers, RegisterType.INPUT
                )
                data.update(cached_data)
                
        return data

    def _read_holding_registers_enhanced(self) -> Dict[str, Any]:
        """Read holding registers using register manager."""
        data = {}
        enabled_registers = self.register_manager.get_enabled_registers(RegisterType.HOLDING)
        
        # Read holding registers individually due to potential gaps
        for register_id, register_config in enabled_registers.items():
            try:
                result = self._client.read_holding_registers(
                    address=register_config.address,
                    count=1,
                    slave=self.slave_id
                )
                
                if not result.isError():
                    raw_value = result.registers[0]
                    processed_data = self._process_register_value(
                        register_config, raw_value
                    )
                    
                    if processed_data:
                        data[register_id] = processed_data
                        
                else:
                    _LOGGER.error("Error reading holding register %s (addr %d): %s",
                                register_id, register_config.address, result)
                    self._error_counts[f"holding_{register_config.address}"] += 1
                    
            except Exception as err:
                _LOGGER.error("Error reading holding register %s: %s", register_id, err)
                self._error_counts[f"holding_{register_config.address}"] += 1
                
        return data

    def _read_coil_registers_enhanced(self) -> Dict[str, Any]:
        """Read coil registers using register manager."""
        data = {}
        enabled_registers = self.register_manager.get_enabled_registers(RegisterType.COIL)
        
        # Read coil registers individually for reliability
        for register_id, register_config in enabled_registers.items():
            try:
                result = self._client.read_coils(
                    address=register_config.address,
                    count=1,
                    slave=self.slave_id
                )
                
                if not result.isError():
                    value = result.bits[0]
                    data[register_id] = {
                        "value": value,
                        "name": register_config.name,
                        "description": register_config.description,
                        "address": register_config.address,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    _LOGGER.error("Error reading coil register %s (addr %d): %s",
                                register_id, register_config.address, result)
                    self._error_counts[f"coil_{register_config.address}"] += 1
                    
            except Exception as err:
                _LOGGER.error("Error reading coil register %s: %s", register_id, err)
                self._error_counts[f"coil_{register_config.address}"] += 1
                
        return data

    def _process_register_value(self, register_config, raw_value: int) -> Optional[Dict[str, Any]]:
        """Process raw register value according to configuration."""
        try:
            # Handle signed values (temperature can be negative)
            if raw_value > 32767:
                raw_value = raw_value - 65536
            
            # Apply scaling
            scaled_value = raw_value * register_config.scale
            
            # Validate value
            if not self._data_validator.validate_value(register_config, scaled_value):
                _LOGGER.warning(
                    "Invalid value for register %s: %f (raw: %d)",
                    register_config.name, scaled_value, raw_value
                )
                return None
            
            # Apply enum mapping if available
            display_value = scaled_value
            if register_config.enum_mapping and raw_value in register_config.enum_mapping:
                display_value = register_config.enum_mapping[raw_value]
            
            return {
                "value": scaled_value,
                "display_value": display_value,
                "raw_value": raw_value,
                "name": register_config.name,
                "unit": register_config.unit,
                "device_class": register_config.device_class,
                "address": register_config.address,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as err:
            _LOGGER.error("Error processing register %s: %s", register_config.name, err)
            return None

    def _group_registers_into_blocks(self, registers: Dict[str, Any]) -> List[tuple]:
        """Group registers into contiguous blocks for efficient reading."""
        if not registers:
            return []
            
        # Sort registers by address
        sorted_registers = sorted(
            registers.values(), 
            key=lambda r: r.address
        )
        
        blocks = []
        current_start = sorted_registers[0].address
        current_end = current_start
        
        for register in sorted_registers:
            if register.address <= current_end + 1:
                # Extend current block
                current_end = register.address
            else:
                # Start new block
                blocks.append((current_start, current_end - current_start + 1))
                current_start = register.address
                current_end = register.address
                
        # Add final block
        blocks.append((current_start, current_end - current_start + 1))
        
        return blocks

    def _get_cached_data_for_block(self, start_addr: int, count: int, 
                                 registers: Dict[str, Any], 
                                 register_type: RegisterType) -> Dict[str, Any]:
        """Get cached data for a register block when read fails."""
        cached_data = {}
        cache_key = f"{register_type.value}_{start_addr}"
        
        if cache_key in self._last_successful_read:
            cached_registers = self._last_successful_read[cache_key]
            
            for register_id, register_config in registers.items():
                if start_addr <= register_config.address < start_addr + count:
                    offset = register_config.address - start_addr
                    if offset < len(cached_registers):
                        raw_value = cached_registers[offset]
                        processed_data = self._process_register_value(
                            register_config, raw_value
                        )
                        
                        if processed_data:
                            # Mark as cached data
                            processed_data["cached"] = True
                            processed_data["cache_age"] = "unknown"
                            cached_data[register_id] = processed_data
                            
        return cached_data

    async def async_write_holding_register_enhanced(self, register_id: str, value: float) -> bool:
        """Write to a holding register using register manager."""
        # Validate write permission for security
        if not self.register_manager.validate_register_write_permission(register_id):
            return False
            
        register_config = self.register_manager._register_definitions.get(register_id)
        
        if not register_config or register_config.register_type != RegisterType.HOLDING:
            _LOGGER.error("Invalid holding register ID: %s", register_id)
            return False
            
        # Validate register address for security
        if not self.register_manager.validate_register_address(
            register_config.address, RegisterType.HOLDING
        ):
            return False
            
        # Validate value against min/max
        if register_config.min_value is not None and value < register_config.min_value:
            _LOGGER.error("Value %f below minimum %f for register %s", 
                        value, register_config.min_value, register_id)
            return False
            
        if register_config.max_value is not None and value > register_config.max_value:
            _LOGGER.error("Value %f above maximum %f for register %s", 
                        value, register_config.max_value, register_id)
            return False
            
        # Scale value for transmission
        scaled_value = int(value / register_config.scale)
        
        try:
            success = await self.hass.async_add_executor_job(
                self._write_holding_register, register_config.address, scaled_value
            )
            if success:
                # Trigger immediate refresh after successful write
                await self.async_request_refresh()
            return success
        except Exception as err:
            _LOGGER.error("Error writing holding register %s: %s", register_id, err)
            return False

    async def async_write_coil_enhanced(self, register_id: str, value: bool) -> bool:
        """Write to a coil register using register manager."""
        # Validate write permission for security
        if not self.register_manager.validate_register_write_permission(register_id):
            return False
            
        register_config = self.register_manager._register_definitions.get(register_id)
        
        if not register_config or register_config.register_type != RegisterType.COIL:
            _LOGGER.error("Invalid coil register ID: %s", register_id)
            return False
            
        # Validate register address for security
        if not self.register_manager.validate_register_address(
            register_config.address, RegisterType.COIL
        ):
            return False
            
        try:
            success = await self.hass.async_add_executor_job(
                self._write_coil, register_config.address, value
            )
            if success:
                # Trigger immediate refresh after successful write
                await self.async_request_refresh()
            return success
        except Exception as err:
            _LOGGER.error("Error writing coil register %s: %s", register_id, err)
            return False

    def _write_holding_register(self, address: int, value: int) -> bool:
        """Write to a holding register (runs in executor)."""
        try:
            if not self._client.connect():
                return False
                
            result = self._client.write_register(
                address=address,
                value=value,
                slave=self.slave_id
            )
            
            success = not result.isError()
            if success:
                # Note: async_request_refresh will be called by the calling async method
                _LOGGER.debug("Holding register write successful for address %d", address)
            
            return success
            
        finally:
            self._client.close()

    def _write_coil(self, address: int, value: bool) -> bool:
        """Write to a coil register (runs in executor)."""
        try:
            if not self._client.connect():
                return False
                
            result = self._client.write_coil(
                address=address,
                value=value,
                slave=self.slave_id
            )
            
            success = not result.isError()
            if success:
                # Note: async_request_refresh will be called by the calling async method
                _LOGGER.debug("Coil register write successful for address %d", address)
            
            return success
            
        finally:
            self._client.close()

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for the coordinator."""
        stats = {
            "total_enabled_registers": len(self.register_manager._enabled_registers),
            "error_counts": dict(self._error_counts),
            "connection_errors": self._connection_errors,
            "register_performance": {}
        }
        
        for register_id, durations in self._read_performance.items():
            if durations:
                stats["register_performance"][register_id] = {
                    "avg_read_time": sum(durations) / len(durations),
                    "max_read_time": max(durations),
                    "min_read_time": min(durations),
                    "read_count": len(durations)
                }
                
        return stats
    
    async def async_cleanup(self) -> None:
        """Clean up resources on shutdown."""
        try:
            # Close Modbus client if open
            if self._client and hasattr(self._client, 'close'):
                await self.hass.async_add_executor_job(self._client.close)
                
            # Clear performance tracking data
            self._read_performance.clear()
            self._error_counts.clear()
            self._last_successful_read.clear()
            
            # Clean up weather compensation
            if hasattr(self.weather_compensation, 'async_cleanup'):
                await self.weather_compensation.async_cleanup()
                
            _LOGGER.debug("Enhanced coordinator cleanup completed")
            
        except Exception as err:
            _LOGGER.error("Error during coordinator cleanup: %s", err)


class DataValidator:
    """Validates register data for consistency and sanity."""
    
    def __init__(self):
        """Initialize data validator."""
        self.validation_rules = {
            "temperature": {"min": -50.0, "max": 100.0},
            "power": {"min": 0.0, "max": 20000.0},
            "frequency": {"min": 0.0, "max": 150.0},
            "humidity": {"min": 0.0, "max": 100.0},
        }
        
    def validate_value(self, register_config, value: float) -> bool:
        """Validate a register value."""
        # Check device class specific rules
        if register_config.device_class in self.validation_rules:
            rules = self.validation_rules[register_config.device_class]
            
            if value < rules["min"] or value > rules["max"]:
                return False
                
        # Check register-specific min/max
        if register_config.min_value is not None and value < register_config.min_value:
            return False
            
        if register_config.max_value is not None and value > register_config.max_value:
            return False
            
        return True