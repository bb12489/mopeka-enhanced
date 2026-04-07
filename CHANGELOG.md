# Changelog

All notable changes to this project will be documented in this file.

## [0.2.3] - 2026-04-07

### Changed

- Consolidated recent tank/key naming updates in the release notes: normalized tank preset keys to canonical orientation suffixes (`_v` / `_h`) and standardized horizontal ASME naming (`*_asme_h`) while preserving legacy alias compatibility for existing configs.
- Hardened config-flow naming/default handling so persisted preset keys are normalized and selector defaults remain valid after naming updates.

### Added

- Added CI quality coverage in `.github/workflows/validate.yml` for `pytest`, `ruff check`, and `ruff format --check`.
- Added the `tests/` directory to version control and updated `.gitignore` accordingly so CI can execute the full suite.

### Fixed

- Fixed GitHub Actions `pytest` failures caused by a non-subscriptable test stub type in `tests/conftest.py` (`_PassiveBluetoothDataProcessor`) under CI Python typing paths.
- Bumped integration version in `custom_components/mopeka/manifest.json` to `0.2.3`.

## [0.2.2] - 2026-04-07

### Added

- Added a `quality` GitHub Actions job in `.github/workflows/validate.yml` to run the same required local checks in CI: `pytest`, `ruff check`, and `ruff format --check`.

### Changed

- Added the `tests/` directory to version control so automated checks can run against the full test suite in GitHub Actions.
- Updated `.gitignore` to stop ignoring `tests/`.
- Bumped integration version in `custom_components/mopeka/manifest.json` to `0.2.2`.

## [0.2.1] - 2026-04-07

### Fixed

- Corrected `manifest.json` version, which still reported `0.1.9` at the time the `0.2.0` release was published, causing a version mismatch between what Home Assistant displayed and what HACS reported.

## [0.2.0] - 2026-04-06

### Added

- Added new propane tank presets sourced directly from the official Mopeka app `tank_types.js` file: 120 gal vertical, 150 gal horizontal, 250 gal horizontal, 12 kg, 18 kg, and 48 kg.

### Changed

- Updated existing tank presets to match the official Mopeka app `tank_types.js` data, including the horizontal 120 gal preset mapping and the 1000 gal horizontal tank height.
- Updated the related preset labels and translations to match the revised and newly added tank options.

## [0.1.9] - 2026-04-05

### Fixed

- Fixed capacity unit dropdown not updating the number input field unit label in custom tank configuration forms. Changing the unit now refreshes the form so the input field label reflects the selected unit (gallons, kilograms, or liters) before saving.

## [0.1.8] - 2026-04-05

### Added

- Added custom tank capacity unit selection for propane custom tanks: `gallons` or `kilograms`.
- Added custom tank capacity unit selection for non-propane custom tanks: `gallons` or `liters`.

### Changed

- Updated custom tank configuration forms to display capacity input fields with the correct unit based on the selected capacity unit.
- Updated synthesized tank level capacity sensor behavior so custom tanks report in the selected unit (`gallons`, `kilograms`, or `liters`).
- Updated related UI text and translations for consistent capacity unit labeling.

## [0.1.7] - 2026-04-05

### Fixed

- Corrected top-down (TD40/TD200) tank math to explicitly convert air-gap readings into fluid height before calculating tank fill percentage and volume.
- Updated top-down custom and IBC range handling to use a standard `0..depth` calibration range, with conversion applied as `fluid_height = depth - air_gap`.
- Top-down `tank_level` now reports fluid height after conversion, matching bottom-mount semantics.

### Changed

- Updated inline documentation/comments to reflect explicit top-down air-gap conversion behavior.

## [0.1.6] - 2026-04-05

### Changed

- Simplified IBC tote preset names by removing inch/centimeter dimensions from display labels.
- Updated horizontal ASME propane preset labels to remove legacy under-mount wording and display as "Horizontal ASME".

## [0.1.5] - 2026-04-05

### Added

- **Euro propane tank presets** — three new presets for European-style LPG cylinders are now available in the propane tank configuration selector:
  - 6 kg (Euro) — fill height range 38.1 mm – 336.0 mm
  - 11 kg (Euro) — fill height range 38.1 mm – 366.0 mm
  - 14 kg (Euro) — fill height range 38.1 mm – 467.0 mm
- Heights sourced from the Mopeka ESPHome component. Usable volume (gallons) is derived at propane density ≈ 1.921 kg/gal.
- The "Tank preset" diagnostic sensor correctly labels the Euro presets.
- The "Tank fill" percentage sensor works for Euro presets with no additional configuration.
