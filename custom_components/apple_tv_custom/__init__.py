"""Apple TV Custom integration."""
from __future__ import annotations

import logging
from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.remote import ATTR_COMMAND
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, SERVICE_TURN_OFF, SERVICE_TURN_ON
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.entity_platform import EntityPlatform

from .const import APPLE_TV_DOMAIN, DOMAIN, SERVICE_SEND_COMMAND, SERVICE_SEND_COMMAND_BUTTON

_LOGGER = logging.getLogger(__name__)

# Supported platforms
PLATFORMS = [Platform.REMOTE]

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema({}),
    },
    extra=vol.ALLOW_EXTRA,
)

SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_COMMAND): cv.string,
        vol.Optional(SERVICE_SEND_COMMAND_BUTTON): cv.string,
    }
)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Apple TV Custom component."""
    _LOGGER.debug("Setting up Apple TV Custom component")
    hass.data.setdefault(DOMAIN, {})

    # Check if the standard Apple TV component is available
    if APPLE_TV_DOMAIN not in hass.data:
        _LOGGER.warning(
            "Standard Apple TV component not found in hass.data. "
            "The Apple TV Custom component requires the standard Apple TV integration to be set up first."
        )
        # Don't fail setup - we'll check again during entry setup
    else:
        _LOGGER.debug("Found standard Apple TV component in hass.data")
        
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Apple TV Custom from a config entry."""
    _LOGGER.debug("Setting up Apple TV Custom entry: %s", entry.entry_id)
    
    # Store config entry in hass data
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entry.data
    
    # Double check if the standard Apple TV component is available
    if APPLE_TV_DOMAIN not in hass.data:
        _LOGGER.error(
            "Standard Apple TV component not available. "
            "Please make sure the Apple TV integration is set up and functioning properly."
        )
        return False
    
    # Check if there are any Apple TV devices configured
    apple_tv_data = hass.data.get(APPLE_TV_DOMAIN, {})
    if not apple_tv_data:
        _LOGGER.error(
            "No Apple TV devices found. "
            "Please make sure at least one Apple TV device is set up in Home Assistant."
        )
        return False
        
    _LOGGER.debug("Found Apple TV data: %s", apple_tv_data)
    
    # Forward entry to platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    entry.async_on_unload(entry.add_update_listener(update_listener))
    
    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    _LOGGER.debug("Config entry was updated, reloading integration: %s", entry.entry_id)
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok 