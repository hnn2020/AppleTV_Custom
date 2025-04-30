"""Custom Apple TV component for Home Assistant with enhanced swipe functionality."""

import logging

import voluptuous as vol

from homeassistant.components.apple_tv import DOMAIN as APPLE_TV_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, Platform
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.typing import ConfigType

DOMAIN = "apple_tv_custom"
_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.REMOTE]

# This allows YAML configuration as a fallback
CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Apple TV Custom component from YAML."""
    hass.data.setdefault(DOMAIN, {})
    
    # Check device registry for Apple TV devices
    device_reg = dr.async_get(hass)
    apple_tv_devices = []
    
    for device_id, device in device_reg.devices.items():
        for identifier in device.identifiers:
            if identifier[0] == APPLE_TV_DOMAIN:
                apple_tv_devices.append(device.name)
                break
    
    if apple_tv_devices:
        _LOGGER.info("Found %d Apple TV devices: %s", 
                    len(apple_tv_devices), ", ".join(apple_tv_devices))
    else:
        _LOGGER.warning("No Apple TV devices found in device registry. "
                      "Please set up the standard Apple TV integration first.")
                      
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Apple TV Custom from a config entry."""
    # Store our data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    # Check device registry for Apple TV devices
    device_reg = dr.async_get(hass)
    has_apple_tv = False
    
    for device_id, device in device_reg.devices.items():
        for identifier in device.identifiers:
            if identifier[0] == APPLE_TV_DOMAIN:
                has_apple_tv = True
                _LOGGER.info("Found Apple TV device: %s", device.name)
                
    if not has_apple_tv:
        _LOGGER.warning("No Apple TV devices found in device registry. "
                       "Please set up Apple TV devices first.")
    
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
