"""Fixtures for real Home Assistant end-to-end tests.

These tests run against the actual `homeassistant` package and
`pytest-homeassistant-custom-component` test harness (real `hass` fixture,
`MockConfigEntry`, etc.), unlike the stub-based unit tests in `tests/`,
which hand-roll lightweight fakes for `homeassistant.*` and load the
integration source directly via `importlib`.

Kept in a separate top-level directory from `tests/` so pytest never
collects both suites' conftests into the same module — the stub-based
suite mutates `sys.modules` with fake `homeassistant`/`custom_components`
entries, which would corrupt real imports if the two suites shared a
session.
"""

from __future__ import annotations

import pytest

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Enable loading custom_components/mopeka for every test in this suite."""
