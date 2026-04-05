## Tank Preset Addition

Thanks for contributing a new tank preset! Fill out the sections below before submitting.
All preset data lives in `custom_components/mopeka/const.py` — no config flow or sensor logic changes
are needed for a standard preset addition.

---

### Preset Summary

<!--
Preset type:
  - Propane vertical   → tall upright cylinder (most common)
  - Propane horizontal → laid-on-its-side tank (uses non-linear fill geometry)
  - Euro propane       → European-style LPG cylinder measured in kg
  - IBC                → IBC tote for non-propane media (water, diesel, etc.)

Internal preset key: the short string value used in code, e.g. "20lb", "6kg", "100gal_h".
  - Use only lowercase letters, digits, and underscores/hyphens.
  - Must be unique across all existing TankSize entries in const.py.

Display name: the human-readable label shown in the HA UI, e.g. "6 kg (Euro)", "100 gal (horizontal)".
-->

- Preset type: Propane vertical / Propane horizontal / Euro propane / IBC
- Preset display name:
- Internal preset key:
- Medium type: Propane / Water / Diesel / Other
- Horizontal tank: Yes / No

---

### Measurements

<!--
empty_mm: the sensor reading (in mm) when the tank is considered empty.
  - For propane presets, use TANK_EMPTY_MM (38.1 mm) — this accounts for the physical
    dead-zone at the bottom of the tank and matches every other propane preset.
  - For IBC presets, use TANK_EMPTY_MM (38.1 mm) as well unless you have a specific reason not to.

full_mm: the sensor reading (in mm) when the tank is full.
  - For vertical tanks: the maximum usable liquid column height in mm.
  - For horizontal tanks: the inner diameter of the cylinder in mm
    (not the length — the integration uses circular-segment geometry for fill %).

Capacity in gallons: total usable volume at full fill.
  - For lb-rated propane tanks: divide the rated weight by 4.236 lb/gal.
  - For kg-rated propane tanks: divide the rated weight by 1.921 kg/gal.
  - For gallon-labelled tanks: use the label value directly.

Source: where did you get the empty/full values?
  Examples: official Mopeka app, Mopeka ESPHome component, manufacturer datasheet,
  physical measurement with a ruler, Google/research.
-->

- Empty reading in mm:
- Full reading in mm:
- Total usable capacity in gallons:
- Source of measurements:
- Verification method: Real tank / Manufacturer spec / Mopeka app / ESPHome / Other

---

### Required Code Changes

Every preset PR must touch all of the following. Check each item off once done.

- [ ] Added the preset key to `TankSize` (enum) in `custom_components/mopeka/const.py`
- [ ] Added the preset to `PROPANE_TANK_SIZES` **or** `IBC_TANK_SIZES` in `custom_components/mopeka/const.py` (propane presets go in `PROPANE_TANK_SIZES`; IBC and other-medium presets go in `IBC_TANK_SIZES`)
- [ ] Added `(empty_mm, full_mm)` to `TANK_SIZE_RANGES` **or** `IBC_TANK_SIZE_RANGES` in `custom_components/mopeka/const.py`
- [ ] Added the gallon capacity to `TANK_SIZE_CAPACITIES` in `custom_components/mopeka/const.py`
- [ ] Added the preset to `HORIZONTAL_TANK_SIZES` **only if the tank is horizontal** (this enables non-linear fill geometry)
- [ ] Added selector and diagnostic-sensor labels in `custom_components/mopeka/strings.json` (`selector.tank_size.options` **and** `entity.sensor.propane_preset.state`)
- [ ] Mirrored those labels in `custom_components/mopeka/translations/en.json` (same two locations)
- [ ] Added a release note entry in `CHANGELOG.md` describing the new preset(s) and their source
- [ ] Updated `README.md` only if the preset warrants a note in the documentation

---

### Validation

- [ ] Confirmed the preset appears in the correct setup dropdown in HA
- [ ] Confirmed the **Tank preset** diagnostic sensor displays the expected label
- [ ] Confirmed the **Tank fill** percentage sensor behaves correctly for this geometry
- [ ] Confirmed the measurement values come from a reliable, documented source

---

### Maintainer Guardrails

Please confirm the following to keep the PR scope tight:

- [ ] This PR does **not** bump the version in `custom_components/mopeka/manifest.json` — version bumps are done by the maintainer at release time
- [ ] This PR does **not** modify `custom_components/mopeka/config_flow.py` — the selector lists are driven dynamically from `PROPANE_TANK_SIZES` / `IBC_TANK_SIZES`; no flow changes are needed for standard presets
- [ ] If this is a horizontal preset, the `full_mm` value is the **inner diameter** (not tank length), consistent with the existing horizontal presets in `custom_components/mopeka/sensor.py`

---

### Notes

Add any extra context here — especially if the preset required non-standard handling, if there is
uncertainty about the source data, or if you would like the maintainer to double-check the values.
