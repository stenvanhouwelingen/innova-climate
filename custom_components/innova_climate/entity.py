"""Base entity for Innova Climate integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import InnovaDataUpdateCoordinator


class InnovaEntity(CoordinatorEntity[InnovaDataUpdateCoordinator]):
    """Base class for all Innova Climate entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: InnovaDataUpdateCoordinator,
        entity_key: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.entity_key = entity_key
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{coordinator.device.slave_id}_{entity_key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device registry information."""
        board_family = self.coordinator.device.board_family
        sw_version = (
            f"v{self.coordinator.data.firmware_release}"
            if self.coordinator.data.firmware_release is not None
            else None
        )
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self.coordinator.config_entry.entry_id}_{self.coordinator.device.slave_id}")},
            name=f"Innova Fancoil ({self.coordinator.device.slave_id})",
            manufacturer="Innova",
            model=f"Fancoil Control Board ({board_family.upper()})",
            sw_version=sw_version,
        )
