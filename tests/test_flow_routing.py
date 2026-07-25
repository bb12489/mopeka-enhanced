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
    assert capacity_selector.config.unit_of_measurement is None


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
    assert capacity_selector.config.unit_of_measurement is None


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


def test_ibc_tank_config_top_mount_preset_routes_to_sensor_height(config_flow_module):
    """Top-mount + preset selection collects the sensor mount height first."""
    flow = config_flow_module.MopekaConfigFlow()
    flow._is_top_mount = True
    flow._medium_type = "air"
    flow.async_show_form = lambda **kwargs: kwargs

    result = asyncio.run(
        flow.async_step_ibc_tank_config(user_input={"tank_size": "ibc_275gal"})
    )

    assert result["step_id"] == "top_mount_height"
    assert flow._pending_tank_size == "ibc_275gal"


def test_ibc_tank_config_bottom_mount_preset_creates_entry_directly(
    config_flow_module,
):
    """Bottom-mount + preset selection is unaffected — creates the entry directly."""
    flow = config_flow_module.MopekaConfigFlow()
    flow._is_top_mount = False
    flow._medium_type = "fresh_water"

    calls: list[tuple] = []

    async def _fake_create(tank_size, height, capacity, unit, **kwargs):
        calls.append((tank_size, height, capacity, unit, kwargs))
        return {"step": "created"}

    flow._async_create_config_entry = _fake_create

    result = asyncio.run(
        flow.async_step_ibc_tank_config(user_input={"tank_size": "ibc_275gal"})
    )

    assert result == {"step": "created"}
    assert calls == [("ibc_275gal", 0, 0.0, "gal", {})]


def test_top_mount_height_creates_entry_with_sensor_height(config_flow_module):
    """Submitting the sensor height step creates the entry with it persisted."""
    flow = config_flow_module.MopekaConfigFlow()
    flow._pending_tank_size = "ibc_275gal"
    flow._is_top_mount = True
    flow._medium_type = "air"

    calls: list[tuple] = []

    async def _fake_create(tank_size, height, capacity, unit, **kwargs):
        calls.append((tank_size, height, capacity, unit, kwargs))
        return {"step": "created"}

    flow._async_create_config_entry = _fake_create

    result = asyncio.run(
        flow.async_step_top_mount_height(user_input={"top_mount_sensor_height": 1150})
    )

    assert result == {"step": "created"}
    assert calls == [("ibc_275gal", 0, 0.0, "gal", {"top_mount_sensor_height": 1150})]


def test_custom_height_top_mount_includes_sensor_height_field(config_flow_module):
    """The custom height form includes the sensor height field for top-mount devices."""
    flow = config_flow_module.MopekaConfigFlow()
    flow._medium_type = "air"
    flow._is_top_mount = True
    flow._custom_capacity_unit = "gal"
    flow.async_show_form = lambda **kwargs: kwargs

    result = asyncio.run(flow.async_step_custom_height())

    assert result["step_id"] == "custom_height"
    _schema_value(result["data_schema"], "top_mount_sensor_height")


def test_custom_height_bottom_mount_excludes_sensor_height_field(config_flow_module):
    """The custom height form omits the sensor height field for bottom-mount devices."""
    flow = config_flow_module.MopekaConfigFlow()
    flow._medium_type = "propane"
    flow._is_top_mount = False
    flow._custom_capacity_unit = "gal"
    flow.async_show_form = lambda **kwargs: kwargs

    result = asyncio.run(flow.async_step_custom_height())

    assert result["step_id"] == "custom_height"
    try:
        _schema_value(result["data_schema"], "top_mount_sensor_height")
    except AssertionError:
        pass
    else:
        raise AssertionError("top_mount_sensor_height should not be present")


def test_custom_height_invalid_sensor_height_returns_field_error(config_flow_module):
    """An invalid top-mount sensor height value returns a field error."""
    flow = config_flow_module.MopekaConfigFlow()
    flow._medium_type = "air"
    flow._is_top_mount = True
    flow._custom_capacity_unit = "gal"
    flow.async_show_form = lambda **kwargs: kwargs

    result = asyncio.run(
        flow.async_step_custom_height(
            user_input={
                "custom_tank_height": 1000,
                "top_mount_sensor_height": "bad-value",
                "tank_capacity": 10.0,
                "tank_capacity_unit": "gal",
            }
        )
    )

    assert result["step_id"] == "custom_height"
    assert result["errors"] == {"top_mount_sensor_height": "invalid_number"}


def test_reconfigure_ibc_tank_config_top_mount_preset_routes_to_sensor_height(
    config_flow_module,
):
    """Reconfigure: top-mount + preset selection routes to the sensor height step."""
    flow = config_flow_module.MopekaConfigFlow()
    flow._medium_type = "air"
    flow._get_reconfigure_entry = lambda: type(
        "Entry",
        (),
        {"data": {"tank_size": "ibc_275gal", "top_mount": True}},
    )()
    flow.async_show_form = lambda **kwargs: kwargs

    result = asyncio.run(
        flow.async_step_reconfigure_ibc_tank_config(
            user_input={"tank_size": "ibc_330gal"}
        )
    )

    assert result["step_id"] == "reconfigure_top_mount_height"
    assert flow._pending_tank_size == "ibc_330gal"


def test_reconfigure_top_mount_height_updates_entry(config_flow_module):
    """Submitting the reconfigure sensor height step updates the entry and reloads."""
    flow = config_flow_module.MopekaConfigFlow()
    flow._medium_type = "air"
    flow._pending_tank_size = "ibc_330gal"
    flow._get_reconfigure_entry = lambda: type(
        "Entry",
        (),
        {"data": {"tank_size": "ibc_275gal", "top_mount": True}},
    )()

    calls: list[dict] = []

    def _fake_update_reload_and_abort(entry, *, data_updates):
        calls.append(data_updates)
        return {"step": "done"}

    flow.async_update_reload_and_abort = _fake_update_reload_and_abort

    result = asyncio.run(
        flow.async_step_reconfigure_top_mount_height(
            user_input={"top_mount_sensor_height": 1150}
        )
    )

    assert result == {"step": "done"}
    assert calls[0]["tank_size"] == "ibc_330gal"
    assert calls[0]["top_mount_sensor_height"] == 1150
