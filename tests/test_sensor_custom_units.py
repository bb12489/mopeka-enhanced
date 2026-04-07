from __future__ import annotations

import pytest


def _build_update(stub_types, level_mm: float):
    device_key = stub_types["DeviceKey"]("tank_level", "dev1")
    sensor_value = stub_types["SensorValue"](native_value=level_mm, name=None)
    sensor_update = stub_types["SensorUpdate"](
        entity_descriptions={},
        entity_values={device_key: sensor_value},
        devices={"dev1": {"name": "Test Device"}},
    )
    return sensor_update


def test_custom_non_propane_liters_volume_sensor(sensor_module, stub_types):
    converter = sensor_module.make_sensor_update_to_bluetooth_data_update(
        tank_range=(0.0, 1000.0, False),
        top_mount=False,
        medium_type="fresh_water",
        propane_preset="custom",
        tank_capacity=(200.0, "l"),
    )

    update = converter(_build_update(stub_types, level_mm=500.0))
    key = stub_types["PassiveBluetoothEntityKey"]("tank_volume", "dev1")

    assert update.entity_data[key] == 100.0
    assert update.entity_names[key] == "Tank level (liters)"
    assert (
        update.entity_descriptions[key].native_unit_of_measurement
        == stub_types["UnitOfVolume"].LITERS
    )


def test_custom_propane_kilograms_volume_sensor(sensor_module, stub_types):
    converter = sensor_module.make_sensor_update_to_bluetooth_data_update(
        tank_range=(0.0, 600.0, False),
        top_mount=False,
        medium_type="propane",
        propane_preset="custom",
        tank_capacity=(40.0, "kg"),
    )

    update = converter(_build_update(stub_types, level_mm=300.0))
    key = stub_types["PassiveBluetoothEntityKey"]("tank_volume", "dev1")

    assert update.entity_data[key] == 20.0
    assert update.entity_names[key] == "Tank level (kilograms)"
    assert (
        update.entity_descriptions[key].native_unit_of_measurement
        == stub_types["UnitOfMass"].KILOGRAMS
    )


def test_custom_top_mount_uses_air_gap_conversion(sensor_module, stub_types):
    converter = sensor_module.make_sensor_update_to_bluetooth_data_update(
        tank_range=(0.0, 1000.0, False),
        top_mount=True,
        medium_type="air",
        propane_preset="custom",
        tank_capacity=(100.0, "gal"),
    )

    update = converter(_build_update(stub_types, level_mm=250.0))
    level_key = stub_types["PassiveBluetoothEntityKey"]("tank_level", "dev1")
    pct_key = stub_types["PassiveBluetoothEntityKey"]("tank_level_percent", "dev1")

    assert update.entity_data[level_key] == 750.0
    assert update.entity_data[pct_key] == 75.0


def test_custom_capacity_unit_resolution(sensor_module):
    assert sensor_module._get_tank_capacity(
        {
            "tank_size": "custom",
            "medium_type": "propane",
            "tank_capacity": 11.0,
            "tank_capacity_unit": "kg",
        }
    ) == (11.0, "kg")

    assert sensor_module._get_tank_capacity(
        {
            "tank_size": "custom",
            "medium_type": "fresh_water",
            "tank_capacity": 210.0,
            "tank_capacity_unit": "l",
        }
    ) == (210.0, "l")

    assert sensor_module._get_tank_capacity(
        {
            "tank_size": "custom",
            "medium_type": "fresh_water",
            "tank_capacity": 75.0,
            "tank_capacity_unit": "gal",
        }
    ) == (75.0, "gal")


@pytest.mark.parametrize(
    (
        "medium_type",
        "tank_capacity_unit",
        "capacity",
        "expected_unit",
        "expected_label",
    ),
    [
        ("propane", "gal", 80.0, "gal", None),
        ("propane", "kg", 40.0, "kg", "Tank level (kilograms)"),
        ("fresh_water", "l", 200.0, "L", "Tank level (liters)"),
    ],
)
def test_dropdown_unit_and_capacity_drive_tank_volume_output(
    sensor_module,
    stub_types,
    medium_type,
    tank_capacity_unit,
    capacity,
    expected_unit,
    expected_label,
):
    entry_data = {
        "tank_size": "custom",
        "medium_type": medium_type,
        "tank_capacity": capacity,
        "tank_capacity_unit": tank_capacity_unit,
    }
    tank_capacity = sensor_module._get_tank_capacity(entry_data)

    converter = sensor_module.make_sensor_update_to_bluetooth_data_update(
        tank_range=(0.0, 1000.0, False),
        top_mount=False,
        medium_type=medium_type,
        propane_preset="custom",
        tank_capacity=tank_capacity,
    )

    # 250mm in a 0..1000mm tank yields 25% volume.
    update = converter(_build_update(stub_types, level_mm=250.0))
    key = stub_types["PassiveBluetoothEntityKey"]("tank_volume", "dev1")

    assert update.entity_data[key] == pytest.approx(capacity * 0.25)
    assert update.entity_names[key] == expected_label
    assert update.entity_descriptions[key].native_unit_of_measurement == expected_unit
