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
from homeassistant.helpers import device_registry as dr, entity_registry as er
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
    
    # Check if device registry has Apple TV devices
    device_reg = dr.async_get(hass)
    entity_reg = er.async_get(hass)
    
    # Find Apple TV devices in the device registry
    apple_tv_devices = []
    
    for device_id, device in device_reg.devices.items():
        # Check if any of the device's identifiers belong to the Apple TV domain
        for identifier in device.identifiers:
            if identifier[0] == APPLE_TV_DOMAIN:
                _LOGGER.info(f"Found Apple TV device: {device.name} with id {device_id}")
                apple_tv_devices.append((device_id, device.name))
                break
    
    if not apple_tv_devices:
        _LOGGER.warning("No Apple TV devices found in device registry")
        return
        
    entities = []
    
    # Get all media_player entities for each Apple TV device
    for device_id, device_name in apple_tv_devices:
        # Search for the original Apple TV entities
        remote_entities = []
        
        # Find existing remotes for this device
        for entity in entity_reg.entities.values():
            if (entity.domain == "remote" and 
                entity.platform == APPLE_TV_DOMAIN and
                entity.device_id == device_id):
                remote_entities.append(entity)
                
        if not remote_entities:
            _LOGGER.warning(f"No remote entities found for Apple TV device: {device_name}")
            continue
            
        # Create custom remote for each found entity
        for remote_entity in remote_entities:
            entity_id = remote_entity.entity_id
            unique_id = remote_entity.unique_id
            
            # Create our entity
            _LOGGER.info(f"Adding swipe remote for {device_name} based on {entity_id}")
            entities.append(
                AppleTVRemoteWithSwipe(
                    device_name,
                    device_id,  # Use device ID for device info
                    unique_id,  # Use original entity ID for unique ID
                    entity_id   # Store original entity ID for reference
                )
            )
            
    if not entities:
        _LOGGER.warning("No Apple TV remotes were created. Please set up the standard Apple TV integration first.")
        return
        
    async_add_entities(entities)


class AppleTVRemoteWithSwipe(RemoteEntity):
    """Device that sends commands to an Apple TV with swipe support."""

    _attr_has_entity_name = True
    
    def __init__(self, name, device_id, unique_id, source_entity_id):
        """Initialize the Apple TV remote with swipe."""
        self._attr_name = f"{name} with Swipe"
        self._attr_unique_id = f"{unique_id}_swipe"
        self._device_id = device_id
        self._source_entity_id = source_entity_id
        self._source_entity = None
        self._available = True
        
    @property
    def device_info(self):
        """Return device info for this device."""
        return {"identifiers": {(DOMAIN, self._device_id)}}
    
    async def async_added_to_hass(self):
        """Handle being added to Home Assistant."""
        await super().async_added_to_hass()
        # Get the source entity
        self._source_entity = self.hass.states.get(self._source_entity_id)
        
    @property
    def is_on(self) -> bool:
        """Return true if device is on."""
        if self._source_entity:
            state = self.hass.states.get(self._source_entity_id)
            return state is not None and state.state != "unavailable"
        return self._available

    async def async_send_command(self, command: Iterable[str], **kwargs: Any) -> None:
        """Send a command to one device."""
        num_repeats = kwargs.get(ATTR_NUM_REPEATS, 1)
        delay = kwargs.get(ATTR_DELAY_SECS, DEFAULT_DELAY_SECS)
        
        # Pass swipe commands to the original entity
        for _ in range(num_repeats):
            for single_command in command:
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
                    
                    # Use the service to send the swipe command to the source entity
                    _LOGGER.info("Sending swipe %s (dx=%f, dy=%f) via %s", 
                                direction, dx, dy, self._source_entity_id)
                    
                    # Create service data for the remote.send_command service
                    service_data = {
                        "entity_id": self._source_entity_id,
                        "command": [single_command],
                        "num_repeats": 1,
                        "delay_secs": delay,
                        "hold_secs": kwargs.get(ATTR_HOLD_SECS, DEFAULT_HOLD_SECS),
                        ATTR_SWIPE_DELTA: delta,
                    }
                    
                    # Call the service
                    await self.hass.services.async_call(
                        "remote", "send_command", service_data, blocking=True
                    )
                    
                    # Wait for the specified delay
                    await asyncio.sleep(delay)
                else:
                    # Forward other commands to the original entity
                    service_data = {
                        "entity_id": self._source_entity_id,
                        "command": [single_command],
                        "num_repeats": 1,
                        "delay_secs": delay,
                        "hold_secs": kwargs.get(ATTR_HOLD_SECS, DEFAULT_HOLD_SECS),
                    }
                    
                    await self.hass.services.async_call(
                        "remote", "send_command", service_data, blocking=True
                    )
