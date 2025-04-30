"""Custom Apple TV component for Home Assistant with enhanced swipe functionality."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

# Import from the original Apple TV component
from homeassistant.components.apple_tv import AppleTvConfigEntry

DOMAIN = "apple_tv_custom"
_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.REMOTE]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Apple TV Custom from a config entry."""
    # This component extends the built-in Apple TV component
    # We just need to set up the platform entities
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Apple TV Custom config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
