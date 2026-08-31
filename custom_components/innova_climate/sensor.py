"""Sensor platform for Innova Climate integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfTemperature, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .innova_modbus import InnovaData

from .coordinator import InnovaDataUpdateCoordinator
from .entity import InnovaEntity


@dataclass(frozen=True, kw_only=True)
class InnovaSensorEntityDescription(SensorEntityDescription):
    """Describes Innova sensor entity."""

    value_fn: Callable[[InnovaData], float | str | None]


SENSOR_DESCRIPTIONS: tuple[InnovaSensorEntityDescription, ...] = (
    InnovaSensorEntityDescription(
        key="inlet_water_temperature",
        translation_key="inlet_water_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        value_fn=lambda data: data.inlet_water_temp_t2,
    ),
    InnovaSensorEntityDescription(
        key="coil_water_temperature",
        translation_key="coil_water_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        value_fn=lambda data: data.coil_water_temp_t3,
    ),
    InnovaSensorEntityDescription(
        key="relative_humidity",
        translation_key="relative_humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0,
        value_fn=lambda data: data.relative_humidity,
    ),
    InnovaSensorEntityDescription(
        key="alarm_description",
        translation_key="alarm_description",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.alarm_description,
    ),
    InnovaSensorEntityDescription(
        key="status_description",
        translation_key="status_description",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.status_description,
    ),
    InnovaSensorEntityDescription(
        key="fan_status_description",
        translation_key="fan_status_description",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.fan_status_description,
    ),
    InnovaSensorEntityDescription(
        key="firmware_release",
        translation_key="firmware_release",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: f"v{data.firmware_release}" if data.firmware_release is not None else None,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Innova Climate sensor entities."""
    coordinator: InnovaDataUpdateCoordinator = entry.runtime_data
    entities: list[InnovaSensorEntity] = []

    for description in SENSOR_DESCRIPTIONS:
        # Don't add humidity sensor if hardware doesn't have it
        if description.key == "relative_humidity" and not coordinator.data.rh_sensor_present:
            continue
        # Don't add T3 coil water sensor if probe is not installed (2-pipe models)
        if description.key == "coil_water_temperature" and not coordinator.data.t3_probe_present:
            continue
        entities.append(InnovaSensorEntity(coordinator, description))

    async_add_entities(entities)


class InnovaSensorEntity(InnovaEntity, SensorEntity):
    """Representation of an Innova Fancoil sensor."""

    entity_description: InnovaSensorEntityDescription

    def __init__(
        self,
        coordinator: InnovaDataUpdateCoordinator,
        description: InnovaSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> float | str | None:
        """Return sensor value."""
        return self.entity_description.value_fn(self.coordinator.data)
