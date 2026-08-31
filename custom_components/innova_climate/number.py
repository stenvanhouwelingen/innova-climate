"""Number platform for Innova Climate integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Coroutine

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
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()
