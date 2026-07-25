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


def test_every_sensor_description_has_a_matching_strings_json_entity_name(
    sensor_module,
):
    """Every SENSOR_DESCRIPTIONS translation_key must have a corresponding
    entity.sensor.<key>.name entry in both strings.json and en.json.

    This is the naming-consistency guard: it ensures every sensor entity's
    display name is sourced from this integration's own translations (and is
    therefore sentence case and localizable), rather than silently falling
    back to an upstream library's own (Title Case, non-localizable) name —
    see the entity_names construction in sensor.py for how that's enforced
    at runtime.
    """
    root = Path(__file__).resolve().parents[1]
    strings = json.loads((root / "custom_components/mopeka/strings.json").read_text())
    en = json.loads(
        (root / "custom_components/mopeka/translations/en.json").read_text()
    )

    for key, description in sensor_module.SENSOR_DESCRIPTIONS.items():
        translation_key = description.translation_key
        assert translation_key == key, f"{key}: translation_key mismatch"
        for doc, label in ((strings, "strings.json"), (en, "en.json")):
            entity_entry = doc["entity"]["sensor"].get(translation_key)
            assert entity_entry is not None, f"{label}: missing entity for {key!r}"
            assert entity_entry.get("name"), f"{label}: missing name for {key!r}"


def test_tank_volume_sensor_name_reflects_remaining_amount():
    """Regression guard for the tank_volume -> 'Tank volume remaining' rename.

    The sensor reports the amount of medium currently in the tank, not the
    tank's total/rated capacity, so the name must say "remaining" to avoid
    reading like a spec value.
    """
    root = Path(__file__).resolve().parents[1]
    strings = json.loads((root / "custom_components/mopeka/strings.json").read_text())
    en = json.loads(
        (root / "custom_components/mopeka/translations/en.json").read_text()
    )

    assert strings["entity"]["sensor"]["tank_volume"]["name"] == "Tank volume remaining"
    assert en["entity"]["sensor"]["tank_volume"]["name"] == "Tank volume remaining"


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


def test_top_mount_sensor_height_field_present_in_strings_and_en_json():
    """CONF_TOP_MOUNT_SENSOR_HEIGHT must have a label/description everywhere
    the custom-height form appears (config, reconfigure, options), plus its
    own dedicated preset-path step (top_mount_height / reconfigure_top_mount_height).
    """
    root = Path(__file__).resolve().parents[1]
    strings = json.loads((root / "custom_components/mopeka/strings.json").read_text())
    en = json.loads(
        (root / "custom_components/mopeka/translations/en.json").read_text()
    )

    custom_height_steps = [
        ("config", "custom_height"),
        ("config", "reconfigure_custom_height"),
        ("options", "custom_height"),
    ]
    for flow, step in custom_height_steps:
        for doc, label in ((strings, "strings.json"), (en, "en.json")):
            data = doc[flow]["step"][step]["data"]
            desc = doc[flow]["step"][step]["data_description"]
            assert "top_mount_sensor_height" in data, f"{label}:{flow}.{step}.data"
            assert "top_mount_sensor_height" in desc, (
                f"{label}:{flow}.{step}.data_description"
            )

    sensor_height_steps = [
        ("config", "top_mount_height"),
        ("config", "reconfigure_top_mount_height"),
        ("options", "top_mount_height"),
    ]
    for flow, step in sensor_height_steps:
        for doc, label in ((strings, "strings.json"), (en, "en.json")):
            step_def = doc[flow]["step"][step]
            assert "top_mount_sensor_height" in step_def["data"], (
                f"{label}:{flow}.{step}.data"
            )
            assert "top_mount_sensor_height" in step_def["data_description"], (
                f"{label}:{flow}.{step}.data_description"
            )
            assert step_def["title"], f"{label}:{flow}.{step}.title"
