"""Diagnostics support for Innova Climate integration."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import InnovaDataUpdateCoordinator


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: InnovaDataUpdateCoordinator = entry.runtime_data
    data = coordinator.data

    return {
        "config_entry": {
            "title": entry.title,
            "data": dict(entry.data),
            "options": dict(entry.options),
        },
        "device": {
            "slave_id": coordinator.device.slave_id,
            "board_family": coordinator.device.board_family,
            "state": {
                "room_temperature": data.room_temperature,
                "inlet_water_temp_t2": data.inlet_water_temp_t2,
                "coil_water_temp_t3": data.coil_water_temp_t3,
                "relative_humidity": data.relative_humidity,
                "target_temperature": data.target_temperature,
                "mode": str(data.mode),
                "fan_speed": str(data.fan_speed),
                "power_on": data.power_on,
                "action": str(data.action),
                "raw_status": bin(data.raw_status),
                "raw_alarms": bin(data.raw_alarms),
                "raw_program": bin(data.raw_program),
                "raw_web_flags": bin(data.raw_web_flags),
                "firmware_release": data.firmware_release,
                "firmware_id": data.firmware_id,
                "alarm_active": data.alarm_active,
                "alarm_description": data.alarm_description,
                "status_description": data.status_description,
                "fan_status_description": data.fan_status_description,
                "t2_probe_present": data.t2_probe_present,
                "t3_probe_present": data.t3_probe_present,
                "rh_sensor_present": data.rh_sensor_present,
                "window_contact_open": data.window_contact_open,
                "supervisor_mode": data.supervisor_mode,
                "keypad_locked": data.keypad_locked,
                "flap_swing": data.flap_swing,
                "room_temp_offset": data.room_temp_offset,
            },
        },
    }
