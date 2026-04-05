# Changelog

All notable changes to this project will be documented in this file.

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
- Updated horizontal ASME propane preset labels to remove "RV" wording and display as "Horizontal ASME".

## [0.1.5] - 2026-04-05

### Added

- **Euro propane tank presets** — three new presets for European-style LPG cylinders are now available in the propane tank configuration selector:
  - 6 kg (Euro) — fill height range 38.1 mm – 336.0 mm
  - 11 kg (Euro) — fill height range 38.1 mm – 366.0 mm
  - 14 kg (Euro) — fill height range 38.1 mm – 467.0 mm
- Heights sourced from the Mopeka ESPHome component. Usable volume (gallons) is derived at propane density ≈ 1.921 kg/gal.
- The "Tank preset" diagnostic sensor correctly labels the Euro presets.
- The "Tank fill" percentage sensor works for Euro presets with no additional configuration.
