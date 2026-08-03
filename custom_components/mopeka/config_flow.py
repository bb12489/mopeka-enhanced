"""Config flow for mopeka integration."""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import selector
from mopeka_iot_ble import MopekaIOTBluetoothDeviceData as DeviceData

from . import _mopeka_iot_ble_compat  # noqa: F401
from .const import (
    CAPACITY_UNIT_GALLONS,
    CAPACITY_UNIT_KILOGRAMS,
    CAPACITY_UNIT_LITERS,
    CONF_CUSTOM_TANK_HEIGHT,
    CONF_MEDIUM_TYPE,
    CONF_TANK_CAPACITY,
    CONF_TANK_CAPACITY_UNIT,
    CONF_TANK_SIZE,
    CONF_TOP_MOUNT,
    CONF_TOP_MOUNT_SENSOR_HEIGHT,
    DEFAULT_CUSTOM_TANK_HEIGHT,
    DEFAULT_IBC_TANK_SIZE,
    DEFAULT_MEDIUM_TYPE,
    DEFAULT_TANK_CAPACITY,
    DEFAULT_TANK_CAPACITY_UNIT,
    DEFAULT_TANK_SIZE,
    DEFAULT_TOP_MOUNT_SENSOR_HEIGHT,
    DOMAIN,
    IBC_TANK_SIZES,
    MOPEKA_MANUFACTURER_ID,
    PROPANE_TANK_SIZES,
    TOP_MOUNT_MODEL_IDS,
    MediumType,
    TankSize,
    normalize_tank_size,
)

_LOGGER = logging.getLogger(__name__)


def _is_top_mount_sensor(discovery_info: BluetoothServiceInfoBleak) -> bool:
    """Return True if the device is a top-mount sensor (TD40/TD200/Pro-200B).

    Top-mount sensors always measure the air gap above the liquid surface and
    must use the AIR acoustic coefficient — the user cannot override this.
    """
    mfr_data = discovery_info.manufacturer_data.get(MOPEKA_MANUFACTURER_ID)
    if not mfr_data:
        return False
    return mfr_data[0] in TOP_MOUNT_MODEL_IDS


def format_medium_type(medium_type: Enum) -> str:
    """Format the medium type for human reading."""
    return medium_type.name.replace("_", " ").title()


MEDIUM_TYPES_BY_NAME = {
    medium.value: format_medium_type(medium) for medium in MediumType
}

_CUSTOM_HEIGHT_SELECTOR = selector.NumberSelector(
    selector.NumberSelectorConfig(
        min=0,
        max=5000,
        step=1,
        unit_of_measurement="mm",
        mode=selector.NumberSelectorMode.BOX,
    )
)

# Height of a top-mount sensor's physical mounting point above the tank bottom
# (Mopeka app's "Overall Height"). Same range as the tank height selector since
# it measures the same physical dimension, just from a different reference.
_TOP_MOUNT_SENSOR_HEIGHT_SELECTOR = selector.NumberSelector(
    selector.NumberSelectorConfig(
        min=0,
        max=5000,
        step=1,
        unit_of_measurement="mm",
        mode=selector.NumberSelectorMode.BOX,
    )
)

_CUSTOM_CAPACITY_SELECTOR = selector.NumberSelector(
    selector.NumberSelectorConfig(
        min=0,
        max=100000,
        step=0.1,
        mode=selector.NumberSelectorMode.BOX,
    )
)


def _coerce_int(value: Any, default: int) -> int:
    """Safely coerce a value to int, returning default on invalid input."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _coerce_float(value: Any, default: float) -> float:
    """Safely coerce a value to float, returning default on invalid input."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _parse_custom_height_values(
    user_input: dict[str, Any],
    *,
    top_mount: bool = False,
) -> tuple[int | None, float | None, int | None, dict[str, str]]:
    """Parse custom height/capacity/(top-mount sensor height) values.

    Returns (height, capacity, top_mount_sensor_height, errors). When
    top_mount is False, top_mount_sensor_height is always
    DEFAULT_TOP_MOUNT_SENSOR_HEIGHT (0) and never parsed/validated, since the
    field is not shown for bottom-mount entries.
    """
    errors: dict[str, str] = {}

    try:
        height = int(
            user_input.get(CONF_CUSTOM_TANK_HEIGHT, DEFAULT_CUSTOM_TANK_HEIGHT)
        )
    except (TypeError, ValueError):
        height = None
        errors[CONF_CUSTOM_TANK_HEIGHT] = "invalid_number"

    try:
        capacity = float(user_input.get(CONF_TANK_CAPACITY, DEFAULT_TANK_CAPACITY))
    except (TypeError, ValueError):
        capacity = None
        errors[CONF_TANK_CAPACITY] = "invalid_number"

    sensor_height: int | None = DEFAULT_TOP_MOUNT_SENSOR_HEIGHT
    if top_mount:
        try:
            sensor_height = int(
                user_input.get(
                    CONF_TOP_MOUNT_SENSOR_HEIGHT, DEFAULT_TOP_MOUNT_SENSOR_HEIGHT
                )
            )
        except (TypeError, ValueError):
            sensor_height = None
            errors[CONF_TOP_MOUNT_SENSOR_HEIGHT] = "invalid_number"

    return height, capacity, sensor_height, errors


def _is_propane_medium(medium_type: str | None) -> bool:
    """Return True when the selected medium is propane."""
    return medium_type == DEFAULT_MEDIUM_TYPE


def _async_generate_capacity_unit_selector(medium_type: str) -> selector.SelectSelector:
    """Return selector for custom tank capacity input unit."""
    unit_options = (
        [CAPACITY_UNIT_GALLONS, CAPACITY_UNIT_KILOGRAMS]
        if _is_propane_medium(medium_type)
        else [CAPACITY_UNIT_GALLONS, CAPACITY_UNIT_LITERS]
    )
    return selector.SelectSelector(
        selector.SelectSelectorConfig(
            options=unit_options,
            mode=selector.SelectSelectorMode.DROPDOWN,
            translation_key="tank_capacity_unit",
        )
    )


def _async_generate_medium_type_schema(
    medium_type: str | None = None,
) -> vol.Schema:
    """Return a schema containing only the medium type selector."""
    return vol.Schema(
        {
            vol.Required(
                CONF_MEDIUM_TYPE, default=medium_type or DEFAULT_MEDIUM_TYPE
            ): vol.In(MEDIUM_TYPES_BY_NAME),
        }
    )


def _async_generate_tank_schema(
    tank_size: str | None = None,
) -> vol.Schema:
    """Return a schema containing only the tank preset selector."""
    return vol.Schema(
        {
            vol.Required(
                CONF_TANK_SIZE, default=tank_size or DEFAULT_TANK_SIZE
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[size.value for size in PROPANE_TANK_SIZES],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                    translation_key="tank_size",
                )
            ),
        }
    )


def _async_generate_ibc_tank_schema(
    tank_size: str | None = None,
) -> vol.Schema:
    """Return a schema containing the IBC tote tank preset selector."""
    return vol.Schema(
        {
            vol.Required(
                CONF_TANK_SIZE, default=tank_size or DEFAULT_IBC_TANK_SIZE
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[size.value for size in IBC_TANK_SIZES],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                    translation_key="ibc_tank_size",
                )
            ),
        }
    )


def _async_generate_custom_height_schema(
    medium_type: str,
    custom_tank_height: int | None = None,
    tank_capacity: float | None = None,
    tank_capacity_unit: str | None = None,
    *,
    top_mount: bool = False,
    top_mount_sensor_height: int | None = None,
) -> vol.Schema:
    """Return a schema containing the custom tank height and capacity inputs.

    When top_mount is True, also includes CONF_TOP_MOUNT_SENSOR_HEIGHT (the
    Mopeka app's "Overall Height") so the sensor's air-gap readings can be
    correctly converted to fluid height even when the sensor is mounted above
    the max water level (headspace). Not shown for bottom-mount entries,
    where the raw reading is already fluid height and no offset applies.
    """
    schema: dict[Any, Any] = {
        vol.Required(
            CONF_CUSTOM_TANK_HEIGHT,
            default=custom_tank_height
            if custom_tank_height is not None
            else DEFAULT_CUSTOM_TANK_HEIGHT,
        ): _CUSTOM_HEIGHT_SELECTOR,
    }

    if top_mount:
        schema[
            vol.Required(
                CONF_TOP_MOUNT_SENSOR_HEIGHT,
                default=top_mount_sensor_height
                if top_mount_sensor_height is not None
                else DEFAULT_TOP_MOUNT_SENSOR_HEIGHT,
            )
        ] = _TOP_MOUNT_SENSOR_HEIGHT_SELECTOR

    is_propane = _is_propane_medium(medium_type)
    allowed_units = (
        {CAPACITY_UNIT_GALLONS, CAPACITY_UNIT_KILOGRAMS}
        if is_propane
        else {CAPACITY_UNIT_GALLONS, CAPACITY_UNIT_LITERS}
    )
    selected_unit = (
        tank_capacity_unit
        if tank_capacity_unit in allowed_units
        else DEFAULT_TANK_CAPACITY_UNIT
    )

    schema[
        vol.Required(
            CONF_TANK_CAPACITY_UNIT,
            default=selected_unit,
        )
    ] = _async_generate_capacity_unit_selector(medium_type)

    schema[
        vol.Required(
            CONF_TANK_CAPACITY,
            default=tank_capacity
            if tank_capacity is not None
            else DEFAULT_TANK_CAPACITY,
        )
    ] = _CUSTOM_CAPACITY_SELECTOR

    return vol.Schema(schema)


def _async_generate_top_mount_height_schema(
    top_mount_sensor_height: int | None = None,
) -> vol.Schema:
    """Return a schema containing only the top-mount sensor height input.

    Used when a top-mount device selects a fixed-geometry preset (e.g. an IBC
    tote) rather than Custom, since presets don't otherwise show a height
    form where CONF_TOP_MOUNT_SENSOR_HEIGHT could be collected.
    """
    return vol.Schema(
        {
            vol.Required(
                CONF_TOP_MOUNT_SENSOR_HEIGHT,
                default=top_mount_sensor_height
                if top_mount_sensor_height is not None
                else DEFAULT_TOP_MOUNT_SENSOR_HEIGHT,
            ): _TOP_MOUNT_SENSOR_HEIGHT_SELECTOR,
        }
    )


def _normalized_propane_tank_size_or_default(tank_size: str | None) -> str:
    """Return a valid propane preset key suitable for selector defaults."""
    normalized_tank_size = normalize_tank_size(tank_size)
    valid_sizes = {size.value for size in PROPANE_TANK_SIZES}
    if normalized_tank_size not in valid_sizes:
        return DEFAULT_TANK_SIZE
    return normalized_tank_size


class MopekaConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for mopeka."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovery_info: BluetoothServiceInfoBleak | None = None
        self._discovered_device: DeviceData | None = None
        self._discovered_devices: dict[str, str] = {}
        self._discovered_service_infos: dict[str, BluetoothServiceInfoBleak] = {}
        self._medium_type: str = DEFAULT_MEDIUM_TYPE
        self._is_top_mount: bool = False
        self._custom_capacity_unit: str = DEFAULT_TANK_CAPACITY_UNIT
        self._title: str = ""
        self._address: str | None = None
        # Preset tank size chosen by a top-mount device on the IBC preset step,
        # held while collecting CONF_TOP_MOUNT_SENSOR_HEIGHT on the next step.
        self._pending_tank_size: str | None = None

    @callback
    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> MopekaOptionsFlow:
        """Return the options flow for this handler."""
        return MopekaOptionsFlow()

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> ConfigFlowResult:
        """Handle the bluetooth discovery step."""
        _LOGGER.debug(
            "Discovered Mopeka device via bluetooth: %s", discovery_info.address
        )
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        device = DeviceData()
        if not device.supported(discovery_info):
            _LOGGER.debug(
                "Discovered device %s is not a supported Mopeka device",
                discovery_info.address,
            )
            return self.async_abort(reason="not_supported")
        self._discovery_info = discovery_info
        self._discovered_device = device
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm discovery and select medium type."""
        # Invariant: async_step_bluetooth always sets these before routing here.
        if self._discovered_device is None or self._discovery_info is None:
            raise HomeAssistantError(
                "Bluetooth confirm step reached without prior discovery"
            )
        device = self._discovered_device
        discovery_info = self._discovery_info
        title = device.title or device.get_device_name() or discovery_info.name

        # Top-mount sensors (TD40/TD200/Pro-200B) always use AIR — bypass the medium type form.
        if _is_top_mount_sensor(discovery_info):
            self._is_top_mount = True
            self._medium_type = MediumType.AIR.value
            self._title = title
            self._discovered_devices[discovery_info.address] = title
            return await self.async_step_ibc_tank_config()

        if user_input is not None:
            self._medium_type = user_input[CONF_MEDIUM_TYPE]
            self._title = title
            self._discovered_devices[discovery_info.address] = title
            if self._medium_type == DEFAULT_MEDIUM_TYPE:
                return await self.async_step_tank_config()
            return await self.async_step_ibc_tank_config()

        placeholders = {"name": title}
        self.context["title_placeholders"] = placeholders
        return self.async_show_form(
            step_id="bluetooth_confirm",
            description_placeholders=placeholders,
            data_schema=_async_generate_medium_type_schema(),
        )

    async def _async_create_config_entry(
        self,
        tank_size: str,
        custom_height: int,
        tank_capacity: float = 0.0,
        tank_capacity_unit: str = DEFAULT_TANK_CAPACITY_UNIT,
        top_mount_sensor_height: int = DEFAULT_TOP_MOUNT_SENSOR_HEIGHT,
    ) -> ConfigFlowResult:
        """Create the config entry with the collected parameters."""
        data = {
            CONF_MEDIUM_TYPE: self._medium_type,
            CONF_TANK_SIZE: normalize_tank_size(tank_size),
            CONF_CUSTOM_TANK_HEIGHT: custom_height,
            CONF_TANK_CAPACITY: tank_capacity,
            CONF_TANK_CAPACITY_UNIT: tank_capacity_unit,
            CONF_TOP_MOUNT: self._is_top_mount,
            CONF_TOP_MOUNT_SENSOR_HEIGHT: top_mount_sensor_height,
        }
        if self._discovery_info is not None:
            return self.async_create_entry(title=self._title, data=data)
        # Invariant: async_step_user always sets this before routing here.
        if self._address is None:
            raise HomeAssistantError(
                "Config entry creation reached without a selected address"
            )
        await self.async_set_unique_id(self._address, raise_on_progress=False)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title=self._discovered_devices[self._address], data=data
        )

    async def async_step_tank_config(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Select a propane tank preset."""
        if user_input is not None:
            tank_size = user_input.get(CONF_TANK_SIZE, TankSize.CUSTOM)
            if tank_size == TankSize.CUSTOM:
                return await self.async_step_custom_height()
            return await self._async_create_config_entry(
                tank_size,
                0,
                0.0,
                DEFAULT_TANK_CAPACITY_UNIT,
            )

        return self.async_show_form(
            step_id="tank_config",
            data_schema=_async_generate_tank_schema(),
        )

    async def async_step_ibc_tank_config(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Select an IBC tote tank preset (non-propane media)."""
        if user_input is not None:
            tank_size = user_input.get(CONF_TANK_SIZE, TankSize.CUSTOM)
            if tank_size == TankSize.CUSTOM:
                return await self.async_step_custom_height()
            if self._is_top_mount:
                # Presets have a fixed max water level height, but the sensor's
                # own mount height above the tank bottom is still install-
                # specific and isn't collected anywhere else for preset tanks.
                self._pending_tank_size = tank_size
                return await self.async_step_top_mount_height()
            return await self._async_create_config_entry(
                tank_size,
                0,
                0.0,
                DEFAULT_TANK_CAPACITY_UNIT,
            )

        return self.async_show_form(
            step_id="ibc_tank_config",
            data_schema=_async_generate_ibc_tank_schema(),
        )

    async def async_step_top_mount_height(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Enter the top-mount sensor's mounting height (preset tank path)."""
        # Invariant: async_step_ibc_tank_config always sets this before routing here.
        if self._pending_tank_size is None:
            raise HomeAssistantError(
                "Top-mount sensor height step reached without a selected tank size"
            )
        if user_input is not None:
            sensor_height = _coerce_int(
                user_input.get(
                    CONF_TOP_MOUNT_SENSOR_HEIGHT, DEFAULT_TOP_MOUNT_SENSOR_HEIGHT
                ),
                DEFAULT_TOP_MOUNT_SENSOR_HEIGHT,
            )
            return await self._async_create_config_entry(
                self._pending_tank_size,
                0,
                0.0,
                DEFAULT_TANK_CAPACITY_UNIT,
                top_mount_sensor_height=sensor_height,
            )

        return self.async_show_form(
            step_id="top_mount_height",
            data_schema=_async_generate_top_mount_height_schema(),
        )

    async def async_step_custom_height(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Enter a custom tank height and total capacity."""
        if user_input is not None:
            capacity_unit = user_input.get(
                CONF_TANK_CAPACITY_UNIT, self._custom_capacity_unit
            )
            if capacity_unit != self._custom_capacity_unit:
                self._custom_capacity_unit = capacity_unit
                return self.async_show_form(
                    step_id="custom_height",
                    data_schema=_async_generate_custom_height_schema(
                        medium_type=self._medium_type,
                        custom_tank_height=_coerce_int(
                            user_input.get(
                                CONF_CUSTOM_TANK_HEIGHT, DEFAULT_CUSTOM_TANK_HEIGHT
                            ),
                            DEFAULT_CUSTOM_TANK_HEIGHT,
                        ),
                        tank_capacity=_coerce_float(
                            user_input.get(CONF_TANK_CAPACITY, DEFAULT_TANK_CAPACITY),
                            DEFAULT_TANK_CAPACITY,
                        ),
                        tank_capacity_unit=self._custom_capacity_unit,
                        top_mount=self._is_top_mount,
                        top_mount_sensor_height=_coerce_int(
                            user_input.get(
                                CONF_TOP_MOUNT_SENSOR_HEIGHT,
                                DEFAULT_TOP_MOUNT_SENSOR_HEIGHT,
                            ),
                            DEFAULT_TOP_MOUNT_SENSOR_HEIGHT,
                        ),
                    ),
                )
            height, capacity, sensor_height, errors = _parse_custom_height_values(
                user_input, top_mount=self._is_top_mount
            )
            if errors:
                return self.async_show_form(
                    step_id="custom_height",
                    data_schema=_async_generate_custom_height_schema(
                        medium_type=self._medium_type,
                        custom_tank_height=_coerce_int(
                            user_input.get(
                                CONF_CUSTOM_TANK_HEIGHT, DEFAULT_CUSTOM_TANK_HEIGHT
                            ),
                            DEFAULT_CUSTOM_TANK_HEIGHT,
                        ),
                        tank_capacity=_coerce_float(
                            user_input.get(CONF_TANK_CAPACITY, DEFAULT_TANK_CAPACITY),
                            DEFAULT_TANK_CAPACITY,
                        ),
                        tank_capacity_unit=self._custom_capacity_unit,
                        top_mount=self._is_top_mount,
                        top_mount_sensor_height=_coerce_int(
                            user_input.get(
                                CONF_TOP_MOUNT_SENSOR_HEIGHT,
                                DEFAULT_TOP_MOUNT_SENSOR_HEIGHT,
                            ),
                            DEFAULT_TOP_MOUNT_SENSOR_HEIGHT,
                        ),
                    ),
                    errors=errors,
                )
            # _parse_custom_height_values only returns an empty errors dict when
            # height, capacity, and (when top-mount) sensor_height all parsed
            # successfully.
            if height is None or capacity is None or sensor_height is None:
                raise HomeAssistantError(
                    "Custom height parsed without errors but returned no value"
                )
            return await self._async_create_config_entry(
                TankSize.CUSTOM,
                height,
                capacity,
                capacity_unit,
                top_mount_sensor_height=sensor_height,
            )

        self._custom_capacity_unit = DEFAULT_TANK_CAPACITY_UNIT
        return self.async_show_form(
            step_id="custom_height",
            data_schema=_async_generate_custom_height_schema(
                medium_type=self._medium_type,
                tank_capacity_unit=self._custom_capacity_unit,
                top_mount=self._is_top_mount,
            ),
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration — select medium type."""
        entry = self._get_reconfigure_entry()
        # Top-mount sensors have their medium type locked to AIR.
        if entry.data.get(CONF_TOP_MOUNT, False):
            self._medium_type = MediumType.AIR.value
            return await self.async_step_reconfigure_ibc_tank_config()

        if user_input is not None:
            self._medium_type = user_input[CONF_MEDIUM_TYPE]
            if self._medium_type == DEFAULT_MEDIUM_TYPE:
                return await self.async_step_reconfigure_tank_config()
            return await self.async_step_reconfigure_ibc_tank_config()

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_async_generate_medium_type_schema(
                medium_type=entry.data.get(CONF_MEDIUM_TYPE),
            ),
        )

    async def async_step_reconfigure_tank_config(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration — select tank preset."""
        entry = self._get_reconfigure_entry()
        if user_input is not None:
            tank_size = user_input.get(CONF_TANK_SIZE, TankSize.CUSTOM)
            if tank_size == TankSize.CUSTOM:
                return await self.async_step_reconfigure_custom_height()
            return self.async_update_reload_and_abort(
                entry,
                data_updates={
                    CONF_MEDIUM_TYPE: self._medium_type,
                    CONF_TANK_SIZE: tank_size,
                    CONF_CUSTOM_TANK_HEIGHT: 0,
                    CONF_TANK_CAPACITY: 0.0,
                    CONF_TANK_CAPACITY_UNIT: DEFAULT_TANK_CAPACITY_UNIT,
                },
            )

        existing_tank_size = _normalized_propane_tank_size_or_default(
            entry.data.get(CONF_TANK_SIZE, DEFAULT_TANK_SIZE)
        )
        return self.async_show_form(
            step_id="reconfigure_tank_config",
            data_schema=_async_generate_tank_schema(
                tank_size=existing_tank_size,
            ),
        )

    async def async_step_reconfigure_ibc_tank_config(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration — select IBC tote tank preset."""
        entry = self._get_reconfigure_entry()
        if user_input is not None:
            tank_size = user_input.get(CONF_TANK_SIZE, TankSize.CUSTOM)
            if tank_size == TankSize.CUSTOM:
                return await self.async_step_reconfigure_custom_height()
            if entry.data.get(CONF_TOP_MOUNT, False):
                self._pending_tank_size = tank_size
                return await self.async_step_reconfigure_top_mount_height()
            return self.async_update_reload_and_abort(
                entry,
                data_updates={
                    CONF_MEDIUM_TYPE: self._medium_type,
                    CONF_TANK_SIZE: tank_size,
                    CONF_CUSTOM_TANK_HEIGHT: 0,
                    CONF_TANK_CAPACITY: 0.0,
                    CONF_TANK_CAPACITY_UNIT: DEFAULT_TANK_CAPACITY_UNIT,
                },
            )

        existing_tank_size = normalize_tank_size(entry.data.get(CONF_TANK_SIZE))
        if existing_tank_size not in IBC_TANK_SIZES:
            existing_tank_size = DEFAULT_IBC_TANK_SIZE
        return self.async_show_form(
            step_id="reconfigure_ibc_tank_config",
            data_schema=_async_generate_ibc_tank_schema(
                tank_size=existing_tank_size,
            ),
        )

    async def async_step_reconfigure_top_mount_height(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration — enter top-mount sensor height (preset path)."""
        entry = self._get_reconfigure_entry()
        # Invariant: async_step_reconfigure_ibc_tank_config always sets this
        # before routing here.
        if self._pending_tank_size is None:
            raise HomeAssistantError(
                "Top-mount sensor height step reached without a selected tank size"
            )
        if user_input is not None:
            sensor_height = _coerce_int(
                user_input.get(
                    CONF_TOP_MOUNT_SENSOR_HEIGHT, DEFAULT_TOP_MOUNT_SENSOR_HEIGHT
                ),
                DEFAULT_TOP_MOUNT_SENSOR_HEIGHT,
            )
            return self.async_update_reload_and_abort(
                entry,
                data_updates={
                    CONF_MEDIUM_TYPE: self._medium_type,
                    CONF_TANK_SIZE: self._pending_tank_size,
                    CONF_CUSTOM_TANK_HEIGHT: 0,
                    CONF_TANK_CAPACITY: 0.0,
                    CONF_TANK_CAPACITY_UNIT: DEFAULT_TANK_CAPACITY_UNIT,
                    CONF_TOP_MOUNT_SENSOR_HEIGHT: sensor_height,
                },
            )

        return self.async_show_form(
            step_id="reconfigure_top_mount_height",
            data_schema=_async_generate_top_mount_height_schema(
                top_mount_sensor_height=entry.data.get(
                    CONF_TOP_MOUNT_SENSOR_HEIGHT, DEFAULT_TOP_MOUNT_SENSOR_HEIGHT
                ),
            ),
        )

    async def async_step_reconfigure_custom_height(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration — enter custom tank height and total capacity."""
        entry = self._get_reconfigure_entry()
        is_top_mount = entry.data.get(CONF_TOP_MOUNT, False)
        if user_input is not None:
            capacity_unit = user_input.get(
                CONF_TANK_CAPACITY_UNIT,
                self._custom_capacity_unit,
            )
            if capacity_unit != self._custom_capacity_unit:
                self._custom_capacity_unit = capacity_unit
                return self.async_show_form(
                    step_id="reconfigure_custom_height",
                    data_schema=_async_generate_custom_height_schema(
                        medium_type=self._medium_type,
                        custom_tank_height=_coerce_int(
                            user_input.get(
                                CONF_CUSTOM_TANK_HEIGHT, DEFAULT_CUSTOM_TANK_HEIGHT
                            ),
                            DEFAULT_CUSTOM_TANK_HEIGHT,
                        ),
                        tank_capacity=_coerce_float(
                            user_input.get(CONF_TANK_CAPACITY, DEFAULT_TANK_CAPACITY),
                            DEFAULT_TANK_CAPACITY,
                        ),
                        tank_capacity_unit=self._custom_capacity_unit,
                        top_mount=is_top_mount,
                        top_mount_sensor_height=_coerce_int(
                            user_input.get(
                                CONF_TOP_MOUNT_SENSOR_HEIGHT,
                                DEFAULT_TOP_MOUNT_SENSOR_HEIGHT,
                            ),
                            DEFAULT_TOP_MOUNT_SENSOR_HEIGHT,
                        ),
                    ),
                )
            height, capacity, sensor_height, errors = _parse_custom_height_values(
                user_input, top_mount=is_top_mount
            )
            if errors:
                return self.async_show_form(
                    step_id="reconfigure_custom_height",
                    data_schema=_async_generate_custom_height_schema(
                        medium_type=self._medium_type,
                        custom_tank_height=_coerce_int(
                            user_input.get(
                                CONF_CUSTOM_TANK_HEIGHT, DEFAULT_CUSTOM_TANK_HEIGHT
                            ),
                            DEFAULT_CUSTOM_TANK_HEIGHT,
                        ),
                        tank_capacity=_coerce_float(
                            user_input.get(CONF_TANK_CAPACITY, DEFAULT_TANK_CAPACITY),
                            DEFAULT_TANK_CAPACITY,
                        ),
                        tank_capacity_unit=self._custom_capacity_unit,
                        top_mount=is_top_mount,
                        top_mount_sensor_height=_coerce_int(
                            user_input.get(
                                CONF_TOP_MOUNT_SENSOR_HEIGHT,
                                DEFAULT_TOP_MOUNT_SENSOR_HEIGHT,
                            ),
                            DEFAULT_TOP_MOUNT_SENSOR_HEIGHT,
                        ),
                    ),
                    errors=errors,
                )
            return self.async_update_reload_and_abort(
                entry,
                data_updates={
                    CONF_MEDIUM_TYPE: self._medium_type,
                    CONF_TANK_SIZE: TankSize.CUSTOM,
                    CONF_CUSTOM_TANK_HEIGHT: height,
                    CONF_TANK_CAPACITY: capacity,
                    CONF_TANK_CAPACITY_UNIT: capacity_unit,
                    CONF_TOP_MOUNT_SENSOR_HEIGHT: sensor_height,
                },
            )

        existing_height = entry.data.get(
            CONF_CUSTOM_TANK_HEIGHT, DEFAULT_CUSTOM_TANK_HEIGHT
        )
        existing_capacity = float(
            entry.data.get(CONF_TANK_CAPACITY, DEFAULT_TANK_CAPACITY)
        )
        self._custom_capacity_unit = entry.data.get(
            CONF_TANK_CAPACITY_UNIT, DEFAULT_TANK_CAPACITY_UNIT
        )
        return self.async_show_form(
            step_id="reconfigure_custom_height",
            data_schema=_async_generate_custom_height_schema(
                medium_type=self._medium_type,
                custom_tank_height=existing_height,
                tank_capacity=existing_capacity,
                tank_capacity_unit=self._custom_capacity_unit,
                top_mount=is_top_mount,
                top_mount_sensor_height=entry.data.get(
                    CONF_TOP_MOUNT_SENSOR_HEIGHT, DEFAULT_TOP_MOUNT_SENSOR_HEIGHT
                ),
            ),
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the user step to pick a discovered device and select medium type."""
        if user_input is not None:
            self._address = user_input[CONF_ADDRESS]
            self._medium_type = user_input[CONF_MEDIUM_TYPE]
            # Top-mount sensors always use AIR regardless of user selection.
            service_info = self._discovered_service_infos.get(self._address)
            if service_info is not None and _is_top_mount_sensor(service_info):
                self._is_top_mount = True
                self._medium_type = MediumType.AIR.value
                return await self.async_step_ibc_tank_config()
            if self._medium_type == DEFAULT_MEDIUM_TYPE:
                return await self.async_step_tank_config()
            return await self.async_step_ibc_tank_config()

        current_addresses = self._async_current_ids(include_ignore=False)
        for discovery_info in async_discovered_service_info(self.hass, False):
            address = discovery_info.address
            if address in current_addresses or address in self._discovered_devices:
                continue
            device = DeviceData()
            if device.supported(discovery_info):
                self._discovered_devices[address] = (
                    device.title or device.get_device_name() or discovery_info.name
                )
                self._discovered_service_infos[address] = discovery_info

        if not self._discovered_devices:
            return self.async_abort(reason="no_devices_found")

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ADDRESS): vol.In(self._discovered_devices),
                    **_async_generate_medium_type_schema().schema,
                }
            ),
        )


class MopekaOptionsFlow(config_entries.OptionsFlow):
    """Handle options for the Mopeka component."""

    def __init__(self) -> None:
        """Initialize options flow."""
        self._medium_type: str | None = None
        self._custom_capacity_unit: str = DEFAULT_TANK_CAPACITY_UNIT
        # Preset tank size chosen by a top-mount device on the IBC preset step,
        # held while collecting CONF_TOP_MOUNT_SENSOR_HEIGHT on the next step.
        self._pending_tank_size: str | None = None

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle options flow — select medium type."""
        # Top-mount sensors have their medium type locked to AIR.
        if self.config_entry.data.get(CONF_TOP_MOUNT, False):
            self._medium_type = MediumType.AIR.value
            return await self.async_step_ibc_tank_config()

        if user_input is not None:
            self._medium_type = user_input[CONF_MEDIUM_TYPE]
            if self._medium_type == DEFAULT_MEDIUM_TYPE:
                return await self.async_step_tank_config()
            return await self.async_step_ibc_tank_config()

        return self.async_show_form(
            step_id="init",
            data_schema=_async_generate_medium_type_schema(
                medium_type=self.config_entry.data.get(CONF_MEDIUM_TYPE),
            ),
        )

    async def async_step_tank_config(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Select a propane tank preset."""
        # Invariant: async_step_init always sets this before routing here.
        if self._medium_type is None:
            raise HomeAssistantError(
                "Options flow step reached without a selected medium type"
            )
        if user_input is not None:
            tank_size = user_input.get(CONF_TANK_SIZE, TankSize.CUSTOM)
            if tank_size == TankSize.CUSTOM:
                return await self.async_step_custom_height()
            new_data = {
                **self.config_entry.data,
                CONF_MEDIUM_TYPE: self._medium_type,
                CONF_TANK_SIZE: tank_size,
                CONF_CUSTOM_TANK_HEIGHT: 0,
                CONF_TANK_CAPACITY: 0.0,
                CONF_TANK_CAPACITY_UNIT: DEFAULT_TANK_CAPACITY_UNIT,
            }
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=new_data
            )
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data={})

        existing_tank_size = _normalized_propane_tank_size_or_default(
            self.config_entry.data.get(CONF_TANK_SIZE, DEFAULT_TANK_SIZE)
        )
        return self.async_show_form(
            step_id="tank_config",
            data_schema=_async_generate_tank_schema(
                tank_size=existing_tank_size,
            ),
        )

    async def async_step_ibc_tank_config(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Select an IBC tote tank preset (non-propane media)."""
        # Invariant: async_step_init always sets this before routing here.
        if self._medium_type is None:
            raise HomeAssistantError(
                "Options flow step reached without a selected medium type"
            )
        if user_input is not None:
            tank_size = user_input.get(CONF_TANK_SIZE, TankSize.CUSTOM)
            if tank_size == TankSize.CUSTOM:
                return await self.async_step_custom_height()
            if self.config_entry.data.get(CONF_TOP_MOUNT, False):
                self._pending_tank_size = tank_size
                return await self.async_step_top_mount_height()
            new_data = {
                **self.config_entry.data,
                CONF_MEDIUM_TYPE: self._medium_type,
                CONF_TANK_SIZE: tank_size,
                CONF_CUSTOM_TANK_HEIGHT: 0,
                CONF_TANK_CAPACITY: 0.0,
                CONF_TANK_CAPACITY_UNIT: DEFAULT_TANK_CAPACITY_UNIT,
            }
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=new_data
            )
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data={})

        existing_tank_size = normalize_tank_size(
            self.config_entry.data.get(CONF_TANK_SIZE)
        )
        if existing_tank_size not in IBC_TANK_SIZES:
            existing_tank_size = DEFAULT_IBC_TANK_SIZE
        return self.async_show_form(
            step_id="ibc_tank_config",
            data_schema=_async_generate_ibc_tank_schema(
                tank_size=existing_tank_size,
            ),
        )

    async def async_step_top_mount_height(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Enter the top-mount sensor's mounting height (preset tank path)."""
        # Invariant: async_step_ibc_tank_config always sets this before routing here.
        if self._pending_tank_size is None:
            raise HomeAssistantError(
                "Top-mount sensor height step reached without a selected tank size"
            )
        if user_input is not None:
            sensor_height = _coerce_int(
                user_input.get(
                    CONF_TOP_MOUNT_SENSOR_HEIGHT, DEFAULT_TOP_MOUNT_SENSOR_HEIGHT
                ),
                DEFAULT_TOP_MOUNT_SENSOR_HEIGHT,
            )
            new_data = {
                **self.config_entry.data,
                CONF_MEDIUM_TYPE: self._medium_type,
                CONF_TANK_SIZE: self._pending_tank_size,
                CONF_CUSTOM_TANK_HEIGHT: 0,
                CONF_TANK_CAPACITY: 0.0,
                CONF_TANK_CAPACITY_UNIT: DEFAULT_TANK_CAPACITY_UNIT,
                CONF_TOP_MOUNT_SENSOR_HEIGHT: sensor_height,
            }
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=new_data
            )
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="top_mount_height",
            data_schema=_async_generate_top_mount_height_schema(
                top_mount_sensor_height=self.config_entry.data.get(
                    CONF_TOP_MOUNT_SENSOR_HEIGHT, DEFAULT_TOP_MOUNT_SENSOR_HEIGHT
                ),
            ),
        )

    async def async_step_custom_height(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Enter a custom tank height and total capacity."""
        # Invariant: async_step_init always sets this before routing here.
        if self._medium_type is None:
            raise HomeAssistantError(
                "Options flow step reached without a selected medium type"
            )
        is_top_mount = self.config_entry.data.get(CONF_TOP_MOUNT, False)
        if user_input is not None:
            capacity_unit = user_input.get(
                CONF_TANK_CAPACITY_UNIT,
                self._custom_capacity_unit,
            )
            if capacity_unit != self._custom_capacity_unit:
                self._custom_capacity_unit = capacity_unit
                return self.async_show_form(
                    step_id="custom_height",
                    data_schema=_async_generate_custom_height_schema(
                        medium_type=self._medium_type,
                        custom_tank_height=_coerce_int(
                            user_input.get(
                                CONF_CUSTOM_TANK_HEIGHT, DEFAULT_CUSTOM_TANK_HEIGHT
                            ),
                            DEFAULT_CUSTOM_TANK_HEIGHT,
                        ),
                        tank_capacity=_coerce_float(
                            user_input.get(CONF_TANK_CAPACITY, DEFAULT_TANK_CAPACITY),
                            DEFAULT_TANK_CAPACITY,
                        ),
                        tank_capacity_unit=self._custom_capacity_unit,
                        top_mount=is_top_mount,
                        top_mount_sensor_height=_coerce_int(
                            user_input.get(
                                CONF_TOP_MOUNT_SENSOR_HEIGHT,
                                DEFAULT_TOP_MOUNT_SENSOR_HEIGHT,
                            ),
                            DEFAULT_TOP_MOUNT_SENSOR_HEIGHT,
                        ),
                    ),
                )
            height, capacity, sensor_height, errors = _parse_custom_height_values(
                user_input, top_mount=is_top_mount
            )
            if errors:
                return self.async_show_form(
                    step_id="custom_height",
                    data_schema=_async_generate_custom_height_schema(
                        medium_type=self._medium_type,
                        custom_tank_height=_coerce_int(
                            user_input.get(
                                CONF_CUSTOM_TANK_HEIGHT, DEFAULT_CUSTOM_TANK_HEIGHT
                            ),
                            DEFAULT_CUSTOM_TANK_HEIGHT,
                        ),
                        tank_capacity=_coerce_float(
                            user_input.get(CONF_TANK_CAPACITY, DEFAULT_TANK_CAPACITY),
                            DEFAULT_TANK_CAPACITY,
                        ),
                        tank_capacity_unit=self._custom_capacity_unit,
                        top_mount=is_top_mount,
                        top_mount_sensor_height=_coerce_int(
                            user_input.get(
                                CONF_TOP_MOUNT_SENSOR_HEIGHT,
                                DEFAULT_TOP_MOUNT_SENSOR_HEIGHT,
                            ),
                            DEFAULT_TOP_MOUNT_SENSOR_HEIGHT,
                        ),
                    ),
                    errors=errors,
                )
            new_data = {
                **self.config_entry.data,
                CONF_MEDIUM_TYPE: self._medium_type,
                CONF_TANK_SIZE: TankSize.CUSTOM,
                CONF_CUSTOM_TANK_HEIGHT: height,
                CONF_TANK_CAPACITY: capacity,
                CONF_TANK_CAPACITY_UNIT: capacity_unit,
                CONF_TOP_MOUNT_SENSOR_HEIGHT: sensor_height,
            }
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=new_data
            )
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data={})

        existing_height = self.config_entry.data.get(
            CONF_CUSTOM_TANK_HEIGHT, DEFAULT_CUSTOM_TANK_HEIGHT
        )
        existing_capacity = float(
            self.config_entry.data.get(CONF_TANK_CAPACITY, DEFAULT_TANK_CAPACITY)
        )
        self._custom_capacity_unit = self.config_entry.data.get(
            CONF_TANK_CAPACITY_UNIT, DEFAULT_TANK_CAPACITY_UNIT
        )
        return self.async_show_form(
            step_id="custom_height",
            data_schema=_async_generate_custom_height_schema(
                medium_type=self._medium_type,
                custom_tank_height=existing_height,
                tank_capacity=existing_capacity,
                tank_capacity_unit=self._custom_capacity_unit,
                top_mount=is_top_mount,
                top_mount_sensor_height=self.config_entry.data.get(
                    CONF_TOP_MOUNT_SENSOR_HEIGHT, DEFAULT_TOP_MOUNT_SENSOR_HEIGHT
                ),
            ),
        )
