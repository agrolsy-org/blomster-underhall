from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
pytest.importorskip("homeassistant")
pytest.importorskip("pytest_homeassistant_custom_component")

from homeassistant.exceptions import ServiceValidationError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.blomster_maintenance import async_setup_entry, async_unload_entry
from custom_components.blomster_maintenance.const import (
    CONF_BLADE_INTERVAL_HOURS,
    CONF_BLADE_USAGE_ENTITY,
    CONF_BLADE_WARNING_ENTITY,
    CONF_WATER_INSTALLATION_DATE,
    CONF_WATER_SOURCE_ENTITY,
    DOMAIN,
    SERVICE_ACKNOWLEDGE_MAINTENANCE,
    SERVICE_CONFIGURE_ITEM,
    SERVICE_DELETE_MAINTENANCE,
    SERVICE_IMPORT_WATER_HISTORY,
    SERVICE_RECORD_MAINTENANCE,
    SERVICE_SET_WATER_BASELINE,
)
from custom_components.blomster_maintenance.storage import MaintenanceItem


ENTRY_DATA = {
    CONF_WATER_SOURCE_ENTITY: "sensor.water",
    CONF_WATER_INSTALLATION_DATE: date(2026, 1, 1),
    CONF_BLADE_USAGE_ENTITY: "sensor.blade_hours",
    CONF_BLADE_WARNING_ENTITY: "sensor.blade_limit",
    CONF_BLADE_INTERVAL_HOURS: 150,
}
SERVICES = {
    SERVICE_SET_WATER_BASELINE,
    SERVICE_CONFIGURE_ITEM,
    SERVICE_RECORD_MAINTENANCE,
    SERVICE_DELETE_MAINTENANCE,
    SERVICE_IMPORT_WATER_HISTORY,
    SERVICE_ACKNOWLEDGE_MAINTENANCE,
}


@pytest.mark.usefixtures("enable_custom_integrations")
async def test_setup_preserves_metadata_registers_services_and_unloads(hass):
    entry = MockConfigEntry(domain=DOMAIN, data=ENTRY_DATA, options={})
    entry.add_to_hass(hass)
    saved_item = MaintenanceItem(
        item_id="luba_blades",
        name="Mina knivar",
        location="Garage",
        warning_entities=["binary_sensor.external_warning"],
    )

    async def load_with_saved_item(store):
        store.items = {"luba_blades": saved_item}

    with (
        patch("custom_components.blomster_maintenance.MaintenanceStore.async_load", load_with_saved_item),
        patch("custom_components.blomster_maintenance.MaintenanceStore.async_save", new=AsyncMock()),
        patch("custom_components.blomster_maintenance.async_import_water_history", new=AsyncMock(return_value=True)),
        patch("custom_components.blomster_maintenance.async_start_water_tracking", new=AsyncMock(return_value=lambda: None)),
        patch("custom_components.blomster_maintenance.async_setup_frontend", new=AsyncMock()),
        patch.object(hass.http, "async_register_static_paths", new=AsyncMock()),
        patch.object(hass.config_entries, "async_forward_entry_setups", new=AsyncMock()),
        patch.object(hass.config_entries, "async_unload_platforms", new=AsyncMock(return_value=True)),
    ):
        assert await async_setup_entry(hass, entry)
        store = hass.data[DOMAIN][entry.entry_id]
        assert store.items["luba_blades"].name == "Mina knivar"
        assert store.items["luba_blades"].location == "Garage"
        assert store.items["luba_blades"].warning_entities == ["binary_sensor.external_warning"]
        assert SERVICES == {name for name in SERVICES if hass.services.has_service(DOMAIN, name)}

        for service in SERVICES - {SERVICE_IMPORT_WATER_HISTORY}:
            with pytest.raises(ServiceValidationError):
                await hass.services.async_call(DOMAIN, service, {}, blocking=True)

        assert await async_unload_entry(hass, entry)
        assert DOMAIN not in hass.data or entry.entry_id not in hass.data[DOMAIN]
        assert not any(hass.services.has_service(DOMAIN, name) for name in SERVICES)


@pytest.mark.usefixtures("enable_custom_integrations")
async def test_options_listener_reloads_entry(hass):
    entry = MockConfigEntry(domain=DOMAIN, data=ENTRY_DATA, options={})
    entry.add_to_hass(hass)
    with patch.object(hass.config_entries, "async_reload", new=AsyncMock(return_value=True)) as reload_entry:
        from custom_components.blomster_maintenance import _async_reload_entry

        await _async_reload_entry(hass, entry)
    reload_entry.assert_awaited_once_with(entry.entry_id)
