<p align="center">
  <img src="https://raw.githubusercontent.com/CharlieLuemmel/ha-tuya-matter-thermostat/main/custom_components/tuya_matter_thermostat/brand/icon@2x.png" width="128" alt="Tuya/AVATTO Matter Thermostat Relay icon">
</p>

<h1 align="center">Tuya/AVATTO Matter Thermostat Relay</h1>

<p align="center">
  See whether your Tuya-based Matter thermostat is actually heating.
</p>

<p align="center">
  <a href="https://hacs.xyz"><img src="https://img.shields.io/badge/HACS-Custom-41BDF5.svg" alt="HACS Custom"></a>
  <a href="https://github.com/CharlieLuemmel/ha-tuya-matter-thermostat/releases"><img src="https://img.shields.io/github/v/release/CharlieLuemmel/ha-tuya-matter-thermostat" alt="Release"></a>
  <a href="https://www.home-assistant.io"><img src="https://img.shields.io/badge/Home%20Assistant-2026.3%2B-41BDF5?logo=home-assistant&logoColor=white" alt="Home Assistant 2026.3+"></a>
  <a href="https://github.com/CharlieLuemmel/ha-tuya-matter-thermostat/actions/workflows/validate.yml"><img src="https://github.com/CharlieLuemmel/ha-tuya-matter-thermostat/actions/workflows/validate.yml/badge.svg" alt="Validate"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/CharlieLuemmel/ha-tuya-matter-thermostat" alt="License"></a>
</p>

<p align="center">
  <a href="#installation">Installation</a> ·
  <a href="#supported-devices">Supported devices</a> ·
  <a href="#how-it-works">How it works</a> ·
  <a href="#faq">FAQ</a> ·
  <a href="#discussion--feedback">Discussion</a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/CharlieLuemmel/ha-tuya-matter-thermostat/main/docs/images/device-page.png" width="700" alt="Device page: thermostat control and the Heating sensor (here named &quot;Heizt&quot;) on the same Matter device">
  <br>
  <em>The relay sensor sits on the existing Matter device, right below the thermostat.</em>
</p>

## Why

Home Assistant's Matter integration exposes the standard Thermostat cluster: current temperature, setpoint, mode. It does not tell you whether the relay is on.

Tuya-based Matter thermostats keep that in a Tuya manufacturer cluster (`0x125DFC41`). Home Assistant ignores it. This integration reads it and adds a binary sensor **Heating** to the existing Matter device.

Use it to:

- see at a glance whether the floor heating or radiator is running
- track heating runtime per day with a *History stats* helper
- trigger automations when heating starts or stops

## Features

- ⚡ **Push, no polling.** Uses the existing Matter subscription. Updates arrive the moment the relay clicks.
- 🔗 **No extra devices.** The sensor appears on the existing Matter device, next to the thermostat.
- 🔍 **Automatic discovery.** Every supported thermostat gets its sensor, including ones you commission later.
- ⚙️ **One setting.** The Matter Server URL, prefilled from your Matter integration.
- 🌍 **Translated.** English and German.

## Supported devices

| Device | Matter vendor ID | Product ID | Status |
|---|---|---|---|
| WT410 Matter (micuda / AVATTO) | 5461 (MIUC) | 2416 | ✅ Tested |

> [!NOTE]
> **micuda** and **AVATTO** are retail brands. The device reports **MIUC** as Matter vendor. It runs on Tuya's platform (Wi-Fi module and firmware), hence the Tuya cluster (`0x125D` = Tuya's vendor prefix).

Only devices in `SUPPORTED_DEVICES` (`const.py`) are handled. Other Tuya devices may use the same attribute for something else. Got another model? See [Add a device](#add-a-device).

## Requirements

- Home Assistant **2026.3** or newer
- [Matter integration](https://www.home-assistant.io/integrations/matter/) with the Matter Server app
- Thermostat commissioned to Home Assistant via Matter

## Installation

### HACS (recommended)

[![Open your Home Assistant instance and open this repository in HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=CharlieLuemmel&repository=ha-tuya-matter-thermostat&category=integration)

Or add it by hand:

1. Open HACS → ⋮ → **Custom repositories**.
2. Add `https://github.com/CharlieLuemmel/ha-tuya-matter-thermostat`, type **Integration**.
3. Search for **Tuya/AVATTO Matter Thermostat Relay** and download it.
4. Restart Home Assistant.

### Manual

1. Download the [latest release](https://github.com/CharlieLuemmel/ha-tuya-matter-thermostat/releases/latest).
2. Copy `custom_components/tuya_matter_thermostat` to `/config/custom_components/`.
3. Restart Home Assistant.

## Configuration

[![Open your Home Assistant instance and start setting up this integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=tuya_matter_thermostat)

1. Go to **Settings → Devices & services → Add integration**.
2. Search for **Tuya/AVATTO Matter Thermostat Relay**.
3. Confirm the Matter Server URL. The default comes from your Matter integration (usually `ws://localhost:5580/ws`).

Done. Each supported thermostat now has a **Heating** sensor.

<!-- Screenshot: setup dialog
<img src="docs/images/config-flow.png" width="500" alt="Setup dialog">
-->

## Entities

| Entity | Type | Device class | States |
|---|---|---|---|
| `binary_sensor.<device>_heating` | Binary sensor | `power` | `on` = relay closed (heating), `off` = relay open |

The sensor is `unavailable` while the Matter Server connection is down or the thermostat is offline.

## Examples

**Heating runtime today** – add a *History stats* helper (Settings → Devices & services → Helpers):

| Field | Value |
|---|---|
| Entity | `binary_sensor.<device>_heating` |
| State | `on` |
| Type | Time |
| Start | `{{ today_at() }}` |
| End | `{{ now() }}` |

**Notify when heating starts:**

```yaml
triggers:
  - trigger: state
    entity_id: binary_sensor.living_room_floor_heating_heating
    to: "on"
actions:
  - action: notify.notify
    data:
      message: "Living room heating is on."
```

<!-- Screenshot: history graph with temperature, setpoint and heating
<img src="docs/images/history.png" width="700" alt="History with temperature, setpoint and heating state">
-->

## How it works

```
Thermostat ──(Matter subscription)──► Matter Server ──► HA Matter integration   (ignores Tuya cluster)
                                            │
                                            └─────────► this integration ──► binary_sensor.<device>_heating
```

| Attribute | Path | Value |
|---|---|---|
| Relay | `1/308149313/1` | `1` = on, `0` = off |

`308149313` = `0x125DFC41`. The integration opens one WebSocket connection to the Matter Server, calls `start_listening`, reads initial values from the node list and updates on `attribute_updated`. It reconnects automatically after 10 seconds.

The thermostat switches a few seconds after a setpoint change. The sensor follows the relay, not the setpoint.

## Add a device

1. Download diagnostics: **Matter integration → device → ⋮ → Download diagnostics**.
2. Note vendor ID `0/40/2` and product ID `0/40/4`.
3. Change the setpoint until the relay clicks. Download diagnostics again.
4. Check that `1/308149313/1` flipped between `0` and `1`.
5. [Open an issue](https://github.com/CharlieLuemmel/ha-tuya-matter-thermostat/issues/new) with model name, vendor ID and product ID.

## FAQ

<details>
<summary><b>No Heating sensor appears.</b></summary>

- Check that the thermostat is listed under [Supported devices](#supported-devices).
- Reload the integration: **Settings → Devices & services → Tuya/AVATTO Matter Thermostat Relay → ⋮ → Reload**.
- Enable debug logging (below) and look for `Found supported thermostat on Matter node`.
</details>

<details>
<summary><b>The sensor is unavailable.</b></summary>

The integration can't reach the Matter Server, or the thermostat is offline. Check the Matter integration first. The integration retries every 10 seconds.
</details>

<details>
<summary><b>The thermostat shows "heating" but the sensor is off.</b></summary>

The device's mode is *heat*, but the relay only closes below the setpoint. The sensor shows the relay.
</details>

<details>
<summary><b>How do I enable debug logging?</b></summary>

```yaml
logger:
  default: warning
  logs:
    custom_components.tuya_matter_thermostat: debug
```

Or use **Enable debug logging** on the integration page.
</details>

## Known limitations

- **Unofficial.** Depends on the Matter Server WebSocket format (`start_listening`, `attribute_updated`). If a Matter Server update changes it, the sensor becomes unavailable.
- **Relay only.** The other attributes in the Tuya cluster are undocumented.
- **HACS store icon.** HACS shows "icon not available" in its list. Home Assistant itself shows the icon (shipped in `brand/`).

## Discussion & feedback

Questions, ideas, experiences? Join the thread in the German-speaking simon42 community (English replies welcome):

- 💬 [Integration announcement & discussion](https://community.simon42.com/t/heizt-sie-oder-heizt-sie-nicht-relais-status-fuer-tuya-avatto-matter-thermostate-integration-hacs/93779)
- 🛠️ [Guide: Matter devices in a different VLAN than Home Assistant (pfSense, Avahi, IPv6)](https://community.simon42.com/t/matter-geraete-in-einem-anderen-vlan-als-home-assistant-so-klappts-mit-pfsense-avahi-ipv6-firewall/93781)

Bugs and device reports go to [GitHub issues](https://github.com/CharlieLuemmel/ha-tuya-matter-thermostat/issues).

## Contributing

Issues and pull requests are welcome. Most useful: confirmed vendor/product IDs of other Tuya-based Matter thermostats.

## License

[MIT](LICENSE)

Not affiliated with Tuya, AVATTO, micuda, MIUC or the Connectivity Standards Alliance. All trademarks belong to their owners.
