"""Config flow for Tuya/AVATTO Matter Thermostat Relay."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import CONF_URL, DEFAULT_URL, DOMAIN


class TuyaMatterThermostatConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(
                title="Tuya/AVATTO Matter Thermostat Relay", data=user_input
            )

        # Default: same URL as the Matter integration
        default_url = DEFAULT_URL
        for matter_entry in self.hass.config_entries.async_entries("matter"):
            default_url = matter_entry.data.get("url", default_url)
            break

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_URL, default=default_url): str}),
        )
