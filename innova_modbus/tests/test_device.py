"""Unit tests for Innova Modbus device operations."""

import pytest
from innova_modbus.const import (
    InnovaBoardFamily,
    InnovaFanSpeed,
    InnovaFlapMode,
    InnovaMode,
    InnovaRegistersLegacy,
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

    # 6. Test flap swing & multi-position flap control
    await device.async_set_flap_swing(True)
    assert (InnovaRegistersModern.FSW, 7) in mock_conn.written_registers
    assert device.data.flap_swing is True
    assert device.data.flap_mode == InnovaFlapMode.SWING

    await device.async_set_flap_mode(InnovaFlapMode.POSITION_1)
    assert (InnovaRegistersModern.FSW, 1) in mock_conn.written_registers
    assert device.data.flap_mode == InnovaFlapMode.POSITION_1
    assert device.data.flap_swing is False

    await device.async_set_flap_swing(False)
    assert (InnovaRegistersModern.FSW, 0) in mock_conn.written_registers
    assert device.data.flap_swing is False
    assert device.data.flap_mode == InnovaFlapMode.AUTO

    # 6b. Test display LED off and setpoint limits
    await device.async_set_led_off(True)
    assert device.data.web_led_off is True
    await device.async_set_min_setpoint_limit(18.0)
    assert (InnovaRegistersModern.SPL_W, 180) in mock_conn.written_registers
    assert device.data.web_min_setpoint == 18.0
    await device.async_set_max_setpoint_limit(26.0)
    assert (InnovaRegistersModern.SPH_W, 260) in mock_conn.written_registers
    assert device.data.web_max_setpoint == 26.0

    # 7. Test min heating water temp and max cooling water temp (Modern)
    await device.async_set_min_water_temp_heating(25.5)
    assert (InnovaRegistersModern.LLO, 255) in mock_conn.written_registers
    assert device.data.min_water_temp_heating == 25.5

    await device.async_set_max_water_temp_cooling(18.0)
    assert (InnovaRegistersModern.LHI, 180) in mock_conn.written_registers
    assert device.data.max_water_temp_cooling == 18.0

    # 8. Test min heating water temp and max cooling water temp (Legacy)
    legacy_conn = MockModbusConnection({218: 300, 219: 200})
    legacy_device = InnovaFancoil(connection=legacy_conn, slave_id=1, board_family=InnovaBoardFamily.N273025C)
    await legacy_device.async_set_min_water_temp_heating(26.0)
    assert (InnovaRegistersLegacy.LLO, 260) in legacy_conn.written_registers
    assert legacy_device.data.min_water_temp_heating == 26.0

    await legacy_device.async_set_max_water_temp_cooling(19.5)
    assert (InnovaRegistersLegacy.LHI, 195) in legacy_conn.written_registers
    assert legacy_device.data.max_water_temp_cooling == 19.5


@pytest.mark.asyncio
async def test_fast_slow_polling_and_optional_batch_skipping():
    """Verify slow batches are cached on fast cycles and unsupported optional batches are skipped."""
    read_calls: list[tuple[int, int]] = []

    class TrackingConnection(MockModbusConnection):
        async def read_holding_registers(self, address: int, count: int, slave: int = 1) -> list[int]:
            read_calls.append((address, count))
            if (address, count) == (457, 1):
                raise RuntimeError("Illegal Data Address")
            return await super().read_holding_registers(address, count, slave)

    conn = TrackingConnection({0: 215, 198: 15, 199: 1190, 510: 250, 511: 180})
    device = InnovaFancoil(connection=conn, slave_id=1, board_family=InnovaBoardFamily.N273025D)

    # First poll (poll_count=0): reads both fast and slow batches
    data1 = await device.async_update()
    assert data1.firmware_release == 1.5
    assert data1.min_water_temp_heating == 25.0
    assert (198, 2) in read_calls
    assert (510, 2) in read_calls
    assert (457, 1) in device._unsupported_batches

    # Second poll (poll_count=1): skips slow batches and unsupported optional batches, retains cached values
    read_calls.clear()
    data2 = await device.async_update()
    assert (198, 2) not in read_calls
    assert (510, 2) not in read_calls
    assert (457, 1) not in read_calls
    assert data2.firmware_release == 1.5
    assert data2.min_water_temp_heating == 25.0
