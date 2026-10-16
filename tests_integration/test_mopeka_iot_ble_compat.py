"""Regression test for the Pro-200B compat shim against the real mopeka-iot-ble.

The pinned mopeka-iot-ble release (0.8.0) doesn't know about device type
0x12 (Mopeka Pro-200B), even though our manifest.json already discovers it.
custom_components/mopeka/_mopeka_iot_ble_compat.py patches the library's
device table in place to cover the gap until upstream ships a release with
https://github.com/Bluetooth-Devices/mopeka-iot-ble/pull/71 included.

This advertisement fixture is upstream's own PR #71 test vector, so a
correct parse here should track what a real future release would produce.
"""

from __future__ import annotations

from home_assistant_bluetooth import BluetoothServiceInfo
from mopeka_iot_ble import MopekaIOTBluetoothDeviceData

# Importing config_flow (transitively imports __init__, which imports the
# compat shim) is what real bluetooth discovery does before it ever calls
# MopekaIOTBluetoothDeviceData.supported() on a Pro-200B advertisement.
from custom_components.mopeka import config_flow  # noqa: F401

PRO_200B_SERVICE_INFO = BluetoothServiceInfo(
    name="",
    address="CB:A1:6C:CC:E5:2B",
    rssi=-63,
    manufacturer_data={89: b"\x12\x5f\x31\x78\xc7\xcc\xe5\x2b\xa8\x3f"},
    service_uuids=["0000fee5-0000-1000-8000-00805f9b34fb"],
    service_data={},
    source="local",
)


def test_pro_200b_is_supported() -> None:
    """Without the compat patch this returns False and discovery aborts."""
    parser = MopekaIOTBluetoothDeviceData()
    assert parser.supported(PRO_200B_SERVICE_INFO) is True


def test_pro_200b_parses_device_info_and_sensors() -> None:
    parser = MopekaIOTBluetoothDeviceData()
    result = parser.update(PRO_200B_SERVICE_INFO)

    device_info = result.devices[None]
    assert device_info.name == "Pro-200B E52B"
    assert device_info.manufacturer == "Mopeka IOT"

    values = {
        key.key: value.native_value for key, value in result.entity_values.items()
    }
    assert values["battery"] == 100
    assert values["tank_level"] == 806
