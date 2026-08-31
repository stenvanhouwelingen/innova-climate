"""The Innova Climate integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_BAUDRATE,
    CONF_BOARD_FAMILY,
    CONF_CONNECTION_TYPE,
    CONF_HOST,
    CONF_PORT,
    CONF_SERIAL_PORT,
    CONF_SLAVE_ID,
    CONNECTION_TYPE_SERIAL,
    CONNECTION_TYPE_TCP,
    DEFAULT_BAUDRATE,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_SLAVE_ID,
    DEFAULT_TCP_PORT,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import InnovaDataUpdateCoordinator
from .innova_modbus import InnovaBoardFamily, InnovaFancoil

_LOGGER = logging.getLogger(__name__)

SERVICE_SET_SUPERVISOR_MODE = "set_supervisor_mode"
SERVICE_SET_ROOM_TEMP_OFFSET = "set_room_temperature_offset"
SERVICE_SET_KEYPAD_LOCK = "set_keypad_lock"

ATTR_ENABLED = "enabled"
ATTR_OFFSET = "offset"
ATTR_LOCKED = "locked"


class AsyncModbusClientWrapper:
    """Wrapper to bridge pymodbus / serialx async clients with innova_modbus."""

    def __init__(self, client: Any) -> None:
        self.client = client

    async def read_holding_registers(self, address: int, count: int, slave: int = 1) -> list[int]:
        """Read holding registers with auto-reconnect and cross-version parameter support."""
        for attempt in range(2):
            try:
                if not self.client.connected:
                    await self.client.connect()

                # In PyModbus 3.8+ (HA 2026 / PyModbus 3.13): device_id
                # In PyModbus 3.0-3.7: slave
                # In PyModbus 2.x: unit
                res = None
                for kw in ({"device_id": slave}, {"slave": slave}, {"unit": slave}):
                    try:
                        res = await self.client.read_holding_registers(address=address, count=count, **kw)
                        break
                    except TypeError:
                        continue
                if res is None:
                    res = await self.client.read_holding_registers(address=address, count=count)

                if res.isError():
                    raise RuntimeError(f"Modbus read error: {res}")
                return list(res.registers)
            except Exception as err:
                if attempt == 0:
                    _LOGGER.debug("Retrying Modbus read after connection reset: %s", err)
                    try:
                        self.client.close()
                    except Exception:
                        pass
                    continue
                raise

        return []

    async def write_holding_register(self, address: int, value: int, slave: int = 1) -> None:
        """Write holding register with auto-reconnect and cross-version parameter support."""
        for attempt in range(2):
            try:
                if not self.client.connected:
                    await self.client.connect()

                res = None
                for kw in ({"device_id": slave}, {"slave": slave}, {"unit": slave}):
                    try:
                        res = await self.client.write_register(address=address, value=value, **kw)
                        break
                    except TypeError:
                        continue
                if res is None:
                    res = await self.client.write_register(address=address, value=value)

                if res.isError():
                    raise RuntimeError(f"Modbus write error: {res}")
                return
            except Exception as err:
                if attempt == 0:
                    _LOGGER.debug("Retrying Modbus write after connection reset: %s", err)
                    try:
                        self.client.close()
                    except Exception:
                        pass
                    continue
                raise


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the Innova Climate services."""
    async def async_handle_supervisor(call: ServiceCall) -> None:
        enabled: bool = call.data[ATTR_ENABLED]
        for entry in hass.config_entries.async_entries(DOMAIN):
            if hasattr(entry, "runtime_data") and isinstance(entry.runtime_data, InnovaDataUpdateCoordinator):
                coordinator: InnovaDataUpdateCoordinator = entry.runtime_data
                await coordinator.device.async_set_supervisor_mode(enabled)
                await coordinator.async_request_refresh()

    async def async_handle_offset(call: ServiceCall) -> None:
        offset: float = float(call.data[ATTR_OFFSET])
        for entry in hass.config_entries.async_entries(DOMAIN):
            if hasattr(entry, "runtime_data") and isinstance(entry.runtime_data, InnovaDataUpdateCoordinator):
                coordinator: InnovaDataUpdateCoordinator = entry.runtime_data
                await coordinator.device.async_set_room_temp_offset(offset)
                await coordinator.async_request_refresh()

    async def async_handle_keypad_lock(call: ServiceCall) -> None:
        locked: bool = call.data[ATTR_LOCKED]
        for entry in hass.config_entries.async_entries(DOMAIN):
            if hasattr(entry, "runtime_data") and isinstance(entry.runtime_data, InnovaDataUpdateCoordinator):
                coordinator: InnovaDataUpdateCoordinator = entry.runtime_data
                await coordinator.device.async_set_keypad_lock(locked)
                await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_SUPERVISOR_MODE,
        async_handle_supervisor,
        schema=vol.Schema({vol.Required(ATTR_ENABLED): cv.boolean}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_ROOM_TEMP_OFFSET,
        async_handle_offset,
        schema=vol.Schema({vol.Required(ATTR_OFFSET): vol.Coerce(float)}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_KEYPAD_LOCK,
        async_handle_keypad_lock,
        schema=vol.Schema({vol.Required(ATTR_LOCKED): cv.boolean}),
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Innova Climate from a config entry."""
    data = entry.data
    conn_type = data.get(CONF_CONNECTION_TYPE, CONNECTION_TYPE_SERIAL)
    slave_id = int(data.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID))
    board_family = data.get(CONF_BOARD_FAMILY, InnovaBoardFamily.N273025D)
    poll_interval = int(entry.options.get("scan_interval", DEFAULT_POLL_INTERVAL))

    try:
        from pymodbus.framer import FramerType

        if conn_type == CONNECTION_TYPE_SERIAL:
            port_path = data[CONF_SERIAL_PORT]
            baud = int(data.get(CONF_BAUDRATE, DEFAULT_BAUDRATE))

            if str(port_path).startswith("socket://"):
                from pymodbus.client import AsyncModbusTcpClient

                raw_host_port = str(port_path).replace("socket://", "")
                parts = raw_host_port.split(":")
                host = parts[0]
                tcp_port = int(parts[1]) if len(parts) > 1 else DEFAULT_TCP_PORT
                client = AsyncModbusTcpClient(
                    host=host,
                    port=tcp_port,
                    framer=FramerType.RTU,
                    timeout=2.0,
                )
            else:
                from pymodbus.client import AsyncModbusSerialClient

                client = AsyncModbusSerialClient(
                    port=port_path,
                    baudrate=baud,
                    bytesize=8,
                    parity="N",
                    stopbits=1,
                    timeout=1.0,
                )
        else:
            from pymodbus.client import AsyncModbusTcpClient

            host = data[CONF_HOST]
            tcp_port = int(data.get(CONF_PORT, DEFAULT_TCP_PORT))
            client = AsyncModbusTcpClient(
                host=host,
                port=tcp_port,
                framer=FramerType.RTU,
                timeout=2.0,
            )

        await client.connect()
    except Exception as err:
        raise ConfigEntryNotReady(f"Failed to connect to Modbus connection {conn_type}: {err}") from err

    wrapper = AsyncModbusClientWrapper(client)
    device = InnovaFancoil(
        connection=wrapper,
        slave_id=slave_id,
        board_family=InnovaBoardFamily(board_family),
    )

    coordinator = InnovaDataUpdateCoordinator(hass, device, poll_interval=poll_interval)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: InnovaDataUpdateCoordinator = entry.runtime_data
        if hasattr(coordinator.device._connection, "client"):
            try:
                coordinator.device._connection.client.close()
            except Exception:
                pass
    return unload_ok
