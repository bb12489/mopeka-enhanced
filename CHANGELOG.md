# Changelog

All notable changes to this project will be documented in this file.

## [0.1.5] - 2026-04-05

### Added

- **Euro propane tank presets** — three new presets for European-style LPG cylinders are now available in the propane tank configuration selector:
  - 6 kg (Euro) — fill height range 38.1 mm – 336.0 mm
  - 11 kg (Euro) — fill height range 38.1 mm – 366.0 mm
  - 14 kg (Euro) — fill height range 38.1 mm – 467.0 mm
- Heights sourced from the Mopeka ESPHome component. Usable volume (gallons) is derived at propane density ≈ 1.921 kg/gal.
- The "Tank preset" diagnostic sensor correctly labels the Euro presets.
- The "Tank fill" percentage sensor works for Euro presets with no additional configuration.
