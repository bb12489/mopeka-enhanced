"""End-to-end tests for config entry setup/unload/reload against a real hass."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.mopeka.const import (
    CONF_CUSTOM_TANK_HEIGHT,
    CONF_MEDIUM_TYPE,
    CONF_TANK_CAPACITY,
    CONF_TANK_CAPACITY_UNIT,
    CONF_TANK_SIZE,
    CONF_TOP_MOUNT,
    DEFAULT_MEDIUM_TYPE,
    DOMAIN,
)

TEST_ADDRESS = "AA:BB:CC:DD:EE:FF"


def _make_entry() -> MockConfigEntry:
    return MockConfigEntry(
        domain=DOMAIN,
        unique_id=TEST_ADDRESS,
        data={
            CONF_MEDIUM_TYPE: DEFAULT_MEDIUM_TYPE,
            CONF_TANK_SIZE: "custom",
            CONF_CUSTOM_TANK_HEIGHT: 0,
            CONF_TANK_CAPACITY: 0.0,
            CONF_TANK_CAPACITY_UNIT: "gal",
            CONF_TOP_MOUNT: False,
        },
    )


async def test_setup_and_unload_entry(
    hass: HomeAssistant, mock_bluetooth: None
) -> None:
    """A config entry sets up its coordinator/platforms and tears them down cleanly."""
    entry = _make_entry()
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED
    assert entry.runtime_data is not None

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.NOT_LOADED


async def test_options_update_reloads_entry(
    hass: HomeAssistant, mock_bluetooth: None
) -> None:
    """Updating options triggers a reload via the registered update listener."""
    entry = _make_entry()
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.LOADED

    hass.config_entries.async_update_entry(
        entry, data={**entry.data, CONF_TANK_SIZE: "30lb_v"}
    )
    await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED
