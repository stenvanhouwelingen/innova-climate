"""Innova Fancoil Modbus Device Controller."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Protocol

from .const import (
    InnovaBoardFamily,
    InnovaFanSpeed,
    InnovaMode,
    InnovaRegistersLegacy,
    InnovaRegistersModern,
    MAX_REGISTERS_PER_READ,
    MIN_COMMAND_INTERVAL_SECONDS,
)
from .model import InnovaData

_LOGGER = logging.getLogger(__name__)


class ModbusConnectionProtocol(Protocol):
    """Protocol for Modbus unit connection interface."""

    async def read_holding_registers(self, address: int, count: int) -> list[int]:
        """Read a range of holding registers."""
        ...

    async def write_holding_register(self, address: int, value: int) -> None:
        """Write a single holding register."""
        ...


class InnovaFancoil:
    """Device controller for an Innova Fancoil unit over Modbus."""

    def __init__(
        self,
        connection: Any,
        slave_id: int = 1,
        board_family: InnovaBoardFamily = InnovaBoardFamily.N273025D,
    ) -> None:
        """Initialize the Innova fancoil device."""
        self._connection = connection
        self._slave_id = slave_id
        self._board_family = board_family
        self.data: InnovaData = InnovaData(board_family=board_family)
        self._lock = asyncio.Lock()

    @property
    def slave_id(self) -> int:
        """Return the Modbus slave address."""
        return self._slave_id

    @property
    def board_family(self) -> InnovaBoardFamily:
        """Return the active board family."""
        return self._board_family

    async def async_update(self) -> InnovaData:
        """Fetch all device registers in safe batches and parse into InnovaData."""
        async with self._lock:
            registers: dict[int, int] = {}

            if self._board_family == InnovaBoardFamily.N273025D:
                batches = [
                    (0, 3),     # Regs 0, 1, 2 (T_AIR, T_WATER_2, T_WATER_4)
                    (20, 1),    # Reg 20 (RH)
                    (150, 2),   # Regs 150, 151 (Status, Alarms)
                    (198, 2),   # Regs 198, 199 (FW_Release, FW_ID)
                    (302, 2),   # Regs 302, 303 (SPL_W, SPH_W)
                    (305, 1),   # Reg 305 (Target Setpoint)
                    (457, 1),   # Reg 457 (Flap Swing)
                    (530, 1),   # Reg 530 (T1 Sensor Offset)
                    (553, 1),   # Reg 553 (PRG Program Control)
                    (556, 2),   # Regs 556, 557 (Seasonal Mode, Web Flags)
                ]
            else:
                batches = [
                    (0, 3),     # Regs 0, 1, 2 (T_AIR, T_WATER_2, T_WATER_4)
                    (20, 1),    # Reg 20 (RH)
                    (104, 2),   # Regs 104, 105 (Status, Alarms)
                    (201, 1),   # Reg 201 (PRG Program Control)
                    (231, 1),   # Reg 231 (Target Setpoint)
                    (233, 1),   # Reg 233 (Seasonal Mode)
                    (242, 1),   # Reg 242 (T1 Sensor Offset)
                    (245, 3),   # Regs 245, 246, 247 (SPL_W, SPH_W, Web Flags)
                ]

            for start_addr, count in batches:
                try:
                    vals = await self._read_registers(start_addr, count)
                    for i, val in enumerate(vals):
                        registers[start_addr + i] = val
                except Exception as err:
                    _LOGGER.warning(
                        "Failed to read Modbus registers starting at %d (count %d): %s",
                        start_addr,
                        count,
                        err,
                    )
                await asyncio.sleep(MIN_COMMAND_INTERVAL_SECONDS)

            if not registers:
                raise RuntimeError(
                    f"Failed to communicate with Innova Fancoil (slave_id={self._slave_id}): No registers could be read"
                )

            if self._board_family == InnovaBoardFamily.N273025D:
                self.data = InnovaData.from_registers_modern(registers)
            else:
                self.data = InnovaData.from_registers_legacy(registers)

            return self.data

    async def async_set_target_temperature(self, temperature: float) -> None:
        """Set the target room temperature setpoint."""
        async with self._lock:
            val = int(round(temperature * 10.0))
            reg = (
                InnovaRegistersModern.SP
                if self._board_family == InnovaBoardFamily.N273025D
                else InnovaRegistersLegacy.SP
            )
            await self._write_register(reg, val)
            self.data.target_temperature = temperature

    async def async_set_mode(self, mode: InnovaMode) -> None:
        """Set the seasonal operating mode (Heating, Cooling, Auto, or Off)."""
        async with self._lock:
            if mode == InnovaMode.OFF:
                await self._set_power_unlocked(False)
                self.data.mode = InnovaMode.OFF
                return

            await self._set_power_unlocked(True)

            if self._board_family == InnovaBoardFamily.N273025D:
                reg = InnovaRegistersModern.MAN
                val = 1 if mode == InnovaMode.HEATING else (2 if mode == InnovaMode.COOLING else 0)
            else:
                reg = InnovaRegistersLegacy.MAN
                val = 3 if mode == InnovaMode.HEATING else (5 if mode == InnovaMode.COOLING else 0)

            await self._write_register(reg, val)
            self.data.mode = mode

    async def async_set_fan_speed(self, fan_speed: InnovaFanSpeed) -> None:
        """Set the ventilation fan speed mode."""
        async with self._lock:
            prg_reg = (
                InnovaRegistersModern.PRG
                if self._board_family == InnovaBoardFamily.N273025D
                else InnovaRegistersLegacy.PRG
            )

            current_prg = self.data.raw_program
            base_prg = current_prg & ~0x07

            if self._board_family == InnovaBoardFamily.N273025D:
                speed_bits = 1 if fan_speed == InnovaFanSpeed.NIGHT else (2 if fan_speed == InnovaFanSpeed.MAX else 0)
            else:
                speed_bits = 1 if fan_speed == InnovaFanSpeed.NIGHT else (3 if fan_speed == InnovaFanSpeed.MAX else 0)

            new_prg = base_prg | speed_bits
            await self._write_register(prg_reg, new_prg)
            self.data.fan_speed = fan_speed
            self.data.raw_program = new_prg

    async def async_set_power(self, power_on: bool) -> None:
        """Turn the fancoil ON or into Standby (OFF)."""
        async with self._lock:
            await self._set_power_unlocked(power_on)

    async def _set_power_unlocked(self, power_on: bool) -> None:
        """Internal helper to set power register while lock is held."""
        prg_reg = (
            InnovaRegistersModern.PRG
            if self._board_family == InnovaBoardFamily.N273025D
            else InnovaRegistersLegacy.PRG
        )

        current_prg = self.data.raw_program
        if self._board_family == InnovaBoardFamily.N273025D:
            new_prg = (current_prg & ~0x0010) if power_on else (current_prg | 0x0010)
        else:
            new_prg = (current_prg & ~0x0080) if power_on else (current_prg | 0x0080)

        await self._write_register(prg_reg, new_prg)
        self.data.power_on = power_on
        self.data.raw_program = new_prg

    async def async_set_supervisor_mode(self, enable: bool) -> None:
        """Enable or disable remote supervisor mode (locks local panel buttons)."""
        async with self._lock:
            web_reg = (
                InnovaRegistersModern.WEB
                if self._board_family == InnovaBoardFamily.N273025D
                else InnovaRegistersLegacy.WEB
            )

            current_web = self.data.raw_web_flags
            if enable:
                new_web = current_web | (1 << 3) | (1 << 2)
            else:
                new_web = current_web & ~((1 << 3) | (1 << 2))

            await self._write_register(web_reg, new_web)
            self.data.supervisor_mode = enable
            self.data.raw_web_flags = new_web

    async def async_set_flap_swing(self, swing: bool) -> None:
        """Enable or disable motorized flap swing."""
        if self._board_family != InnovaBoardFamily.N273025D:
            return
        async with self._lock:
            val = 1 if swing else 0
            await self._write_register(InnovaRegistersModern.FSW, val)
            self.data.flap_swing = swing

    async def async_set_keypad_lock(self, locked: bool) -> None:
        """Lock or unlock the physical on-board touch panel."""
        async with self._lock:
            prg_reg = (
                InnovaRegistersModern.PRG
                if self._board_family == InnovaBoardFamily.N273025D
                else InnovaRegistersLegacy.PRG
            )
            current_prg = self.data.raw_program
            bit = 3 if self._board_family == InnovaBoardFamily.N273025D else 4
            new_prg = (current_prg | (1 << bit)) if locked else (current_prg & ~(1 << bit))

            await self._write_register(prg_reg, new_prg)
            self.data.keypad_locked = locked
            self.data.raw_program = new_prg

    async def async_set_room_temp_offset(self, offset: float) -> None:
        """Set calibration offset for T1 room air sensor (-1.2 °C to +1.2 °C)."""
        async with self._lock:
            val = int(round(offset * 10.0))
            if val < 0:
                val = (val + 65536) & 0xFFFF
            reg = (
                InnovaRegistersModern.OS1
                if self._board_family == InnovaBoardFamily.N273025D
                else InnovaRegistersLegacy.OS1
            )
            await self._write_register(reg, val)
            self.data.room_temp_offset = offset

    async def _read_registers(self, start_addr: int, count: int) -> list[int]:
        """Read a chunk of holding registers from the Modbus connection."""
        if hasattr(self._connection, "read_holding_registers"):
            res = None
            for kw in ({"slave": self._slave_id}, {"device_id": self._slave_id}, {"unit": self._slave_id}):
                try:
                    res = await self._connection.read_holding_registers(
                        address=start_addr,
                        count=count,
                        **kw,
                    )
                    break
                except TypeError:
                    continue
            if res is None:
                res = await self._connection.read_holding_registers(
                    address=start_addr,
                    count=count,
                )

            if hasattr(res, "registers"):
                return list(res.registers)
            if isinstance(res, (list, tuple)):
                return list(res)
        raise RuntimeError(f"Unsupported connection backend: {type(self._connection)}")

    async def _write_register(self, address: int, value: int) -> None:
        """Write a single holding register value to the Modbus connection."""
        if hasattr(self._connection, "write_holding_register"):
            res = None
            for kw in ({"slave": self._slave_id}, {"device_id": self._slave_id}, {"unit": self._slave_id}):
                try:
                    res = await self._connection.write_holding_register(
                        address=address,
                        value=value,
                        **kw,
                    )
                    break
                except TypeError:
                    continue
            if res is None:
                await self._connection.write_holding_register(
                    address=address,
                    value=value,
                )

            await asyncio.sleep(MIN_COMMAND_INTERVAL_SECONDS)
            return
        raise RuntimeError(f"Unsupported connection backend: {type(self._connection)}")
