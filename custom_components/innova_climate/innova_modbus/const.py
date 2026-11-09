"""Constants and Enums for the Innova Modbus library."""

from __future__ import annotations

from enum import StrEnum


class InnovaBoardFamily(StrEnum):
    """Supported Innova control board families."""

    N273025D = "n273025d"  # Modern (OSMO, AirLeaf, FÄRNA, Filomuro, M7/PU boards)
    N273025C = "n273025c"  # Legacy / Bridge retrofits (Filoterra, INN-FR-B32)


class InnovaMode(StrEnum):
    """Innova seasonal operating mode."""

    AUTO = "auto"
    HEATING = "heating"
    COOLING = "cooling"
    OFF = "off"


class InnovaFanSpeed(StrEnum):
    """Innova ventilation fan speed."""

    AUTO = "auto"
    NIGHT = "night"  # Silent / Minimum speed
    MAX = "max"      # Maximum / Boost speed


class InnovaAction(StrEnum):
    """Active operating action."""

    OFF = "off"
    STANDBY = "standby"
    IDLE = "idle"
    HEATING = "heating"
    COOLING = "cooling"


class InnovaFlapMode(StrEnum):
    """Innova Filomuro motorized flap mode / position."""

    AUTO = "auto"              # 0: Automatic / Default opening
    POSITION_1 = "position_1"  # 1: Fixed Position 1 (Halfway / 45 deg)
    POSITION_2 = "position_2"  # 2: Fixed Position 2 (Horizontal)
    POSITION_3 = "position_3"  # 3: Fixed Position 3 (Fully Open)
    SWING = "swing"            # 7 (or 4): Continuous oscillation


FLAP_MODE_TO_REG: dict[InnovaFlapMode, int] = {
    InnovaFlapMode.AUTO: 0,
    InnovaFlapMode.POSITION_1: 1,
    InnovaFlapMode.POSITION_2: 2,
    InnovaFlapMode.POSITION_3: 3,
    InnovaFlapMode.SWING: 7,
}

REG_TO_FLAP_MODE: dict[int, InnovaFlapMode] = {
    0: InnovaFlapMode.AUTO,
    1: InnovaFlapMode.POSITION_1,
    2: InnovaFlapMode.POSITION_2,
    3: InnovaFlapMode.POSITION_3,
    4: InnovaFlapMode.SWING,
    7: InnovaFlapMode.SWING,
}


class InnovaRegistersModern:
    """Holding register addresses for the n273025d modern board family."""

    # Temperature & Humidity (Read Only)
    T_AIR = 0          # Room air temperature (0.1 °C)
    T_WATER_2 = 1      # Inlet / return water temperature (0.1 °C)
    T_WATER_4 = 2      # Coil / supply water temperature (0.1 °C)
    RH = 20            # Relative humidity (% RH)

    # Diagnostic & Status
    STATUS = 150       # Operating status bitmask
    ALARMS = 151       # Alarm code bitmask
    FW_RELEASE = 198   # Firmware version (0.1 scale)
    FW_ID = 199        # Firmware ID (e.g. 1190 for PU board)

    # Setpoints & Configuration
    SPL_W = 302        # Web minimum setpoint limit (0.1 °C)
    SPH_W = 303        # Web maximum setpoint limit (0.1 °C)
    SP = 305           # Target temperature setpoint (0.1 °C)
    FSW = 457          # Flap swing motorized louver (0=Off, 1=On)
    LLO = 510          # Minimum water temperature for heating (0.1 °C)
    LHI = 511          # Maximum water temperature for cooling (0.1 °C)
    OS1 = 530          # Room sensor calibration offset (0.1 °C)
    ADR = 550          # Modbus slave address
    PRG = 553          # Program control (Fan speed, standby, keypad lock)
    MAN = 556          # Seasonal mode (0=Auto, 1=Heating, 2=Cooling)
    WEB = 557          # Webserver lockout flags
    TY = 574           # Unit type & buzzer config


class InnovaRegistersLegacy:
    """Holding register addresses for the n273025c legacy / bridge family."""

    # Temperature & Humidity (Read Only)
    T_AIR = 0          # Room air temperature (0.1 °C)
    T_WATER_2 = 1      # Inlet / return water temperature (0.1 °C)
    T_WATER_4 = 2      # Coil / supply water temperature (0.1 °C)
    RH = 20            # Relative humidity (% RH)

    # Diagnostic & Status
    STATUS = 104       # Operating status bitmask
    ALARMS = 105       # Alarm code bitmask

    # Setpoints & Configuration
    ADR = 200          # Modbus slave address
    PRG = 201          # Program control (Fan speed, standby, keypad lock)
    LLO = 218          # Minimum water temperature for heating (0.1 °C)
    LHI = 219          # Maximum water temperature for cooling (0.1 °C)
    SP = 231           # Target temperature setpoint (0.1 °C)
    MAN = 233          # Seasonal mode (0=Auto, 3=Heating, 5=Cooling)
    OS1 = 242          # Room sensor calibration offset (0.1 °C)
    SPL_W = 245        # Web minimum setpoint limit (0.1 °C)
    SPH_W = 246        # Web maximum setpoint limit (0.1 °C)
    WEB = 247          # Webserver lockout flags


# Timing Constraints
MIN_COMMAND_INTERVAL_SECONDS = 0.15  # 150ms between Modbus requests
MAX_REGISTERS_PER_READ = 3           # Hardware limit: max 3 registers per read request

# Temperature Limits
TEMP_MIN_VALID = -30.0  # Celsius (values below indicate disconnected/faulty sensor)
TEMP_MAX_VALID = 80.0   # Celsius
DEFAULT_SETPOINT = 20.0 # Celsius
MIN_SETPOINT = 16.0     # Celsius
MAX_SETPOINT = 30.0     # Celsius
