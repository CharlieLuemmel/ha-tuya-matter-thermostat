"""Tuya/AVATTO Matter Thermostat Relay.

Exposes the relay state (heating / idle) of Tuya-based Matter thermostats such
as the WT410 (micuda / AVATTO). The value lives in the Tuya manufacturer
cluster 0x125DFC41, which the Home Assistant Matter integration ignores.

The integration listens to the Matter Server WebSocket API (start_listening).
The thermostat reports changes through the existing Matter subscription, so
there is no polling.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import (
    CONF_URL,
    DEFAULT_URL,
    PRODUCT_ID_PATH,
    RECONNECT_DELAY,
    RELAY_PATH,
    SIGNAL_NEW_NODE,
    SIGNAL_UPDATE,
    SUPPORTED_DEVICES,
    VENDOR_ID_PATH,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.BINARY_SENSOR]

type TuyaMatterThermostatConfigEntry = ConfigEntry[RelayHub]


class RelayHub:
    """Keeps a WebSocket connection to the Matter Server and the relay state per node."""

    def __init__(self, hass: HomeAssistant, url: str) -> None:
        self.hass = hass
        self.url = url
        self.connected = False
        self.relay: dict[int, bool] = {}
        self.node_available: dict[int, bool] = {}

    def start(self, entry: ConfigEntry) -> None:
        entry.async_create_background_task(
            self.hass, self._run(), "tuya_matter_thermostat_listener"
        )

    async def _run(self) -> None:
        session = async_get_clientsession(self.hass)
        while True:
            try:
                async with session.ws_connect(
                    self.url, heartbeat=30, max_msg_size=0
                ) as ws:
                    await ws.send_json(
                        {"message_id": "listen", "command": "start_listening"}
                    )
                    async for msg in ws:
                        if msg.type != aiohttp.WSMsgType.TEXT:
                            break
                        self._handle(msg.json())
            except asyncio.CancelledError:
                raise
            except Exception as err:  # noqa: BLE001
                _LOGGER.warning("Connection to Matter Server failed: %s", err)
            if self.connected:
                _LOGGER.info("Disconnected from Matter Server, retrying")
            self.connected = False
            async_dispatcher_send(self.hass, SIGNAL_UPDATE)
            await asyncio.sleep(RECONNECT_DELAY)

    @callback
    def _handle(self, data: dict[str, Any]) -> None:
        if data.get("message_id") == "listen":
            if "error_code" in data:
                _LOGGER.error("start_listening failed: %s", data)
                return
            self.connected = True
            for node in data.get("result") or []:
                self._handle_node(node)
            async_dispatcher_send(self.hass, SIGNAL_UPDATE)
            return

        event = data.get("event")
        if event == "attribute_updated":
            node_id, path, value = data["data"]
            if path == RELAY_PATH and node_id in self.relay:
                self.relay[node_id] = bool(value)
                async_dispatcher_send(self.hass, SIGNAL_UPDATE)
        elif event in ("node_added", "node_updated"):
            self._handle_node(data["data"])
            async_dispatcher_send(self.hass, SIGNAL_UPDATE)
        elif event == "node_removed":
            self.node_available[data["data"]] = False
            async_dispatcher_send(self.hass, SIGNAL_UPDATE)

    @callback
    def _handle_node(self, node: dict[str, Any]) -> None:
        attrs = node.get("attributes") or {}
        ids = (attrs.get(VENDOR_ID_PATH), attrs.get(PRODUCT_ID_PATH))
        if ids not in SUPPORTED_DEVICES or RELAY_PATH not in attrs:
            return
        node_id = node["node_id"]
        is_new = node_id not in self.relay
        self.relay[node_id] = bool(attrs[RELAY_PATH])
        self.node_available[node_id] = bool(node.get("available", True))
        if is_new:
            _LOGGER.info("Found supported thermostat on Matter node %s", node_id)
            async_dispatcher_send(self.hass, SIGNAL_NEW_NODE, node_id)


async def async_setup_entry(
    hass: HomeAssistant, entry: TuyaMatterThermostatConfigEntry
) -> bool:
    hub = RelayHub(hass, entry.data.get(CONF_URL, DEFAULT_URL))
    entry.runtime_data = hub
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    hub.start(entry)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: TuyaMatterThermostatConfigEntry
) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
