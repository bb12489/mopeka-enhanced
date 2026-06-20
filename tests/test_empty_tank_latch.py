"""Tests for the empty-tank quality latch in sensor.py."""

from __future__ import annotations

import pytest


def _build_update(stub_types, level_mm: float | None, quality_pct: int | None):
    """Return a SensorUpdate carrying a tank_level and reading_quality value.

    level_mm=None simulates a quality-0 packet where the library sets
    tank_level to None to signal an unusable reading.
    quality_pct=None omits the reading_quality key entirely.
    """
    device_id = "dev1"
    level_key = stub_types["DeviceKey"]("tank_level", device_id)
    level_value = stub_types["SensorValue"](native_value=level_mm, name=None)
    entity_values = {level_key: level_value}

    if quality_pct is not None:
        quality_key = stub_types["DeviceKey"]("reading_quality", device_id)
        quality_value = stub_types["SensorValue"](
            native_value=quality_pct, name="Reading quality"
        )
        entity_values[quality_key] = quality_value

    return stub_types["SensorUpdate"](
        entity_descriptions={},
        entity_values=entity_values,
        devices={device_id: {"name": "Test Device"}},
    )


# ---------------------------------------------------------------------------
# Latch engages (quality ≤ 33 % = 0–1 stars)
# ---------------------------------------------------------------------------


def test_latch_engages_on_low_quality_forces_zero(sensor_module, stub_types):
    """Level should be 0 % when quality is 1 star (33 %)."""
    converter = sensor_module.make_sensor_update_to_bluetooth_data_update(
        tank_range=(38.1, 600.0, False),
        top_mount=False,
        medium_type="propane",
        propane_preset="20lb_v",
        tank_capacity=None,
    )
    pct_key = stub_types["PassiveBluetoothEntityKey"]("tank_level_percent", "dev1")
    level_key = stub_types["PassiveBluetoothEntityKey"]("tank_level", "dev1")

    # Simulate a "bounce" reading: tank looks ~25 % full but quality = 1 star (33 %)
    update = converter(_build_update(stub_types, level_mm=200.0, quality_pct=33))

    assert update.entity_data[pct_key] == 0.0
    assert update.entity_data[level_key] == 38.1  # reset to empty_mm


def test_latch_engages_on_zero_quality(sensor_module, stub_types):
    """Level should be 0 % when quality is 0 stars (0 %)."""
    converter = sensor_module.make_sensor_update_to_bluetooth_data_update(
        tank_range=(38.1, 600.0, False),
        top_mount=False,
        medium_type="propane",
        propane_preset="20lb_v",
        tank_capacity=None,
    )
    pct_key = stub_types["PassiveBluetoothEntityKey"]("tank_level_percent", "dev1")

    # Library reports quality=0 → sets tank_level to None, but latch still fires
    update = converter(_build_update(stub_types, level_mm=None, quality_pct=0))

    assert update.entity_data[pct_key] == 0.0


# ---------------------------------------------------------------------------
# Latch releases (quality > 33 % = 2–3 stars)
# ---------------------------------------------------------------------------


def test_latch_not_engaged_on_good_quality(sensor_module, stub_types):
    """Normal level should be reported when quality is high (no latch)."""
    converter = sensor_module.make_sensor_update_to_bluetooth_data_update(
        tank_range=(38.1, 600.0, False),
        top_mount=False,
        medium_type="propane",
        propane_preset="20lb_v",
        tank_capacity=None,
    )
    pct_key = stub_types["PassiveBluetoothEntityKey"]("tank_level_percent", "dev1")

    # quality = 67 % = 2 stars → good reading, use actual level
    update = converter(_build_update(stub_types, level_mm=319.05, quality_pct=67))

    assert update.entity_data[pct_key] == pytest.approx(50.0, abs=1.0)


def test_latch_releases_after_quality_recovers(sensor_module, stub_types):
    """After engaging the latch, recovering quality should restore real readings."""
    converter = sensor_module.make_sensor_update_to_bluetooth_data_update(
        tank_range=(38.1, 600.0, False),
        top_mount=False,
        medium_type="propane",
        propane_preset="20lb_v",
        tank_capacity=None,
    )
    pct_key = stub_types["PassiveBluetoothEntityKey"]("tank_level_percent", "dev1")

    # First update: quality = 1 star → latch on
    converter(_build_update(stub_types, level_mm=200.0, quality_pct=33))

    # Second update: quality = 2 stars, tank refilled to ~50 %
    update = converter(_build_update(stub_types, level_mm=319.05, quality_pct=67))

    assert update.entity_data[pct_key] == pytest.approx(50.0, abs=1.0)


# ---------------------------------------------------------------------------
# Latch with volume sensor
# ---------------------------------------------------------------------------


def test_latch_zeroes_volume_sensor(sensor_module, stub_types):
    """Volume sensor must also read 0 when latch is active."""
    converter = sensor_module.make_sensor_update_to_bluetooth_data_update(
        tank_range=(38.1, 600.0, False),
        top_mount=False,
        medium_type="propane",
        propane_preset="20lb_v",
        tank_capacity=(4.7, "gal"),
    )
    vol_key = stub_types["PassiveBluetoothEntityKey"]("tank_volume", "dev1")

    update = converter(_build_update(stub_types, level_mm=200.0, quality_pct=33))

    assert update.entity_data[vol_key] == 0.0


# ---------------------------------------------------------------------------
# No quality key in update → latch state is unchanged (safe default)
# ---------------------------------------------------------------------------


def test_no_quality_key_does_not_change_latch(sensor_module, stub_types):
    """If reading_quality is absent the converter should not crash or change latch."""
    converter = sensor_module.make_sensor_update_to_bluetooth_data_update(
        tank_range=(38.1, 600.0, False),
        top_mount=False,
        medium_type="propane",
        propane_preset="20lb_v",
        tank_capacity=None,
    )
    pct_key = stub_types["PassiveBluetoothEntityKey"]("tank_level_percent", "dev1")

    # No quality key → latch stays False (initial state) → actual level reported
    update = converter(_build_update(stub_types, level_mm=319.05, quality_pct=None))

    assert update.entity_data[pct_key] == pytest.approx(50.0, abs=1.0)
