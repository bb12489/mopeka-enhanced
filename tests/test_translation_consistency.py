from __future__ import annotations

import json
from pathlib import Path


# ---------------------------------------------------------------------------
# Data-completeness tests
# ---------------------------------------------------------------------------


def test_all_propane_presets_have_tank_size_range(const_module):
    """Every entry in PROPANE_TANK_SIZES (except CUSTOM) must have a range."""
    missing = [
        size
        for size in const_module.PROPANE_TANK_SIZES
        if size != const_module.TankSize.CUSTOM
        and size not in const_module.TANK_SIZE_RANGES
    ]
    assert missing == [], f"Missing TANK_SIZE_RANGES entries: {missing}"


def test_all_propane_presets_have_capacity(const_module):
    """Every entry in PROPANE_TANK_SIZES (except CUSTOM) must have a capacity."""
    missing = [
        size
        for size in const_module.PROPANE_TANK_SIZES
        if size != const_module.TankSize.CUSTOM
        and size not in const_module.TANK_SIZE_CAPACITIES
    ]
    assert missing == [], f"Missing TANK_SIZE_CAPACITIES entries: {missing}"


def test_all_propane_presets_have_translation_label(const_module):
    """Every entry in PROPANE_TANK_SIZES (except CUSTOM) must have a label in en.json."""
    root = Path(__file__).resolve().parents[1]
    en = json.loads(
        (root / "custom_components/mopeka/translations/en.json").read_text()
    )
    options = en["entity"]["sensor"]["propane_preset"]["state"]
    missing = [
        size
        for size in const_module.PROPANE_TANK_SIZES
        if size != const_module.TankSize.CUSTOM and size not in options
    ]
    assert missing == [], f"Missing en.json propane_preset state labels: {missing}"


# ---------------------------------------------------------------------------
# Original tests
# ---------------------------------------------------------------------------


def test_capacity_unit_selector_has_all_expected_options():
    root = Path(__file__).resolve().parents[1]
    strings = json.loads((root / "custom_components/mopeka/strings.json").read_text())
    en = json.loads(
        (root / "custom_components/mopeka/translations/en.json").read_text()
    )

    strings_options = strings["selector"]["tank_capacity_unit"]["options"]
    en_options = en["selector"]["tank_capacity_unit"]["options"]

    expected = {"gal", "kg", "l"}
    assert expected.issubset(strings_options.keys())
    assert expected.issubset(en_options.keys())


def test_custom_step_contains_capacity_unit_label_and_description():
    root = Path(__file__).resolve().parents[1]
    strings = json.loads((root / "custom_components/mopeka/strings.json").read_text())

    custom_step = strings["config"]["step"]["custom_height"]
    assert "tank_capacity_unit" in custom_step["data"]
    assert "tank_capacity_unit" in custom_step["data_description"]


def test_invalid_number_error_is_translated_in_strings_and_en_json():
    root = Path(__file__).resolve().parents[1]
    strings = json.loads((root / "custom_components/mopeka/strings.json").read_text())
    en = json.loads(
        (root / "custom_components/mopeka/translations/en.json").read_text()
    )

    assert strings["config"]["error"]["invalid_number"]
    assert en["config"]["error"]["invalid_number"]
