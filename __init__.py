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
CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Apple TV Custom component from YAML."""
    hass.data.setdefault(DOMAIN, {})
    # Log discovered Apple TV devices for debugging
    if APPLE_TV_DOMAIN in hass.data:
        _LOGGER.info("Found standard Apple TV component with data: %s", 
                    {key: "..." for key in hass.data[APPLE_TV_DOMAIN].keys()})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Apple TV Custom from a config entry."""
    # Store our data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    # Check if standard Apple TV component is loaded
    has_apple_tv = False
    if APPLE_TV_DOMAIN in hass.data:
        # Check if we have any entries in the Apple TV domain
        has_entries = bool(hass.config_entries.async_entries(APPLE_TV_DOMAIN))
        if has_entries:
            has_apple_tv = True
            _LOGGER.info("Found Apple TV entries: %s", 
                        [e.title for e in hass.config_entries.async_entries(APPLE_TV_DOMAIN)])
    
    if not has_apple_tv:
        _LOGGER.warning("Standard Apple TV component not set up or no devices found. "
                       "Please set up Apple TV devices first.")
        _LOGGER.debug("Available domains in hass.data: %s", list(hass.data.keys()))
        # Continue anyway since the user might add devices later
    
    # Set up platforms
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
