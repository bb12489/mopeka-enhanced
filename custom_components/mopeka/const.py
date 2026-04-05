"""Constants for the Mopeka integration."""

from enum import StrEnum
from typing import Final

from mopeka_iot_ble import MediumType

DOMAIN = "mopeka"

CONF_CUSTOM_TANK_HEIGHT: Final = "custom_tank_height"
CONF_MEDIUM_TYPE: Final = "medium_type"
CONF_TANK_CAPACITY: Final = "tank_capacity"
CONF_TANK_SIZE: Final = "tank_size"
CONF_TOP_MOUNT: Final = "top_mount"

# Manufacturer ID used by all Mopeka BLE devices.
MOPEKA_MANUFACTURER_ID: Final = 89

# Model IDs (lower nibble of manufacturer data byte 0) for top-mount sensors.
# These sensors measure the air gap above the liquid surface, so fill %
# increases as the reading decreases.
TOP_MOUNT_MODEL_IDS: Final[frozenset[int]] = frozenset({0x0A, 0x0B})

DEFAULT_MEDIUM_TYPE: Final = MediumType.PROPANE.value
DEFAULT_CUSTOM_TANK_HEIGHT: Final = 0
DEFAULT_TANK_CAPACITY: Final = 0.0


class TankSize(StrEnum):
    """Predefined tank sizes matching the Mopeka app presets."""

    LB_20 = "20lb"
    LB_30 = "30lb"
    LB_40 = "40lb"
    LB_100 = "100lb"
    KG_6 = "6kg"
    KG_11 = "11kg"
    KG_14 = "14kg"
    GAL_100_H = "100gal_h"
    GAL_500_H = "500gal_h"
    GAL_1000_H = "1000gal_h"
    GAL_12_2_RV_H = "12_2gal_rv_h"
    GAL_16_RV_H = "16gal_rv_h"
    GAL_20_3_RV_H = "20_3gal_rv_h"
    GAL_29_3_RV_H = "29_3gal_rv_h"
    IBC_275 = "ibc_275gal"
    IBC_330 = "ibc_330gal"
    CUSTOM = "custom"


DEFAULT_TANK_SIZE: Final = TankSize.LB_20

# Ordered list of tank sizes shown in the propane preset selector.
PROPANE_TANK_SIZES: Final[list[TankSize]] = [
    TankSize.LB_20,
    TankSize.LB_30,
    TankSize.LB_40,
    TankSize.LB_100,
    TankSize.GAL_100_H,
    TankSize.GAL_500_H,
    TankSize.GAL_1000_H,
    TankSize.GAL_12_2_RV_H,
    TankSize.GAL_16_RV_H,
    TankSize.GAL_20_3_RV_H,
    TankSize.GAL_29_3_RV_H,
    TankSize.KG_6,
    TankSize.KG_11,
    TankSize.KG_14,
    TankSize.CUSTOM,
]

# Ordered list of tank sizes shown in the IBC tote preset selector (non-propane media).
IBC_TANK_SIZES: Final[list[TankSize]] = [
    TankSize.IBC_275,
    TankSize.IBC_330,
    TankSize.CUSTOM,
]

DEFAULT_IBC_TANK_SIZE: Final = TankSize.IBC_275

# Minimum readable fluid height in mm.  Accounts for the physical curvature at the
# bottom of the tank and the ultrasonic sensor's dead zone.
TANK_EMPTY_MM: Final = 38.1

# Propane-specific (empty_mm, full_mm) tank dimensions in millimeters.
# The mopeka_iot_ble library converts raw acoustic measurements to physical
# fluid-height mm using a temperature-dependent speed-of-sound polynomial chosen
# for the configured medium type.  These preset ranges represent what the library
# reports when CONF_MEDIUM_TYPE == "propane"; other media use different acoustic
# coefficients and therefore produce different mm values for the same physical
# fill level, making these ranges inapplicable.
#
# Vertical tank full heights are the maximum liquid column heights for standard
# US DOT propane cylinders.  Horizontal / RV ASME full heights are the inner
# diameter (the geometric maximum fluid height when the tank is on its side).
#
# Fill % = clamp((reading - empty_mm) / (full_mm - empty_mm) * 100, 0, 100)
# (horizontal tanks apply cylindrical cross-section geometry for volume accuracy).
#
# Only referenced when CONF_MEDIUM_TYPE == "propane".
TANK_SIZE_RANGES: Final[dict[str, tuple[float, float]]] = {
    TankSize.LB_20: (TANK_EMPTY_MM, 254.0),
    TankSize.LB_30: (TANK_EMPTY_MM, 381.0),
    TankSize.LB_40: (TANK_EMPTY_MM, 508.0),
    TankSize.LB_100: (TANK_EMPTY_MM, 813.0),
    TankSize.GAL_100_H: (TANK_EMPTY_MM, 600.7),
    TankSize.GAL_500_H: (TANK_EMPTY_MM, 939.8),
    TankSize.GAL_1000_H: (TANK_EMPTY_MM, 1025.7),
    TankSize.GAL_12_2_RV_H: (TANK_EMPTY_MM, 301.0),
    TankSize.GAL_16_RV_H: (TANK_EMPTY_MM, 346.7),
    TankSize.GAL_20_3_RV_H: (TANK_EMPTY_MM, 393.7),
    TankSize.GAL_29_3_RV_H: (TANK_EMPTY_MM, 369.6),
    TankSize.KG_6: (TANK_EMPTY_MM, 336.0),
    TankSize.KG_11: (TANK_EMPTY_MM, 366.0),
    TankSize.KG_14: (TANK_EMPTY_MM, 467.0),
}

# IBC tote tank dimensions in millimeters for non-propane media (bottom-mount and
# top-mount sensors).  Internal heights sourced from standard US IBC tote specs:
#   275 gal: 38.5 in (≈ 98 cm) → 980 mm
#   330 gal: 46 in   (≈ 114 cm) → 1140 mm
#
# For bottom-mount sensors: fill% = (reading - TANK_EMPTY_MM) / (height - TANK_EMPTY_MM)
# For top-mount sensors: the raw reading is air gap and is converted to fluid
# height in sensor.py as (height - air_gap) before fill% is calculated.
IBC_TANK_SIZE_RANGES: Final[dict[str, tuple[float, float]]] = {
    TankSize.IBC_275: (TANK_EMPTY_MM, 980.0),
    TankSize.IBC_330: (TANK_EMPTY_MM, 1140.0),
}

# Tank sizes that are mounted horizontally.  For these tanks the full_mm value
# is the internal diameter and the relationship between fluid height and fill
# volume is non-linear (circular cross-section geometry).
HORIZONTAL_TANK_SIZES: Final[frozenset[str]] = frozenset(
    {
        TankSize.GAL_100_H,
        TankSize.GAL_500_H,
        TankSize.GAL_1000_H,
        TankSize.GAL_12_2_RV_H,
        TankSize.GAL_16_RV_H,
        TankSize.GAL_20_3_RV_H,
        TankSize.GAL_29_3_RV_H,
    }
)

# Total usable capacity in gallons for each preset tank size.  Used to synthesize
# the "tank volume remaining" sensor.  For pound-rated propane cylinders the
# value is the liquid propane capacity at max fill (propane ≈ 4.236 lb/gal).
# For gallon-labelled and IBC presets the label value is used directly.
# Custom tanks supply their own capacity via CONF_TANK_CAPACITY.
TANK_SIZE_CAPACITIES: Final[dict[str, float]] = {
    TankSize.LB_20: 4.7,
    TankSize.LB_30: 7.1,
    TankSize.LB_40: 9.4,
    TankSize.LB_100: 23.6,
    TankSize.GAL_100_H: 100.0,
    TankSize.GAL_500_H: 500.0,
    TankSize.GAL_1000_H: 1000.0,
    TankSize.GAL_12_2_RV_H: 12.2,
    TankSize.GAL_16_RV_H: 16.0,
    TankSize.GAL_20_3_RV_H: 20.3,
    TankSize.GAL_29_3_RV_H: 29.3,
    TankSize.IBC_275: 275.0,
    TankSize.IBC_330: 330.0,
    TankSize.KG_6: 3.1,
    TankSize.KG_11: 5.7,
    TankSize.KG_14: 7.3,
}
