"""End-to-end tests for config entry setup/unload/reload against a real hass."""

from __future__ import annotations

from unittest.mock import patch

from homeassistant.config_entries import SOURCE_RECONFIGURE, ConfigEntryState
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

    with patch.object(
        hass.config_entries,
        "async_reload",
        wraps=hass.config_entries.async_reload,
    ) as reload_mock:
        hass.config_entries.async_update_entry(
            entry, data={**entry.data, CONF_TANK_SIZE: "30lb_v"}
        )
        await hass.async_block_till_done()
        assert reload_mock.await_count == 1

        # An unchanged save should not schedule another reload.
        hass.config_entries.async_update_entry(entry, data=dict(entry.data))
        await hass.async_block_till_done()
        assert reload_mock.await_count == 1

    assert entry.state is ConfigEntryState.LOADED


async def test_options_flow_reloads_once(
    hass: HomeAssistant, mock_bluetooth: None
) -> None:
    """Saving a tank preset in the options flow reloads the entry once."""
    entry = _make_entry()
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["step_id"] == "init"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={CONF_MEDIUM_TYPE: DEFAULT_MEDIUM_TYPE, CONF_TOP_MOUNT: False},
    )
    assert result["step_id"] == "tank_config"

    with patch.object(
        hass.config_entries,
        "async_reload",
        wraps=hass.config_entries.async_reload,
    ) as reload_mock:
        await hass.config_entries.options.async_configure(
            result["flow_id"], user_input={CONF_TANK_SIZE: "30lb_v"}
        )
        await hass.async_block_till_done()
        assert reload_mock.await_count == 1

    assert entry.state is ConfigEntryState.LOADED
    assert entry.data[CONF_TANK_SIZE] == "30lb_v"


async def test_reconfigure_flow_reloads_once(
    hass: HomeAssistant, mock_bluetooth: None
) -> None:
    """Reconfiguring a tank preset reloads the entry once."""
    entry = _make_entry()
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_RECONFIGURE, "entry_id": entry.entry_id},
    )
    assert result["step_id"] == "reconfigure"
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_MEDIUM_TYPE: DEFAULT_MEDIUM_TYPE, CONF_TOP_MOUNT: False},
    )
    assert result["step_id"] == "reconfigure_tank_config"

    with patch.object(
        hass.config_entries,
        "async_reload",
        wraps=hass.config_entries.async_reload,
    ) as reload_mock:
        await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input={CONF_TANK_SIZE: "30lb_v"}
        )
        await hass.async_block_till_done()
        assert reload_mock.await_count == 1

    assert entry.state is ConfigEntryState.LOADED
    assert entry.data[CONF_TANK_SIZE] == "30lb_v"
