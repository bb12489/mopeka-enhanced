"""Temporary compatibility shim for the pinned mopeka-iot-ble release.

The pinned `mopeka-iot-ble` release (0.8.0, from July 2024) does not
recognize device type `0x12`, the Mopeka Pro-200B. Our own manifest.json
already discovers it (manufacturer_data_start [18] == 0x12, added in our
v0.2.6), but without this patch `MopekaIOTBluetoothDeviceData.supported()`
returns False for it, so Home Assistant's bluetooth discovery flow aborts
with "not_supported" and the device never gets sensors.

Upstream merged support for this device
(https://github.com/Bluetooth-Devices/mopeka-iot-ble/pull/71) but has not
cut a release that includes it yet. This patches the library's device
table in place to match that upstream fix exactly.

Remove this file (and its imports in __init__.py/config_flow.py) once
mopeka-iot-ble publishes a release with 0x12 support, and bump the pinned
version in manifest.json/requirements-dev.txt accordingly.
"""

from __future__ import annotations

import logging

_LOGGER = logging.getLogger(__name__)


def _patch_pro_200b_support() -> None:
    try:
        from mopeka_iot_ble.parser import DEVICE_TYPES, MopekaDevice
    except ImportError:
        _LOGGER.debug(
            "mopeka_iot_ble.parser.DEVICE_TYPES not found; "
            "skipping Pro-200B compat patch"
        )
        return
    # setdefault: a no-op once a real release already defines 0x12, so this
    # stays harmless after the pin is bumped past that release.
    DEVICE_TYPES.setdefault(0x12, MopekaDevice("Pro-200", "Pro-200B", 10))


_patch_pro_200b_support()
