"""Switch platform for Innova Climate integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Coroutine

from homeassistant.components.switch import (
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .innova_modbus import InnovaBoardFamily, InnovaData, InnovaFancoil

from .coordinator import InnovaDataUpdateCoordinator
from .entity import InnovaEntity


@dataclass(frozen=True, kw_only=True)
class InnovaSwitchEntityDescription(SwitchEntityDescription):
    """Describes Innova switch entity."""

    is_on_fn: Callable[[InnovaData], bool]
    set_fn: Callable[[InnovaFancoil, bool], Coroutine[Any, Any, None]]


SWITCH_DESCRIPTIONS: tuple[InnovaSwitchEntityDescription, ...] = (
    InnovaSwitchEntityDescription(
        key="supervisor_mode",
        translation_key="supervisor_mode",
        icon="mdi:shield-account",
        entity_category=EntityCategory.CONFIG,
        is_on_fn=lambda data: data.supervisor_mode,
        set_fn=lambda device, val: device.async_set_supervisor_mode(val),
    ),
    InnovaSwitchEntityDescription(
        key="keypad_lock",
        translation_key="keypad_lock",
        icon="mdi:lock",
        entity_category=EntityCategory.CONFIG,
        is_on_fn=lambda data: data.keypad_locked,
        set_fn=lambda device, val: device.async_set_keypad_lock(val),
    ),
    InnovaSwitchEntityDescription(
        key="web_led_off",
        translation_key="web_led_off",
        icon="mdi:led-off",
        entity_category=EntityCategory.CONFIG,
        is_on_fn=lambda data: data.web_led_off,
        set_fn=lambda device, val: device.async_set_led_off(val),
    ),
    InnovaSwitchEntityDescription(
        key="flap_swing",
        translation_key="flap_swing",
        icon="mdi:weather-windy",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
        is_on_fn=lambda data: data.flap_swing,
        set_fn=lambda device, val: device.async_set_flap_swing(val),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Innova Climate switch entities."""
    coordinator: InnovaDataUpdateCoordinator = entry.runtime_data
    entities: list[InnovaSwitchEntity] = []
    for description in SWITCH_DESCRIPTIONS:
        if (
            description.key == "flap_swing"
            and coordinator.device.board_family != InnovaBoardFamily.N273025D
        ):
            continue
        entities.append(InnovaSwitchEntity(coordinator, description))
    async_add_entities(entities)


class InnovaSwitchEntity(InnovaEntity, SwitchEntity):
    """Representation of an Innova Fancoil switch."""

    entity_description: InnovaSwitchEntityDescription

    def __init__(
        self,
        coordinator: InnovaDataUpdateCoordinator,
        description: InnovaSwitchEntityDescription,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        return self.entity_description.is_on_fn(self.coordinator.data)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self.entity_description.set_fn(self.coordinator.device, True)
        await self.coordinator.async_notify_write()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self.entity_description.set_fn(self.coordinator.device, False)
        await self.coordinator.async_notify_write()
