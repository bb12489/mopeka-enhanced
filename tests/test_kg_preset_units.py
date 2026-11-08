"""Kilogram-rated presets must report the tank volume sensor in kilograms."""

from __future__ import annotations

import pytest


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


def _convert(sensor_module, stub_types, preset: str, level_mm: float):
    entry = {"tank_size": preset, "medium_type": "propane"}
    converter = sensor_module.make_sensor_update_to_bluetooth_data_update(
        tank_range=sensor_module._get_tank_level_range(entry),
        top_mount=False,
        medium_type="propane",
        propane_preset=preset,
        tank_capacity=sensor_module._get_tank_capacity(entry),
    )
    update = converter(_build_update(stub_types, level_mm=level_mm))
    key = stub_types["PassiveBluetoothEntityKey"]("tank_volume", "dev1")
    return update.entity_descriptions[key].native_unit_of_measurement, (
        update.entity_data[key]
    )


def test_every_kg_preset_has_a_rated_kg_and_a_gallon_capacity(const_module):
    for preset, kg in const_module.TANK_SIZE_RATED_KG.items():
        assert kg > 0
        assert preset in const_module.TANK_SIZE_CAPACITIES, preset
        assert "kg" in str(preset), preset


def test_all_kg_named_presets_are_in_rated_kg_table(const_module):
    kg_presets = {str(s) for s in const_module.TankSize if "kg" in str(s)}
    assert kg_presets == {str(s) for s in const_module.TANK_SIZE_RATED_KG}


def test_rated_kg_agrees_with_gallon_capacity(const_module):
    # kg / 1.921 kg-per-gal should round to the stored gallon figure (+-0.1).
    for preset, kg in const_module.TANK_SIZE_RATED_KG.items():
        gal = const_module.TANK_SIZE_CAPACITIES[preset]
        assert kg / 1.921 == pytest.approx(gal, abs=0.1), preset


@pytest.mark.parametrize(
    ("preset", "kg"),
    [("6kg_v", 6.0), ("11kg_v", 11.0), ("4_5kg_za_v", 4.5), ("9kg_nz_v", 9.0)],
)
def test_kg_preset_capacity_is_kilograms(sensor_module, preset, kg):
    entry = {"tank_size": preset, "medium_type": "propane"}
    assert sensor_module._get_tank_capacity(entry) == (kg, "kg")


@pytest.mark.parametrize("preset", ["20lb_v", "5lb_fk_v", "10lb_fk_v", "40lb_v"])
def test_lb_presets_stay_in_gallons(sensor_module, preset):
    entry = {"tank_size": preset, "medium_type": "propane"}
    assert sensor_module._get_tank_capacity(entry)[1] == "gal"


def test_switching_gallon_preset_to_kg_preset_changes_volume_unit(
    sensor_module, stub_types
):
    """Regression: 5 lb Flame King (gal) -> Euro 6 kg must report kg."""
    gal_unit, gal_value = _convert(sensor_module, stub_types, "5lb_fk_v", 155.0)
    kg_unit, kg_value = _convert(sensor_module, stub_types, "6kg_v", 336.0)
    assert gal_unit == "gal" and gal_value == 1.2
    assert kg_unit == "kg" and kg_value == 6.0


def test_kg_preset_volume_scales_with_fill(sensor_module, stub_types):
    # Halfway between empty (38.1 mm) and full (336 mm) is 50 % of 6 kg.
    mid_mm = 38.1 + (336.0 - 38.1) / 2
    unit, value = _convert(sensor_module, stub_types, "6kg_v", mid_mm)
    assert unit == "kg"
    assert value == 3.0


def test_custom_tank_unit_behaviour_unchanged(sensor_module):
    entry = {
        "tank_size": "custom",
        "medium_type": "propane",
        "tank_capacity": 10,
        "tank_capacity_unit": "kg",
    }
    assert sensor_module._get_tank_capacity(entry) == (10.0, "kg")
