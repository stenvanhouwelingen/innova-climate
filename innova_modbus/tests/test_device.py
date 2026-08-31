"""Unit tests for Innova Modbus device operations."""

import pytest
from innova_modbus.const import (
    InnovaBoardFamily,
    InnovaFanSpeed,
    InnovaMode,
    InnovaRegistersModern,
)
from innova_modbus.device import InnovaFancoil


class MockModbusConnection:
    """Mock Modbus connection backend."""

    def __init__(self, register_map: dict[int, int] | None = None) -> None:
        self.registers = register_map or {}
        self.written_registers: list[tuple[int, int]] = []

    async def read_holding_registers(self, address: int, count: int, slave: int = 1) -> list[int]:
        """Mock reading registers."""
        return [self.registers.get(address + i, 0) for i in range(count)]

    async def write_holding_register(self, address: int, value: int, slave: int = 1) -> None:
        """Mock writing registers."""
        self.written_registers.append((address, value))
        self.registers[address] = value


@pytest.mark.asyncio
async def test_device_async_update_and_commands():
    """Test device update and control commands."""
    mock_regs = {
        0: 220,       # T1: 22.0 °C
        1: 500,       # T2: 50.0 °C
        2: 480,       # T3: 48.0 °C
        20: 450,      # RH: 45.0%
        150: 0x0002,  # Status: Heating (bit 1)
        151: 0,
        305: 210,     # Setpoint: 21.0 °C
        553: 0x0000,  # Auto fan, Power ON
        556: 1,       # Heating
    }
    mock_conn = MockModbusConnection(mock_regs)
    device = InnovaFancoil(connection=mock_conn, slave_id=1, board_family=InnovaBoardFamily.N273025D)

    data = await device.async_update()
    assert data.room_temperature == 22.0
    assert data.target_temperature == 21.0
    assert data.mode == InnovaMode.HEATING

    # 1. Test setting target temperature
    await device.async_set_target_temperature(23.5)
    assert (InnovaRegistersModern.SP, 235) in mock_conn.written_registers
    assert device.data.target_temperature == 23.5

    # 2. Test setting fan speed
    await device.async_set_fan_speed(InnovaFanSpeed.MAX)
    assert (InnovaRegistersModern.PRG, 0x0002) in mock_conn.written_registers
    assert device.data.fan_speed == InnovaFanSpeed.MAX

    # 3. Test setting mode to Cooling
    await device.async_set_mode(InnovaMode.COOLING)
    assert (InnovaRegistersModern.MAN, 2) in mock_conn.written_registers
    assert device.data.mode == InnovaMode.COOLING

    # 4. Test setting mode to OFF
    await device.async_set_mode(InnovaMode.OFF)
    assert (InnovaRegistersModern.PRG, 0x0012) in mock_conn.written_registers  # Bit 4 set (standby)
    assert device.data.mode == InnovaMode.OFF

    # 5. Test supervisor mode
    await device.async_set_supervisor_mode(True)
    assert (InnovaRegistersModern.WEB, 0x000C) in mock_conn.written_registers
    assert device.data.supervisor_mode is True
