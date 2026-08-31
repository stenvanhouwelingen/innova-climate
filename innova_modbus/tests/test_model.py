"""Unit tests for Innova Modbus data models."""

from innova_modbus.const import (
    InnovaAction,
    InnovaBoardFamily,
    InnovaFanSpeed,
    InnovaMode,
)
from innova_modbus.model import InnovaData


def test_modern_registers_decoding():
    """Test register decoding for modern n273025d board."""
    raw_regs = {
        0: 215,       # Room temp: 21.5 °C
        1: 450,       # Inlet water T2: 45.0 °C
        2: 435,       # Coil water T3: 43.5 °C
        20: 550,      # Relative humidity: 55.0%
        150: 0x0002,  # Status: Heating active (bit 1)
        151: 0x0000,  # No alarms
        198: 15,      # FW release: 1.5
        199: 1190,    # FW ID: 1190 (PU board)
        305: 220,     # Setpoint: 22.0 °C
        553: 0x0001,  # Program: Night mode (001), Power ON (bit 4 is 0)
        556: 1,       # Seasonal Mode: Heating
        557: 0x000C,  # Supervisor mode: bits 2 & 3 set
        457: 1,       # Flap swing: ON
        530: 5,       # Sensor offset: +0.5 °C
    }

    data = InnovaData.from_registers_modern(raw_regs)

    assert data.board_family == InnovaBoardFamily.N273025D
    assert data.room_temperature == 21.5
    assert data.inlet_water_temp_t2 == 45.0
    assert data.coil_water_temp_t3 == 43.5
    assert data.relative_humidity == 55.0
    assert data.target_temperature == 22.0
    assert data.mode == InnovaMode.HEATING
    assert data.fan_speed == InnovaFanSpeed.NIGHT
    assert data.power_on is True
    assert data.action == InnovaAction.HEATING
    assert data.supervisor_mode is True
    assert data.flap_swing is True
    assert data.room_temp_offset == 0.5
    assert data.firmware_release == 1.5
    assert data.firmware_id == 1190
    assert data.alarm_active is False
    assert data.alarm_description == "No faults"


def test_legacy_registers_decoding():
    """Test register decoding for legacy n273025c board."""
    raw_regs = {
        0: 195,       # Room temp: 19.5 °C
        1: 120,       # Inlet water T2: 12.0 °C
        2: 115,       # Coil water T3: 11.5 °C
        20: 0,        # No RH sensor
        104: 0x0001,  # Status: Cooling active (bit 0)
        105: 0x0000,  # No alarms
        201: 0x0003,  # Program: Max speed (011), Power ON (bit 7 is 0)
        231: 200,     # Setpoint: 20.0 °C
        233: 5,       # Seasonal Mode: Cooling (5)
        247: 0x000C,  # Supervisor mode
    }

    data = InnovaData.from_registers_legacy(raw_regs)

    assert data.board_family == InnovaBoardFamily.N273025C
    assert data.room_temperature == 19.5
    assert data.inlet_water_temp_t2 == 12.0
    assert data.coil_water_temp_t3 == 11.5
    assert data.relative_humidity is None
    assert data.target_temperature == 20.0
    assert data.mode == InnovaMode.COOLING
    assert data.fan_speed == InnovaFanSpeed.MAX
    assert data.power_on is True
    assert data.action == InnovaAction.COOLING
    assert data.supervisor_mode is True


def test_alarm_and_sensor_disconnection():
    """Test negative temperatures and alarm flags."""
    raw_regs = {
        0: 65136,     # -40.0 °C (signed -400 -> disconnected probe)
        150: 0x0100,  # Alarm active flag (bit 8)
        151: 0x0002,  # T1 Room Air probe fault (bit 1)
        553: 0x0010,  # Standby bit 4 is set -> Power is OFF
    }

    data = InnovaData.from_registers_modern(raw_regs)

    assert data.room_temperature is None
    assert data.alarm_active is True
    assert "Air Temp Sensor (T1) Fault" in data.alarm_description
    assert data.power_on is False
    assert data.mode == InnovaMode.OFF
