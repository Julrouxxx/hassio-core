"""The GoodHome integration.."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import GoodHomeCoordinator
from .goodhome import GoodHomeHelper

PLATFORMS: list[Platform] = [Platform.CLIMATE, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up GoodHome from a config entry.."""
    hass.data.setdefault(DOMAIN, {entry.entry_id: {}})
    hass.data[DOMAIN][entry.entry_id] = {
        "credentials": entry.data,
        "coordinator": GoodHomeCoordinator(
            hass, GoodHomeHelper(entry.data), entry.entry_id
        ),
    }
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, PLATFORMS[0])
    )
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, PLATFORMS[1])
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry.."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
