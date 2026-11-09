"""Innova Fancoil Modbus Library (Vendored for Home Assistant Integration)."""

from .const import (
    FLAP_MODE_TO_REG,
    MAX_REGISTERS_PER_READ,
    MIN_COMMAND_INTERVAL_SECONDS,
    REG_TO_FLAP_MODE,
    InnovaAction,
    InnovaBoardFamily,
    InnovaFanSpeed,
    InnovaFlapMode,
    InnovaMode,
    InnovaRegistersLegacy,
    InnovaRegistersModern,
)
from .device import InnovaFancoil
from .model import InnovaData

__all__ = [
    "FLAP_MODE_TO_REG",
    "MAX_REGISTERS_PER_READ",
    "MIN_COMMAND_INTERVAL_SECONDS",
    "REG_TO_FLAP_MODE",
    "InnovaAction",
    "InnovaBoardFamily",
    "InnovaData",
    "InnovaFanSpeed",
    "InnovaFancoil",
    "InnovaFlapMode",
    "InnovaMode",
    "InnovaRegistersLegacy",
    "InnovaRegistersModern",
]
