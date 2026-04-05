"""Config flow for mopeka integration."""

from __future__ import annotations

from enum import Enum
from typing import Any

from mopeka_iot_ble import MopekaIOTBluetoothDeviceData as DeviceData
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import callback
from homeassistant.helpers import selector

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
    DEFAULT_CUSTOM_TANK_HEIGHT,
    DEFAULT_IBC_TANK_SIZE,
    DEFAULT_MEDIUM_TYPE,
    DEFAULT_TANK_CAPACITY,
    DEFAULT_TANK_CAPACITY_UNIT,
    DEFAULT_TANK_SIZE,
    DOMAIN,
    IBC_TANK_SIZES,
    MOPEKA_MANUFACTURER_ID,
    PROPANE_TANK_SIZES,
    TOP_MOUNT_MODEL_IDS,
    MediumType,
    TankSize,
)


def _is_top_mount_sensor(discovery_info: BluetoothServiceInfoBleak) -> bool:
    """Return True if the device is a top-mount sensor (TD40/TD200).

    Top-mount sensors always measure the air gap above the liquid surface and
    must use the AIR acoustic coefficient — the user cannot override this.
    """
    mfr_data = discovery_info.manufacturer_data.get(MOPEKA_MANUFACTURER_ID)
    if not mfr_data:
        return False
    return (mfr_data[0] & 0x0F) in TOP_MOUNT_MODEL_IDS


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

_CUSTOM_CAPACITY_SELECTOR = selector.NumberSelector(
    selector.NumberSelectorConfig(
        min=0,
        max=100000,
        step=0.1,
        unit_of_measurement="gal",
        mode=selector.NumberSelectorMode.BOX,
    )
)

_CUSTOM_CAPACITY_KG_SELECTOR = selector.NumberSelector(
    selector.NumberSelectorConfig(
        min=0,
        max=100000,
        step=0.1,
        unit_of_measurement="kg",
        mode=selector.NumberSelectorMode.BOX,
    )
)

_CUSTOM_CAPACITY_L_SELECTOR = selector.NumberSelector(
    selector.NumberSelectorConfig(
        min=0,
        max=100000,
        step=0.1,
        unit_of_measurement="L",
        mode=selector.NumberSelectorMode.BOX,
    )
)


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
) -> vol.Schema:
    """Return a schema containing the custom tank height and capacity inputs."""
    schema: dict[Any, Any] = {
        vol.Required(
            CONF_CUSTOM_TANK_HEIGHT,
            default=custom_tank_height
            if custom_tank_height is not None
            else DEFAULT_CUSTOM_TANK_HEIGHT,
        ): _CUSTOM_HEIGHT_SELECTOR,
    }

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
    ] = (
        _CUSTOM_CAPACITY_KG_SELECTOR
        if is_propane and selected_unit == CAPACITY_UNIT_KILOGRAMS
        else _CUSTOM_CAPACITY_L_SELECTOR
        if (not is_propane and selected_unit == CAPACITY_UNIT_LITERS)
        else _CUSTOM_CAPACITY_SELECTOR
    )

    return vol.Schema(schema)


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
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        device = DeviceData()
        if not device.supported(discovery_info):
            return self.async_abort(reason="not_supported")
        self._discovery_info = discovery_info
        self._discovered_device = device
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm discovery and select medium type."""
        assert self._discovered_device is not None
        device = self._discovered_device
        assert self._discovery_info is not None
        discovery_info = self._discovery_info
        title = device.title or device.get_device_name() or discovery_info.name

        # Top-mount sensors (TD40/TD200) always use AIR — bypass the medium type form.
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
    ) -> ConfigFlowResult:
        """Create the config entry with the collected parameters."""
        data = {
            CONF_MEDIUM_TYPE: self._medium_type,
            CONF_TANK_SIZE: tank_size,
            CONF_CUSTOM_TANK_HEIGHT: custom_height,
            CONF_TANK_CAPACITY: tank_capacity,
            CONF_TANK_CAPACITY_UNIT: tank_capacity_unit,
            CONF_TOP_MOUNT: self._is_top_mount,
        }
        if self._discovery_info is not None:
            return self.async_create_entry(title=self._title, data=data)
        assert self._address is not None
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

    async def async_step_custom_height(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Enter a custom tank height and total capacity."""
        if user_input is not None:
            height = int(
                user_input.get(CONF_CUSTOM_TANK_HEIGHT, DEFAULT_CUSTOM_TANK_HEIGHT)
            )
            capacity = float(user_input.get(CONF_TANK_CAPACITY, DEFAULT_TANK_CAPACITY))
            capacity_unit = user_input.get(
                CONF_TANK_CAPACITY_UNIT, DEFAULT_TANK_CAPACITY_UNIT
            )
            if capacity_unit != self._custom_capacity_unit:
                self._custom_capacity_unit = capacity_unit
                return self.async_show_form(
                    step_id="custom_height",
                    data_schema=_async_generate_custom_height_schema(
                        medium_type=self._medium_type,
                        custom_tank_height=height,
                        tank_capacity=capacity,
                        tank_capacity_unit=self._custom_capacity_unit,
                    ),
                )
            return await self._async_create_config_entry(
                TankSize.CUSTOM, height, capacity, capacity_unit
            )

        self._custom_capacity_unit = DEFAULT_TANK_CAPACITY_UNIT
        return self.async_show_form(
            step_id="custom_height",
            data_schema=_async_generate_custom_height_schema(
                medium_type=self._medium_type,
                tank_capacity_unit=self._custom_capacity_unit,
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

        existing_tank_size = entry.data.get(CONF_TANK_SIZE, DEFAULT_TANK_SIZE)
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

        existing_tank_size = entry.data.get(CONF_TANK_SIZE)
        if existing_tank_size not in IBC_TANK_SIZES:
            existing_tank_size = DEFAULT_IBC_TANK_SIZE
        return self.async_show_form(
            step_id="reconfigure_ibc_tank_config",
            data_schema=_async_generate_ibc_tank_schema(
                tank_size=existing_tank_size,
            ),
        )

    async def async_step_reconfigure_custom_height(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration — enter custom tank height and total capacity."""
        entry = self._get_reconfigure_entry()
        if user_input is not None:
            height = int(
                user_input.get(CONF_CUSTOM_TANK_HEIGHT, DEFAULT_CUSTOM_TANK_HEIGHT)
            )
            capacity = float(user_input.get(CONF_TANK_CAPACITY, DEFAULT_TANK_CAPACITY))
            capacity_unit = user_input.get(
                CONF_TANK_CAPACITY_UNIT,
                entry.data.get(CONF_TANK_CAPACITY_UNIT, DEFAULT_TANK_CAPACITY_UNIT),
            )
            if capacity_unit != self._custom_capacity_unit:
                self._custom_capacity_unit = capacity_unit
                return self.async_show_form(
                    step_id="reconfigure_custom_height",
                    data_schema=_async_generate_custom_height_schema(
                        medium_type=self._medium_type,
                        custom_tank_height=height,
                        tank_capacity=capacity,
                        tank_capacity_unit=self._custom_capacity_unit,
                    ),
                )
            return self.async_update_reload_and_abort(
                entry,
                data_updates={
                    CONF_MEDIUM_TYPE: self._medium_type,
                    CONF_TANK_SIZE: TankSize.CUSTOM,
                    CONF_CUSTOM_TANK_HEIGHT: height,
                    CONF_TANK_CAPACITY: capacity,
                    CONF_TANK_CAPACITY_UNIT: capacity_unit,
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
        assert self._medium_type is not None
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

        existing_tank_size = self.config_entry.data.get(
            CONF_TANK_SIZE, DEFAULT_TANK_SIZE
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
        assert self._medium_type is not None
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

        existing_tank_size = self.config_entry.data.get(CONF_TANK_SIZE)
        if existing_tank_size not in IBC_TANK_SIZES:
            existing_tank_size = DEFAULT_IBC_TANK_SIZE
        return self.async_show_form(
            step_id="ibc_tank_config",
            data_schema=_async_generate_ibc_tank_schema(
                tank_size=existing_tank_size,
            ),
        )

    async def async_step_custom_height(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Enter a custom tank height and total capacity."""
        assert self._medium_type is not None
        if user_input is not None:
            height = int(
                user_input.get(CONF_CUSTOM_TANK_HEIGHT, DEFAULT_CUSTOM_TANK_HEIGHT)
            )
            capacity = float(user_input.get(CONF_TANK_CAPACITY, DEFAULT_TANK_CAPACITY))
            capacity_unit = user_input.get(
                CONF_TANK_CAPACITY_UNIT,
                self.config_entry.data.get(
                    CONF_TANK_CAPACITY_UNIT, DEFAULT_TANK_CAPACITY_UNIT
                ),
            )
            if capacity_unit != self._custom_capacity_unit:
                self._custom_capacity_unit = capacity_unit
                return self.async_show_form(
                    step_id="custom_height",
                    data_schema=_async_generate_custom_height_schema(
                        medium_type=self._medium_type,
                        custom_tank_height=height,
                        tank_capacity=capacity,
                        tank_capacity_unit=self._custom_capacity_unit,
                    ),
                )
            new_data = {
                **self.config_entry.data,
                CONF_MEDIUM_TYPE: self._medium_type,
                CONF_TANK_SIZE: TankSize.CUSTOM,
                CONF_CUSTOM_TANK_HEIGHT: height,
                CONF_TANK_CAPACITY: capacity,
                CONF_TANK_CAPACITY_UNIT: capacity_unit,
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
            ),
        )
