from __future__ import annotations

from dataclasses import dataclass
import enum
from enum import Enum
import importlib.util
from pathlib import Path
import re
import sys
import types

import pytest


@dataclass(frozen=True)
class _DeviceKey:
    key: str
    device_id: str


@dataclass
class _SensorValue:
    native_value: float | int | str | None
    name: str | None = None


@dataclass
class _SensorUpdate:
    entity_descriptions: dict
    entity_values: dict
    devices: dict


@dataclass(frozen=True)
class _PassiveBluetoothEntityKey:
    key: str
    device_id: str


@dataclass
class _PassiveBluetoothDataUpdate:
    devices: dict
    entity_descriptions: dict
    entity_data: dict
    entity_names: dict


class _PassiveBluetoothDataProcessor:
    def __class_getitem__(cls, _item):
        return cls

    def __init__(self, update_method):
        self.update_method = update_method


class _PassiveBluetoothProcessorEntity:
    def __class_getitem__(cls, _item):
        return cls


class _PassiveBluetoothProcessorCoordinator:
    def __init__(self, hass, logger, address, mode, update_method):
        self.hass = hass
        self.logger = logger
        self.address = address
        self.mode = mode
        self.update_method = update_method

    def async_start(self):
        return lambda: None

    def async_register_processor(self, _processor):
        return lambda: None


class _BluetoothScanningMode:
    PASSIVE = "passive"


@dataclass
class _BluetoothServiceInfoBleak:
    address: str
    manufacturer_data: dict[int, bytes]
    name: str = "Mopeka"


class _ConfigEntry:
    def __class_getitem__(cls, _item):
        return cls


class _ConfigFlow:
    def __init_subclass__(cls, **_kwargs):
        return


class _OptionsFlow:
    pass


class _Platform:
    SENSOR = "sensor"


def _callback(func):
    return func


class _NumberSelectorMode:
    BOX = "box"


class _SelectSelectorMode:
    DROPDOWN = "dropdown"


@dataclass
class _NumberSelectorConfig:
    min: float
    max: float
    step: float
    unit_of_measurement: str
    mode: str


@dataclass
class _SelectSelectorConfig:
    options: list[str]
    mode: str
    translation_key: str


class _NumberSelector:
    def __init__(self, config):
        self.config = config


class _SelectSelector:
    def __init__(self, config):
        self.config = config


class _VolSchema:
    def __init__(self, schema):
        self.schema = schema


def _vol_required(key, default=None):
    return ("required", key, default)


def _vol_in(options):
    return ("in", options)


class _MopekaIOTBluetoothDeviceData:
    def __init__(self, medium_type=None):
        self.medium_type = medium_type
        self.title = "Mopeka"

    def supported(self, _discovery_info):
        return True

    def get_device_name(self):
        return "Mopeka"

    def update(self, *_args, **_kwargs):
        return None


class _DeviceEntry:
    pass


class _FakeConfigFlowResult(dict):
    pass


@dataclass
class _SensorEntityDescription:
    key: str
    device_class: str | None = None
    native_unit_of_measurement: str | None = None
    state_class: str | None = None
    entity_category: str | None = None
    entity_registry_enabled_default: bool = True
    translation_key: str | None = None
    suggested_display_precision: int | None = None


class _SensorEntity:
    pass


class _SensorDeviceClass:
    BATTERY = "battery"
    VOLTAGE = "voltage"
    SIGNAL_STRENGTH = "signal_strength"
    DISTANCE = "distance"
    TEMPERATURE = "temperature"


class _SensorStateClass:
    MEASUREMENT = "measurement"


class _EntityCategory:
    DIAGNOSTIC = "diagnostic"


class _UnitOfElectricPotential:
    VOLT = "V"


class _UnitOfLength:
    MILLIMETERS = "mm"


class _UnitOfTemperature:
    CELSIUS = "C"


class _UnitOfVolume:
    GALLONS = "gal"
    LITERS = "L"


class _UnitOfMass:
    KILOGRAMS = "kg"


class _MediumType(Enum):
    PROPANE = "propane"
    AIR = "air"
    FRESH_WATER = "fresh_water"
    WASTE_WATER = "waste_water"


def _install_stubs() -> None:
    if not hasattr(enum, "StrEnum"):

        class _CompatStrEnum(str, enum.Enum):
            pass

        enum.StrEnum = _CompatStrEnum

    mopeka_iot_ble = types.ModuleType("mopeka_iot_ble")
    mopeka_iot_ble.DeviceKey = _DeviceKey
    mopeka_iot_ble.SensorUpdate = _SensorUpdate
    mopeka_iot_ble.MediumType = _MediumType
    mopeka_iot_ble.MopekaIOTBluetoothDeviceData = _MopekaIOTBluetoothDeviceData
    sys.modules["mopeka_iot_ble"] = mopeka_iot_ble

    vol = types.ModuleType("voluptuous")
    vol.Schema = _VolSchema
    vol.Required = _vol_required
    vol.In = _vol_in
    sys.modules["voluptuous"] = vol

    ha = types.ModuleType("homeassistant")
    sys.modules["homeassistant"] = ha

    ha_components = types.ModuleType("homeassistant.components")
    sys.modules["homeassistant.components"] = ha_components

    ha_bt = types.ModuleType("homeassistant.components.bluetooth")
    ha_bt.BluetoothScanningMode = _BluetoothScanningMode
    ha_bt.BluetoothServiceInfoBleak = _BluetoothServiceInfoBleak
    ha_bt.async_discovered_service_info = lambda _hass, _connectable: []
    sys.modules["homeassistant.components.bluetooth"] = ha_bt

    ha_bt_pup = types.ModuleType(
        "homeassistant.components.bluetooth.passive_update_processor"
    )
    ha_bt_pup.PassiveBluetoothDataProcessor = _PassiveBluetoothDataProcessor
    ha_bt_pup.PassiveBluetoothDataUpdate = _PassiveBluetoothDataUpdate
    ha_bt_pup.PassiveBluetoothEntityKey = _PassiveBluetoothEntityKey
    ha_bt_pup.PassiveBluetoothProcessorEntity = _PassiveBluetoothProcessorEntity
    ha_bt_pup.PassiveBluetoothProcessorCoordinator = (
        _PassiveBluetoothProcessorCoordinator
    )
    sys.modules["homeassistant.components.bluetooth.passive_update_processor"] = (
        ha_bt_pup
    )

    ha_sensor = types.ModuleType("homeassistant.components.sensor")
    ha_sensor.SensorDeviceClass = _SensorDeviceClass
    ha_sensor.SensorEntity = _SensorEntity
    ha_sensor.SensorEntityDescription = _SensorEntityDescription
    ha_sensor.SensorStateClass = _SensorStateClass
    sys.modules["homeassistant.components.sensor"] = ha_sensor

    ha_const = types.ModuleType("homeassistant.const")
    ha_const.PERCENTAGE = "%"
    ha_const.SIGNAL_STRENGTH_DECIBELS_MILLIWATT = "dBm"
    ha_const.EntityCategory = _EntityCategory
    ha_const.UnitOfElectricPotential = _UnitOfElectricPotential
    ha_const.UnitOfLength = _UnitOfLength
    ha_const.UnitOfTemperature = _UnitOfTemperature
    ha_const.UnitOfVolume = _UnitOfVolume
    ha_const.UnitOfMass = _UnitOfMass
    ha_const.CONF_ADDRESS = "address"
    ha_const.Platform = _Platform
    sys.modules["homeassistant.const"] = ha_const

    ha_core = types.ModuleType("homeassistant.core")
    ha_core.HomeAssistant = object
    ha_core.callback = _callback
    sys.modules["homeassistant.core"] = ha_core

    ha_config_entries = types.ModuleType("homeassistant.config_entries")
    ha_config_entries.ConfigEntry = _ConfigEntry
    ha_config_entries.ConfigFlow = _ConfigFlow
    ha_config_entries.ConfigFlowResult = _FakeConfigFlowResult
    ha_config_entries.OptionsFlow = _OptionsFlow
    sys.modules["homeassistant.config_entries"] = ha_config_entries

    ha.config_entries = ha_config_entries

    ha_helpers = types.ModuleType("homeassistant.helpers")
    sys.modules["homeassistant.helpers"] = ha_helpers

    ha_helpers_device_registry = types.ModuleType(
        "homeassistant.helpers.device_registry"
    )
    ha_helpers_device_registry.DeviceEntry = _DeviceEntry
    sys.modules["homeassistant.helpers.device_registry"] = ha_helpers_device_registry

    ha_helpers_selector = types.ModuleType("homeassistant.helpers.selector")
    ha_helpers_selector.NumberSelector = _NumberSelector
    ha_helpers_selector.NumberSelectorConfig = _NumberSelectorConfig
    ha_helpers_selector.NumberSelectorMode = _NumberSelectorMode
    ha_helpers_selector.SelectSelector = _SelectSelector
    ha_helpers_selector.SelectSelectorConfig = _SelectSelectorConfig
    ha_helpers_selector.SelectSelectorMode = _SelectSelectorMode
    sys.modules["homeassistant.helpers.selector"] = ha_helpers_selector

    ha_helpers.selector = ha_helpers_selector

    ha_helpers_entity = types.ModuleType("homeassistant.helpers.entity")
    ha_helpers_entity.EntityDescription = object
    sys.modules["homeassistant.helpers.entity"] = ha_helpers_entity

    ha_helpers_entity_platform = types.ModuleType(
        "homeassistant.helpers.entity_platform"
    )
    ha_helpers_entity_platform.AddConfigEntryEntitiesCallback = object
    sys.modules["homeassistant.helpers.entity_platform"] = ha_helpers_entity_platform

    ha_helpers_sensor = types.ModuleType("homeassistant.helpers.sensor")
    ha_helpers_sensor.sensor_device_info_to_hass_device_info = lambda info: info
    sys.modules["homeassistant.helpers.sensor"] = ha_helpers_sensor


def _load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, str(path))
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module

    if sys.version_info < (3, 10) and module_name == "custom_components.mopeka.sensor":
        source = path.read_text(encoding="utf-8")
        marker = "class MopekaBluetoothSensorEntity("
        if marker in source:
            source = source.split(marker, maxsplit=1)[0] + (
                "\n\nclass MopekaBluetoothSensorEntity:\n"
                '    """Py3.9 test placeholder for runtime entity class."""\n'
                "\n"
                "    pass\n"
            )
        exec(compile(source, str(path), "exec"), module.__dict__)
        return module

    if (
        sys.version_info < (3, 12)
        and module_name == "custom_components.mopeka.__init__"
    ):
        source = path.read_text(encoding="utf-8")
        source = re.sub(
            r"^type\s+MopekaConfigEntry\s*=.*$",
            "MopekaConfigEntry = _ConfigEntry",
            source,
            flags=re.MULTILINE,
        )
        module.__dict__["_ConfigEntry"] = _ConfigEntry
        exec(compile(source, str(path), "exec"), module.__dict__)
        return module

    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def sensor_module():
    _install_stubs()

    repo_root = Path(__file__).resolve().parents[1]
    custom_components_path = repo_root / "custom_components"
    mopeka_path = custom_components_path / "mopeka"

    cc_pkg = types.ModuleType("custom_components")
    cc_pkg.__path__ = [str(custom_components_path)]
    sys.modules["custom_components"] = cc_pkg

    mopeka_pkg = types.ModuleType("custom_components.mopeka")
    mopeka_pkg.__path__ = [str(mopeka_path)]
    mopeka_pkg.MopekaConfigEntry = object
    sys.modules["custom_components.mopeka"] = mopeka_pkg

    _load_module("custom_components.mopeka.const", mopeka_path / "const.py")
    _load_module("custom_components.mopeka.device", mopeka_path / "device.py")
    return _load_module("custom_components.mopeka.sensor", mopeka_path / "sensor.py")


@pytest.fixture(scope="session")
def const_module():
    _install_stubs()
    repo_root = Path(__file__).resolve().parents[1]
    custom_components_path = repo_root / "custom_components"
    mopeka_path = custom_components_path / "mopeka"

    cc_pkg = types.ModuleType("custom_components")
    cc_pkg.__path__ = [str(custom_components_path)]
    sys.modules["custom_components"] = cc_pkg

    mopeka_pkg = types.ModuleType("custom_components.mopeka")
    mopeka_pkg.__path__ = [str(mopeka_path)]
    mopeka_pkg.MopekaConfigEntry = object
    sys.modules["custom_components.mopeka"] = mopeka_pkg

    return _load_module("custom_components.mopeka.const", mopeka_path / "const.py")


@pytest.fixture(scope="session")
def config_flow_module(const_module):
    _install_stubs()
    repo_root = Path(__file__).resolve().parents[1]
    mopeka_path = repo_root / "custom_components" / "mopeka"
    return _load_module(
        "custom_components.mopeka.config_flow", mopeka_path / "config_flow.py"
    )


@pytest.fixture(scope="session")
def device_module(const_module):
    _install_stubs()
    repo_root = Path(__file__).resolve().parents[1]
    mopeka_path = repo_root / "custom_components" / "mopeka"
    return _load_module("custom_components.mopeka.device", mopeka_path / "device.py")


@pytest.fixture(scope="session")
def integration_module(const_module):
    _install_stubs()
    repo_root = Path(__file__).resolve().parents[1]
    mopeka_path = repo_root / "custom_components" / "mopeka"
    return _load_module(
        "custom_components.mopeka.__init__", mopeka_path / "__init__.py"
    )


@pytest.fixture(scope="session")
def stub_types():
    return {
        "DeviceKey": _DeviceKey,
        "SensorValue": _SensorValue,
        "SensorUpdate": _SensorUpdate,
        "PassiveBluetoothEntityKey": _PassiveBluetoothEntityKey,
        "UnitOfVolume": _UnitOfVolume,
        "UnitOfMass": _UnitOfMass,
        "BluetoothServiceInfoBleak": _BluetoothServiceInfoBleak,
    }
