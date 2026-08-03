from __future__ import annotations


def _schema_value(schema, target_key: str):
    for required_key, value in schema.schema.items():
        if (
            isinstance(required_key, tuple)
            and len(required_key) >= 2
            and required_key[1] == target_key
        ):
            return value
    raise AssertionError(f"Missing schema key: {target_key}")


def test_top_mount_sensor_detection(config_flow_module, stub_types):
    bleak = stub_types["BluetoothServiceInfoBleak"](
        address="AA:BB",
        manufacturer_data={89: bytes([0x0A])},
    )
    assert config_flow_module._is_top_mount_sensor(bleak) is True


def test_top_mount_sensor_detection_false_when_missing_data(
    config_flow_module, stub_types
):
    bleak = stub_types["BluetoothServiceInfoBleak"](
        address="AA:BB",
        manufacturer_data={},
    )
    assert config_flow_module._is_top_mount_sensor(bleak) is False


def test_top_mount_sensor_detection_true_for_pro_200b(config_flow_module, stub_types):
    bleak = stub_types["BluetoothServiceInfoBleak"](
        address="AA:BB",
        manufacturer_data={89: bytes([0x12])},
    )
    assert config_flow_module._is_top_mount_sensor(bleak) is True


def test_capacity_unit_selector_propane(config_flow_module):
    selector = config_flow_module._async_generate_capacity_unit_selector("propane")
    assert selector.config.options == ["gal", "kg"]


def test_capacity_unit_selector_non_propane(config_flow_module):
    selector = config_flow_module._async_generate_capacity_unit_selector("fresh_water")
    assert selector.config.options == ["gal", "l"]


def test_custom_schema_uses_kg_input_when_propane_kg_selected(config_flow_module):
    schema = config_flow_module._async_generate_custom_height_schema(
        medium_type="propane",
        tank_capacity=11.0,
        tank_capacity_unit="kg",
    )
    capacity_selector = _schema_value(schema, "tank_capacity")
    assert capacity_selector.config.unit_of_measurement is None


def test_custom_schema_uses_liters_input_when_non_propane_l_selected(
    config_flow_module,
):
    schema = config_flow_module._async_generate_custom_height_schema(
        medium_type="fresh_water",
        tank_capacity=200.0,
        tank_capacity_unit="l",
    )
    capacity_selector = _schema_value(schema, "tank_capacity")
    assert capacity_selector.config.unit_of_measurement is None


def test_custom_schema_defaults_to_gallons_for_invalid_unit(config_flow_module):
    schema = config_flow_module._async_generate_custom_height_schema(
        medium_type="fresh_water",
        tank_capacity=50.0,
        tank_capacity_unit="kg",
    )
    capacity_selector = _schema_value(schema, "tank_capacity")
    assert capacity_selector.config.unit_of_measurement is None


def test_format_medium_type(config_flow_module):
    medium = type("Dummy", (), {"name": "FRESH_WATER"})()
    assert config_flow_module.format_medium_type(medium) == "Fresh Water"


def test_parse_custom_height_values_top_mount_defaults_to_zero(config_flow_module):
    height, capacity, sensor_height, errors = (
        config_flow_module._parse_custom_height_values(
            {"custom_tank_height": 1000, "tank_capacity": 50.0},
            top_mount=True,
        )
    )
    assert (height, capacity, sensor_height, errors) == (1000, 50.0, 0, {})


def test_parse_custom_height_values_top_mount_parses_explicit_value(
    config_flow_module,
):
    height, capacity, sensor_height, errors = (
        config_flow_module._parse_custom_height_values(
            {
                "custom_tank_height": 1000,
                "tank_capacity": 50.0,
                "top_mount_sensor_height": 1150,
            },
            top_mount=True,
        )
    )
    assert (height, capacity, sensor_height, errors) == (1000, 50.0, 1150, {})


def test_parse_custom_height_values_top_mount_invalid_returns_error(
    config_flow_module,
):
    _height, _capacity, sensor_height, errors = (
        config_flow_module._parse_custom_height_values(
            {
                "custom_tank_height": 1000,
                "tank_capacity": 50.0,
                "top_mount_sensor_height": "bad",
            },
            top_mount=True,
        )
    )
    assert sensor_height is None
    assert errors == {"top_mount_sensor_height": "invalid_number"}


def test_parse_custom_height_values_bottom_mount_ignores_sensor_height(
    config_flow_module,
):
    # top_mount=False (default): sensor height is never parsed/validated, even
    # if present and invalid in user_input.
    _height, _capacity, sensor_height, errors = (
        config_flow_module._parse_custom_height_values(
            {
                "custom_tank_height": 1000,
                "tank_capacity": 50.0,
                "top_mount_sensor_height": "bad",
            }
        )
    )
    assert (sensor_height, errors) == (0, {})


def test_custom_schema_includes_sensor_height_field_when_top_mount(config_flow_module):
    schema = config_flow_module._async_generate_custom_height_schema(
        medium_type="air",
        top_mount=True,
    )
    _schema_value(schema, "top_mount_sensor_height")


def test_custom_schema_excludes_sensor_height_field_when_bottom_mount(
    config_flow_module,
):
    schema = config_flow_module._async_generate_custom_height_schema(
        medium_type="propane",
        top_mount=False,
    )
    try:
        _schema_value(schema, "top_mount_sensor_height")
    except AssertionError:
        pass
    else:
        raise AssertionError("top_mount_sensor_height should not be present")


def test_top_mount_height_schema_default(config_flow_module):
    schema = config_flow_module._async_generate_top_mount_height_schema()
    selector = _schema_value(schema, "top_mount_sensor_height")
    assert selector.config.min == 0
    assert selector.config.max == 5000
