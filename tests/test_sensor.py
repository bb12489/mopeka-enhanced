"""Tests for the Mopeka sensor module."""

from __future__ import annotations

import math
from typing import Any

import pytest

from custom_components.mopeka.const import (
    CONF_CUSTOM_TANK_HEIGHT,
    CONF_MEDIUM_TYPE,
    CONF_TANK_CAPACITY,
    CONF_TANK_SIZE,
    CONF_TOP_MOUNT,
    DEFAULT_MEDIUM_TYPE,
    TANK_EMPTY_MM,
    TankSize,
)
from custom_components.mopeka.sensor import (
    _circular_segment_fraction,
    _get_tank_capacity_gallons,
    _get_tank_level_range,
)


class TestCircularSegmentFraction:
    """Tests for the horizontal-tank volume-fraction calculation."""

    def test_empty_tank_returns_zero(self) -> None:
        """Height of 0 mm should give a fraction of 0."""
        assert _circular_segment_fraction(0.0, 600.0) == 0.0

    def test_full_tank_returns_one(self) -> None:
        """Height equal to diameter should give a fraction of 1."""
        assert _circular_segment_fraction(600.0, 600.0) == 1.0

    def test_half_full_returns_half(self) -> None:
        """Height equal to radius (half diameter) should give exactly 0.5."""
        diameter = 600.0
        result = _circular_segment_fraction(diameter / 2, diameter)
        assert abs(result - 0.5) < 1e-9

    def test_negative_height_clamps_to_zero(self) -> None:
        """Negative height should be treated as empty."""
        assert _circular_segment_fraction(-10.0, 600.0) == 0.0

    def test_over_full_clamps_to_one(self) -> None:
        """Height greater than diameter should be treated as full."""
        assert _circular_segment_fraction(700.0, 600.0) == 1.0

    def test_quarter_full_less_than_half(self) -> None:
        """A quarter-diameter height gives less than 25% volume (non-linear)."""
        diameter = 600.0
        frac = _circular_segment_fraction(diameter / 4, diameter)
        # Due to circular cross-section, a quarter-height < 25% volume
        assert frac < 0.25

    def test_three_quarter_full_greater_than_75pct(self) -> None:
        """A three-quarter-diameter height gives more than 75% volume (non-linear)."""
        diameter = 600.0
        frac = _circular_segment_fraction(3 * diameter / 4, diameter)
        assert frac > 0.75

    def test_result_is_monotonically_increasing(self) -> None:
        """Fill fraction must increase as height increases."""
        diameter = 939.8  # 500-gal tank diameter
        heights = [i * diameter / 10 for i in range(11)]
        fractions = [_circular_segment_fraction(h, diameter) for h in heights]
        assert fractions == sorted(fractions)

    def test_uses_circular_segment_formula(self) -> None:
        """Verify the formula against a manual calculation."""
        r = 300.0
        h = 150.0  # quarter height
        expected = (
            r**2 * math.acos((r - h) / r) - (r - h) * math.sqrt(2 * r * h - h**2)
        ) / (math.pi * r**2)
        assert abs(_circular_segment_fraction(h, 2 * r) - expected) < 1e-12


class TestGetTankLevelRange:
    """Tests for the tank calibration range helper."""

    def test_no_tank_size_returns_none(self) -> None:
        """Entry without CONF_TANK_SIZE should return None."""
        assert _get_tank_level_range({}) is None

    def test_custom_zero_height_returns_none(self) -> None:
        """Custom tank with height 0 should return None (user opted out)."""
        data: dict[str, Any] = {
            CONF_TANK_SIZE: TankSize.CUSTOM,
            CONF_CUSTOM_TANK_HEIGHT: 0,
        }
        assert _get_tank_level_range(data) is None

    def test_custom_valid_height_vertical(self) -> None:
        """Custom bottom-mount tank returns (0, height, False)."""
        data: dict[str, Any] = {
            CONF_TANK_SIZE: TankSize.CUSTOM,
            CONF_CUSTOM_TANK_HEIGHT: 500,
        }
        result = _get_tank_level_range(data)
        assert result == (0.0, 500.0, False)

    def test_custom_top_mount_inverts_range(self) -> None:
        """Custom top-mount tank returns (height, 0.0, False) (inverted)."""
        data: dict[str, Any] = {
            CONF_TANK_SIZE: TankSize.CUSTOM,
            CONF_CUSTOM_TANK_HEIGHT: 500,
            CONF_TOP_MOUNT: True,
        }
        result = _get_tank_level_range(data)
        assert result == (500.0, 0.0, False)

    def test_propane_preset_with_propane_medium(self) -> None:
        """Standard propane preset returns a valid range for propane medium."""
        data: dict[str, Any] = {
            CONF_TANK_SIZE: TankSize.LB_40,
            CONF_MEDIUM_TYPE: DEFAULT_MEDIUM_TYPE,
        }
        result = _get_tank_level_range(data)
        assert result is not None
        empty_mm, full_mm, is_horizontal = result
        assert empty_mm == TANK_EMPTY_MM
        assert full_mm == 508.0
        assert is_horizontal is False

    def test_propane_preset_with_non_propane_medium_returns_none(self) -> None:
        """Propane preset with non-propane medium should return None."""
        data: dict[str, Any] = {
            CONF_TANK_SIZE: TankSize.LB_40,
            CONF_MEDIUM_TYPE: "water",
        }
        assert _get_tank_level_range(data) is None

    def test_horizontal_tank_flag_set(self) -> None:
        """Horizontal tank preset should set is_horizontal to True."""
        data: dict[str, Any] = {
            CONF_TANK_SIZE: TankSize.GAL_100_H,
            CONF_MEDIUM_TYPE: DEFAULT_MEDIUM_TYPE,
        }
        result = _get_tank_level_range(data)
        assert result is not None
        assert result[2] is True

    def test_vertical_propane_tank_flag_not_set(self) -> None:
        """Vertical propane preset should set is_horizontal to False."""
        data: dict[str, Any] = {
            CONF_TANK_SIZE: TankSize.LB_20,
            CONF_MEDIUM_TYPE: DEFAULT_MEDIUM_TYPE,
        }
        result = _get_tank_level_range(data)
        assert result is not None
        assert result[2] is False

    def test_ibc_preset_any_medium(self) -> None:
        """IBC preset is valid for any medium (not propane-specific)."""
        data: dict[str, Any] = {
            CONF_TANK_SIZE: TankSize.IBC_275,
            CONF_MEDIUM_TYPE: "water",
        }
        result = _get_tank_level_range(data)
        assert result is not None
        empty_mm, full_mm, is_horizontal = result
        assert empty_mm == TANK_EMPTY_MM
        assert full_mm == 980.0
        assert is_horizontal is False

    def test_ibc_top_mount_inverts_range(self) -> None:
        """IBC top-mount sensor should invert the range."""
        data: dict[str, Any] = {
            CONF_TANK_SIZE: TankSize.IBC_330,
            CONF_MEDIUM_TYPE: "water",
            CONF_TOP_MOUNT: True,
        }
        result = _get_tank_level_range(data)
        assert result is not None
        empty_mm, full_mm, is_horizontal = result
        # Inverted: empty becomes full_mm of the preset, full becomes 0
        assert empty_mm == 1140.0
        assert full_mm == 0.0
        assert is_horizontal is False

    def test_defaults_to_propane_medium_when_missing(self) -> None:
        """Entry without CONF_MEDIUM_TYPE should default to propane."""
        data: dict[str, Any] = {CONF_TANK_SIZE: TankSize.LB_30}
        result = _get_tank_level_range(data)
        assert result is not None
        assert result[0] == TANK_EMPTY_MM
        assert result[1] == 381.0


class TestGetTankCapacityGallons:
    """Tests for the tank capacity lookup helper."""

    def test_no_tank_size_returns_none(self) -> None:
        """Entry without CONF_TANK_SIZE should return None."""
        assert _get_tank_capacity_gallons({}) is None

    def test_preset_returns_known_capacity(self) -> None:
        """Known preset should return its documented gallon capacity."""
        data: dict[str, Any] = {CONF_TANK_SIZE: TankSize.LB_40}
        assert _get_tank_capacity_gallons(data) == pytest.approx(9.4)

    def test_ibc_275_capacity(self) -> None:
        """IBC 275-gal preset should return 275.0 gallons."""
        data: dict[str, Any] = {CONF_TANK_SIZE: TankSize.IBC_275}
        assert _get_tank_capacity_gallons(data) == pytest.approx(275.0)

    def test_custom_capacity_from_conf(self) -> None:
        """Custom tank uses CONF_TANK_CAPACITY value."""
        data: dict[str, Any] = {
            CONF_TANK_SIZE: TankSize.CUSTOM,
            CONF_TANK_CAPACITY: 120.5,
        }
        assert _get_tank_capacity_gallons(data) == pytest.approx(120.5)

    def test_custom_zero_capacity_returns_none(self) -> None:
        """Custom tank with capacity 0 should return None (disabled)."""
        data: dict[str, Any] = {
            CONF_TANK_SIZE: TankSize.CUSTOM,
            CONF_TANK_CAPACITY: 0.0,
        }
        assert _get_tank_capacity_gallons(data) is None

    def test_custom_missing_capacity_returns_none(self) -> None:
        """Custom tank without CONF_TANK_CAPACITY set returns None."""
        data: dict[str, Any] = {CONF_TANK_SIZE: TankSize.CUSTOM}
        assert _get_tank_capacity_gallons(data) is None

    def test_all_preset_capacities_positive(self) -> None:
        """All preset tank sizes should yield a positive capacity."""
        non_custom = [s for s in TankSize if s != TankSize.CUSTOM]
        for size in non_custom:
            data: dict[str, Any] = {CONF_TANK_SIZE: size}
            result = _get_tank_capacity_gallons(data)
            # Capacities are defined for all non-IBC presets and IBC presets too
            if result is not None:
                assert result > 0, f"Expected positive capacity for {size}"
