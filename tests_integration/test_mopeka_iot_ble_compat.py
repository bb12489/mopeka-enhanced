"""Regression test for Pro-200B support in the pinned mopeka-iot-ble.

mopeka-iot-ble>=1.0.0 natively supports device type 0x12 (Mopeka Pro-200B),
via https://github.com/Bluetooth-Devices/mopeka-iot-ble/pull/71. Our own
manifest.json also discovers it (manufacturer_data_start [18] == 0x12,
added in our v0.2.6). This test guards against either side regressing.

This advertisement fixture is upstream's own PR #71 test vector.
"""

from __future__ import annotations

from home_assistant_bluetooth import BluetoothServiceInfo
from mopeka_iot_ble import MopekaIOTBluetoothDeviceData

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
    """On mopeka-iot-ble<1.0.0 this returns False and discovery aborts."""
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
