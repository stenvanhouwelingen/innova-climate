"""Data models for Innova Fancoil devices."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .const import (
    InnovaAction,
    InnovaBoardFamily,
    InnovaFanSpeed,
    InnovaMode,
    TEMP_MAX_VALID,
    TEMP_MIN_VALID,
)


@dataclass
class InnovaData:
    """State representation of an Innova fancoil device."""

    # Board Family
    board_family: InnovaBoardFamily = InnovaBoardFamily.N273025D

    # Temperatures & Environment
    room_temperature: float | None = None
    inlet_water_temp_t2: float | None = None
    coil_water_temp_t3: float | None = None
    relative_humidity: float | None = None

    # Climate Controls
    target_temperature: float = 20.0
    mode: InnovaMode = InnovaMode.AUTO
    fan_speed: InnovaFanSpeed = InnovaFanSpeed.AUTO
    power_on: bool = True
    action: InnovaAction = InnovaAction.IDLE

    # System Status & Diagnostic Bitmasks
    raw_status: int = 0
    raw_alarms: int = 0
    raw_program: int = 0
    raw_web_flags: int = 0

    # Diagnostic & Hardware Info
    firmware_release: float | None = None
    firmware_id: int | None = None
    alarm_active: bool = False
    alarm_description: str = "No faults"
    status_description: str = "Idle"
    fan_status_description: str = "Stopped"

    # Hardware Feature Flags
    t2_probe_present: bool = True
    t3_probe_present: bool = True
    rh_sensor_present: bool = False
    window_contact_open: bool = False

    # Configuration Switches
    supervisor_mode: bool = False
    keypad_locked: bool = False
    web_led_off: bool = False
    web_force_off: bool = False
    web_disable_mode_change: bool = False
    web_disable_power_control: bool = False
    web_inhibit_extremes: bool = False
    web_enable_setpoint_restriction: bool = False
    web_disable_all_keys: bool = False
    web_disable_seasonal_key: bool = False
    flap_swing: bool = False

    # Calibration & Setpoint Limits
    room_temp_offset: float = 0.0
    web_min_setpoint: float = 16.0
    web_max_setpoint: float = 30.0

    @classmethod
    def from_registers_modern(cls, registers: dict[int, int]) -> InnovaData:
        """Parse raw registers for modern n273025d board family."""
        data = cls(board_family=InnovaBoardFamily.N273025D)

        # 1. Temperatures
        if 0 in registers:
            raw_t1 = cls._to_signed_16(registers[0])
            t1 = raw_t1 * 0.1
            data.room_temperature = round(t1, 1) if TEMP_MIN_VALID <= t1 <= TEMP_MAX_VALID else None

        if 1 in registers:
            raw_t2 = cls._to_signed_16(registers[1])
            t2 = raw_t2 * 0.1
            data.inlet_water_temp_t2 = round(t2, 1) if TEMP_MIN_VALID <= t2 <= TEMP_MAX_VALID else None

        if 2 in registers:
            raw_t3 = cls._to_signed_16(registers[2])
            t3 = raw_t3 * 0.1
            data.coil_water_temp_t3 = round(t3, 1) if TEMP_MIN_VALID <= t3 <= TEMP_MAX_VALID else None

        if 20 in registers:
            rh = registers[20] * 0.1
            if 0 < rh <= 100:
                data.relative_humidity = round(rh, 1)
                data.rh_sensor_present = True
            else:
                data.relative_humidity = None
                data.rh_sensor_present = False

        # 2. Firmware Version & ID
        if 198 in registers:
            data.firmware_release = round(registers[198] * 0.1, 1)
        if 199 in registers:
            data.firmware_id = registers[199]

        # 3. Target Temperature Setpoint
        if 305 in registers:
            sp = registers[305] * 0.1
            if 5.0 <= sp <= 40.0:
                data.target_temperature = round(sp, 1)

        # 4. Status Register 150
        if 150 in registers:
            status = registers[150]
            data.raw_status = status
            data.alarm_active = bool(status & (1 << 8))

            # Probes presence flags
            data.t2_probe_present = (data.inlet_water_temp_t2 is not None) and not bool(status & (1 << 12))
            data.t3_probe_present = (data.coil_water_temp_t3 is not None) and not bool(status & (1 << 13)) and not bool(status & (1 << 14))

            # Action determination
            if status & (1 << 10):
                data.action = InnovaAction.STANDBY
                data.status_description = "Standby"
                data.fan_status_description = "Stopped (Standby)"
            elif status & (1 << 0):
                data.action = InnovaAction.COOLING
                data.status_description = "Cooling"
                data.fan_status_description = "Running"
            elif status & (1 << 1):
                data.action = InnovaAction.HEATING
                data.status_description = "Heating"
                data.fan_status_description = "Running"
            else:
                data.action = InnovaAction.IDLE
                data.status_description = "Idle"

                if status & (1 << 2):
                    data.fan_status_description = "Stopped (Water unsuitable for cooling)"
                elif status & (1 << 3):
                    data.fan_status_description = "Stopped (Water unsuitable for heating)"
                elif status & (1 << 4):
                    data.fan_status_description = "Stopped (Inadequate Inlet T2 temp)"
                elif status & (1 << 5):
                    data.fan_status_description = "Stopped (Inadequate Coil T3 temp)"
                elif status & (1 << 6):
                    data.fan_status_description = "Stopped (Inadequate water temp trend)"
                else:
                    data.fan_status_description = "Running"

        # 5. Alarms Register 151
        if 151 in registers:
            alarm = registers[151]
            data.raw_alarms = alarm
            data.window_contact_open = bool(alarm & (1 << 8))
            data.alarm_description = cls._decode_alarms_modern(alarm)

        # 6. Program Register 553
        if 553 in registers:
            prg = registers[553]
            data.raw_program = prg
            # Power state: Bit 4 is Standby (1 = OFF, 0 = ON)
            data.power_on = not bool(prg & (1 << 4))
            if not data.power_on:
                data.mode = InnovaMode.OFF
            data.keypad_locked = bool(prg & (1 << 3))

            # Fan Speed: Bits [2:0]
            fan_mode = prg & 0x07
            if fan_mode == 1:
                data.fan_speed = InnovaFanSpeed.NIGHT
            elif fan_mode == 2:
                data.fan_speed = InnovaFanSpeed.MAX
            else:
                data.fan_speed = InnovaFanSpeed.AUTO

        # 7. Seasonal Mode Register 556
        if 556 in registers:
            man = registers[556]
            if not data.power_on:
                data.mode = InnovaMode.OFF
            elif man == 1:
                data.mode = InnovaMode.HEATING
            elif man == 2:
                data.mode = InnovaMode.COOLING
            else:
                data.mode = InnovaMode.AUTO

        # 8. Webserver Lockout Register 557
        if 557 in registers:
            web = registers[557]
            data.raw_web_flags = web
            data.web_led_off = bool(web & (1 << 0))
            data.web_force_off = bool(web & (1 << 1))
            data.web_disable_mode_change = bool(web & (1 << 2))
            data.web_disable_power_control = bool(web & (1 << 3))
            data.web_inhibit_extremes = bool(web & (1 << 4))
            data.web_enable_setpoint_restriction = bool(web & (1 << 5))
            data.web_disable_all_keys = bool(web & (1 << 6))
            data.web_disable_seasonal_key = bool(web & (1 << 8))
            data.supervisor_mode = bool(web & (1 << 3) and web & (1 << 2))

        # 9. Flap Swing Register 457
        if 457 in registers:
            data.flap_swing = bool(registers[457] & 0x01)

        # 10. Sensor Offset 530 & Limits 302, 303
        if 530 in registers:
            data.room_temp_offset = cls._to_signed_16(registers[530]) * 0.1
        if 302 in registers:
            data.web_min_setpoint = registers[302] * 0.1
        if 303 in registers:
            data.web_max_setpoint = registers[303] * 0.1

        return data

    @classmethod
    def from_registers_legacy(cls, registers: dict[int, int]) -> InnovaData:
        """Parse raw registers for legacy n273025c board family."""
        data = cls(board_family=InnovaBoardFamily.N273025C)

        # 1. Temperatures
        if 0 in registers:
            raw_t1 = cls._to_signed_16(registers[0])
            t1 = raw_t1 * 0.1
            data.room_temperature = t1 if TEMP_MIN_VALID <= t1 <= TEMP_MAX_VALID else None

        if 1 in registers:
            raw_t2 = cls._to_signed_16(registers[1])
            t2 = raw_t2 * 0.1
            data.inlet_water_temp_t2 = t2 if TEMP_MIN_VALID <= t2 <= TEMP_MAX_VALID else None

        if 2 in registers:
            raw_t3 = cls._to_signed_16(registers[2])
            t3 = raw_t3 * 0.1
            data.coil_water_temp_t3 = t3 if TEMP_MIN_VALID <= t3 <= TEMP_MAX_VALID else None

        if 20 in registers:
            rh = registers[20] * 0.1
            if 0 < rh <= 100:
                data.relative_humidity = round(rh, 1)
                data.rh_sensor_present = True

        # 2. Target Temperature Setpoint
        if 231 in registers:
            sp = registers[231] * 0.1
            if 5.0 <= sp <= 40.0:
                data.target_temperature = round(sp, 1)

        # 3. Status Register 104
        if 104 in registers:
            status = registers[104]
            data.raw_status = status
            data.alarm_active = bool(status & (1 << 6))
            data.t2_probe_present = not bool(status & (1 << 11))
            data.t3_probe_present = not bool(status & (1 << 12))

            if status & (1 << 8):
                data.action = InnovaAction.STANDBY
                data.status_description = "Standby"
            elif status & (1 << 0):
                data.action = InnovaAction.COOLING
                data.status_description = "Cooling"
            elif status & (1 << 1):
                data.action = InnovaAction.HEATING
                data.status_description = "Heating"
            else:
                data.action = InnovaAction.IDLE
                data.status_description = "Idle"

        # 4. Alarms Register 105
        if 105 in registers:
            alarm = registers[105]
            data.raw_alarms = alarm
            data.alarm_description = cls._decode_alarms_legacy(alarm)

        # 5. Program Register 201
        if 201 in registers:
            prg = registers[201]
            data.raw_program = prg
            data.power_on = not bool(prg & (1 << 7))
            if not data.power_on:
                data.mode = InnovaMode.OFF
            data.keypad_locked = bool(prg & (1 << 4))

            fan_mode = prg & 0x07
            if fan_mode in (1, 2):
                data.fan_speed = InnovaFanSpeed.NIGHT
            elif fan_mode == 3:
                data.fan_speed = InnovaFanSpeed.MAX
            else:
                data.fan_speed = InnovaFanSpeed.AUTO

        # 6. Seasonal Mode Register 233
        if 233 in registers:
            man = registers[233]
            if not data.power_on:
                data.mode = InnovaMode.OFF
            elif man == 3:
                data.mode = InnovaMode.HEATING
            elif man == 5:
                data.mode = InnovaMode.COOLING
            else:
                data.mode = InnovaMode.AUTO

        # 7. Webserver Register 247
        if 247 in registers:
            web = registers[247]
            data.raw_web_flags = web
            data.supervisor_mode = bool(web & (1 << 3) and web & (1 << 2))

        return data

    @staticmethod
    def _to_signed_16(val: int) -> int:
        """Convert unsigned 16-bit word to signed integer."""
        return val - 65536 if val > 32767 else val

    @staticmethod
    def _decode_alarms_modern(alarm: int) -> str:
        """Decode alarm bitmask into human-readable description for modern boards."""
        if alarm == 0:
            return "No faults"
        faults: list[str] = []
        if alarm & (1 << 0):
            faults.append("Modbus Comm Error")
        if alarm & (1 << 1):
            faults.append("Air Temp Sensor (T1) Fault")
        if alarm & (1 << 2):
            faults.append("Coil Water Sensor (T3) Fault")
        if alarm & (1 << 3):
            faults.append("Overall Water Temp Inadequate")
        if alarm & (1 << 4):
            faults.append("Inlet Water Sensor (T2) Fault")
        if alarm & (1 << 5):
            faults.append("Inadequate Coil Water (T3) Temp")
        if alarm & (1 << 6):
            faults.append("Electric Heater Over-temp")
        if alarm & (1 << 7):
            faults.append("Fan Motor Failure")
        if alarm & (1 << 8):
            faults.append("Window/Door Contact Open (IN1)")
        if alarm & (1 << 9):
            faults.append("Inadequate Inlet Water (T2) Temp")
        if alarm & (1 << 10):
            faults.append("Air Filter Needs Cleaning")
        if alarm & (1 << 11):
            faults.append("Lock: Inadequate Inlet Water (T2) Temp")
        if alarm & (1 << 12):
            faults.append("Lock: Inadequate Coil Water (T3) Temp")
        return ", ".join(faults) if faults else f"Alarm code: {alarm}"

    @staticmethod
    def _decode_alarms_legacy(alarm: int) -> str:
        """Decode alarm bitmask into human-readable description for legacy boards."""
        if alarm == 0:
            return "No faults"
        faults: list[str] = []
        if alarm & (1 << 0):
            faults.append("Bridge Comm Error")
        if alarm & (1 << 1):
            faults.append("Air Temp Sensor (T1) Fault")
        if alarm & (1 << 2):
            faults.append("Water Sensor (T3) Fault")
        if alarm & (1 << 3):
            faults.append("Harmful Water Temperature")
        if alarm & (1 << 4):
            faults.append("Water Sensor (T2) Fault")
        return ", ".join(faults) if faults else f"Alarm code: {alarm}"
