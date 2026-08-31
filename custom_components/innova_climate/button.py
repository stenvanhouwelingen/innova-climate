"""Button platform for Innova Climate integration."""

from __future__ import annotations

from homeassistant.components.button import (
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import InnovaDataUpdateCoordinator
from .entity import InnovaEntity

BUTTON_DESCRIPTIONS: tuple[ButtonEntityDescription, ...] = (
    ButtonEntityDescription(
        key="force_refresh",
        translation_key="force_refresh",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Innova Climate button entities."""
    coordinator: InnovaDataUpdateCoordinator = entry.runtime_data
    async_add_entities(
        InnovaButtonEntity(coordinator, description)
        for description in BUTTON_DESCRIPTIONS
    )


class InnovaButtonEntity(InnovaEntity, ButtonEntity):
    """Representation of an Innova Fancoil button entity."""

    entity_description: ButtonEntityDescription

    def __init__(
        self,
        coordinator: InnovaDataUpdateCoordinator,
        description: ButtonEntityDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    async def async_press(self) -> None:
        """Handle button press."""
        await self.coordinator.async_request_refresh()
