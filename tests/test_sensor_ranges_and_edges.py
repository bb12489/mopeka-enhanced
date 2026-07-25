from __future__ import annotations


def _build_update(stub_types, level_mm: float | str):
    device_key = stub_types["DeviceKey"]("tank_level", "dev1")
    sensor_value = stub_types["SensorValue"](native_value=level_mm, name=None)
    return stub_types["SensorUpdate"](
        entity_descriptions={},
        entity_values={device_key: sensor_value},
        devices={"dev1": {"name": "Test Device"}},
    )


def test_circular_segment_fraction_boundaries(sensor_module):
    assert sensor_module._circular_segment_fraction(0.0, 100.0) == 0.0
    assert sensor_module._circular_segment_fraction(100.0, 100.0) == 1.0


def test_circular_segment_fraction_monotonic(sensor_module):
    f = sensor_module._circular_segment_fraction
    assert f(10.0, 100.0) < f(30.0, 100.0) < f(60.0, 100.0)


def test_tank_level_range_missing_size(sensor_module):
    assert sensor_module._get_tank_level_range({}) is None


def test_tank_level_range_custom_height_zero(sensor_module):
    assert (
        sensor_module._get_tank_level_range(
            {"tank_size": "custom", "custom_tank_height": 0}
        )
        is None
    )


def test_tank_level_range_top_mount_custom(sensor_module):
    # No CONF_TOP_MOUNT_SENSOR_HEIGHT set: falls back to the max water level
    # height (0 headspace), reproducing pre-existing behavior.
    assert sensor_module._get_tank_level_range(
        {
            "tank_size": "custom",
            "custom_tank_height": 1200,
            "top_mount": True,
            "medium_type": "air",
        }
    ) == (0.0, 1200.0, False, 1200.0)


def test_tank_level_range_top_mount_custom_with_headspace(sensor_module):
    # Sensor mounted above the max-fill line: sensor_mount_height (the fourth
    # element) reflects the physical mount height, distinct from the max
    # water level height (the second element).
    assert sensor_module._get_tank_level_range(
        {
            "tank_size": "custom",
            "custom_tank_height": 1200,
            "top_mount_sensor_height": 1350,
            "top_mount": True,
            "medium_type": "air",
        }
    ) == (0.0, 1200.0, False, 1350.0)


def test_tank_level_range_ibc_top_mount_preset_falls_back_to_preset_height(
    sensor_module,
):
    # IBC preset + top-mount, no CONF_TOP_MOUNT_SENSOR_HEIGHT set: falls back
    # to the preset's own height (0 headspace), same as the Custom case.
    assert sensor_module._get_tank_level_range(
        {
            "tank_size": "ibc_275gal",
            "top_mount": True,
            "medium_type": "air",
        }
    ) == (0.0, 980.0, False, 980.0)


def test_tank_level_range_ibc_top_mount_preset_with_headspace(sensor_module):
    assert sensor_module._get_tank_level_range(
        {
            "tank_size": "ibc_275gal",
            "top_mount_sensor_height": 1050,
            "top_mount": True,
            "medium_type": "air",
        }
    ) == (0.0, 980.0, False, 1050.0)


def test_resolve_sensor_mount_height_unset_falls_back(sensor_module):
    assert sensor_module._resolve_sensor_mount_height({}, 1200.0) == 1200.0
    assert (
        sensor_module._resolve_sensor_mount_height(
            {"top_mount_sensor_height": 0}, 1200.0
        )
        == 1200.0
    )


def test_resolve_sensor_mount_height_explicit_value(sensor_module):
    assert (
        sensor_module._resolve_sensor_mount_height(
            {"top_mount_sensor_height": 1350}, 1200.0
        )
        == 1350.0
    )


def test_tank_level_range_propane_preset_non_propane_medium_returns_none(sensor_module):
    assert (
        sensor_module._get_tank_level_range(
            {
                "tank_size": "20lb_v",
                "medium_type": "fresh_water",
            }
        )
        is None
    )


def test_tank_level_range_horizontal_preset_sets_horizontal(sensor_module):
    assert sensor_module._get_tank_level_range(
        {
            "tank_size": "500gal_h",
            "medium_type": "propane",
        }
    ) == (38.1, 939.8, True, None)


def test_fill_percent_clamps_low_and_high(sensor_module, stub_types):
    converter = sensor_module.make_sensor_update_to_bluetooth_data_update(
        tank_range=(0.0, 1000.0, False, None),
        top_mount=False,
        medium_type="fresh_water",
        propane_preset="custom",
        tank_capacity=(100.0, "gal"),
    )
    key = stub_types["PassiveBluetoothEntityKey"]("tank_level_percent", "dev1")

    low_update = converter(_build_update(stub_types, -50.0))
    high_update = converter(_build_update(stub_types, 1500.0))

    assert low_update.entity_data[key] == 0.0
    assert high_update.entity_data[key] == 100.0


def test_non_numeric_tank_level_disables_synthesized_values(sensor_module, stub_types):
    converter = sensor_module.make_sensor_update_to_bluetooth_data_update(
        tank_range=(0.0, 1000.0, False, None),
        top_mount=False,
        medium_type="fresh_water",
        propane_preset="custom",
        tank_capacity=(100.0, "gal"),
    )
    pct_key = stub_types["PassiveBluetoothEntityKey"]("tank_level_percent", "dev1")
    vol_key = stub_types["PassiveBluetoothEntityKey"]("tank_volume", "dev1")

    update = converter(_build_update(stub_types, "bad"))

    assert update.entity_data[pct_key] is None
    assert update.entity_data[vol_key] is None


def test_zero_capacity_disables_volume_sensor(sensor_module, stub_types):
    converter = sensor_module.make_sensor_update_to_bluetooth_data_update(
        tank_range=(0.0, 1000.0, False, None),
        top_mount=False,
        medium_type="fresh_water",
        propane_preset="custom",
        tank_capacity=None,
    )
    vol_key = stub_types["PassiveBluetoothEntityKey"]("tank_volume", "dev1")

    update = converter(_build_update(stub_types, 500.0))

    assert vol_key not in update.entity_data
