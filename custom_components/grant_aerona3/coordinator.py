"""Data update coordinator for Grant Aerona3 Heat Pump."""
import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

from .const import (
    CONF_SCAN_INTERVAL,
    CONF_SLAVE_ID,
    COIL_REGISTER_MAP,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    HOLDING_REGISTER_MAP,
    INPUT_REGISTER_MAP,
)

_LOGGER = logging.getLogger(__name__)


class GrantAerona3Coordinator(DataUpdateCoordinator):
    """Grant Aerona3 data update coordinator."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
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

        self._client = ModbusTcpClient(
            host=self.host,
            port=self.port,
            timeout=10
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the heat pump."""
        try:
            return await self.hass.async_add_executor_job(self._fetch_data)
        except Exception as err:
            raise UpdateFailed(f"Error communicating with heat pump: {err}") from err

    def _fetch_data(self) -> dict[str, Any]:
        """Fetch data from the heat pump (runs in executor)."""
        data = {}
        
        try:
            if not self._client.connect():
                raise ModbusException("Failed to connect to Modbus device")

            # Read input registers
            input_data = self._read_input_registers()
            data.update(input_data)

            # Read holding registers
            holding_data = self._read_holding_registers()
            data.update(holding_data)

            # Read coil registers
            coil_data = self._read_coil_registers()
            data.update(coil_data)

        finally:
            self._client.close()

        return data

    def _read_input_registers(self) -> dict[str, Any]:
        """Read input registers."""
        data = {}
        
        # Read all input registers in one go (0-18)
        try:
            result = self._client.read_input_registers(
                address=0,
                count=19,
                slave=self.slave_id
            )
            
            if result.isError():
                _LOGGER.error("Error reading input registers: %s", result)
                return data
                
            for addr, config in INPUT_REGISTER_MAP.items():
                if addr < len(result.registers):
                    raw_value = result.registers[addr]
                    
                    # Handle signed values (temperature can be negative)
                    if raw_value > 32767:
                        raw_value = raw_value - 65536
                    
                    # Apply scaling
                    scaled_value = raw_value * config["scale"]
                    
                    data[f"input_{addr}"] = {
                        "value": scaled_value,
                        "raw_value": result.registers[addr],
                        "name": config["name"],
                        "unit": config["unit"],
                        "device_class": config["device_class"]
                    }
                    
        except Exception as err:
            _LOGGER.error("Error reading input registers: %s", err)
            
        return data

    def _read_holding_registers(self) -> dict[str, Any]:
        """Read holding registers."""
        data = {}
        
        # Read holding registers for setpoints
        for addr, config in HOLDING_REGISTER_MAP.items():
            try:
                result = self._client.read_holding_registers(
                    address=addr,
                    count=1,
                    slave=self.slave_id
                )
                
                if not result.isError():
                    raw_value = result.registers[0]
                    
                    # Handle signed values
                    if raw_value > 32767:
                        raw_value = raw_value - 65536
                    
                    # Apply scaling
                    scaled_value = raw_value * config["scale"]
                    
                    data[f"holding_{addr}"] = {
                        "value": scaled_value,
                        "raw_value": result.registers[0],
                        "name": config["name"],
                        "unit": config["unit"],
                        "min": config["min"],
                        "max": config["max"]
                    }
                    
            except Exception as err:
                _LOGGER.error("Error reading holding register %s: %s", addr, err)
                
        return data

    def _read_coil_registers(self) -> dict[str, Any]:
        """Read coil registers."""
        data = {}
        
        # Read coil registers for switches
        for addr, config in COIL_REGISTER_MAP.items():
            try:
                result = self._client.read_coils(
                    address=addr,
                    count=1,
                    slave=self.slave_id
                )
                
                if not result.isError():
                    data[f"coil_{addr}"] = {
                        "value": result.bits[0],
                        "name": config["name"],
                        "description": config["description"]
                    }
                    
            except Exception as err:
                _LOGGER.error("Error reading coil register %s: %s", addr, err)
                
        return data

    async def async_write_holding_register(self, address: int, value: int) -> bool:
        """Write to a holding register."""
        try:
            return await self.hass.async_add_executor_job(
                self._write_holding_register, address, value
            )
        except Exception as err:
            _LOGGER.error("Error writing holding register %s: %s", address, err)
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
            
            return not result.isError()
            
        finally:
            self._client.close()

    async def async_write_coil(self, address: int, value: bool) -> bool:
        """Write to a coil register."""
        try:
            return await self.hass.async_add_executor_job(
                self._write_coil, address, value
            )
        except Exception as err:
            _LOGGER.error("Error writing coil register %s: %s", address, err)
            return False

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
            
            return not result.isError()
            
        finally:
            self._client.close()