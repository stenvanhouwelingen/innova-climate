"""Climate platform for Innova Climate integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.components.climate.const import (
    FAN_AUTO,
    FAN_HIGH,
    FAN_LOW,
    PRESET_BOOST,
    PRESET_NONE,
    PRESET_SLEEP,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .innova_modbus import (
    InnovaAction,
    InnovaFanSpeed,
    InnovaMode,
)

from .coordinator import InnovaDataUpdateCoordinator
from .entity import InnovaEntity

_LOGGER = logging.getLogger(__name__)

FAN_MODE_MAP = {
    FAN_AUTO: InnovaFanSpeed.AUTO,
    FAN_LOW: InnovaFanSpeed.NIGHT,
    FAN_HIGH: InnovaFanSpeed.MAX,
}

REVERSE_FAN_MAP = {
    InnovaFanSpeed.AUTO: FAN_AUTO,
    InnovaFanSpeed.NIGHT: FAN_LOW,
    InnovaFanSpeed.MAX: FAN_HIGH,
}

HVAC_MODE_MAP = {
    HVACMode.OFF: InnovaMode.OFF,
    HVACMode.HEAT: InnovaMode.HEATING,
    HVACMode.COOL: InnovaMode.COOLING,
    HVACMode.AUTO: InnovaMode.AUTO,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Innova Climate platform."""
    coordinator: InnovaDataUpdateCoordinator = entry.runtime_data
    async_add_entities([InnovaClimateEntity(coordinator)])


class InnovaClimateEntity(InnovaEntity, ClimateEntity):
    """Innova Fancoil Climate entity."""

    _attr_translation_key = "thermostat"
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_target_temperature_step = 0.5
    _attr_min_temp = 16.0
    _attr_max_temp = 30.0

    _attr_hvac_modes = [
        HVACMode.OFF,
        HVACMode.HEAT,
        HVACMode.COOL,
        HVACMode.AUTO,
    ]
    _attr_fan_modes = [
        FAN_AUTO,
        FAN_LOW,
        FAN_HIGH,
    ]
    _attr_preset_modes = [
        PRESET_NONE,
        PRESET_SLEEP,
        PRESET_BOOST,
    ]

    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.TURN_ON
    )

    def __init__(self, coordinator: InnovaDataUpdateCoordinator) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator, "climate")

    @property
    def current_temperature(self) -> float | None:
        """Return the current room air temperature."""
        return self.coordinator.data.room_temperature

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature setpoint."""
        return self.coordinator.data.target_temperature

    @property
    def current_humidity(self) -> float | None:
        """Return the relative humidity if fitted."""
        return self.coordinator.data.relative_humidity

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current operating mode."""
        if not self.coordinator.data.power_on:
            return HVACMode.OFF
        mode = self.coordinator.data.mode
        if mode == InnovaMode.HEATING:
            return HVACMode.HEAT
        if mode == InnovaMode.COOLING:
            return HVACMode.COOL
        if mode == InnovaMode.AUTO:
            return HVACMode.AUTO
        return HVACMode.OFF

    @property
    def hvac_action(self) -> HVACAction:
        """Return current active action."""
        if not self.coordinator.data.power_on:
            return HVACAction.OFF
        act = self.coordinator.data.action
        if act == InnovaAction.HEATING:
            return HVACAction.HEATING
        if act == InnovaAction.COOLING:
            return HVACAction.COOLING
        if act == InnovaAction.STANDBY:
            return HVACAction.OFF
        return HVACAction.IDLE

    @property
    def fan_mode(self) -> str:
        """Return current fan speed mode."""
        return REVERSE_FAN_MAP.get(self.coordinator.data.fan_speed, FAN_AUTO)

    @property
    def preset_mode(self) -> str:
        """Return the current preset mode."""
        if self.coordinator.data.fan_speed == InnovaFanSpeed.NIGHT:
            return PRESET_SLEEP
        if self.coordinator.data.fan_speed == InnovaFanSpeed.MAX:
            return PRESET_BOOST
        return PRESET_NONE

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temp := kwargs.get(ATTR_TEMPERATURE)) is not None:
            await self.coordinator.device.async_set_target_temperature(temp)
            self.async_write_ha_state()
            await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target HVAC mode."""
        if hvac_mode in HVAC_MODE_MAP:
            await self.coordinator.device.async_set_mode(HVAC_MODE_MAP[hvac_mode])
            self.async_write_ha_state()
            await self.coordinator.async_request_refresh()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new target fan speed."""
        if fan_mode in FAN_MODE_MAP:
            await self.coordinator.device.async_set_fan_speed(FAN_MODE_MAP[fan_mode])
            self.async_write_ha_state()
            await self.coordinator.async_request_refresh()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode (Night / Boost / None)."""
        if preset_mode == PRESET_SLEEP:
            await self.coordinator.device.async_set_fan_speed(InnovaFanSpeed.NIGHT)
        elif preset_mode == PRESET_BOOST:
            await self.coordinator.device.async_set_fan_speed(InnovaFanSpeed.MAX)
        else:
            await self.coordinator.device.async_set_fan_speed(InnovaFanSpeed.AUTO)
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self) -> None:
        """Turn on the fancoil."""
        await self.coordinator.device.async_set_power(True)
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn off the fancoil (Standby)."""
        await self.coordinator.device.async_set_power(False)
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()
