"""Tests for the Flame King 5 lb / 10 lb vertical propane presets."""

from __future__ import annotations

import pytest

FLAME_KING_PRESETS = ["5lb_fk_v", "10lb_fk_v"]


def _build_update(stub_types, level_mm: float, quality_pct: int = 100):
    device_id = "dev1"
    level_key = stub_types["DeviceKey"]("tank_level", device_id)
    quality_key = stub_types["DeviceKey"]("reading_quality", device_id)
    return stub_types["SensorUpdate"](
        entity_descriptions={},
        entity_values={
            level_key: stub_types["SensorValue"](native_value=level_mm, name=None),
            quality_key: stub_types["SensorValue"](
                native_value=quality_pct, name="Reading quality"
            ),
        },
        devices={device_id: {"name": "Test Device"}},
    )


@pytest.mark.parametrize("preset", FLAME_KING_PRESETS)
def test_flame_king_presets_are_selectable_propane_presets(const_module, preset):
    sizes = [str(s) for s in const_module.PROPANE_TANK_SIZES]
    assert preset in sizes
    # The default (first) preset must stay 20 lb so existing flows are unchanged.
    assert str(const_module.PROPANE_TANK_SIZES[0]) == "20lb_v"


def test_flame_king_ranges_and_capacities(const_module):
    ranges = const_module.TANK_SIZE_RANGES
    caps = const_module.TANK_SIZE_CAPACITIES
    tank = const_module.TankSize
    assert ranges[tank.LB_5_FK] == (const_module.TANK_EMPTY_MM, 155.0)
    assert ranges[tank.LB_10_FK] == (const_module.TANK_EMPTY_MM, 253.0)
    assert caps[tank.LB_5_FK] == 1.2
    assert caps[tank.LB_10_FK] == 2.5
    # Sizes must be ordered sensibly relative to the existing 20 lb preset.
    assert ranges[tank.LB_5_FK][1] < ranges[tank.LB_10_FK][1] < ranges[tank.LB_20][1]
    assert caps[tank.LB_5_FK] < caps[tank.LB_10_FK] < caps[tank.LB_20]


def test_flame_king_presets_are_vertical(const_module):
    horizontal = const_module.HORIZONTAL_TANK_SIZES
    assert const_module.TankSize.LB_5_FK not in horizontal
    assert const_module.TankSize.LB_10_FK not in horizontal


@pytest.mark.parametrize(
    ("preset", "full_mm", "capacity"),
    [("5lb_fk_v", 155.0, 1.2), ("10lb_fk_v", 253.0, 2.5)],
)
def test_flame_king_tank_range_and_capacity_via_sensor_helpers(
    sensor_module, preset, full_mm, capacity
):
    entry = {"tank_size": preset, "medium_type": "propane"}
    assert sensor_module._get_tank_level_range(entry) == (
        38.1,
        full_mm,
        False,
        None,
    )
    assert sensor_module._get_tank_capacity(entry) == (capacity, "gal")


def test_flame_king_preset_not_offered_for_non_propane_media(sensor_module):
    assert (
        sensor_module._get_tank_level_range(
            {"tank_size": "5lb_fk_v", "medium_type": "fresh_water"}
        )
        is None
    )


@pytest.mark.parametrize(
    ("preset", "full_mm", "capacity"),
    [("5lb_fk_v", 155.0, 1.2), ("10lb_fk_v", 253.0, 2.5)],
)
def test_flame_king_fill_percent_and_volume(
    sensor_module, stub_types, preset, full_mm, capacity
):
    entry = {"tank_size": preset, "medium_type": "propane"}
    converter = sensor_module.make_sensor_update_to_bluetooth_data_update(
        tank_range=sensor_module._get_tank_level_range(entry),
        top_mount=False,
        medium_type="propane",
        propane_preset=preset,
        tank_capacity=sensor_module._get_tank_capacity(entry),
    )
    pct_key = stub_types["PassiveBluetoothEntityKey"]("tank_level_percent", "dev1")
    vol_key = stub_types["PassiveBluetoothEntityKey"]("tank_volume", "dev1")

    full = converter(_build_update(stub_types, level_mm=full_mm))
    assert full.entity_data[pct_key] == 100.0
    assert full.entity_data[vol_key] == capacity

    # Above the calibrated full height clamps at 100 %.
    over = converter(_build_update(stub_types, level_mm=full_mm + 40))
    assert over.entity_data[pct_key] == 100.0

    # Halfway between empty (38.1 mm) and full is 50 %.
    mid_mm = 38.1 + (full_mm - 38.1) / 2
    mid = converter(_build_update(stub_types, level_mm=mid_mm))
    assert mid.entity_data[pct_key] == 50.0
    assert mid.entity_data[vol_key] == round(capacity / 2, 2)

    # At or below the empty offset reads 0 %.
    empty = converter(_build_update(stub_types, level_mm=10.0))
    assert empty.entity_data[pct_key] == 0.0


def test_flame_king_labels_present_in_all_translation_files(const_module):
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[1] / "custom_components/mopeka"
    for rel in ("strings.json", "translations/en.json", "translations/de.json"):
        text = (root / rel).read_text()
        data = json.loads(text)
        assert text.count('"5lb_fk_v"') >= 2, rel
        assert text.count('"10lb_fk_v"') >= 2, rel
        assert "Flame King 5 lb" in text and "Flame King 10 lb" in text, rel
        assert data  # parses
