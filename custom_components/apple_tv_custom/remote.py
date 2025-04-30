"""Support for Apple TV Custom Remote platform."""

from __future__ import annotations

import logging
from typing import Any

from pyatv.const import Command

from homeassistant.components.apple_tv import DOMAIN as APPLE_TV_DOMAIN
from homeassistant.components.remote import RemoteEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Dictionary mapping custom commands to Apple TV commands
COMMAND_MAP = {
    "swipe_up": Command.UP,
    "swipe_down": Command.DOWN,
    "swipe_left": Command.LEFT,
    "swipe_right": Command.RIGHT,
    "select": Command.SELECT,
    "menu": Command.MENU,
    "home": Command.HOME,
    "home_hold": Command.MENU_HOLD,
    "top_menu": Command.TOP_MENU,
    "suspend": Command.SUSPEND,
    "wakeup": Command.WAKEUP,
    "volume_up": Command.VOLUME_UP,
    "volume_down": Command.VOLUME_DOWN,
}


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Apple TV Custom Remote platform."""
    if discovery_info is None:
        return

    entities = []
    # Add code to create entities
    async_add_entities(entities, True)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Apple TV Custom Remote from a config entry."""
    # Check if standard Apple TV component is set up
    if APPLE_TV_DOMAIN not in hass.data:
        _LOGGER.error("Apple TV domain not found in Home Assistant data")
        return
    
    apple_tv_data = hass.data[APPLE_TV_DOMAIN]
    if not apple_tv_data:
        _LOGGER.error("Standard Apple TV component not set up or no devices found")
        return
    
    _LOGGER.debug("Apple TV data structure: %s", apple_tv_data)
    
    entities = []
    
    # Try different ways to access Apple TV devices
    for atv_id, atv_data in apple_tv_data.items():
        _LOGGER.debug("Examining Apple TV device with ID %s: %s", atv_id, atv_data)
        
        # Case 1: Standard structure with apple_tv attribute
        if hasattr(atv_data, "apple_tv") and hasattr(atv_data, "name"):
            atv = atv_data.apple_tv
            name = atv_data.name
            entities.append(AppleTVCustomRemote(atv, name, atv_id))
            _LOGGER.debug("Added remote for %s using standard structure", name)
        
        # Case 2: Dictionary structure with apple_tv key
        elif isinstance(atv_data, dict) and "apple_tv" in atv_data and "name" in atv_data:
            atv = atv_data["apple_tv"]
            name = atv_data["name"]
            identifier = atv_data.get("identifier", atv_id)
            entities.append(AppleTVCustomRemote(atv, name, identifier))
            _LOGGER.debug("Added remote for %s using dictionary structure", name)
        
        # Case 3: Nested structure where atv_data might contain entries
        elif isinstance(atv_data, dict) and "entries" in atv_data:
            for entry in atv_data["entries"]:
                if hasattr(entry, "apple_tv") and hasattr(entry, "name"):
                    atv = entry.apple_tv
                    name = entry.name
                    identifier = getattr(entry, "identifier", atv_id)
                    entities.append(AppleTVCustomRemote(atv, name, identifier))
                    _LOGGER.debug("Added remote for %s from entries", name)
        
        # Case 4: Other possible structures
        else:
            _LOGGER.warning("Unknown Apple TV data structure for %s: %s", atv_id, atv_data)
            # Try to extract apple_tv and name if possible
            atv = None
            name = None
            
            if hasattr(atv_data, "__dict__"):
                attrs = atv_data.__dict__
                if "apple_tv" in attrs:
                    atv = attrs["apple_tv"]
                if "name" in attrs:
                    name = attrs["name"]
            
            if atv and name:
                entities.append(AppleTVCustomRemote(atv, name, atv_id))
                _LOGGER.debug("Added remote for %s using attribute extraction", name)
    
    if not entities:
        _LOGGER.warning("No Apple TV devices found to set up custom remotes")
        return
        
    async_add_entities(entities, True)


class AppleTVCustomRemote(RemoteEntity):
    """Representation of an Apple TV Custom Remote."""

    def __init__(self, apple_tv, name, identifier):
        """Initialize the Apple TV Custom Remote."""
        self._apple_tv = apple_tv
        self._name = name
        self._identifier = identifier
        self._attr_unique_id = f"{identifier}_remote_custom"
        self._attr_is_on = True
        self._attr_device_info = {
            "identifiers": {(DOMAIN, identifier)},
            "name": f"{name} (Custom Remote)",
            "manufacturer": "Apple",
            "model": "Apple TV Custom Remote",
            "sw_version": "0.1.0",
            "via_device": (APPLE_TV_DOMAIN, identifier),
        }
        
    @property
    def name(self):
        """Return the name of the device."""
        return f"{self._name} Custom Remote"
        
    @property
    def available(self) -> bool:
        """Return if the remote is available."""
        return self._apple_tv is not None
        
    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        if not self._apple_tv:
            _LOGGER.error("No Apple TV instance available")
            return
            
        try:
            await self._apple_tv.power.turn_on()
        except Exception as ex:
            _LOGGER.error("Failed to turn on Apple TV: %s", ex)
        
    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        if not self._apple_tv:
            _LOGGER.error("No Apple TV instance available")
            return
            
        try:
            await self._apple_tv.power.turn_off()
        except Exception as ex:
            _LOGGER.error("Failed to turn off Apple TV: %s", ex)
        
    async def async_send_command(self, command, **kwargs):
        """Send a command to the device."""
        if not self._apple_tv:
            _LOGGER.error("No Apple TV instance available")
            return
            
        num_repeats = kwargs.get("num_repeats", 1)
        delay_secs = kwargs.get("delay_secs", 0)
        hold_secs = kwargs.get("hold_secs", 0)
        
        for _ in range(num_repeats):
            for single_command in command:
                try:
                    await self._send_command(single_command, hold_secs)
                    if delay_secs > 0:
                        import asyncio
                        await asyncio.sleep(delay_secs)
                except Exception as ex:
                    _LOGGER.error("Error sending command %s: %s", single_command, ex)
            
    async def _send_command(self, command, hold_secs=0):
        """Send a single command to the device."""
        if not self._apple_tv:
            _LOGGER.error("No Apple TV instance available")
            return
        
        remote = self._apple_tv.remote_control
        
        # Check if we need to use a different command method based on pyatv version
        if hasattr(remote, "press_and_hold") and hold_secs > 0:
            # Newer pyatv version with press_and_hold support
            press_and_hold = getattr(remote, "press_and_hold", None)
            if press_and_hold and callable(press_and_hold):
                _LOGGER.debug("Using press_and_hold method for command: %s, hold: %s", command, hold_secs)
                try:
                    # Try using the new API
                    await self._execute_press_and_hold_command(command, hold_secs)
                    return
                except (AttributeError, TypeError) as ex:
                    _LOGGER.warning("press_and_hold failed, falling back to regular command: %s", ex)
        
        # If we get here, use regular commands
        await self._execute_regular_command(command)
        
    async def _execute_press_and_hold_command(self, command, hold_secs):
        """Execute command using press and hold if available."""
        from pyatv.const import Command as PyatvCommand
        
        # Convert string command to pyatv Command enum
        pyatv_command = None
        for key, value in vars(PyatvCommand).items():
            if key.lower() == command.lower():
                pyatv_command = value
                break
        
        if pyatv_command:
            await self._apple_tv.remote_control.press_and_hold(pyatv_command, hold_secs)
        else:
            # Fall back to regular command
            await self._execute_regular_command(command)
            
    async def _execute_regular_command(self, command):
        """Execute remote command using the appropriate method."""
        _LOGGER.debug("Sending command: %s", command)
        
        # Map commands to Apple TV remote functions
        if command == "up":
            await self._apple_tv.remote_control.up()
        elif command == "down":
            await self._apple_tv.remote_control.down()
        elif command == "left":
            await self._apple_tv.remote_control.left()
        elif command == "right":
            await self._apple_tv.remote_control.right()
        elif command == "select":
            await self._apple_tv.remote_control.select()
        elif command == "menu":
            await self._apple_tv.remote_control.menu()
        elif command == "play":
            await self._apple_tv.remote_control.play()
        elif command == "pause":
            await self._apple_tv.remote_control.pause()
        elif command == "next":
            await self._apple_tv.remote_control.next()
        elif command == "previous":
            await self._apple_tv.remote_control.previous()
        elif command == "home":
            # Try both methods as the API has changed across versions
            if hasattr(self._apple_tv.remote_control, "home"):
                await self._apple_tv.remote_control.home()
            elif hasattr(self._apple_tv.remote_control, "top_menu"):
                await self._apple_tv.remote_control.top_menu()
        elif command == "home_hold" or command == "menu_hold":
            # Try both methods as the API has changed across versions
            if hasattr(self._apple_tv.remote_control, "home_hold"):
                await self._apple_tv.remote_control.home_hold()
            elif hasattr(self._apple_tv.remote_control, "menu_hold"):
                await self._apple_tv.remote_control.menu_hold()
        elif command == "top_menu":
            if hasattr(self._apple_tv.remote_control, "top_menu"):
                await self._apple_tv.remote_control.top_menu()
        elif command == "suspend":
            if hasattr(self._apple_tv.power, "turn_off"):
                await self._apple_tv.power.turn_off()
        elif command == "wakeup":
            if hasattr(self._apple_tv.power, "turn_on"):
                await self._apple_tv.power.turn_on()
        elif command == "volume_up":
            if hasattr(self._apple_tv.remote_control, "volume_up"):
                await self._apple_tv.remote_control.volume_up()
        elif command == "volume_down":
            if hasattr(self._apple_tv.remote_control, "volume_down"):
                await self._apple_tv.remote_control.volume_down()
        elif command == "skip_forward":
            if hasattr(self._apple_tv.remote_control, "skip_forward"):
                await self._apple_tv.remote_control.skip_forward()
        elif command == "skip_backward":
            if hasattr(self._apple_tv.remote_control, "skip_backward"):
                await self._apple_tv.remote_control.skip_backward()
        else:
            _LOGGER.warning("Unrecognized command: %s", command)


class AppleTVRemoteWithSwipe(RemoteEntity):
    """Representation of an Apple TV remote with Swipe capabilities."""

    def __init__(self, device_id: str, device_name: str, remote_entity_id: str) -> None:
        """Initialize the Apple TV Remote."""
        self._device_id = device_id
        self._attr_name = f"{device_name} Remote with Swipe"
        self._attr_unique_id = f"{device_id}_remote_with_swipe"
        self._remote_entity_id = remote_entity_id

    async def async_send_command(self, command: list[str], **kwargs: Any) -> None:
        """Send commands to the Apple TV."""
        _LOGGER.debug("Received commands: %s with kwargs: %s", command, kwargs)
        
        for cmd in command:
            # First check if it's a custom command we want to handle
            if cmd in COMMAND_MAP:
                _LOGGER.debug("Executing mapped command: %s -> %s", cmd, COMMAND_MAP[cmd].name)
                await self.hass.services.async_call(
                    "remote", 
                    "send_command", 
                    {
                        "entity_id": self._remote_entity_id,
                        "command": COMMAND_MAP[cmd].name,
                    },
                    blocking=True,
                )
            else:
                # Pass through any other commands to the original remote
                _LOGGER.debug("Passing through command: %s", cmd)
                await self.hass.services.async_call(
                    "remote", 
                    "send_command", 
                    {
                        "entity_id": self._remote_entity_id,
                        "command": cmd,
                    },
                    blocking=True,
                ) 