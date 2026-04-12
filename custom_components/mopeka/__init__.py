"""The Mopeka integration."""

from __future__ import annotations

import logging

from mopeka_iot_ble import MediumType, MopekaIOTBluetoothDeviceData

from homeassistant.components.bluetooth import BluetoothScanningMode
from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothProcessorCoordinator,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import (
    CONF_MEDIUM_TYPE,
    CONF_TANK_SIZE,
    DEFAULT_MEDIUM_TYPE,
    is_beer_medium,
    normalize_tank_size,
)

PLATFORMS: list[Platform] = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)


type MopekaConfigEntry = ConfigEntry[PassiveBluetoothProcessorCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: MopekaConfigEntry) -> bool:
    """Set up Mopeka BLE device from a config entry."""
    address = entry.unique_id
    assert address is not None

    tank_size = entry.data.get(CONF_TANK_SIZE)
    normalized_tank_size = normalize_tank_size(tank_size)
    if normalized_tank_size != tank_size:
        hass.config_entries.async_update_entry(
            entry,
            data={**entry.data, CONF_TANK_SIZE: normalized_tank_size},
        )

    # Default sensors configured prior to the introduction of MediumType.
    # Beer sub-types are stored as custom values (e.g. "beer_ipa") and are not
    # present in the library's MediumType enum.  Fresh water is the closest
    # acoustic proxy; sensor.py applies a per-beer SOS multiplier correction.
    medium_type_str = entry.data.get(CONF_MEDIUM_TYPE, DEFAULT_MEDIUM_TYPE)
    library_medium = (
        MediumType.FRESH_WATER
        if is_beer_medium(medium_type_str)
        else MediumType(medium_type_str)
    )
    data = MopekaIOTBluetoothDeviceData(library_medium)
    coordinator = entry.runtime_data = PassiveBluetoothProcessorCoordinator(
        hass,
        _LOGGER,
        address=address,
        mode=BluetoothScanningMode.PASSIVE,
        update_method=data.update,
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    # only start after all platforms have had a chance to subscribe
    entry.async_on_unload(coordinator.async_start())
    entry.async_on_unload(entry.add_update_listener(update_listener))
    return True


async def update_listener(hass: HomeAssistant, entry: MopekaConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: MopekaConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry: MopekaConfigEntry, device_entry: dr.DeviceEntry
) -> bool:
    """Allow removal of a device that is no longer advertising."""
    return True
