"""Top-mount detection and reversible manual configuration."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace


def _schema_default(schema, key: str):
    for marker in schema.schema:
        if isinstance(marker, tuple) and marker[1] == key:
            return marker[2]
    raise AssertionError(f"Missing schema key: {key}")


def _flow_entry(data: dict, unique_id: str = "AA:BB") -> SimpleNamespace:
    return SimpleNamespace(data=data, unique_id=unique_id)


def test_legacy_offline_entry_can_uncheck_top_mount(config_flow_module):
    """Existing manual entries remain selected but can return to bottom mount."""
    flow = config_flow_module.MopekaConfigFlow()
    flow.hass = object()
    flow._get_reconfigure_entry = lambda: _flow_entry(
        {"top_mount": True, "medium_type": "air"}
    )
    flow.async_show_form = lambda **kwargs: kwargs

    form = asyncio.run(flow.async_step_reconfigure())
    assert form["step_id"] == "reconfigure"
    assert _schema_default(form["data_schema"], "top_mount") is True

    async def _tank_step():
        return {"step": "propane_tank"}

    flow.async_step_reconfigure_tank_config = _tank_step
    result = asyncio.run(
        flow.async_step_reconfigure(
            user_input={"top_mount": False, "medium_type": "propane"}
        )
    )
    assert result == {"step": "propane_tank"}
    assert flow._is_top_mount is False
    assert flow._auto_top_mount is False


def test_auto_detected_entry_stays_locked(config_flow_module):
    flow = config_flow_module.MopekaConfigFlow()
    flow.hass = object()
    flow._get_reconfigure_entry = lambda: _flow_entry(
        {"top_mount": True, "top_mount_auto": True, "medium_type": "air"}
    )

    async def _ibc_step():
        return {"step": "ibc"}

    flow.async_step_reconfigure_ibc_tank_config = _ibc_step
    result = asyncio.run(flow.async_step_reconfigure())
    assert result == {"step": "ibc"}
    assert flow._auto_top_mount is True
    assert flow._is_top_mount is True


def test_legacy_online_hardware_is_identified(
    config_flow_module, stub_types, monkeypatch
):
    info = stub_types["BluetoothServiceInfoBleak"](
        address="AA:BB", manufacturer_data={89: bytes([0x0A])}
    )
    monkeypatch.setattr(
        config_flow_module,
        "async_last_service_info",
        lambda _hass, _address, connectable=False: info,
    )
    entry = _flow_entry({"top_mount": True})
    assert config_flow_module._is_auto_top_mount_entry(object(), entry) is True


def test_options_legacy_offline_entry_can_uncheck_top_mount(config_flow_module):
    flow = config_flow_module.MopekaOptionsFlow()
    flow.hass = object()
    flow.config_entry = _flow_entry({"top_mount": True, "medium_type": "air"})
    flow.async_show_form = lambda **kwargs: kwargs

    form = asyncio.run(flow.async_step_init())
    assert form["step_id"] == "init"
    assert _schema_default(form["data_schema"], "top_mount") is True

    async def _tank_step():
        return {"step": "propane_tank"}

    flow.async_step_tank_config = _tank_step
    result = asyncio.run(
        flow.async_step_init(user_input={"top_mount": False, "medium_type": "propane"})
    )
    assert result == {"step": "propane_tank"}
    assert flow._is_top_mount is False


def test_options_save_clears_manual_top_mount(config_flow_module):
    flow = config_flow_module.MopekaOptionsFlow()
    entry = _flow_entry(
        {"top_mount": True, "medium_type": "air", "top_mount_sensor_height": 1100}
    )
    updated: list[dict] = []
    flow.config_entry = entry
    flow.hass = SimpleNamespace(
        config_entries=SimpleNamespace(
            async_update_entry=lambda _entry, *, data: updated.append(data)
        )
    )
    flow.async_create_entry = lambda **kwargs: kwargs
    flow._medium_type = "propane"

    asyncio.run(flow.async_step_tank_config(user_input={"tank_size": "20lb_v"}))
    assert updated[0]["top_mount"] is False
    assert updated[0]["top_mount_auto"] is False
    assert updated[0]["top_mount_sensor_height"] == 0


def test_new_hardware_entry_persists_auto_marker(config_flow_module, stub_types):
    flow = config_flow_module.MopekaConfigFlow()
    flow._discovered_device = SimpleNamespace(
        title="TD40", get_device_name=lambda: "TD40"
    )
    flow._discovery_info = stub_types["BluetoothServiceInfoBleak"](
        address="AA:BB", manufacturer_data={89: bytes([0x0A])}
    )

    async def _ibc_step():
        return {"step": "ibc"}

    flow.async_step_ibc_tank_config = _ibc_step
    asyncio.run(flow.async_step_bluetooth_confirm())
    flow.async_create_entry = lambda **kwargs: kwargs
    result = asyncio.run(flow._async_create_config_entry("ibc_275gal", 0))
    assert result["data"]["top_mount"] is True
    assert result["data"]["top_mount_auto"] is True
