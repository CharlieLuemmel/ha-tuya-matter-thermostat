"""Binary sensor "Heating" for each supported Matter thermostat."""

from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import RelayHub, TuyaMatterThermostatConfigEntry
from .const import SIGNAL_NEW_NODE, SIGNAL_UPDATE

_LOGGER = logging.getLogger(__name__)


@callback
def _find_matter_device(
    hass: HomeAssistant, node_id: int
) -> tuple[str, dr.DeviceEntry] | None:
    """Find the device the HA Matter integration created for this node.

    Matter entities use the unique_id <fabric>-<node>-MatterNodeDevice-...
    (both 16-digit hex). We look the device up through one of them and attach
    our entity via device_entry, like template helpers do. Using device_info
    with the Matter identifiers would create a separate device.
    """
    marker = f"-{node_id:016X}-MatterNodeDevice"
    dev_reg = dr.async_get(hass)
    for entity in er.async_get(hass).entities.values():
        if entity.platform != "matter" or marker not in entity.unique_id:
            continue
        if entity.device_id and (device := dev_reg.async_get(entity.device_id)):
            device_key = entity.unique_id.split(marker)[0] + marker
            return device_key, device
    return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TuyaMatterThermostatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    hub = entry.runtime_data
    known: set[int] = set()

    @callback
    def add_node(node_id: int) -> None:
        if node_id in known:
            return
        found = _find_matter_device(hass, node_id)
        if found is None:
            _LOGGER.warning("No Matter device found for node %s", node_id)
            return
        known.add(node_id)
        device_key, device = found
        async_add_entities([RelaySensor(hub, node_id, device_key, device)])

    for node_id in list(hub.relay):
        add_node(node_id)
    entry.async_on_unload(async_dispatcher_connect(hass, SIGNAL_NEW_NODE, add_node))


class RelaySensor(BinarySensorEntity):
    """Thermostat relay: on = heating."""

    _attr_has_entity_name = True
    _attr_translation_key = "heating"
    _attr_device_class = BinarySensorDeviceClass.POWER
    _attr_icon = "mdi:radiator"
    _attr_should_poll = False

    def __init__(
        self, hub: RelayHub, node_id: int, device_key: str, device: dr.DeviceEntry
    ) -> None:
        self._hub = hub
        self._node_id = node_id
        self._attr_unique_id = f"{device_key}-relay"
        # Attach to the existing Matter device (no own device_info)
        self.device_entry = device

    @property
    def available(self) -> bool:
        return self._hub.connected and self._hub.node_available.get(self._node_id, False)

    @property
    def is_on(self) -> bool | None:
        return self._hub.relay.get(self._node_id)

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_UPDATE, self.async_write_ha_state)
        )
