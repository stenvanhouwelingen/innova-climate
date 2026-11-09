"""Number platform for Innova Climate integration."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import InnovaDataUpdateCoordinator
from .entity import InnovaEntity
from .innova_modbus import InnovaData, InnovaFancoil


@dataclass(frozen=True, kw_only=True)
class InnovaNumberEntityDescription(NumberEntityDescription):
    """Describes Innova number entity."""

    value_fn: Callable[[InnovaData], float | None]
    set_fn: Callable[[InnovaFancoil, float], Coroutine[Any, Any, None]]


NUMBER_DESCRIPTIONS: tuple[InnovaNumberEntityDescription, ...] = (
    InnovaNumberEntityDescription(
        key="t1_sensor_offset",
        translation_key="t1_sensor_offset",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=-1.2,
        native_max_value=1.2,
        native_step=0.1,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda data: data.room_temp_offset,
        set_fn=lambda device, val: device.async_set_room_temp_offset(val),
    ),
    InnovaNumberEntityDescription(
        key="min_water_temp_heating",
        translation_key="min_water_temp_heating",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=10.0,
        native_max_value=50.0,
        native_step=0.5,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda data: data.min_water_temp_heating,
        set_fn=lambda device, val: device.async_set_min_water_temp_heating(val),
    ),
    InnovaNumberEntityDescription(
        key="max_water_temp_cooling",
        translation_key="max_water_temp_cooling",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=10.0,
        native_max_value=35.0,
        native_step=0.5,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda data: data.max_water_temp_cooling,
        set_fn=lambda device, val: device.async_set_max_water_temp_cooling(val),
    ),
    InnovaNumberEntityDescription(
        key="web_min_setpoint",
        translation_key="web_min_setpoint",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=5.0,
        native_max_value=40.0,
        native_step=0.5,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.web_min_setpoint,
        set_fn=lambda device, val: device.async_set_min_setpoint_limit(val),
    ),
    InnovaNumberEntityDescription(
        key="web_max_setpoint",
        translation_key="web_max_setpoint",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=5.0,
        native_max_value=40.0,
        native_step=0.5,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.web_max_setpoint,
        set_fn=lambda device, val: device.async_set_max_setpoint_limit(val),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Innova Climate number entities."""
    coordinator: InnovaDataUpdateCoordinator = entry.runtime_data
    async_add_entities(
        InnovaNumberEntity(coordinator, description)
        for description in NUMBER_DESCRIPTIONS
    )


class InnovaNumberEntity(InnovaEntity, NumberEntity):
    """Representation of an Innova Fancoil number configuration entity."""

    entity_description: InnovaNumberEntityDescription

    def __init__(
        self,
        coordinator: InnovaDataUpdateCoordinator,
        description: InnovaNumberEntityDescription,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> float | None:
        """Return current value."""
        return self.entity_description.value_fn(self.coordinator.data)

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        await self.entity_description.set_fn(self.coordinator.device, value)
        await self.coordinator.async_notify_write()
