"""Constants for Tuya/AVATTO Matter Thermostat Relay."""

DOMAIN = "tuya_matter_thermostat"

CONF_URL = "url"
DEFAULT_URL = "ws://localhost:5580/ws"

# Tuya manufacturer cluster 0x125DFC41 (0x125D = Tuya), attribute 1 = relay on (1) / off (0).
RELAY_PATH = "1/308149313/1"

# Only these devices (vendor_id, product_id) are handled. Other Tuya devices may
# use attribute 1 of the same cluster for something else. Add verified models here.
SUPPORTED_DEVICES: set[tuple[int, int]] = {
    (5461, 2416),  # MIUC WT410-Matter (sold as micuda / AVATTO WT410)
}

VENDOR_ID_PATH = "0/40/2"
PRODUCT_ID_PATH = "0/40/4"

RECONNECT_DELAY = 10

SIGNAL_NEW_NODE = f"{DOMAIN}_new_node"
SIGNAL_UPDATE = f"{DOMAIN}_update"
