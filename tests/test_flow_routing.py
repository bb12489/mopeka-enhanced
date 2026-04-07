from __future__ import annotations

import asyncio


def _schema_value(schema, target_key: str):
    for required_key, value in schema.schema.items():
        if (
            isinstance(required_key, tuple)
            and len(required_key) >= 2
            and required_key[1] == target_key
        ):
            return value
    raise AssertionError(f"Missing schema key: {target_key}")


class _FakeDiscoveredDevice:
    title = "Mopeka"

    @staticmethod
    def get_device_name():
        return "Mopeka"


def test_bluetooth_confirm_top_mount_routes_to_ibc(config_flow_module, stub_types):
    flow = config_flow_module.MopekaConfigFlow()
    flow._discovered_device = _FakeDiscoveredDevice()
    flow._discovery_info = stub_types["BluetoothServiceInfoBleak"](
        address="AA:BB",
        manufacturer_data={89: bytes([0x0A])},
        name="TD40",
    )

    async def _fake_ibc_step():
        return {"step": "ibc"}

    flow.async_step_ibc_tank_config = _fake_ibc_step

    result = asyncio.run(flow.async_step_bluetooth_confirm())

    assert result == {"step": "ibc"}
    assert flow._is_top_mount is True
    assert flow._medium_type == "air"


def test_bluetooth_confirm_propane_routes_to_tank(config_flow_module, stub_types):
    flow = config_flow_module.MopekaConfigFlow()
    flow._discovered_device = _FakeDiscoveredDevice()
    flow._discovery_info = stub_types["BluetoothServiceInfoBleak"](
        address="AA:CC",
        manufacturer_data={89: bytes([0x01])},
        name="Std",
    )

    async def _fake_tank_step():
        return {"step": "tank"}

    flow.async_step_tank_config = _fake_tank_step

    result = asyncio.run(
        flow.async_step_bluetooth_confirm(user_input={"medium_type": "propane"})
    )

    assert result == {"step": "tank"}
    assert flow._medium_type == "propane"


def test_bluetooth_confirm_non_propane_routes_to_ibc(config_flow_module, stub_types):
    flow = config_flow_module.MopekaConfigFlow()
    flow._discovered_device = _FakeDiscoveredDevice()
    flow._discovery_info = stub_types["BluetoothServiceInfoBleak"](
        address="AA:DD",
        manufacturer_data={89: bytes([0x01])},
        name="Std",
    )

    async def _fake_ibc_step():
        return {"step": "ibc"}

    flow.async_step_ibc_tank_config = _fake_ibc_step

    result = asyncio.run(
        flow.async_step_bluetooth_confirm(user_input={"medium_type": "fresh_water"})
    )

    assert result == {"step": "ibc"}
    assert flow._medium_type == "fresh_water"


def test_custom_height_unit_change_refreshes_capacity_selector(config_flow_module):
    flow = config_flow_module.MopekaConfigFlow()
    flow._medium_type = "propane"
    flow._custom_capacity_unit = "gal"

    flow.async_show_form = lambda **kwargs: kwargs

    result = asyncio.run(
        flow.async_step_custom_height(
            user_input={
                "custom_tank_height": 1000,
                "tank_capacity": 10.0,
                "tank_capacity_unit": "kg",
            }
        )
    )

    assert result["step_id"] == "custom_height"
    capacity_selector = _schema_value(result["data_schema"], "tank_capacity")
    assert capacity_selector.config.unit_of_measurement == "kg"


def test_custom_height_unit_change_refreshes_capacity_selector_liters(
    config_flow_module,
):
    flow = config_flow_module.MopekaConfigFlow()
    flow._medium_type = "fresh_water"
    flow._custom_capacity_unit = "gal"

    flow.async_show_form = lambda **kwargs: kwargs

    result = asyncio.run(
        flow.async_step_custom_height(
            user_input={
                "custom_tank_height": 1000,
                "tank_capacity": 10.0,
                "tank_capacity_unit": "l",
            }
        )
    )

    assert result["step_id"] == "custom_height"
    capacity_selector = _schema_value(result["data_schema"], "tank_capacity")
    assert capacity_selector.config.unit_of_measurement == "L"


def test_reconfigure_tank_config_falls_back_for_unknown_legacy_propane_key(
    config_flow_module,
):
    flow = config_flow_module.MopekaConfigFlow()
    flow._get_reconfigure_entry = lambda: type(
        "Entry",
        (),
        {"data": {"tank_size": "removed_legacy_key"}},
    )()
    flow.async_show_form = lambda **kwargs: kwargs

    result = asyncio.run(flow.async_step_reconfigure_tank_config())

    tank_selector = _schema_value(result["data_schema"], "tank_size")
    assert result["step_id"] == "reconfigure_tank_config"
    assert tank_selector.config.options[0] == "20lb_v"


def test_custom_height_invalid_capacity_returns_field_error(config_flow_module):
    flow = config_flow_module.MopekaConfigFlow()
    flow._medium_type = "propane"
    flow._custom_capacity_unit = "gal"
    flow.async_show_form = lambda **kwargs: kwargs

    result = asyncio.run(
        flow.async_step_custom_height(
            user_input={
                "custom_tank_height": 1000,
                "tank_capacity": "bad-value",
                "tank_capacity_unit": "gal",
            }
        )
    )

    assert result["step_id"] == "custom_height"
    assert result["errors"] == {"tank_capacity": "invalid_number"}
