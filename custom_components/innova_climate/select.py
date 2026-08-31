"""Select platform for Innova Climate integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Coroutine

from homeassistant.components.select import (
    SelectEntity,
    SelectEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .innova_modbus import (
    InnovaData,
    InnovaFancoil,
    InnovaFanSpeed,
    InnovaMode,
)

from .coordinator import InnovaDataUpdateCoordinator
from .entity import InnovaEntity


@dataclass(frozen=True, kw_only=True)
class InnovaSelectEntityDescription(SelectEntityDescription):
    """Describes Innova select entity."""

    current_option_fn: Callable[[InnovaData], str]
    set_option_fn: Callable[[InnovaFancoil, str], Coroutine[Any, Any, None]]


SELECT_DESCRIPTIONS: tuple[InnovaSelectEntityDescription, ...] = (
    InnovaSelectEntityDescription(
        key="fan_speed_select",
        translation_key="fan_speed_select",
        options=[InnovaFanSpeed.AUTO, InnovaFanSpeed.NIGHT, InnovaFanSpeed.MAX],
        entity_category=EntityCategory.CONFIG,
        current_option_fn=lambda data: str(data.fan_speed),
        set_option_fn=lambda device, opt: device.async_set_fan_speed(InnovaFanSpeed(opt)),
    ),
    InnovaSelectEntityDescription(
        key="seasonal_mode_select",
        translation_key="seasonal_mode_select",
        options=[InnovaMode.AUTO, InnovaMode.HEATING, InnovaMode.COOLING],
        entity_category=EntityCategory.CONFIG,
        current_option_fn=lambda data: str(data.mode) if data.mode != InnovaMode.OFF else str(InnovaMode.AUTO),
        set_option_fn=lambda device, opt: device.async_set_mode(InnovaMode(opt)),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Innova Climate select entities."""
    coordinator: InnovaDataUpdateCoordinator = entry.runtime_data
    async_add_entities(
        InnovaSelectEntity(coordinator, description)
        for description in SELECT_DESCRIPTIONS
    )


class InnovaSelectEntity(InnovaEntity, SelectEntity):
    """Representation of an Innova Fancoil select entity."""

    entity_description: InnovaSelectEntityDescription

    def __init__(
        self,
        coordinator: InnovaDataUpdateCoordinator,
        description: InnovaSelectEntityDescription,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def current_option(self) -> str | None:
        """Return currently selected option."""
        return self.entity_description.current_option_fn(self.coordinator.data)

    async def async_select_option(self, option: str) -> None:
        """Change selected option."""
        await self.entity_description.set_option_fn(self.coordinator.device, option)
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()
