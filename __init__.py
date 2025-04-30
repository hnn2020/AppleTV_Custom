"""Custom Apple TV component for Home Assistant with enhanced swipe functionality."""

import logging

import voluptuous as vol

from homeassistant.components.apple_tv import DOMAIN as APPLE_TV_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, Platform
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType

DOMAIN = "apple_tv_custom"
_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.REMOTE]

# This allows YAML configuration as a fallback
CONFIG_SCHEMA = vol.Schema({DOMAIN: cv.schema_with_slug_keys(cv.empty_dict)}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Apple TV Custom component from YAML."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Apple TV Custom from a config entry."""
    # Make sure the standard Apple TV component is set up first
    # so we can build on top of its functionality
    if not hass.data.get(APPLE_TV_DOMAIN):
        _LOGGER.warning("Standard Apple TV component not set up. Make sure it's configured correctly.")
        return False
        
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    # Set up platform(s)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(update_listener))
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Apple TV Custom config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        
    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)
