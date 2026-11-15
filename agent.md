# Agent guide

## Project

Mopeka Enhanced is a Home Assistant custom integration installed through Marketplace (or HACS on Home Assistant 2026.10). It uses `mopeka_iot_ble` to receive passive Bluetooth readings and adds guided tank configuration, fill percentage, volume, and diagnostic sensors. The integration domain remains `mopeka`, so changes must preserve existing config entries and entity identities where possible. Read `README.md` for user-facing behavior before changing it.

## Code map

- `custom_components/mopeka/__init__.py`: config entry setup, BLE coordinator, reload, and unload.
- `custom_components/mopeka/config_flow.py`: Bluetooth/manual discovery, setup, reconfigure, and options flows. Options changes update config entry **data** and reload the entry.
- `custom_components/mopeka/const.py`: config keys, tank presets, measurement ranges, capacities, and legacy preset aliases.
- `custom_components/mopeka/sensor.py`: BLE update conversion, tank fill math, units, empty-tank quality latch, and derived sensors.
- `custom_components/mopeka/_mopeka_iot_ble_compat.py`: compatibility handling for the upstream BLE library.
- `custom_components/mopeka/strings.json` and `translations/en.json`: matching English UI labels; `translations/de.json` contains German translations.

## Change guidance

- Keep the underlying BLE decoding in `mopeka_iot_ble`; this repo configures the device and derives Home Assistant entities from its updates.
- Preserve persisted config keys and normalize older tank preset keys through `normalize_tank_size`. A new config value may need a default for existing entries.
- Propane preset ranges use propane acoustic coefficients. IBC presets and custom tanks support other media. Top-mount devices measure air gap, so their reading is converted to fluid height using the sensor mount height before calculating fill.
- Horizontal tanks use circular-segment geometry. For a new horizontal preset, `full_mm` is the cylinder's inner diameter, not its length. Keep fill percentage clamped to 0–100 and volume in the configured capacity unit.
- For a standard preset addition, follow `.github/PULL_REQUEST_TEMPLATE.md`: update the `TankSize` enum, the relevant selector list and range map, capacity, horizontal set if applicable, both English label locations in `strings.json` and `translations/en.json`, and the changelog. Standard presets do not require config flow changes. Do not bump `manifest.json` for an ordinary change; the maintainer does that when cutting a release.
- When changing flow steps or UI labels, check setup, reconfigure, and options paths, plus translation consistency.

## Validation

Use Python 3.14 and install `requirements-dev.txt`. The test suites must run in separate pytest processes: `tests/` uses Home Assistant stubs that alter `sys.modules`, while `tests_integration/` uses the real Home Assistant test harness.

```sh
python -m pytest -p no:homeassistant -q tests
python -m pytest -q tests_integration
python -m ruff check custom_components tests tests_integration
python -m ruff format --check custom_components tests tests_integration
python -m mypy
```

CI also runs HACS validation and hassfest. Add focused coverage for behavior changes, especially flow routing, backward compatibility, tank edge readings, units, and translation labels.
