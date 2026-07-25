from __future__ import annotations


def _build_update_with_devices(stub_types, level_mm: float, device_ids: list[str]):
    device_key = stub_types["DeviceKey"]("tank_level", device_ids[0])
    sensor_value = stub_types["SensorValue"](native_value=level_mm, name=None)
    devices = {device_id: {"name": device_id} for device_id in device_ids}
    return stub_types["SensorUpdate"](
        entity_descriptions={},
        entity_values={device_key: sensor_value},
        devices=devices,
    )


def test_diagnostic_sensors_injected_for_all_devices(sensor_module, stub_types):
    converter = sensor_module.make_sensor_update_to_bluetooth_data_update(
        tank_range=(0.0, 1000.0, False, None),
        top_mount=False,
        medium_type="fresh_water",
        propane_preset="custom",
        tank_capacity=(100.0, "gal"),
    )
    update = converter(_build_update_with_devices(stub_types, 500.0, ["dev1", "dev2"]))

    med1 = stub_types["PassiveBluetoothEntityKey"]("medium_type", "dev1")
    med2 = stub_types["PassiveBluetoothEntityKey"]("medium_type", "dev2")
    pre1 = stub_types["PassiveBluetoothEntityKey"]("propane_preset", "dev1")
    pre2 = stub_types["PassiveBluetoothEntityKey"]("propane_preset", "dev2")

    assert update.entity_data[med1] == "fresh_water"
    assert update.entity_data[med2] == "fresh_water"
    assert update.entity_data[pre1] == "custom"
    assert update.entity_data[pre2] == "custom"


def test_get_tank_capacity_defaults_to_gallons_for_invalid_custom_unit(sensor_module):
    assert sensor_module._get_tank_capacity(
        {
            "tank_size": "custom",
            "medium_type": "fresh_water",
            "tank_capacity": 123.0,
            "tank_capacity_unit": "bogus",
        }
    ) == (123.0, "gal")


def test_get_tank_capacity_for_preset_tank(sensor_module):
    assert sensor_module._get_tank_capacity(
        {
            "tank_size": "30lb_v",
            "medium_type": "propane",
        }
    ) == (7.1, "gal")


def test_all_sensor_descriptions_have_translation_key(sensor_module):
    """Every SENSOR_DESCRIPTIONS entry must set translation_key == its dict key.

    This locks in the naming convention: all entity display names live in
    strings.json/translations under this same key, sourced from our own
    (sentence case, localizable) strings rather than any upstream library's
    raw sensor name. Prevents a newly-added sensor description from silently
    falling back to a non-localizable, inconsistently-cased upstream name.
    """
    missing = [
        key
        for key, description in sensor_module.SENSOR_DESCRIPTIONS.items()
        if description.translation_key != key
    ]
    assert missing == [], f"Missing/mismatched translation_key for: {missing}"


def test_entity_names_suppressed_for_known_sensor_keys(sensor_module, stub_types):
    """Library-provided names are suppressed to None for any key we have our
    own SENSOR_DESCRIPTIONS/translation_key entry for (e.g. tank_level,
    battery), so translation_key controls the display name instead of the
    upstream mopeka_iot_ble library's own (Title Case) name. Keys with no
    SENSOR_DESCRIPTIONS entry (never rendered as an entity) are passed
    through unchanged, though functionally unused.
    """
    known_key = stub_types["DeviceKey"]("battery", "dev1")
    known_value = stub_types["SensorValue"](native_value=80, name="Battery")
    unknown_key = stub_types["DeviceKey"]("reading_quality_raw", "dev1")
    unknown_value = stub_types["SensorValue"](
        native_value=2, name="Reading quality raw"
    )

    converter = sensor_module.make_sensor_update_to_bluetooth_data_update(
        tank_range=None,
        top_mount=False,
        medium_type=None,
        propane_preset=None,
    )
    update = converter(
        stub_types["SensorUpdate"](
            entity_descriptions={},
            entity_values={known_key: known_value, unknown_key: unknown_value},
            devices={"dev1": {"name": "Test Device"}},
        )
    )

    known_entity_key = stub_types["PassiveBluetoothEntityKey"]("battery", "dev1")
    unknown_entity_key = stub_types["PassiveBluetoothEntityKey"](
        "reading_quality_raw", "dev1"
    )

    assert update.entity_names[known_entity_key] is None
    assert update.entity_names[unknown_entity_key] == "Reading quality raw"
