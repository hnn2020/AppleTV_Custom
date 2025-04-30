"""Entity representation for Apple TV Custom component."""

import logging
from typing import Any

from homeassistant.components.apple_tv.entity import AppleTVEntity as OriginalAppleTVEntity
from homeassistant.helpers.entity import DeviceInfo, Entity

_LOGGER = logging.getLogger(__name__)

# We're importing the original entity to use in remote.py
# No need to redefine it here since we're now importing directly from apple_tv component

class AppleTVEntity(OriginalAppleTVEntity):
    """Representation of an Apple TV entity with enhanced capabilities."""

    # We're extending the original AppleTVEntity to inherit all of its functionality
    # but could add custom methods or properties here if needed in the future.
    pass
