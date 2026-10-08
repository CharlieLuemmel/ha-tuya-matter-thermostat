# Tuya/AVATTO Matter Thermostat Relay

<img src="https://raw.githubusercontent.com/CharlieLuemmel/ha-tuya-matter-thermostat/main/custom_components/tuya_matter_thermostat/brand/icon.png" width="96" align="right" alt="icon">

Home Assistant integration. Shows whether a Tuya-based Matter thermostat is actually heating.

The Matter integration only exposes the standard Thermostat cluster. Tuya keeps the relay state in its own manufacturer cluster (`0x125DFC41`). Home Assistant ignores it. This integration reads it and adds a binary sensor **Heating** to the existing Matter device.

## Features

- Push, no polling. Uses the existing Matter subscription.
- Attaches to the existing Matter device. No extra devices.
- Picks up new thermostats automatically.
- One setting: the Matter Server URL. Defaults to the Matter integration's URL.

## Supported devices

| Device | Matter vendor / product ID | Status |
|---|---|---|
| WT410 Matter (micuda / AVATTO, Matter vendor MIUC) | 5461 / 2416 | Tested |

micuda and AVATTO are retail brands. The device reports MIUC as vendor. It runs on Tuya's platform (module and firmware), hence the Tuya cluster (`0x125D` = Tuya vendor prefix).

We only handle devices listed in `SUPPORTED_DEVICES` (`const.py`). Other Tuya devices may use the same attribute for something else.

## Requirements

- Home Assistant 2026.3 or newer
- Matter integration with the Matter Server app
- Thermostat commissioned to Home Assistant via Matter

## Installation

### HACS

1. Open HACS → ⋮ → **Custom repositories**.
2. Add `https://github.com/CharlieLuemmel/ha-tuya-matter-thermostat`, type **Integration**.
3. Install **Tuya/AVATTO Matter Thermostat Relay**.
4. Restart Home Assistant.
5. Go to Settings → Devices & services → **Add integration** → *Tuya/AVATTO Matter Thermostat Relay*.

### Manual

1. Copy `custom_components/tuya_matter_thermostat` to `/config/custom_components/`.
2. Restart Home Assistant.
3. Add the integration as above.

## How it works

```
Thermostat ──(Matter subscription)──► Matter Server ──► HA Matter integration (ignores Tuya cluster)
                                            └──────────► this integration ──► binary_sensor.<device>_heating
```

| Attribute | Path | Value |
|---|---|---|
| Relay | `1/308149313/1` | `1` = on (heating), `0` = off |

The integration connects to the Matter Server WebSocket and calls `start_listening`. It reads initial values from the node list and updates on `attribute_updated`.

The device switches a few seconds after a setpoint change. The sensor follows the relay, not the setpoint.

## Add a device

1. Download diagnostics: Matter integration → device → *Download diagnostics*.
2. Note vendor ID `0/40/2` and product ID `0/40/4`.
3. Check that `1/308149313/1` exists and changes when the relay clicks.
4. Open an issue or PR with model name and IDs.

## Limitations

- Unofficial. Depends on the Matter Server WebSocket format (`start_listening`, `attribute_updated`). If that changes, the sensor goes unavailable.
- Exposes the relay only. The other Tuya attributes are undocumented.

## License

MIT
