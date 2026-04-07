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
        tank_range=(0.0, 1000.0, False),
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
