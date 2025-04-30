"""Remote control support for Apple TV with enhanced swipe functionality."""

import asyncio
from collections.abc import Iterable
import logging
from typing import Any

from pyatv.const import InputAction

from homeassistant.components.apple_tv import DOMAIN as APPLE_TV_DOMAIN
from homeassistant.components.apple_tv.entity import AppleTVEntity as OriginalAppleTVEntity
from homeassistant.components.remote import (
    ATTR_DELAY_SECS,
    ATTR_HOLD_SECS,
    ATTR_NUM_REPEATS,
    DEFAULT_DELAY_SECS,
    DEFAULT_HOLD_SECS,
    RemoteEntity,
)
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 0
COMMAND_TO_ATTRIBUTE = {
    "wakeup": ("power", "turn_on"),
    "suspend": ("power", "turn_off"),
    "turn_on": ("power", "turn_on"),
    "turn_off": ("power", "turn_off"),
    "volume_up": ("audio", "volume_up"),
    "volume_down": ("audio", "volume_down"),
}

# Custom swipe attributes
ATTR_SWIPE_DIRECTION = "direction"
ATTR_SWIPE_DELTA = "delta"
SWIPE_DIRECTIONS = ["left", "right", "up", "down"]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Load Apple TV remote based on a config entry."""
    # Look for Apple TV devices
    _LOGGER.info("Setting up Apple TV Custom remote")
    
    if APPLE_TV_DOMAIN not in hass.data:
        _LOGGER.error("Apple TV domain not found in Home Assistant data")
        return
    
    # Loop through Apple TV entries in Home Assistant
    apple_tv_entries = hass.config_entries.async_entries(APPLE_TV_DOMAIN)
    _LOGGER.info("Found %d Apple TV configuration entries", len(apple_tv_entries))
    
    entities = []
    
    # Find and add all Apple TV devices with SwipeRemote functionality
    for atv_entry in apple_tv_entries:
        entry_id = atv_entry.entry_id
        if entry_id not in hass.data[APPLE_TV_DOMAIN]:
            _LOGGER.warning("Entry %s does not have manager data in Apple TV domain", entry_id)
            continue
            
        # Get the device manager from the Apple TV integration
        manager = hass.data[APPLE_TV_DOMAIN][entry_id]
        device_name = atv_entry.data.get(CONF_NAME, "Unknown")
        
        _LOGGER.info("Adding Apple TV Custom Remote for %s", device_name)
        entities.append(AppleTVRemoteWithSwipe(device_name, atv_entry.unique_id, manager))
    
    if not entities:
        _LOGGER.warning("No Apple TV devices found. Make sure you have set up Apple TV integration.")
    
    async_add_entities(entities)


class AppleTVRemoteWithSwipe(OriginalAppleTVEntity, RemoteEntity):
    """Device that sends commands to an Apple TV with swipe support."""

    _attr_has_entity_name = True
    
    def __init__(self, name, identifier, manager):
        """Initialize the Apple TV remote with swipe."""
        super().__init__(name, identifier, manager)
        self._attr_name = f"{name} with Swipe"
        self._attr_unique_id = f"{identifier}_swipe_remote"
    
    @property
    def is_on(self) -> bool:
        """Return true if device is on."""
        return self.atv is not None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the device on."""
        await self.manager.connect()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the device off."""
        await self.manager.disconnect()

    async def async_send_command(self, command: Iterable[str], **kwargs: Any) -> None:
        """Send a command to one device."""
        num_repeats = kwargs.get(ATTR_NUM_REPEATS, 1)
        delay = kwargs.get(ATTR_DELAY_SECS, DEFAULT_DELAY_SECS)
        hold_secs = kwargs.get(ATTR_HOLD_SECS, DEFAULT_HOLD_SECS)

        if not self.atv:
            _LOGGER.error("Unable to send commands, not connected to %s", self.name)
            return

        for _ in range(num_repeats):
            for single_command in command:
                # Handle swipe commands
                if single_command.startswith("swipe_"):
                    direction = single_command.split("_")[1]
                    if direction not in SWIPE_DIRECTIONS:
                        _LOGGER.error("Invalid swipe direction: %s", direction)
                        continue
                    
                    delta = kwargs.get(ATTR_SWIPE_DELTA, 0.5)  # Default delta value
                    
                    # Map direction to the appropriate delta values
                    dx, dy = 0, 0
                    if direction == "left":
                        dx = -delta
                    elif direction == "right":
                        dx = delta
                    elif direction == "up":
                        dy = -delta
                    elif direction == "down":
                        dy = delta
                    
                    _LOGGER.info("Sending swipe %s (dx=%f, dy=%f)", direction, dx, dy)
                    try:
                        await self.atv.remote_control.swipe(dx, dy)
                    except Exception as ex:
                        _LOGGER.error("Failed to execute swipe: %s", ex)
                    
                    await asyncio.sleep(delay)
                    continue
                
                # Handle regular commands
                attr_value: Any = None
                if attributes := COMMAND_TO_ATTRIBUTE.get(single_command):
                    attr_value = self.atv
                    for attr_name in attributes:
                        attr_value = getattr(attr_value, attr_name, None)
                if not attr_value:
                    attr_value = getattr(self.atv.remote_control, single_command, None)
                if not attr_value:
                    raise ValueError(f"Command {single_command} not found. Exiting sequence")

                _LOGGER.debug("Sending command %s", single_command)

                if hold_secs >= 1:
                    await attr_value(action=InputAction.Hold)
                else:
                    await attr_value()

                await asyncio.sleep(delay)
