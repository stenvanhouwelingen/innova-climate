"""DataUpdateCoordinator for Innova Climate integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Callable

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_POLL_INTERVAL, DOMAIN, EVENT_INNOVA_ALARM
from .innova_modbus import InnovaData, InnovaFancoil

_LOGGER = logging.getLogger(__name__)


class InnovaDataUpdateCoordinator(DataUpdateCoordinator[InnovaData]):
    """Coordinator to manage polling data from the Innova Fancoil."""

    def __init__(
        self,
        hass: HomeAssistant,
        device: InnovaFancoil,
        poll_interval: int = DEFAULT_POLL_INTERVAL,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{device.slave_id}",
            update_interval=timedelta(seconds=poll_interval),
        )
        self.device = device
        self._prev_alarms: int = 0
        self._prev_window_open: bool = False
        self._event_callbacks: list[Callable[[str, dict], None]] = []

    def register_event_listener(self, callback_fn: Callable[[str, dict], None]) -> Callable[[], None]:
        """Register a callback for alarm events."""
        self._event_callbacks.append(callback_fn)

        def remove() -> None:
            if callback_fn in self._event_callbacks:
                self._event_callbacks.remove(callback_fn)

        return remove

    async def _async_update_data(self) -> InnovaData:
        """Fetch the latest data from the fancoil."""
        try:
            data = await self.device.async_update()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with Innova Fancoil: {err}") from err

        self._check_and_fire_events(data)
        return data

    def _check_and_fire_events(self, data: InnovaData) -> None:
        """Check for state transitions and fire Home Assistant bus events."""
        # 1. New Alarm Triggered
        if data.raw_alarms != self._prev_alarms:
            if data.raw_alarms > 0:
                event_type = "alarm"
                if data.raw_alarms & (1 << 10):
                    event_type = "filter_cleaning_required"
                self._fire_event(
                    event_type=event_type,
                    data={
                        "alarm_code": data.raw_alarms,
                        "description": data.alarm_description,
                        "status": data.status_description,
                    },
                )
            elif self._prev_alarms > 0:
                self._fire_event(
                    event_type="alarm_cleared",
                    data={
                        "alarm_code": 0,
                        "description": "All faults cleared",
                    },
                )
            self._prev_alarms = data.raw_alarms

        # 2. Window Contact Transition
        if data.window_contact_open != self._prev_window_open:
            self._fire_event(
                event_type="window_opened" if data.window_contact_open else "window_closed",
                data={"window_contact_open": data.window_contact_open},
            )
            self._prev_window_open = data.window_contact_open

    def _fire_event(self, event_type: str, data: dict) -> None:
        """Dispatch bus event and notify registered event entities."""
        event_payload = {
            "device_slave_id": self.device.slave_id,
            "board_family": str(self.device.board_family),
            "event_type": event_type,
            **data,
        }
        self.hass.bus.async_fire(EVENT_INNOVA_ALARM, event_payload)

        for callback_fn in self._event_callbacks:
            try:
                callback_fn(event_type, data)
            except Exception as err:
                _LOGGER.error("Error dispatching event callback: %s", err)
