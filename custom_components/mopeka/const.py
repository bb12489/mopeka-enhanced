"""Constants for the Mopeka integration."""

from __future__ import annotations

from enum import StrEnum
from typing import Final

from mopeka_iot_ble import MediumType

DOMAIN = "mopeka"

CONF_CUSTOM_TANK_HEIGHT: Final = "custom_tank_height"
CONF_MEDIUM_TYPE: Final = "medium_type"
CONF_TANK_CAPACITY: Final = "tank_capacity"
CONF_TANK_CAPACITY_UNIT: Final = "tank_capacity_unit"
CONF_TANK_SIZE: Final = "tank_size"
CONF_TOP_MOUNT: Final = "top_mount"
# Height of the sensor's mounting point above the tank bottom (mm), for top-mount
# (TD40/TD200/Pro-200B) devices only. Mirrors the Mopeka app's "Overall Height" field, which
# is distinct from the "Max Water Level Height" (CONF_CUSTOM_TANK_HEIGHT): the sensor
# may be mounted above the true max-fill line, so raw air-gap readings never reach 0
# even at 100% full. 0 (default/unset) means "assume no headspace" for backward
# compatibility with entries created before this field existed.
CONF_TOP_MOUNT_SENSOR_HEIGHT: Final = "top_mount_sensor_height"

# Manufacturer ID used by all Mopeka BLE devices.
MOPEKA_MANUFACTURER_ID: Final = 89

# Model IDs (manufacturer data byte 0) for top-mount sensors. These sensors
# measure the air gap above the liquid surface, so fill % increases as the
# reading decreases. TD40/TD200 (0x0A/0x0B) fit in the lower nibble; Pro-200B
# (0x12) does not, so callers must match the full byte, not a masked nibble.
TOP_MOUNT_MODEL_IDS: Final[frozenset[int]] = frozenset({0x0A, 0x0B, 0x12})

DEFAULT_MEDIUM_TYPE: Final = MediumType.PROPANE.value
DEFAULT_CUSTOM_TANK_HEIGHT: Final = 0
DEFAULT_TOP_MOUNT_SENSOR_HEIGHT: Final = 0
DEFAULT_TANK_CAPACITY: Final = 0.0
CAPACITY_UNIT_GALLONS: Final = "gal"
CAPACITY_UNIT_KILOGRAMS: Final = "kg"
CAPACITY_UNIT_LITERS: Final = "l"
DEFAULT_TANK_CAPACITY_UNIT: Final = CAPACITY_UNIT_GALLONS


class TankSize(StrEnum):
    """Predefined tank sizes matching the Mopeka app presets."""

    LB_20 = "20lb_v"
    LB_30 = "30lb_v"
    LB_40 = "40lb_v"
    LB_100 = "100lb_v"
    # Flame King vertical portable cylinders popular with overlanders (YSN5LB / YSN10LB).
    LB_5_FK = "5lb_fk_v"
    LB_10_FK = "10lb_fk_v"
    KG_6 = "6kg_v"
    KG_11 = "11kg_v"
    KG_12 = "12kg_v"
    KG_14 = "14kg_v"
    KG_18 = "18kg_v"
    KG_48 = "48kg_v"
    # South Africa (za).  SA LPG is a 60% propane / 40% butane blend (propane_ratio=0.6
    # in the official Mopeka app).  The mopeka_iot_ble library has no butane medium type,
    # so these presets use MediumType.PROPANE acoustic coefficients — readings will be
    # slightly approximate but functionally useful.
    ZA_KG_3 = "3kg_za_v"
    ZA_KG_4_5 = "4_5kg_za_v"
    ZA_KG_5 = "5kg_za_v"
    ZA_KG_7 = "7kg_za_v"
    ZA_KG_9 = "9kg_za_v"
    ZA_KG_12 = "12kg_za_v"
    ZA_KG_14 = "14kg_za_v"
    ZA_KG_19 = "19kg_za_v"
    ZA_KG_48 = "48kg_za_v"
    # New Zealand (nz).  Shares tank geometry with the Mopeka app's combined
    # Australia/NZ region, but NZ LPG is a 60% propane / 40% butane blend
    # (propane_ratio=0.6 in the official app, same as South Africa) rather than
    # straight propane (ratio=1.0, used for Australia itself). The mopeka_iot_ble
    # library has no butane medium type, so these presets use MediumType.PROPANE
    # acoustic coefficients — readings will be slightly approximate but functionally
    # useful.
    NZ_KG_4_5 = "4_5kg_nz_v"
    NZ_KG_6 = "6kg_nz_v"
    NZ_KG_9 = "9kg_nz_v"
    NZ_KG_11 = "11kg_nz_v"
    NZ_KG_14 = "14kg_nz_v"
    NZ_KG_18 = "18kg_nz_v"
    GAL_120_V = "120gal_v"
    GAL_120_H = "120gal_h"
    GAL_150_H = "150gal_h"
    GAL_250_H = "250gal_h"
    GAL_500_H = "500gal_h"
    GAL_1000_H = "1000gal_h"
    GAL_5_9_ASME_FK = "5_9gal_asme_fk"
    GAL_6_9_ASME_MANCHESTER = "6_9gal_asme_manchester"
    GAL_7_9_ASME_GENERIC = "7_9gal_asme_generic"
    GAL_9_8_ASME_MANCHESTER = "9_8gal_asme_manchester"
    GAL_10_0_ASME_ARMEBE = "10_0gal_asme_armebe"
    GAL_11_3_ASME_MANCHESTER = "11_3gal_asme_manchester"
    GAL_11_9_ASME_ARMEBE = "11_9gal_asme_armebe"
    GAL_12_2_ASME_ARMEBE = "12_2gal_asme_armebe"
    GAL_12_2_ASME_FK = "12_2gal_asme_fk"
    GAL_14_1_ASME_ARMEBE = "14_1gal_asme_armebe"
    GAL_16_0_ASME_ARMEBE = "16_0gal_asme_armebe"
    GAL_16_0_ASME_FK = "16_0gal_asme_fk"
    GAL_17_6_ASME_MANCHESTER = "17_6gal_asme_manchester"
    GAL_20_3_ASME_ARMEBE = "20_3gal_asme_armebe"
    GAL_20_3_ASME_FK = "20_3gal_asme_fk"
    GAL_24_2_ASME_MANCHESTER = "24_2gal_asme_manchester"
    GAL_24_5_ASME_ARMEBE = "24_5gal_asme_armebe"
    GAL_29_3_ASME_ARMEBE = "29_3gal_asme_armebe"
    GAL_29_3_ASME_FK = "29_3gal_asme_fk"
    GAL_38_0_ASME_MANCHESTER = "38_0gal_asme_manchester"
    IBC_275 = "ibc_275gal"
    IBC_330 = "ibc_330gal"
    # Mexico (mx); Mopeka tank_types.js.
    MX_20KG_V = "20kg_mx_v"
    MX_30KG_V = "30kg_mx_v"
    MX_40KG_V = "40kg_mx_v"
    MX_45KG_V = "45kg_mx_v"
    MX_120L_H = "120l_mx_h"
    MX_180L_H = "180l_mx_h"
    MX_300L_H = "300l_mx_h"
    MX_500L_H = "500l_mx_h"
    # Legacy Latin America (es); Mopeka tank_types.js.
    ES_5KG_V = "5kg_es_v"
    # Chile (cl); Mopeka tank_types.js.
    CL_5KG_V = "5kg_cl_v"
    CL_11KG_V = "11kg_cl_v"
    CL_15KG_V = "15kg_cl_v"
    CL_45KG_V = "45kg_cl_v"
    CL_450L_V = "450l_cl_v"
    CL_470L_V = "470l_cl_v"
    CL_1000L_H = "1000l_cl_h"
    CL_2000L_H = "2000l_cl_h"
    CL_4000L_H = "4000l_cl_h"
    # Argentina (ar); Mopeka tank_types.js.
    AR_2KG_V = "2kg_ar_v"
    AR_3KG_V = "3kg_ar_v"
    AR_5KG_V = "5kg_ar_v"
    AR_10KG_V = "10kg_ar_v"
    AR_15KG_V = "15kg_ar_v"
    AR_30KG_V = "30kg_ar_v"
    AR_45KG_V = "45kg_ar_v"
    AR_500L_V = "500l_ar_v"
    AR_1000L_H = "1000l_ar_h"
    AR_2000L_H = "2000l_ar_h"
    AR_4000L_H = "4000l_ar_h"
    AR_7000L_H = "7000l_ar_h"
    # Brazil (br); Mopeka tank_types.js.
    BR_2KG_V = "2kg_br_v"
    BR_5KG_V = "5kg_br_v"
    BR_8KG_V = "8kg_br_v"
    BR_13KG_V = "13kg_br_v"
    BR_20KG_V = "20kg_br_v"
    BR_45KG_V = "45kg_br_v"
    BR_90KG_V = "90kg_br_v"
    BR_125KG_V = "125kg_br_v"
    BR_190KG_V = "190kg_br_v"
    BR_500KG_V = "500kg_br_v"
    BR_1000KG_V = "1000kg_br_v"
    BR_2000KG_V = "2000kg_br_v"
    BR_500KG_H = "500kg_br_h"
    BR_1000KG_H = "1000kg_br_h"
    BR_2000KG_H = "2000kg_br_h"
    # Colombia (co); Mopeka tank_types.js.
    CO_5KG_V = "5kg_co_v"
    CO_9KG_V = "9kg_co_v"
    CO_15KG_V = "15kg_co_v"
    CO_18KG_V = "18kg_co_v"
    CO_45KG_V = "45kg_co_v"
    CO_120GAL_V = "120gal_co_v"
    CO_250GAL_H = "250gal_co_h"
    CO_1000GAL_H = "1000gal_co_h"
    CO_2000GAL_H = "2000gal_co_h"
    # Ecuador (ec); Mopeka tank_types.js.
    EC_3KG_V = "3kg_ec_v"
    EC_5KG_V = "5kg_ec_v"
    EC_10KG_V = "10kg_ec_v"
    EC_15KG_V = "15kg_ec_v"
    EC_45KG_V = "45kg_ec_v"
    EC_450L_V = "450l_ec_v"
    EC_2000L_H = "2000l_ec_h"
    EC_4000L_H = "4000l_ec_h"
    EC_7000L_H = "7000l_ec_h"
    EC_7500L_H = "7500l_ec_h"
    EC_8000L_H = "8000l_ec_h"
    EC_100000L_H = "100000l_ec_h"
    # Uruguay (uy); Mopeka tank_types.js.
    UY_13KG_V = "13kg_uy_v"
    UY_45KG_V = "45kg_uy_v"
    UY_190KG_V = "190kg_uy_v"
    UY_1000KG_H = "1000kg_uy_h"
    UY_2000KG_H = "2000kg_uy_h"
    UY_3500KG_H = "3500kg_uy_h"
    # Peru (pe); Mopeka tank_types.js.
    PE_3KG_V = "3kg_pe_v"
    PE_5KG_V = "5kg_pe_v"
    PE_10KG_V = "10kg_pe_v"
    PE_15KG_V = "15kg_pe_v"
    PE_45KG_V = "45kg_pe_v"
    PE_120GAL_V = "120gal_pe_v"
    PE_120GAL_H = "120gal_pe_h"
    PE_250GAL_H = "250gal_pe_h"
    PE_500GAL_H = "500gal_pe_h"
    PE_1000GAL_H = "1000gal_pe_h"
    PE_2000GAL_H = "2000gal_pe_h"
    PE_4000GAL_H = "4000gal_pe_h"
    PE_6000GAL_H = "6000gal_pe_h"
    PE_8000GAL_H = "8000gal_pe_h"
    # Paraguay (py); Mopeka tank_types.js.
    PY_5KG_V = "5kg_py_v"
    PY_10KG_V = "10kg_py_v"
    PY_13KG_V = "13kg_py_v"
    PY_45KG_V = "45kg_py_v"
    PY_1000L_H = "1000l_py_h"
    PY_2500L_H = "2500l_py_h"
    PY_4000L_H = "4000l_py_h"
    PY_5000L_H = "5000l_py_h"
    PY_7000L_H = "7000l_py_h"
    PY_8000L_H = "8000l_py_h"
    PY_10000L_H = "10000l_py_h"
    PY_13000L_H = "13000l_py_h"
    PY_16000L_H = "16000l_py_h"
    PY_19000L_H = "19000l_py_h"
    # Israel (il); Mopeka tank_types.js.
    IL_5KG_V = "5kg_il_v"
    IL_12KG_V = "12kg_il_v"
    IL_48KG_V = "48kg_il_v"
    # South Korea (kr); Mopeka tank_types.js.
    KR_3KG_V = "3kg_kr_v"
    KR_5KG_V = "5kg_kr_v"
    KR_10KG_V = "10kg_kr_v"
    KR_20KG_V = "20kg_kr_v"
    # Philippines (ph); Mopeka tank_types.js.
    PH_2_7KG_V = "2_7kg_ph_v"
    PH_11KG_V = "11kg_ph_v"
    PH_22KG_V = "22kg_ph_v"
    PH_50KG_V = "50kg_ph_v"
    # Bangladesh (bn); Mopeka tank_types.js.
    BN_DISPENSER_20000L_H = "dispenser_20000l_bn_h"
    BN_20000L_H = "20000l_bn_h"

    CUSTOM = "custom"


DEFAULT_TANK_SIZE: Final = TankSize.LB_20

# Ordered list of tank sizes shown in the propane preset selector.
PROPANE_TANK_SIZES: Final[list[TankSize]] = [
    TankSize.LB_20,
    TankSize.LB_30,
    TankSize.LB_40,
    TankSize.LB_100,
    TankSize.LB_5_FK,
    TankSize.LB_10_FK,
    TankSize.GAL_120_V,
    TankSize.GAL_120_H,
    TankSize.GAL_150_H,
    TankSize.GAL_250_H,
    TankSize.GAL_500_H,
    TankSize.GAL_1000_H,
    TankSize.GAL_5_9_ASME_FK,
    TankSize.GAL_12_2_ASME_FK,
    TankSize.GAL_16_0_ASME_FK,
    TankSize.GAL_20_3_ASME_FK,
    TankSize.GAL_29_3_ASME_FK,
    TankSize.GAL_6_9_ASME_MANCHESTER,
    TankSize.GAL_9_8_ASME_MANCHESTER,
    TankSize.GAL_11_3_ASME_MANCHESTER,
    TankSize.GAL_17_6_ASME_MANCHESTER,
    TankSize.GAL_24_2_ASME_MANCHESTER,
    TankSize.GAL_38_0_ASME_MANCHESTER,
    TankSize.GAL_10_0_ASME_ARMEBE,
    TankSize.GAL_11_9_ASME_ARMEBE,
    TankSize.GAL_12_2_ASME_ARMEBE,
    TankSize.GAL_14_1_ASME_ARMEBE,
    TankSize.GAL_16_0_ASME_ARMEBE,
    TankSize.GAL_20_3_ASME_ARMEBE,
    TankSize.GAL_24_5_ASME_ARMEBE,
    TankSize.GAL_29_3_ASME_ARMEBE,
    TankSize.GAL_7_9_ASME_GENERIC,
    TankSize.KG_6,
    TankSize.KG_11,
    TankSize.KG_12,
    TankSize.KG_14,
    TankSize.KG_18,
    TankSize.KG_48,
    TankSize.ZA_KG_3,
    TankSize.ZA_KG_4_5,
    TankSize.ZA_KG_5,
    TankSize.ZA_KG_7,
    TankSize.ZA_KG_9,
    TankSize.ZA_KG_12,
    TankSize.ZA_KG_14,
    TankSize.ZA_KG_19,
    TankSize.ZA_KG_48,
    TankSize.NZ_KG_4_5,
    TankSize.NZ_KG_6,
    TankSize.NZ_KG_9,
    TankSize.NZ_KG_11,
    TankSize.NZ_KG_14,
    TankSize.NZ_KG_18,
    # Mexico (mx); Mopeka tank_types.js.
    TankSize.MX_20KG_V,
    TankSize.MX_30KG_V,
    TankSize.MX_40KG_V,
    TankSize.MX_45KG_V,
    TankSize.MX_120L_H,
    TankSize.MX_180L_H,
    TankSize.MX_300L_H,
    TankSize.MX_500L_H,
    # Legacy Latin America (es); Mopeka tank_types.js.
    TankSize.ES_5KG_V,
    # Chile (cl); Mopeka tank_types.js.
    TankSize.CL_5KG_V,
    TankSize.CL_11KG_V,
    TankSize.CL_15KG_V,
    TankSize.CL_45KG_V,
    TankSize.CL_450L_V,
    TankSize.CL_470L_V,
    TankSize.CL_1000L_H,
    TankSize.CL_2000L_H,
    TankSize.CL_4000L_H,
    # Argentina (ar); Mopeka tank_types.js.
    TankSize.AR_2KG_V,
    TankSize.AR_3KG_V,
    TankSize.AR_5KG_V,
    TankSize.AR_10KG_V,
    TankSize.AR_15KG_V,
    TankSize.AR_30KG_V,
    TankSize.AR_45KG_V,
    TankSize.AR_500L_V,
    TankSize.AR_1000L_H,
    TankSize.AR_2000L_H,
    TankSize.AR_4000L_H,
    TankSize.AR_7000L_H,
    # Brazil (br); Mopeka tank_types.js.
    TankSize.BR_2KG_V,
    TankSize.BR_5KG_V,
    TankSize.BR_8KG_V,
    TankSize.BR_13KG_V,
    TankSize.BR_20KG_V,
    TankSize.BR_45KG_V,
    TankSize.BR_90KG_V,
    TankSize.BR_125KG_V,
    TankSize.BR_190KG_V,
    TankSize.BR_500KG_V,
    TankSize.BR_1000KG_V,
    TankSize.BR_2000KG_V,
    TankSize.BR_500KG_H,
    TankSize.BR_1000KG_H,
    TankSize.BR_2000KG_H,
    # Colombia (co); Mopeka tank_types.js.
    TankSize.CO_5KG_V,
    TankSize.CO_9KG_V,
    TankSize.CO_15KG_V,
    TankSize.CO_18KG_V,
    TankSize.CO_45KG_V,
    TankSize.CO_120GAL_V,
    TankSize.CO_250GAL_H,
    TankSize.CO_1000GAL_H,
    TankSize.CO_2000GAL_H,
    # Ecuador (ec); Mopeka tank_types.js.
    TankSize.EC_3KG_V,
    TankSize.EC_5KG_V,
    TankSize.EC_10KG_V,
    TankSize.EC_15KG_V,
    TankSize.EC_45KG_V,
    TankSize.EC_450L_V,
    TankSize.EC_2000L_H,
    TankSize.EC_4000L_H,
    TankSize.EC_7000L_H,
    TankSize.EC_7500L_H,
    TankSize.EC_8000L_H,
    TankSize.EC_100000L_H,
    # Uruguay (uy); Mopeka tank_types.js.
    TankSize.UY_13KG_V,
    TankSize.UY_45KG_V,
    TankSize.UY_190KG_V,
    TankSize.UY_1000KG_H,
    TankSize.UY_2000KG_H,
    TankSize.UY_3500KG_H,
    # Peru (pe); Mopeka tank_types.js.
    TankSize.PE_3KG_V,
    TankSize.PE_5KG_V,
    TankSize.PE_10KG_V,
    TankSize.PE_15KG_V,
    TankSize.PE_45KG_V,
    TankSize.PE_120GAL_V,
    TankSize.PE_120GAL_H,
    TankSize.PE_250GAL_H,
    TankSize.PE_500GAL_H,
    TankSize.PE_1000GAL_H,
    TankSize.PE_2000GAL_H,
    TankSize.PE_4000GAL_H,
    TankSize.PE_6000GAL_H,
    TankSize.PE_8000GAL_H,
    # Paraguay (py); Mopeka tank_types.js.
    TankSize.PY_5KG_V,
    TankSize.PY_10KG_V,
    TankSize.PY_13KG_V,
    TankSize.PY_45KG_V,
    TankSize.PY_1000L_H,
    TankSize.PY_2500L_H,
    TankSize.PY_4000L_H,
    TankSize.PY_5000L_H,
    TankSize.PY_7000L_H,
    TankSize.PY_8000L_H,
    TankSize.PY_10000L_H,
    TankSize.PY_13000L_H,
    TankSize.PY_16000L_H,
    TankSize.PY_19000L_H,
    # Israel (il); Mopeka tank_types.js.
    TankSize.IL_5KG_V,
    TankSize.IL_12KG_V,
    TankSize.IL_48KG_V,
    # South Korea (kr); Mopeka tank_types.js.
    TankSize.KR_3KG_V,
    TankSize.KR_5KG_V,
    TankSize.KR_10KG_V,
    TankSize.KR_20KG_V,
    # Philippines (ph); Mopeka tank_types.js.
    TankSize.PH_2_7KG_V,
    TankSize.PH_11KG_V,
    TankSize.PH_22KG_V,
    TankSize.PH_50KG_V,
    # Bangladesh (bn); Mopeka tank_types.js.
    TankSize.BN_DISPENSER_20000L_H,
    TankSize.BN_20000L_H,
    TankSize.CUSTOM,
]

# Ordered list of tank sizes shown in the IBC tote preset selector (non-propane media).
IBC_TANK_SIZES: Final[list[TankSize]] = [
    TankSize.IBC_275,
    TankSize.IBC_330,
    TankSize.CUSTOM,
]

DEFAULT_IBC_TANK_SIZE: Final = TankSize.IBC_275

# Backward compatibility map for previously persisted tank preset keys.
LEGACY_TANK_SIZE_ALIASES: Final[dict[str, str]] = {
    "20lb": TankSize.LB_20,
    "30lb": TankSize.LB_30,
    "40lb": TankSize.LB_40,
    "100lb": TankSize.LB_100,
    "6kg": TankSize.KG_6,
    "11kg": TankSize.KG_11,
    "12kg": TankSize.KG_12,
    "14kg": TankSize.KG_14,
    "18kg": TankSize.KG_18,
    "48kg": TankSize.KG_48,
    "12_2gal_rv_h": TankSize.GAL_12_2_ASME_FK,
    "16gal_rv_h": TankSize.GAL_16_0_ASME_FK,
    "20_3gal_rv_h": TankSize.GAL_20_3_ASME_FK,
    "29_3gal_rv_h": TankSize.GAL_29_3_ASME_FK,
    "12_2gal_asme_h": TankSize.GAL_12_2_ASME_FK,
    "16gal_asme_h": TankSize.GAL_16_0_ASME_FK,
    "20_3gal_asme_h": TankSize.GAL_20_3_ASME_FK,
    "29_3gal_asme_h": TankSize.GAL_29_3_ASME_FK,
}


def normalize_tank_size(tank_size: str | None) -> str | None:
    """Return the canonical tank preset key, including legacy aliases."""
    if tank_size is None:
        return None
    return LEGACY_TANK_SIZE_ALIASES.get(tank_size, tank_size)


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
# Heights are sourced from the official Mopeka app tank_types.js (converted from
# meters, applying any 0.8 scaling factors used in that file).
#
# Vertical tank full heights are the maximum liquid column heights for standard
# propane cylinders.  Horizontal tank full heights are the inner diameter (the
# geometric maximum fluid height when the tank is on its side).
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
    # Flame King 5 lb (YSN5LB, 8.1 in dia x 12.8 in overall) and 10 lb (YSN10LB,
    # 9 in dia x 17.8 in overall).  These are not in the Mopeka app's tank_types.js,
    # so full heights are ESTIMATED liquid-column heights: propane volume at the
    # cylinder's rated capacity (lb / 4.236 lb per gal) = straight-wall cylinder
    # volume + one 2:1 elliptical bottom head, solved for height from the tank
    # bottom.  The same method reproduces the app's 20 lb (254 mm) and 40 lb
    # (508 mm) heights to within ~3%.  Treat as +/-10% until confirmed with a
    # measured full-tank reading.
    TankSize.LB_5_FK: (TANK_EMPTY_MM, 155.0),
    TankSize.LB_10_FK: (TANK_EMPTY_MM, 253.0),
    TankSize.GAL_120_V: (TANK_EMPTY_MM, 975.4),
    TankSize.GAL_120_H: (TANK_EMPTY_MM, 609.6),
    TankSize.GAL_150_H: (TANK_EMPTY_MM, 609.6),
    TankSize.GAL_250_H: (TANK_EMPTY_MM, 762.0),
    TankSize.GAL_500_H: (TANK_EMPTY_MM, 939.8),
    TankSize.GAL_1000_H: (TANK_EMPTY_MM, 1041.4),
    TankSize.GAL_5_9_ASME_FK: (TANK_EMPTY_MM, 197.0),
    TankSize.GAL_6_9_ASME_MANCHESTER: (TANK_EMPTY_MM, 248.0),
    TankSize.GAL_7_9_ASME_GENERIC: (TANK_EMPTY_MM, 248.0),
    TankSize.GAL_9_8_ASME_MANCHESTER: (TANK_EMPTY_MM, 298.0),
    TankSize.GAL_10_0_ASME_ARMEBE: (TANK_EMPTY_MM, 248.0),
    TankSize.GAL_11_3_ASME_MANCHESTER: (TANK_EMPTY_MM, 298.0),
    TankSize.GAL_11_9_ASME_ARMEBE: (TANK_EMPTY_MM, 358.0),
    TankSize.GAL_12_2_ASME_ARMEBE: (TANK_EMPTY_MM, 298.0),
    TankSize.GAL_12_2_ASME_FK: (TANK_EMPTY_MM, 306.0),
    TankSize.GAL_14_1_ASME_ARMEBE: (TANK_EMPTY_MM, 298.0),
    TankSize.GAL_16_0_ASME_ARMEBE: (TANK_EMPTY_MM, 298.0),
    TankSize.GAL_16_0_ASME_FK: (TANK_EMPTY_MM, 349.0),
    TankSize.GAL_17_6_ASME_MANCHESTER: (TANK_EMPTY_MM, 349.0),
    TankSize.GAL_20_3_ASME_ARMEBE: (TANK_EMPTY_MM, 400.0),
    TankSize.GAL_20_3_ASME_FK: (TANK_EMPTY_MM, 400.0),
    TankSize.GAL_24_2_ASME_MANCHESTER: (TANK_EMPTY_MM, 349.0),
    TankSize.GAL_24_5_ASME_ARMEBE: (TANK_EMPTY_MM, 400.0),
    TankSize.GAL_29_3_ASME_ARMEBE: (TANK_EMPTY_MM, 358.0),
    TankSize.GAL_29_3_ASME_FK: (TANK_EMPTY_MM, 372.0),
    TankSize.GAL_38_0_ASME_MANCHESTER: (TANK_EMPTY_MM, 400.0),
    TankSize.KG_6: (TANK_EMPTY_MM, 336.0),
    TankSize.KG_11: (TANK_EMPTY_MM, 366.0),
    TankSize.KG_12: (TANK_EMPTY_MM, 400.0),
    TankSize.KG_14: (TANK_EMPTY_MM, 467.0),
    TankSize.KG_18: (TANK_EMPTY_MM, 589.3),
    TankSize.KG_48: (TANK_EMPTY_MM, 1000.0),
    # South Africa (za) — heights sourced from tank_types.js za region (metres × 1000).
    # SA LPG is a 60/40 propane/butane blend; propane acoustic coefficients are used
    # since MediumType.BUTANE is not available in the library.
    TankSize.ZA_KG_3: (TANK_EMPTY_MM, 194.0),
    TankSize.ZA_KG_4_5: (TANK_EMPTY_MM, 220.0),
    TankSize.ZA_KG_5: (TANK_EMPTY_MM, 240.0),
    TankSize.ZA_KG_7: (TANK_EMPTY_MM, 267.0),
    TankSize.ZA_KG_9: (TANK_EMPTY_MM, 290.0),
    TankSize.ZA_KG_12: (TANK_EMPTY_MM, 378.0),
    TankSize.ZA_KG_14: (TANK_EMPTY_MM, 459.0),
    TankSize.ZA_KG_19: (TANK_EMPTY_MM, 490.0),
    TankSize.ZA_KG_48: (TANK_EMPTY_MM, 870.0),
    # New Zealand (nz) — heights sourced from tank_types.js au region (Australia/NZ
    # share tank geometry; metres × 1000, with the file's 0.8 scaling factor applied).
    TankSize.NZ_KG_4_5: (TANK_EMPTY_MM, 304.0),
    TankSize.NZ_KG_6: (TANK_EMPTY_MM, 336.0),
    TankSize.NZ_KG_9: (TANK_EMPTY_MM, 372.0),
    TankSize.NZ_KG_11: (TANK_EMPTY_MM, 366.0),
    TankSize.NZ_KG_14: (TANK_EMPTY_MM, 467.0),
    TankSize.NZ_KG_18: (TANK_EMPTY_MM, 589.3),
    # Mexico (mx); Mopeka tank_types.js.
    TankSize.MX_20KG_V: (TANK_EMPTY_MM, 606.0),
    TankSize.MX_30KG_V: (TANK_EMPTY_MM, 838.0),
    TankSize.MX_40KG_V: (TANK_EMPTY_MM, 1160.0),
    TankSize.MX_45KG_V: (TANK_EMPTY_MM, 1008.0),
    TankSize.MX_120L_H: (TANK_EMPTY_MM, 432.0),
    TankSize.MX_180L_H: (TANK_EMPTY_MM, 432.0),
    TankSize.MX_300L_H: (TANK_EMPTY_MM, 540.0),
    TankSize.MX_500L_H: (TANK_EMPTY_MM, 540.0),
    # Legacy Latin America (es); Mopeka tank_types.js.
    TankSize.ES_5KG_V: (TANK_EMPTY_MM, 246.0),
    # Chile (cl); Mopeka tank_types.js.
    TankSize.CL_5KG_V: (TANK_EMPTY_MM, 246.0),
    TankSize.CL_11KG_V: (TANK_EMPTY_MM, 305.0),
    TankSize.CL_15KG_V: (TANK_EMPTY_MM, 291.0),
    TankSize.CL_45KG_V: (TANK_EMPTY_MM, 763.0),
    TankSize.CL_450L_V: (TANK_EMPTY_MM, 940.0),
    TankSize.CL_470L_V: (TANK_EMPTY_MM, 1020.0),
    TankSize.CL_1000L_H: (TANK_EMPTY_MM, 830.0),
    TankSize.CL_2000L_H: (TANK_EMPTY_MM, 1020.0),
    TankSize.CL_4000L_H: (TANK_EMPTY_MM, 1020.0),
    # Argentina (ar); Mopeka tank_types.js.
    TankSize.AR_2KG_V: (TANK_EMPTY_MM, 140.0),
    TankSize.AR_3KG_V: (TANK_EMPTY_MM, 185.0),
    TankSize.AR_5KG_V: (TANK_EMPTY_MM, 224.0),
    TankSize.AR_10KG_V: (TANK_EMPTY_MM, 286.0),
    TankSize.AR_15KG_V: (TANK_EMPTY_MM, 415.0),
    TankSize.AR_30KG_V: (TANK_EMPTY_MM, 752.0),
    TankSize.AR_45KG_V: (TANK_EMPTY_MM, 752.0),
    TankSize.AR_500L_V: (TANK_EMPTY_MM, 1010.0),
    TankSize.AR_1000L_H: (TANK_EMPTY_MM, 830.0),
    TankSize.AR_2000L_H: (TANK_EMPTY_MM, 1170.0),
    TankSize.AR_4000L_H: (TANK_EMPTY_MM, 1170.0),
    TankSize.AR_7000L_H: (TANK_EMPTY_MM, 1160.0),
    # Brazil (br); Mopeka tank_types.js.
    TankSize.BR_2KG_V: (TANK_EMPTY_MM, 120.0),
    TankSize.BR_5KG_V: (TANK_EMPTY_MM, 154.0),
    TankSize.BR_8KG_V: (TANK_EMPTY_MM, 220.0),
    TankSize.BR_13KG_V: (TANK_EMPTY_MM, 227.5),
    TankSize.BR_20KG_V: (TANK_EMPTY_MM, 426.0),
    TankSize.BR_45KG_V: (TANK_EMPTY_MM, 742.0),
    TankSize.BR_90KG_V: (TANK_EMPTY_MM, 674.0),
    TankSize.BR_125KG_V: (TANK_EMPTY_MM, 900.0),
    TankSize.BR_190KG_V: (TANK_EMPTY_MM, 940.0),
    TankSize.BR_500KG_V: (TANK_EMPTY_MM, 1530.0),
    TankSize.BR_1000KG_V: (TANK_EMPTY_MM, 2700.0),
    TankSize.BR_2000KG_V: (TANK_EMPTY_MM, 4740.0),
    TankSize.BR_500KG_H: (TANK_EMPTY_MM, 780.0),
    TankSize.BR_1000KG_H: (TANK_EMPTY_MM, 1010.0),
    TankSize.BR_2000KG_H: (TANK_EMPTY_MM, 1010.0),
    # Colombia (co); Mopeka tank_types.js.
    TankSize.CO_5KG_V: (TANK_EMPTY_MM, 168.0),
    TankSize.CO_9KG_V: (TANK_EMPTY_MM, 250.0),
    TankSize.CO_15KG_V: (TANK_EMPTY_MM, 378.0),
    TankSize.CO_18KG_V: (TANK_EMPTY_MM, 437.0),
    TankSize.CO_45KG_V: (TANK_EMPTY_MM, 749.0),
    TankSize.CO_120GAL_V: (TANK_EMPTY_MM, 940.0),
    TankSize.CO_250GAL_H: (TANK_EMPTY_MM, 760.0),
    TankSize.CO_1000GAL_H: (TANK_EMPTY_MM, 1040.0),
    TankSize.CO_2000GAL_H: (TANK_EMPTY_MM, 1370.0),
    # Ecuador (ec); Mopeka tank_types.js.
    TankSize.EC_3KG_V: (TANK_EMPTY_MM, 143.0),
    TankSize.EC_5KG_V: (TANK_EMPTY_MM, 190.0),
    TankSize.EC_10KG_V: (TANK_EMPTY_MM, 247.0),
    TankSize.EC_15KG_V: (TANK_EMPTY_MM, 353.0),
    TankSize.EC_45KG_V: (TANK_EMPTY_MM, 722.0),
    TankSize.EC_450L_V: (TANK_EMPTY_MM, 1050.0),
    TankSize.EC_2000L_H: (TANK_EMPTY_MM, 1115.0),
    TankSize.EC_4000L_H: (TANK_EMPTY_MM, 992.0),
    TankSize.EC_7000L_H: (TANK_EMPTY_MM, 1010.0),
    TankSize.EC_7500L_H: (TANK_EMPTY_MM, 992.0),
    TankSize.EC_8000L_H: (TANK_EMPTY_MM, 1010.0),
    TankSize.EC_100000L_H: (TANK_EMPTY_MM, 1719.0),
    # Uruguay (uy); Mopeka tank_types.js.
    TankSize.UY_13KG_V: (TANK_EMPTY_MM, 266.0),
    TankSize.UY_45KG_V: (TANK_EMPTY_MM, 815.0),
    TankSize.UY_190KG_V: (TANK_EMPTY_MM, 1010.0),
    TankSize.UY_1000KG_H: (TANK_EMPTY_MM, 1070.0),
    TankSize.UY_2000KG_H: (TANK_EMPTY_MM, 1110.0),
    TankSize.UY_3500KG_H: (TANK_EMPTY_MM, 1170.0),
    # Peru (pe); Mopeka tank_types.js.
    TankSize.PE_3KG_V: (TANK_EMPTY_MM, 143.0),
    TankSize.PE_5KG_V: (TANK_EMPTY_MM, 213.0),
    TankSize.PE_10KG_V: (TANK_EMPTY_MM, 276.0),
    TankSize.PE_15KG_V: (TANK_EMPTY_MM, 276.0),
    TankSize.PE_45KG_V: (TANK_EMPTY_MM, 276.0),
    TankSize.PE_120GAL_V: (TANK_EMPTY_MM, 1000.0),
    TankSize.PE_120GAL_H: (TANK_EMPTY_MM, 580.0),
    TankSize.PE_250GAL_H: (TANK_EMPTY_MM, 770.0),
    TankSize.PE_500GAL_H: (TANK_EMPTY_MM, 880.0),
    TankSize.PE_1000GAL_H: (TANK_EMPTY_MM, 970.0),
    TankSize.PE_2000GAL_H: (TANK_EMPTY_MM, 1470.0),
    TankSize.PE_4000GAL_H: (TANK_EMPTY_MM, 1470.0),
    TankSize.PE_6000GAL_H: (TANK_EMPTY_MM, 1760.0),
    TankSize.PE_8000GAL_H: (TANK_EMPTY_MM, 1960.0),
    # Paraguay (py); Mopeka tank_types.js.
    TankSize.PY_5KG_V: (TANK_EMPTY_MM, 154.0),
    TankSize.PY_10KG_V: (TANK_EMPTY_MM, 276.0),
    TankSize.PY_13KG_V: (TANK_EMPTY_MM, 228.0),
    TankSize.PY_45KG_V: (TANK_EMPTY_MM, 742.0),
    TankSize.PY_1000L_H: (TANK_EMPTY_MM, 980.0),
    TankSize.PY_2500L_H: (TANK_EMPTY_MM, 1170.0),
    TankSize.PY_4000L_H: (TANK_EMPTY_MM, 1170.0),
    TankSize.PY_5000L_H: (TANK_EMPTY_MM, 1170.0),
    TankSize.PY_7000L_H: (TANK_EMPTY_MM, 1170.0),
    TankSize.PY_8000L_H: (TANK_EMPTY_MM, 1170.0),
    TankSize.PY_10000L_H: (TANK_EMPTY_MM, 1460.0),
    TankSize.PY_13000L_H: (TANK_EMPTY_MM, 1460.0),
    TankSize.PY_16000L_H: (TANK_EMPTY_MM, 1460.0),
    TankSize.PY_19000L_H: (TANK_EMPTY_MM, 1460.0),
    # Israel (il); Mopeka tank_types.js.
    TankSize.IL_5KG_V: (TANK_EMPTY_MM, 224.0),
    TankSize.IL_12KG_V: (TANK_EMPTY_MM, 320.0),
    TankSize.IL_48KG_V: (TANK_EMPTY_MM, 832.0),
    # South Korea (kr); Mopeka tank_types.js.
    TankSize.KR_3KG_V: (TANK_EMPTY_MM, 215.0),
    TankSize.KR_5KG_V: (TANK_EMPTY_MM, 235.0),
    TankSize.KR_10KG_V: (TANK_EMPTY_MM, 390.0),
    TankSize.KR_20KG_V: (TANK_EMPTY_MM, 690.0),
    # Philippines (ph); Mopeka tank_types.js.
    TankSize.PH_2_7KG_V: (TANK_EMPTY_MM, 192.0),
    TankSize.PH_11KG_V: (TANK_EMPTY_MM, 321.6),
    TankSize.PH_22KG_V: (TANK_EMPTY_MM, 599.2),
    TankSize.PH_50KG_V: (TANK_EMPTY_MM, 870.4),
    # Bangladesh (bn); Mopeka tank_types.js.
    TankSize.BN_DISPENSER_20000L_H: (TANK_EMPTY_MM, 1850.0),
    TankSize.BN_20000L_H: (TANK_EMPTY_MM, 2200.0),
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
        TankSize.GAL_120_H,
        TankSize.GAL_150_H,
        TankSize.GAL_250_H,
        TankSize.GAL_500_H,
        TankSize.GAL_1000_H,
        TankSize.GAL_5_9_ASME_FK,
        TankSize.GAL_6_9_ASME_MANCHESTER,
        TankSize.GAL_7_9_ASME_GENERIC,
        TankSize.GAL_9_8_ASME_MANCHESTER,
        TankSize.GAL_10_0_ASME_ARMEBE,
        TankSize.GAL_11_3_ASME_MANCHESTER,
        TankSize.GAL_11_9_ASME_ARMEBE,
        TankSize.GAL_12_2_ASME_ARMEBE,
        TankSize.GAL_12_2_ASME_FK,
        TankSize.GAL_14_1_ASME_ARMEBE,
        TankSize.GAL_16_0_ASME_ARMEBE,
        TankSize.GAL_16_0_ASME_FK,
        TankSize.GAL_17_6_ASME_MANCHESTER,
        TankSize.GAL_20_3_ASME_ARMEBE,
        TankSize.GAL_20_3_ASME_FK,
        TankSize.GAL_24_2_ASME_MANCHESTER,
        TankSize.GAL_24_5_ASME_ARMEBE,
        TankSize.GAL_29_3_ASME_ARMEBE,
        TankSize.GAL_29_3_ASME_FK,
        TankSize.GAL_38_0_ASME_MANCHESTER,
        # Mexico (mx); Mopeka tank_types.js.
        TankSize.MX_120L_H,
        TankSize.MX_180L_H,
        TankSize.MX_300L_H,
        TankSize.MX_500L_H,
        # Chile (cl); Mopeka tank_types.js.
        TankSize.CL_1000L_H,
        TankSize.CL_2000L_H,
        TankSize.CL_4000L_H,
        # Argentina (ar); Mopeka tank_types.js.
        TankSize.AR_1000L_H,
        TankSize.AR_2000L_H,
        TankSize.AR_4000L_H,
        TankSize.AR_7000L_H,
        # Brazil (br); Mopeka tank_types.js.
        TankSize.BR_500KG_H,
        TankSize.BR_1000KG_H,
        TankSize.BR_2000KG_H,
        # Colombia (co); Mopeka tank_types.js.
        TankSize.CO_250GAL_H,
        TankSize.CO_1000GAL_H,
        TankSize.CO_2000GAL_H,
        # Ecuador (ec); Mopeka tank_types.js.
        TankSize.EC_2000L_H,
        TankSize.EC_4000L_H,
        TankSize.EC_7000L_H,
        TankSize.EC_7500L_H,
        TankSize.EC_8000L_H,
        TankSize.EC_100000L_H,
        # Uruguay (uy); Mopeka tank_types.js.
        TankSize.UY_1000KG_H,
        TankSize.UY_2000KG_H,
        TankSize.UY_3500KG_H,
        # Peru (pe); Mopeka tank_types.js.
        TankSize.PE_120GAL_H,
        TankSize.PE_250GAL_H,
        TankSize.PE_500GAL_H,
        TankSize.PE_1000GAL_H,
        TankSize.PE_2000GAL_H,
        TankSize.PE_4000GAL_H,
        TankSize.PE_6000GAL_H,
        TankSize.PE_8000GAL_H,
        # Paraguay (py); Mopeka tank_types.js.
        TankSize.PY_1000L_H,
        TankSize.PY_2500L_H,
        TankSize.PY_4000L_H,
        TankSize.PY_5000L_H,
        TankSize.PY_7000L_H,
        TankSize.PY_8000L_H,
        TankSize.PY_10000L_H,
        TankSize.PY_13000L_H,
        TankSize.PY_16000L_H,
        TankSize.PY_19000L_H,
        # Bangladesh (bn); Mopeka tank_types.js.
        TankSize.BN_DISPENSER_20000L_H,
        TankSize.BN_20000L_H,
    }
)

# Total usable capacity in gallons for each preset tank size.  Used to synthesize
# the "tank volume remaining" sensor.  For pound-rated propane cylinders the
# value is the liquid propane capacity at max fill (propane ≈ 4.236 lb/gal).
# For gallon-labelled and IBC presets the label value is used directly.
# Kilogram- and liter-rated presets retain rounded gallon equivalents here;
# TANK_SIZE_RATED_KG and TANK_SIZE_RATED_LITERS provide their displayed units.
# Custom tanks supply their own capacity via CONF_TANK_CAPACITY.
TANK_SIZE_CAPACITIES: Final[dict[str, float]] = {
    TankSize.LB_20: 4.7,
    TankSize.LB_30: 7.1,
    TankSize.LB_40: 9.4,
    TankSize.LB_100: 23.6,
    # Flame King: 5 lb = 5 / 4.236; the 10 lb cylinder's true propane capacity is
    # 10.51 lb (2.48 gal), published by Flame King as 2.5 gal.
    TankSize.LB_5_FK: 1.2,
    TankSize.LB_10_FK: 2.5,
    TankSize.GAL_120_V: 120.0,
    TankSize.GAL_120_H: 120.0,
    TankSize.GAL_150_H: 150.0,
    TankSize.GAL_250_H: 250.0,
    TankSize.GAL_500_H: 500.0,
    TankSize.GAL_1000_H: 1000.0,
    TankSize.GAL_5_9_ASME_FK: 5.9,
    TankSize.GAL_6_9_ASME_MANCHESTER: 6.9,
    TankSize.GAL_7_9_ASME_GENERIC: 7.9,
    TankSize.GAL_9_8_ASME_MANCHESTER: 9.8,
    TankSize.GAL_10_0_ASME_ARMEBE: 10.0,
    TankSize.GAL_11_3_ASME_MANCHESTER: 11.3,
    TankSize.GAL_11_9_ASME_ARMEBE: 11.9,
    TankSize.GAL_12_2_ASME_ARMEBE: 12.2,
    TankSize.GAL_12_2_ASME_FK: 12.2,
    TankSize.GAL_14_1_ASME_ARMEBE: 14.1,
    TankSize.GAL_16_0_ASME_ARMEBE: 16.0,
    TankSize.GAL_16_0_ASME_FK: 16.0,
    TankSize.GAL_17_6_ASME_MANCHESTER: 17.6,
    TankSize.GAL_20_3_ASME_ARMEBE: 20.3,
    TankSize.GAL_20_3_ASME_FK: 20.3,
    TankSize.GAL_24_2_ASME_MANCHESTER: 24.2,
    TankSize.GAL_24_5_ASME_ARMEBE: 24.5,
    TankSize.GAL_29_3_ASME_ARMEBE: 29.3,
    TankSize.GAL_29_3_ASME_FK: 29.3,
    TankSize.GAL_38_0_ASME_MANCHESTER: 38.0,
    TankSize.IBC_275: 275.0,
    TankSize.IBC_330: 330.0,
    TankSize.KG_6: 3.1,
    TankSize.KG_11: 5.7,
    TankSize.KG_12: 6.2,
    TankSize.KG_14: 7.3,
    TankSize.KG_18: 9.4,
    TankSize.KG_48: 24.9,
    # South Africa (za) — capacities converted from kg using propane liquid density
    # (1.921 kg/gal) for consistency with other kg-rated presets.
    TankSize.ZA_KG_3: 1.6,
    TankSize.ZA_KG_4_5: 2.3,
    TankSize.ZA_KG_5: 2.6,
    TankSize.ZA_KG_7: 3.6,
    TankSize.ZA_KG_9: 4.7,
    TankSize.ZA_KG_12: 6.2,
    TankSize.ZA_KG_14: 7.3,
    TankSize.ZA_KG_19: 9.9,
    TankSize.ZA_KG_48: 24.9,
    # New Zealand (nz) — capacities converted from kg using propane liquid density
    # (1.921 kg/gal) for consistency with other kg-rated presets.
    TankSize.NZ_KG_4_5: 2.3,
    TankSize.NZ_KG_6: 3.1,
    TankSize.NZ_KG_9: 4.7,
    TankSize.NZ_KG_11: 5.7,
    TankSize.NZ_KG_14: 7.3,
    TankSize.NZ_KG_18: 9.4,
    # Mexico (mx); Mopeka tank_types.js.
    TankSize.MX_20KG_V: 10.4,
    TankSize.MX_30KG_V: 15.6,
    TankSize.MX_40KG_V: 20.8,
    TankSize.MX_45KG_V: 23.4,
    TankSize.MX_120L_H: 31.7,
    TankSize.MX_180L_H: 47.6,
    TankSize.MX_300L_H: 79.3,
    TankSize.MX_500L_H: 132.1,
    # Legacy Latin America (es); Mopeka tank_types.js.
    TankSize.ES_5KG_V: 2.6,
    # Chile (cl); Mopeka tank_types.js.
    TankSize.CL_5KG_V: 2.6,
    TankSize.CL_11KG_V: 5.7,
    TankSize.CL_15KG_V: 7.8,
    TankSize.CL_45KG_V: 23.4,
    TankSize.CL_450L_V: 118.9,
    TankSize.CL_470L_V: 124.2,
    TankSize.CL_1000L_H: 264.2,
    TankSize.CL_2000L_H: 528.3,
    TankSize.CL_4000L_H: 1056.7,
    # Argentina (ar); Mopeka tank_types.js.
    TankSize.AR_2KG_V: 1.0,
    TankSize.AR_3KG_V: 1.6,
    TankSize.AR_5KG_V: 2.6,
    TankSize.AR_10KG_V: 5.2,
    TankSize.AR_15KG_V: 7.8,
    TankSize.AR_30KG_V: 15.6,
    TankSize.AR_45KG_V: 23.4,
    TankSize.AR_500L_V: 132.1,
    TankSize.AR_1000L_H: 264.2,
    TankSize.AR_2000L_H: 528.3,
    TankSize.AR_4000L_H: 1056.7,
    TankSize.AR_7000L_H: 1849.2,
    # Brazil (br); Mopeka tank_types.js.
    TankSize.BR_2KG_V: 1.0,
    TankSize.BR_5KG_V: 2.6,
    TankSize.BR_8KG_V: 4.2,
    TankSize.BR_13KG_V: 6.8,
    TankSize.BR_20KG_V: 10.4,
    TankSize.BR_45KG_V: 23.4,
    TankSize.BR_90KG_V: 46.9,
    TankSize.BR_125KG_V: 65.1,
    TankSize.BR_190KG_V: 98.9,
    TankSize.BR_500KG_V: 260.3,
    TankSize.BR_1000KG_V: 520.6,
    TankSize.BR_2000KG_V: 1041.1,
    TankSize.BR_500KG_H: 260.3,
    TankSize.BR_1000KG_H: 520.6,
    TankSize.BR_2000KG_H: 1041.1,
    # Colombia (co); Mopeka tank_types.js.
    TankSize.CO_5KG_V: 2.6,
    TankSize.CO_9KG_V: 4.7,
    TankSize.CO_15KG_V: 7.8,
    TankSize.CO_18KG_V: 9.4,
    TankSize.CO_45KG_V: 23.4,
    TankSize.CO_120GAL_V: 120.0,
    TankSize.CO_250GAL_H: 250.0,
    TankSize.CO_1000GAL_H: 1000.0,
    TankSize.CO_2000GAL_H: 2000.0,
    # Ecuador (ec); Mopeka tank_types.js.
    TankSize.EC_3KG_V: 1.6,
    TankSize.EC_5KG_V: 2.6,
    TankSize.EC_10KG_V: 5.2,
    TankSize.EC_15KG_V: 7.8,
    TankSize.EC_45KG_V: 23.4,
    TankSize.EC_450L_V: 118.9,
    TankSize.EC_2000L_H: 528.3,
    TankSize.EC_4000L_H: 1056.7,
    TankSize.EC_7000L_H: 1849.2,
    TankSize.EC_7500L_H: 1981.3,
    TankSize.EC_8000L_H: 2113.4,
    TankSize.EC_100000L_H: 26417.2,
    # Uruguay (uy); Mopeka tank_types.js.
    TankSize.UY_13KG_V: 6.8,
    TankSize.UY_45KG_V: 23.4,
    TankSize.UY_190KG_V: 98.9,
    TankSize.UY_1000KG_H: 520.6,
    TankSize.UY_2000KG_H: 1041.1,
    TankSize.UY_3500KG_H: 1822.0,
    # Peru (pe); Mopeka tank_types.js.
    TankSize.PE_3KG_V: 1.6,
    TankSize.PE_5KG_V: 2.6,
    TankSize.PE_10KG_V: 5.2,
    TankSize.PE_15KG_V: 7.8,
    TankSize.PE_45KG_V: 23.4,
    TankSize.PE_120GAL_V: 120.0,
    TankSize.PE_120GAL_H: 120.0,
    TankSize.PE_250GAL_H: 250.0,
    TankSize.PE_500GAL_H: 500.0,
    TankSize.PE_1000GAL_H: 1000.0,
    TankSize.PE_2000GAL_H: 2000.0,
    TankSize.PE_4000GAL_H: 4000.0,
    TankSize.PE_6000GAL_H: 6000.0,
    TankSize.PE_8000GAL_H: 8000.0,
    # Paraguay (py); Mopeka tank_types.js.
    TankSize.PY_5KG_V: 2.6,
    TankSize.PY_10KG_V: 5.2,
    TankSize.PY_13KG_V: 6.8,
    TankSize.PY_45KG_V: 23.4,
    TankSize.PY_1000L_H: 264.2,
    TankSize.PY_2500L_H: 660.4,
    TankSize.PY_4000L_H: 1056.7,
    TankSize.PY_5000L_H: 1320.9,
    TankSize.PY_7000L_H: 1849.2,
    TankSize.PY_8000L_H: 2113.4,
    TankSize.PY_10000L_H: 2641.7,
    TankSize.PY_13000L_H: 3434.2,
    TankSize.PY_16000L_H: 4226.8,
    TankSize.PY_19000L_H: 5019.3,
    # Israel (il); Mopeka tank_types.js.
    TankSize.IL_5KG_V: 2.6,
    TankSize.IL_12KG_V: 6.2,
    TankSize.IL_48KG_V: 25.0,
    # South Korea (kr); Mopeka tank_types.js.
    TankSize.KR_3KG_V: 1.6,
    TankSize.KR_5KG_V: 2.6,
    TankSize.KR_10KG_V: 5.2,
    TankSize.KR_20KG_V: 10.4,
    # Philippines (ph); Mopeka tank_types.js.
    TankSize.PH_2_7KG_V: 1.4,
    TankSize.PH_11KG_V: 5.7,
    TankSize.PH_22KG_V: 11.5,
    TankSize.PH_50KG_V: 26.0,
    # Bangladesh (bn); Mopeka tank_types.js.
    TankSize.BN_DISPENSER_20000L_H: 5283.4,
    TankSize.BN_20000L_H: 5283.4,
}

# Kilogram-rated propane presets and their rated fill weight in kg.  These presets
# report the tank volume sensor in kilograms (rated capacity x fill percentage)
# instead of gallons, matching how the cylinders are sold and refilled.  The
# gallon value in TANK_SIZE_CAPACITIES is kept for other consumers.
TANK_SIZE_RATED_KG: Final[dict[str, float]] = {
    TankSize.KG_6: 6.0,
    TankSize.KG_11: 11.0,
    TankSize.KG_12: 12.0,
    TankSize.KG_14: 14.0,
    TankSize.KG_18: 18.0,
    TankSize.KG_48: 48.0,
    TankSize.ZA_KG_3: 3.0,
    TankSize.ZA_KG_4_5: 4.5,
    TankSize.ZA_KG_5: 5.0,
    TankSize.ZA_KG_7: 7.0,
    TankSize.ZA_KG_9: 9.0,
    TankSize.ZA_KG_12: 12.0,
    TankSize.ZA_KG_14: 14.0,
    TankSize.ZA_KG_19: 19.0,
    TankSize.ZA_KG_48: 48.0,
    TankSize.NZ_KG_4_5: 4.5,
    TankSize.NZ_KG_6: 6.0,
    TankSize.NZ_KG_9: 9.0,
    TankSize.NZ_KG_11: 11.0,
    TankSize.NZ_KG_14: 14.0,
    TankSize.NZ_KG_18: 18.0,
    # Mexico (mx); Mopeka tank_types.js.
    TankSize.MX_20KG_V: 20.0,
    TankSize.MX_30KG_V: 30.0,
    TankSize.MX_40KG_V: 40.0,
    TankSize.MX_45KG_V: 45.0,
    # Legacy Latin America (es); Mopeka tank_types.js.
    TankSize.ES_5KG_V: 5.0,
    # Chile (cl); Mopeka tank_types.js.
    TankSize.CL_5KG_V: 5.0,
    TankSize.CL_11KG_V: 11.0,
    TankSize.CL_15KG_V: 15.0,
    TankSize.CL_45KG_V: 45.0,
    # Argentina (ar); Mopeka tank_types.js.
    TankSize.AR_2KG_V: 2.0,
    TankSize.AR_3KG_V: 3.0,
    TankSize.AR_5KG_V: 5.0,
    TankSize.AR_10KG_V: 10.0,
    TankSize.AR_15KG_V: 15.0,
    TankSize.AR_30KG_V: 30.0,
    TankSize.AR_45KG_V: 45.0,
    # Brazil (br); Mopeka tank_types.js.
    TankSize.BR_2KG_V: 2.0,
    TankSize.BR_5KG_V: 5.0,
    TankSize.BR_8KG_V: 8.0,
    TankSize.BR_13KG_V: 13.0,
    TankSize.BR_20KG_V: 20.0,
    TankSize.BR_45KG_V: 45.0,
    TankSize.BR_90KG_V: 90.0,
    TankSize.BR_125KG_V: 125.0,
    TankSize.BR_190KG_V: 190.0,
    TankSize.BR_500KG_V: 500.0,
    TankSize.BR_1000KG_V: 1000.0,
    TankSize.BR_2000KG_V: 2000.0,
    TankSize.BR_500KG_H: 500.0,
    TankSize.BR_1000KG_H: 1000.0,
    TankSize.BR_2000KG_H: 2000.0,
    # Colombia (co); Mopeka tank_types.js.
    TankSize.CO_5KG_V: 5.0,
    TankSize.CO_9KG_V: 9.0,
    TankSize.CO_15KG_V: 15.0,
    TankSize.CO_18KG_V: 18.0,
    TankSize.CO_45KG_V: 45.0,
    # Ecuador (ec); Mopeka tank_types.js.
    TankSize.EC_3KG_V: 3.0,
    TankSize.EC_5KG_V: 5.0,
    TankSize.EC_10KG_V: 10.0,
    TankSize.EC_15KG_V: 15.0,
    TankSize.EC_45KG_V: 45.0,
    # Uruguay (uy); Mopeka tank_types.js.
    TankSize.UY_13KG_V: 13.0,
    TankSize.UY_45KG_V: 45.0,
    TankSize.UY_190KG_V: 190.0,
    TankSize.UY_1000KG_H: 1000.0,
    TankSize.UY_2000KG_H: 2000.0,
    TankSize.UY_3500KG_H: 3500.0,
    # Peru (pe); Mopeka tank_types.js.
    TankSize.PE_3KG_V: 3.0,
    TankSize.PE_5KG_V: 5.0,
    TankSize.PE_10KG_V: 10.0,
    TankSize.PE_15KG_V: 15.0,
    TankSize.PE_45KG_V: 45.0,
    # Paraguay (py); Mopeka tank_types.js.
    TankSize.PY_5KG_V: 5.0,
    TankSize.PY_10KG_V: 10.0,
    TankSize.PY_13KG_V: 13.0,
    TankSize.PY_45KG_V: 45.0,
    # Israel (il); Mopeka tank_types.js.
    TankSize.IL_5KG_V: 5.0,
    TankSize.IL_12KG_V: 12.0,
    TankSize.IL_48KG_V: 48.0,
    # South Korea (kr); Mopeka tank_types.js.
    TankSize.KR_3KG_V: 3.0,
    TankSize.KR_5KG_V: 5.0,
    TankSize.KR_10KG_V: 10.0,
    TankSize.KR_20KG_V: 20.0,
    # Philippines (ph); Mopeka tank_types.js.
    TankSize.PH_2_7KG_V: 2.7,
    TankSize.PH_11KG_V: 11.0,
    TankSize.PH_22KG_V: 22.0,
    TankSize.PH_50KG_V: 50.0,
}

# Liter-rated propane presets report remaining volume in liters.
# TANK_SIZE_CAPACITIES retains gallon equivalents for consistency with other presets.
TANK_SIZE_RATED_LITERS: Final[dict[str, float]] = {
    # Mexico (mx); Mopeka tank_types.js.
    TankSize.MX_120L_H: 120.0,
    TankSize.MX_180L_H: 180.0,
    TankSize.MX_300L_H: 300.0,
    TankSize.MX_500L_H: 500.0,
    # Chile (cl); Mopeka tank_types.js.
    TankSize.CL_450L_V: 450.0,
    TankSize.CL_470L_V: 470.0,
    TankSize.CL_1000L_H: 1000.0,
    TankSize.CL_2000L_H: 2000.0,
    TankSize.CL_4000L_H: 4000.0,
    # Argentina (ar); Mopeka tank_types.js.
    TankSize.AR_500L_V: 500.0,
    TankSize.AR_1000L_H: 1000.0,
    TankSize.AR_2000L_H: 2000.0,
    TankSize.AR_4000L_H: 4000.0,
    TankSize.AR_7000L_H: 7000.0,
    # Ecuador (ec); Mopeka tank_types.js.
    TankSize.EC_450L_V: 450.0,
    TankSize.EC_2000L_H: 2000.0,
    TankSize.EC_4000L_H: 4000.0,
    TankSize.EC_7000L_H: 7000.0,
    TankSize.EC_7500L_H: 7500.0,
    TankSize.EC_8000L_H: 8000.0,
    TankSize.EC_100000L_H: 100000.0,
    # Paraguay (py); Mopeka tank_types.js.
    TankSize.PY_1000L_H: 1000.0,
    TankSize.PY_2500L_H: 2500.0,
    TankSize.PY_4000L_H: 4000.0,
    TankSize.PY_5000L_H: 5000.0,
    TankSize.PY_7000L_H: 7000.0,
    TankSize.PY_8000L_H: 8000.0,
    TankSize.PY_10000L_H: 10000.0,
    TankSize.PY_13000L_H: 13000.0,
    TankSize.PY_16000L_H: 16000.0,
    TankSize.PY_19000L_H: 19000.0,
    # Bangladesh (bn); Mopeka tank_types.js.
    TankSize.BN_DISPENSER_20000L_H: 20000.0,
    TankSize.BN_20000L_H: 20000.0,
}
