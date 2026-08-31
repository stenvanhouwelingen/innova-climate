"""Config flow for Innova Climate integration with Auto-Discovery."""

from __future__ import annotations

import logging
from typing import Any

import serial.tools.list_ports
import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

from .const import (
    CONF_BAUDRATE,
    CONF_BOARD_FAMILY,
    CONF_CONNECTION_TYPE,
    CONF_HOST,
    CONF_PORT,
    CONF_SERIAL_PORT,
    CONF_SLAVE_ID,
    CONNECTION_TYPE_SERIAL,
    CONNECTION_TYPE_TCP,
    DEFAULT_BAUDRATE,
    DEFAULT_SLAVE_ID,
    DEFAULT_TCP_PORT,
    DOMAIN,
)
from .innova_modbus.const import InnovaBoardFamily

_LOGGER = logging.getLogger(__name__)


class InnovaClimateConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Innova Climate with Auto-Discovery."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_name: str | None = None
        self._discovered_host: str | None = None

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        """Handle automatic ZeroConf/mDNS discovery of ESPHome proxy devices."""
        name = discovery_info.hostname.split(".")[0]
        host = str(discovery_info.host)

        # Only auto-trigger for devices with innova/fancoil/attic/proxy in hostname
        if not any(k in name.lower() for k in ["innova", "fancoil", "attic", "proxy", "nanoc6", "atom"]):
            return self.async_abort(reason="not_innova_device")

        unique_id = f"innova_tcp_{host}_{DEFAULT_TCP_PORT}_1"
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        self._discovered_name = name
        self._discovered_host = host
        self.context["title_placeholders"] = {"name": name}

        return await self.async_step_discovery_confirm()

    async def async_step_discovery_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm setup of automatically discovered Innova serial proxy device."""
        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]
            slave_id = user_input[CONF_SLAVE_ID]
            board_family = user_input.get(CONF_BOARD_FAMILY, InnovaBoardFamily.N273025D)

            return self.async_create_entry(
                title=f"Innova Fancoil ({self._discovered_name or host})",
                data={
                    CONF_CONNECTION_TYPE: CONNECTION_TYPE_TCP,
                    CONF_HOST: host,
                    CONF_PORT: port,
                    CONF_SLAVE_ID: slave_id,
                    CONF_BOARD_FAMILY: board_family,
                },
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=self._discovered_host or "innova-nanoc6-attic.local"): selector.TextSelector(),
                vol.Required(CONF_PORT, default=DEFAULT_TCP_PORT): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=1, max=65535, mode=selector.NumberSelectorMode.BOX)
                ),
                vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=1, max=254, mode=selector.NumberSelectorMode.BOX)
                ),
                vol.Required(CONF_BOARD_FAMILY, default=InnovaBoardFamily.N273025D): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            selector.SelectOptionDict(
                                value=InnovaBoardFamily.N273025D,
                                label="Modern (OSMO, AirLeaf, FÄRNA, Filomuro M7/PU)",
                            ),
                            selector.SelectOptionDict(
                                value=InnovaBoardFamily.N273025C,
                                label="Legacy / Bridge (Filoterra, INN-FR-B32)",
                            ),
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="discovery_confirm",
            data_schema=schema,
            description_placeholders={
                "name": self._discovered_name or "Innova Attic Fancoil",
            },
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle manual setup - choose connection method."""
        if user_input is not None:
            conn_type = user_input[CONF_CONNECTION_TYPE]
            if conn_type == CONNECTION_TYPE_SERIAL:
                return await self.async_step_serial()
            return await self.async_step_tcp()

        options = [
            selector.SelectOptionDict(
                value=CONNECTION_TYPE_TCP,
                label="Modbus TCP / Network Bridge (ESPHome NanoC6 / Atom, Port 8899) [Recommended]",
            ),
            selector.SelectOptionDict(
                value=CONNECTION_TYPE_SERIAL,
                label="Physical Serial Port (USB / RS485 Dongle on Home Assistant host)",
            ),
        ]

        schema = vol.Schema(
            {
                vol.Required(CONF_CONNECTION_TYPE, default=CONNECTION_TYPE_TCP): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=options,
                        mode=selector.SelectSelectorMode.LIST,
                    )
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_serial(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle serial port configuration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            serial_port = user_input[CONF_SERIAL_PORT]
            slave_id = user_input[CONF_SLAVE_ID]
            unique_id = f"innova_serial_{serial_port}_{slave_id}"

            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            title = f"Innova Fancoil ({serial_port} ID {slave_id})"
            return self.async_create_entry(
                title=title,
                data={
                    CONF_CONNECTION_TYPE: CONNECTION_TYPE_SERIAL,
                    **user_input,
                },
            )

        ports = await self.hass.async_add_executor_job(serial.tools.list_ports.comports)
        port_options = [
            selector.SelectOptionDict(
                value=port.device,
                label=f"{port.device} ({port.description})",
            )
            for port in ports
        ]

        schema_dict: dict[Any, Any] = {}
        if port_options:
            schema_dict[vol.Required(CONF_SERIAL_PORT, default=port_options[0]["value"])] = (
                selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=port_options,
                        custom_value=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                )
            )
        else:
            schema_dict[vol.Required(CONF_SERIAL_PORT, default="/dev/ttyUSB0")] = selector.TextSelector()

        schema_dict[vol.Required(CONF_BAUDRATE, default=str(DEFAULT_BAUDRATE))] = selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[
                    selector.SelectOptionDict(value="9600", label="9600 (Standard)"),
                    selector.SelectOptionDict(value="19200", label="19200"),
                    selector.SelectOptionDict(value="38400", label="38400"),
                    selector.SelectOptionDict(value="57600", label="57600"),
                    selector.SelectOptionDict(value="115200", label="115200"),
                ],
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        )
        schema_dict[vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID)] = selector.NumberSelector(
            selector.NumberSelectorConfig(min=1, max=254, mode=selector.NumberSelectorMode.BOX)
        )
        schema_dict[vol.Required(CONF_BOARD_FAMILY, default=InnovaBoardFamily.N273025D)] = selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[
                    selector.SelectOptionDict(
                        value=InnovaBoardFamily.N273025D,
                        label="Modern (OSMO, AirLeaf, FÄRNA, Filomuro M7/PU)",
                    ),
                    selector.SelectOptionDict(
                        value=InnovaBoardFamily.N273025C,
                        label="Legacy / Bridge (Filoterra, INN-FR-B32)",
                    ),
                ],
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        )

        return self.async_show_form(
            step_id="serial",
            data_schema=vol.Schema(schema_dict),
            errors=errors,
        )

    async def async_step_tcp(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle custom TCP configuration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]
            slave_id = user_input[CONF_SLAVE_ID]
            unique_id = f"innova_tcp_{host}_{port}_{slave_id}"

            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            title = f"Innova Fancoil ({host}:{port} ID {slave_id})"
            return self.async_create_entry(
                title=title,
                data={
                    CONF_CONNECTION_TYPE: CONNECTION_TYPE_TCP,
                    **user_input,
                },
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default="192.168.1.80"): selector.TextSelector(),
                vol.Required(CONF_PORT, default=DEFAULT_TCP_PORT): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=1, max=65535, mode=selector.NumberSelectorMode.BOX)
                ),
                vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=1, max=254, mode=selector.NumberSelectorMode.BOX)
                ),
                vol.Required(CONF_BOARD_FAMILY, default=InnovaBoardFamily.N273025D): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            selector.SelectOptionDict(
                                value=InnovaBoardFamily.N273025D,
                                label="Modern (OSMO, AirLeaf, FÄRNA, Filomuro M7/PU)",
                            ),
                            selector.SelectOptionDict(
                                value=InnovaBoardFamily.N273025C,
                                label="Legacy / Bridge (Filoterra, INN-FR-B32)",
                            ),
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="tcp",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle re-configuration."""
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        if not entry:
            return self.async_abort(reason="reconfigure_failed")

        if user_input is not None:
            return self.async_update_reload_and_abort(
                entry,
                data={**entry.data, **user_input},
            )

        conn_type = entry.data.get(CONF_CONNECTION_TYPE, CONNECTION_TYPE_TCP)
        if conn_type == CONNECTION_TYPE_SERIAL:
            schema = vol.Schema(
                {
                    vol.Required(CONF_SERIAL_PORT, default=entry.data.get(CONF_SERIAL_PORT)): selector.TextSelector(),
                    vol.Required(CONF_BAUDRATE, default=str(entry.data.get(CONF_BAUDRATE, DEFAULT_BAUDRATE))): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                selector.SelectOptionDict(value="9600", label="9600 (Standard)"),
                                selector.SelectOptionDict(value="19200", label="19200"),
                                selector.SelectOptionDict(value="38400", label="38400"),
                                selector.SelectOptionDict(value="57600", label="57600"),
                                selector.SelectOptionDict(value="115200", label="115200"),
                            ],
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Required(CONF_SLAVE_ID, default=entry.data.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID)): selector.NumberSelector(
                        selector.NumberSelectorConfig(min=1, max=254, mode=selector.NumberSelectorMode.BOX)
                    ),
                }
            )
        else:
            schema = vol.Schema(
                {
                    vol.Required(CONF_HOST, default=entry.data.get(CONF_HOST, "192.168.1.80")): selector.TextSelector(),
                    vol.Required(CONF_PORT, default=entry.data.get(CONF_PORT, DEFAULT_TCP_PORT)): selector.NumberSelector(
                        selector.NumberSelectorConfig(min=1, max=65535, mode=selector.NumberSelectorMode.BOX)
                    ),
                    vol.Required(CONF_SLAVE_ID, default=entry.data.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID)): selector.NumberSelector(
                        selector.NumberSelectorConfig(min=1, max=254, mode=selector.NumberSelectorMode.BOX)
                    ),
                }
            )

        return self.async_show_form(step_id="reconfigure", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Get the options flow for this handler."""
        return InnovaClimateOptionsFlow()


class InnovaClimateOptionsFlow(OptionsFlow):
    """Handle options for Innova Climate."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_poll = self.config_entry.options.get("scan_interval", 10)

        schema = vol.Schema(
            {
                vol.Required("scan_interval", default=current_poll): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=2, max=120, unit_of_measurement="seconds", mode=selector.NumberSelectorMode.BOX)
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
