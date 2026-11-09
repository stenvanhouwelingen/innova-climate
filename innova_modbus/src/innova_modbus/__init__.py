"""Innova Fancoil Modbus Library."""

from .const import (
    FLAP_MODE_TO_REG,
    InnovaAction,
    InnovaBoardFamily,
    InnovaFanSpeed,
    InnovaFlapMode,
    InnovaMode,
    InnovaRegistersLegacy,
    InnovaRegistersModern,
    MAX_REGISTERS_PER_READ,
    MIN_COMMAND_INTERVAL_SECONDS,
    REG_TO_FLAP_MODE,
)
from .device import InnovaFancoil
from .model import InnovaData

__version__ = "0.2.0"
__all__ = [
    "FLAP_MODE_TO_REG",
    "InnovaAction",
    "InnovaBoardFamily",
    "InnovaData",
    "InnovaFanSpeed",
    "InnovaFancoil",
    "InnovaFlapMode",
    "InnovaMode",
    "InnovaRegistersLegacy",
    "InnovaRegistersModern",
    "MAX_REGISTERS_PER_READ",
    "MIN_COMMAND_INTERVAL_SECONDS",
    "REG_TO_FLAP_MODE",
]
