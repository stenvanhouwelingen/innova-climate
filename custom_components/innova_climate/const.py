"""Constants for the Innova Climate integration."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "innova_climate"

# Configuration Keys
CONF_CONNECTION_TYPE: Final = "connection_type"
CONF_SERIAL_PORT: Final = "serial_port"
CONF_BAUDRATE: Final = "baudrate"
CONF_HOST: Final = "host"
CONF_PORT: Final = "port"
CONF_SLAVE_ID: Final = "slave_id"
CONF_BOARD_FAMILY: Final = "board_family"

# Connection Types
CONNECTION_TYPE_SERIAL: Final = "serial"
CONNECTION_TYPE_TCP: Final = "tcp"

# Defaults
DEFAULT_BAUDRATE: Final = 9600
DEFAULT_TCP_PORT: Final = 8899
DEFAULT_SLAVE_ID: Final = 1
DEFAULT_POLL_INTERVAL: Final = 10  # seconds

# Events
EVENT_INNOVA_ALARM: Final = "innova_climate_alarm"

# Platforms
PLATFORMS: Final = [
    "climate",
    "sensor",
    "binary_sensor",
    "switch",
    "select",
    "number",
    "button",
    "event",
]
