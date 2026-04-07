from __future__ import annotations

import asyncio


class _FakeConfigEntries:
    def __init__(self):
        self.forward_calls = []
        self.reload_calls = []
        self.unload_calls = []

    async def async_forward_entry_setups(self, entry, platforms):
        self.forward_calls.append((entry, platforms))

    async def async_reload(self, entry_id):
        self.reload_calls.append(entry_id)

    async def async_unload_platforms(self, entry, platforms):
        self.unload_calls.append((entry, platforms))
        return True


class _FakeHass:
    def __init__(self):
        self.config_entries = _FakeConfigEntries()


class _FakeEntry:
    def __init__(self):
        self.unique_id = "AA:BB"
        self.data = {"medium_type": "propane"}
        self.runtime_data = None
        self.entry_id = "entry1"
        self.unload_callbacks = []
        self.listeners = []

    def async_on_unload(self, cb):
        self.unload_callbacks.append(cb)

    def add_update_listener(self, cb):
        self.listeners.append(cb)
        return lambda: None


def test_device_key_mapping(device_module, stub_types):
    device_key = stub_types["DeviceKey"]("tank_level", "dev1")
    result = device_module.device_key_to_bluetooth_entity_key(device_key)
    assert result.key == "tank_level"
    assert result.device_id == "dev1"


def test_async_setup_entry_sets_coordinator(integration_module):
    hass = _FakeHass()
    entry = _FakeEntry()

    result = asyncio.run(integration_module.async_setup_entry(hass, entry))

    assert result is True
    assert entry.runtime_data is not None
    assert len(entry.unload_callbacks) == 2
    assert hass.config_entries.forward_calls


def test_update_listener_triggers_reload(integration_module):
    hass = _FakeHass()
    entry = _FakeEntry()

    asyncio.run(integration_module.update_listener(hass, entry))

    assert hass.config_entries.reload_calls == ["entry1"]


def test_async_unload_entry(integration_module):
    hass = _FakeHass()
    entry = _FakeEntry()

    result = asyncio.run(integration_module.async_unload_entry(hass, entry))

    assert result is True
    assert hass.config_entries.unload_calls


def test_async_remove_config_entry_device_returns_true(integration_module):
    hass = _FakeHass()
    entry = _FakeEntry()

    result = asyncio.run(
        integration_module.async_remove_config_entry_device(hass, entry, object())
    )

    assert result is True
