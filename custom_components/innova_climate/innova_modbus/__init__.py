"""Innova Fancoil Modbus Library (Vendored for Home Assistant Integration)."""

from .const import (
    InnovaAction,
    InnovaBoardFamily,
    InnovaFanSpeed,
    InnovaMode,
    InnovaRegistersLegacy,
    InnovaRegistersModern,
    MAX_REGISTERS_PER_READ,
    MIN_COMMAND_INTERVAL_SECONDS,
)
from .device import InnovaFancoil
from .model import InnovaData

__all__ = [
    "InnovaAction",
    "InnovaBoardFamily",
    "InnovaData",
    "InnovaFanSpeed",
    "InnovaFancoil",
    "InnovaMode",
    "InnovaRegistersLegacy",
    "InnovaRegistersModern",
    "MAX_REGISTERS_PER_READ",
    "MIN_COMMAND_INTERVAL_SECONDS",
]
