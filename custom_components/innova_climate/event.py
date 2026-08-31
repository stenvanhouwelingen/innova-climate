"""Event platform for Innova Climate integration."""

from __future__ import annotations

from homeassistant.components.event import (
    EventDeviceClass,
    EventEntity,
    EventEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import InnovaDataUpdateCoordinator
from .entity import InnovaEntity

EVENT_TYPES = [
    "alarm",
    "alarm_cleared",
    "filter_cleaning_required",
    "window_opened",
    "window_closed",
]

EVENT_DESCRIPTION = EventEntityDescription(
    key="alarm_event",
    translation_key="alarm_event",
    event_types=EVENT_TYPES,
    entity_category=EntityCategory.DIAGNOSTIC,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Innova Climate event entities."""
    coordinator: InnovaDataUpdateCoordinator = entry.runtime_data
    async_add_entities([InnovaAlarmEventEntity(coordinator, EVENT_DESCRIPTION)])


class InnovaAlarmEventEntity(InnovaEntity, EventEntity):
    """Representation of an Innova Fancoil alarm event entity."""

    entity_description: EventEntityDescription

    def __init__(
        self,
        coordinator: InnovaDataUpdateCoordinator,
        description: EventEntityDescription,
    ) -> None:
        """Initialize the event entity."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    async def async_added_to_hass(self) -> None:
        """Register event listener on coordinator."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self.coordinator.register_event_listener(self._handle_event)
        )

    @callback
    def _handle_event(self, event_type: str, event_data: dict) -> None:
        """Trigger event entity in Home Assistant."""
        if event_type in EVENT_TYPES:
            self._trigger_event(event_type, event_data)
            self.async_write_ha_state()
