"""Tests for MopekaOptionsFlow — the three duplicated step methods."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace


# ─────────────────────────── shared test helpers ─────────────────────────────


def _schema_value(schema, target_key: str):
    """Extract a selector from a _VolSchema by config key name."""
    for required_key, value in schema.schema.items():
        if (
            isinstance(required_key, tuple)
            and len(required_key) >= 2
            and required_key[1] == target_key
        ):
            return value
    raise AssertionError(f"Missing schema key: {target_key!r}")


def _make_entry(data: dict, entry_id: str = "test-entry-id"):
    """Return a minimal fake config entry."""
    return SimpleNamespace(data=data, entry_id=entry_id)


def _make_flow(config_flow_module, entry_data: dict, medium_type: str | None = None):
    """
    Build a MopekaOptionsFlow with HA dependencies replaced by simple fakes.

    Returns (flow, update_calls, reload_calls) so tests can assert on side
    effects without touching real Home Assistant internals.
    """
    update_calls: list[dict] = []
    reload_calls: list[str] = []

    def _mock_update(entry, data=None):
        update_calls.append({"entry": entry, "data": data})

    async def _mock_reload(entry_id: str) -> None:
        reload_calls.append(entry_id)

    flow = config_flow_module.MopekaOptionsFlow()
    flow.config_entry = _make_entry(entry_data)
    flow.hass = SimpleNamespace(
        config_entries=SimpleNamespace(
            async_update_entry=_mock_update,
            async_reload=_mock_reload,
        )
    )
    flow.async_show_form = lambda **kwargs: kwargs
    flow.async_create_entry = lambda **kwargs: kwargs

    if medium_type is not None:
        flow._medium_type = medium_type

    return flow, update_calls, reload_calls


# ════════════════════════ async_step_init ════════════════════════════════════


def test_options_flow_init_top_mount_skips_medium_selector(config_flow_module):
    """Top-mount entries bypass the medium-type form and go straight to IBC config."""
    flow, _, _ = _make_flow(
        config_flow_module,
        entry_data={"top_mount": True, "medium_type": "air"},
    )

    async def _fake_ibc():
        return {"step": "ibc"}

    flow.async_step_ibc_tank_config = _fake_ibc

    result = asyncio.run(flow.async_step_init())

    assert result == {"step": "ibc"}
    assert flow._medium_type == "air"


def test_options_flow_init_propane_input_routes_to_tank_config(config_flow_module):
    """Selecting propane medium type routes to the propane tank selector."""
    flow, _, _ = _make_flow(
        config_flow_module,
        entry_data={"top_mount": False, "medium_type": "propane"},
    )

    async def _fake_tank():
        return {"step": "tank"}

    flow.async_step_tank_config = _fake_tank

    result = asyncio.run(flow.async_step_init(user_input={"medium_type": "propane"}))

    assert result == {"step": "tank"}
    assert flow._medium_type == "propane"


def test_options_flow_init_non_propane_input_routes_to_ibc(config_flow_module):
    """Non-propane medium types (water, air) route to the IBC tank selector."""
    flow, _, _ = _make_flow(
        config_flow_module,
        entry_data={"top_mount": False, "medium_type": "fresh_water"},
    )

    async def _fake_ibc():
        return {"step": "ibc"}

    flow.async_step_ibc_tank_config = _fake_ibc

    result = asyncio.run(
        flow.async_step_init(user_input={"medium_type": "fresh_water"})
    )

    assert result == {"step": "ibc"}
    assert flow._medium_type == "fresh_water"


def test_options_flow_init_no_input_shows_form(config_flow_module):
    """Without user input the medium-type selector form is displayed."""
    flow, _, _ = _make_flow(
        config_flow_module,
        entry_data={"top_mount": False, "medium_type": "propane"},
    )

    result = asyncio.run(flow.async_step_init())

    assert result["step_id"] == "init"
    assert "data_schema" in result


# ════════════════════════ async_step_tank_config ═════════════════════════════


def test_options_flow_tank_config_preset_updates_entry_and_completes(
    config_flow_module,
):
    """Selecting a preset updates the config entry, triggers a reload, and finishes."""
    entry_data = {
        "tank_size": "20lb_v",
        "medium_type": "propane",
        "custom_tank_height": 0,
        "tank_capacity": 0.0,
        "tank_capacity_unit": "gal",
    }
    flow, update_calls, reload_calls = _make_flow(
        config_flow_module,
        entry_data=entry_data,
        medium_type="propane",
    )

    result = asyncio.run(
        flow.async_step_tank_config(user_input={"tank_size": "30lb_v"})
    )

    assert len(update_calls) == 1
    updated = update_calls[0]["data"]
    assert updated["tank_size"] == "30lb_v"
    assert updated["medium_type"] == "propane"
    assert updated["custom_tank_height"] == 0
    assert updated["tank_capacity"] == 0.0
    assert updated["tank_capacity_unit"] == "gal"
    # Existing keys should be preserved via **self.config_entry.data spread
    assert "tank_size" in updated

    assert reload_calls == ["test-entry-id"]
    assert result == {"title": "", "data": {}}


def test_options_flow_tank_config_preserves_extra_entry_keys(config_flow_module):
    """Keys not managed by tank selection (e.g. address) survive the update."""
    entry_data = {
        "address": "AA:BB:CC:DD:EE:FF",
        "tank_size": "20lb_v",
        "medium_type": "propane",
        "custom_tank_height": 0,
        "tank_capacity": 0.0,
        "tank_capacity_unit": "gal",
    }
    flow, update_calls, _ = _make_flow(
        config_flow_module,
        entry_data=entry_data,
        medium_type="propane",
    )

    asyncio.run(flow.async_step_tank_config(user_input={"tank_size": "40lb_v"}))

    assert update_calls[0]["data"]["address"] == "AA:BB:CC:DD:EE:FF"


def test_options_flow_tank_config_custom_routes_to_custom_height(config_flow_module):
    """Selecting 'custom' delegates to async_step_custom_height."""
    flow, _, _ = _make_flow(
        config_flow_module,
        entry_data={"tank_size": "20lb_v"},
        medium_type="propane",
    )

    async def _fake_custom():
        return {"step": "custom_height"}

    flow.async_step_custom_height = _fake_custom

    result = asyncio.run(
        flow.async_step_tank_config(user_input={"tank_size": "custom"})
    )

    assert result == {"step": "custom_height"}


def test_options_flow_tank_config_no_input_shows_form(config_flow_module):
    """Without user input the propane tank selector is displayed."""
    flow, _, _ = _make_flow(
        config_flow_module,
        entry_data={"tank_size": "30lb_v"},
        medium_type="propane",
    )

    result = asyncio.run(flow.async_step_tank_config())

    assert result["step_id"] == "tank_config"
    tank_selector = _schema_value(result["data_schema"], "tank_size")
    assert "30lb_v" in tank_selector.config.options


def test_options_flow_tank_config_unknown_size_falls_back_to_default(
    config_flow_module,
):
    """An unrecognized persisted tank key silently falls back to the first preset."""
    flow, _, _ = _make_flow(
        config_flow_module,
        entry_data={"tank_size": "removed_legacy_key"},
        medium_type="propane",
    )

    result = asyncio.run(flow.async_step_tank_config())

    assert result["step_id"] == "tank_config"
    tank_selector = _schema_value(result["data_schema"], "tank_size")
    assert tank_selector.config.options[0] == "20lb_v"  # DEFAULT_TANK_SIZE


# ════════════════════════ async_step_ibc_tank_config ═════════════════════════


def test_options_flow_ibc_tank_config_preset_updates_entry_and_completes(
    config_flow_module,
):
    """Selecting an IBC preset updates the config entry and finishes the flow."""
    entry_data = {
        "tank_size": "ibc_275gal",
        "medium_type": "fresh_water",
        "custom_tank_height": 0,
        "tank_capacity": 0.0,
        "tank_capacity_unit": "gal",
    }
    flow, update_calls, reload_calls = _make_flow(
        config_flow_module,
        entry_data=entry_data,
        medium_type="fresh_water",
    )

    result = asyncio.run(
        flow.async_step_ibc_tank_config(user_input={"tank_size": "ibc_330gal"})
    )

    assert len(update_calls) == 1
    updated = update_calls[0]["data"]
    assert updated["tank_size"] == "ibc_330gal"
    assert updated["medium_type"] == "fresh_water"
    assert updated["custom_tank_height"] == 0
    assert updated["tank_capacity"] == 0.0

    assert reload_calls == ["test-entry-id"]
    assert result == {"title": "", "data": {}}


def test_options_flow_ibc_tank_config_custom_routes_to_custom_height(
    config_flow_module,
):
    """Selecting 'custom' from IBC flow delegates to async_step_custom_height."""
    flow, _, _ = _make_flow(
        config_flow_module,
        entry_data={"tank_size": "ibc_275gal"},
        medium_type="fresh_water",
    )

    async def _fake_custom():
        return {"step": "custom_height"}

    flow.async_step_custom_height = _fake_custom

    result = asyncio.run(
        flow.async_step_ibc_tank_config(user_input={"tank_size": "custom"})
    )

    assert result == {"step": "custom_height"}


def test_options_flow_ibc_tank_config_no_input_shows_form(config_flow_module):
    """Without user input the IBC tank selector is displayed."""
    flow, _, _ = _make_flow(
        config_flow_module,
        entry_data={"tank_size": "ibc_275gal"},
        medium_type="fresh_water",
    )

    result = asyncio.run(flow.async_step_ibc_tank_config())

    assert result["step_id"] == "ibc_tank_config"
    tank_selector = _schema_value(result["data_schema"], "tank_size")
    assert "ibc_275gal" in tank_selector.config.options
    assert "ibc_330gal" in tank_selector.config.options


def test_options_flow_ibc_tank_config_unknown_size_falls_back_to_default(
    config_flow_module,
):
    """An unrecognized IBC tank key falls back to DEFAULT_IBC_TANK_SIZE."""
    flow, _, _ = _make_flow(
        config_flow_module,
        entry_data={"tank_size": "no_such_ibc"},
        medium_type="waste_water",
    )

    result = asyncio.run(flow.async_step_ibc_tank_config())

    assert result["step_id"] == "ibc_tank_config"
    tank_selector = _schema_value(result["data_schema"], "tank_size")
    assert tank_selector.config.options[0] == "ibc_275gal"  # DEFAULT_IBC_TANK_SIZE


# ════════════════════════ async_step_custom_height ═══════════════════════════


def test_options_flow_custom_height_unit_change_rerenders_without_completing(
    config_flow_module,
):
    """Changing the capacity unit refreshes the form; no entry update occurs."""
    flow, update_calls, _ = _make_flow(
        config_flow_module,
        entry_data={},
        medium_type="propane",
    )
    flow._custom_capacity_unit = "gal"

    result = asyncio.run(
        flow.async_step_custom_height(
            user_input={
                "custom_tank_height": 500,
                "tank_capacity": 10.0,
                "tank_capacity_unit": "kg",
            }
        )
    )

    assert result["step_id"] == "custom_height"
    assert len(update_calls) == 0
    assert flow._custom_capacity_unit == "kg"


def test_options_flow_custom_height_invalid_capacity_returns_field_error(
    config_flow_module,
):
    """A non-numeric capacity value returns an inline field error."""
    flow, update_calls, _ = _make_flow(
        config_flow_module,
        entry_data={},
        medium_type="propane",
    )
    flow._custom_capacity_unit = "gal"

    result = asyncio.run(
        flow.async_step_custom_height(
            user_input={
                "custom_tank_height": 500,
                "tank_capacity": "not-a-number",
                "tank_capacity_unit": "gal",
            }
        )
    )

    assert result["step_id"] == "custom_height"
    assert result["errors"] == {"tank_capacity": "invalid_number"}
    assert len(update_calls) == 0


def test_options_flow_custom_height_invalid_height_returns_field_error(
    config_flow_module,
):
    """A non-numeric height value returns an inline field error."""
    flow, update_calls, _ = _make_flow(
        config_flow_module,
        entry_data={},
        medium_type="propane",
    )
    flow._custom_capacity_unit = "gal"

    result = asyncio.run(
        flow.async_step_custom_height(
            user_input={
                "custom_tank_height": "bad",
                "tank_capacity": 10.0,
                "tank_capacity_unit": "gal",
            }
        )
    )

    assert result["step_id"] == "custom_height"
    assert result["errors"] == {"custom_tank_height": "invalid_number"}
    assert len(update_calls) == 0


def test_options_flow_custom_height_valid_input_updates_entry_and_completes(
    config_flow_module,
):
    """Valid custom height/capacity updates the config entry and finishes the flow."""
    entry_data = {
        "medium_type": "propane",
        "tank_size": "custom",
        "custom_tank_height": 0,
        "tank_capacity": 0.0,
        "tank_capacity_unit": "gal",
    }
    flow, update_calls, reload_calls = _make_flow(
        config_flow_module,
        entry_data=entry_data,
        medium_type="propane",
    )
    flow._custom_capacity_unit = "gal"

    result = asyncio.run(
        flow.async_step_custom_height(
            user_input={
                "custom_tank_height": 750,
                "tank_capacity": 25.0,
                "tank_capacity_unit": "gal",
            }
        )
    )

    assert len(update_calls) == 1
    updated = update_calls[0]["data"]
    assert updated["tank_size"] == "custom"
    assert updated["custom_tank_height"] == 750
    assert updated["tank_capacity"] == 25.0
    assert updated["tank_capacity_unit"] == "gal"
    assert updated["medium_type"] == "propane"

    assert reload_calls == ["test-entry-id"]
    assert result == {"title": "", "data": {}}


def test_options_flow_custom_height_valid_input_kg_unit(config_flow_module):
    """Custom height with kg capacity unit is stored correctly."""
    entry_data = {
        "medium_type": "propane",
        "tank_size": "custom",
        "custom_tank_height": 0,
        "tank_capacity": 0.0,
        "tank_capacity_unit": "gal",
    }
    flow, update_calls, reload_calls = _make_flow(
        config_flow_module,
        entry_data=entry_data,
        medium_type="propane",
    )
    flow._custom_capacity_unit = "kg"

    result = asyncio.run(
        flow.async_step_custom_height(
            user_input={
                "custom_tank_height": 400,
                "tank_capacity": 11.0,
                "tank_capacity_unit": "kg",
            }
        )
    )

    updated = update_calls[0]["data"]
    assert updated["custom_tank_height"] == 400
    assert updated["tank_capacity"] == 11.0
    assert updated["tank_capacity_unit"] == "kg"
    assert reload_calls == ["test-entry-id"]
    assert result == {"title": "", "data": {}}


def test_options_flow_custom_height_no_input_shows_form_with_existing_values(
    config_flow_module,
):
    """Without user input the form is pre-populated from the config entry data."""
    entry_data = {
        "custom_tank_height": 800,
        "tank_capacity": 30.0,
        "tank_capacity_unit": "kg",
    }
    flow, _, _ = _make_flow(
        config_flow_module,
        entry_data=entry_data,
        medium_type="propane",
    )

    result = asyncio.run(flow.async_step_custom_height())

    assert result["step_id"] == "custom_height"
    # Unit should be loaded from config entry and stored on the flow
    assert flow._custom_capacity_unit == "kg"
    assert "data_schema" in result


def test_options_flow_custom_height_no_input_missing_entry_data_uses_defaults(
    config_flow_module,
):
    """Missing config entry keys fall back to their defaults gracefully."""
    flow, _, _ = _make_flow(
        config_flow_module,
        entry_data={},  # No custom height/capacity/unit stored yet
        medium_type="fresh_water",
    )

    result = asyncio.run(flow.async_step_custom_height())

    assert result["step_id"] == "custom_height"
    assert flow._custom_capacity_unit == "gal"  # DEFAULT_TANK_CAPACITY_UNIT
    assert "data_schema" in result
