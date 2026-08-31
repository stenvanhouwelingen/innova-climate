"""Binary sensor platform for Innova Climate integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .innova_modbus import InnovaData

from .coordinator import InnovaDataUpdateCoordinator
from .entity import InnovaEntity


@dataclass(frozen=True, kw_only=True)
class InnovaBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes Innova binary sensor entity."""

    is_on_fn: Callable[[InnovaData], bool]


BINARY_SENSOR_DESCRIPTIONS: tuple[InnovaBinarySensorEntityDescription, ...] = (
    InnovaBinarySensorEntityDescription(
        key="alarm_status",
        translation_key="alarm_status",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        is_on_fn=lambda data: data.alarm_active,
    ),
    InnovaBinarySensorEntityDescription(
        key="window_contact",
        translation_key="window_contact",
        device_class=BinarySensorDeviceClass.WINDOW,
        entity_category=EntityCategory.DIAGNOSTIC,
        is_on_fn=lambda data: data.window_contact_open,
    ),
    InnovaBinarySensorEntityDescription(
        key="inlet_water_probe_connected",
        translation_key="inlet_water_probe_connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        is_on_fn=lambda data: data.t2_probe_present,
    ),
    InnovaBinarySensorEntityDescription(
        key="coil_water_probe_connected",
        translation_key="coil_water_probe_connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        is_on_fn=lambda data: data.t3_probe_present,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Innova Climate binary sensor entities."""
    coordinator: InnovaDataUpdateCoordinator = entry.runtime_data
    async_add_entities(
        InnovaBinarySensorEntity(coordinator, description)
        for description in BINARY_SENSOR_DESCRIPTIONS
    )


class InnovaBinarySensorEntity(InnovaEntity, BinarySensorEntity):
    """Representation of an Innova Fancoil binary sensor."""

    entity_description: InnovaBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: InnovaDataUpdateCoordinator,
        description: InnovaBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return self.entity_description.is_on_fn(self.coordinator.data)
