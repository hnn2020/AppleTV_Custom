"""Entity representation for Apple TV Custom component."""

import logging
from typing import Any

from homeassistant.components.apple_tv.entity import AppleTVEntity as OriginalAppleTVEntity
from homeassistant.helpers.entity import DeviceInfo, Entity

_LOGGER = logging.getLogger(__name__)


class AppleTVEntity(OriginalAppleTVEntity):
    """Representation of an Apple TV entity with enhanced capabilities."""

    # We're extending the original AppleTVEntity to inherit all of its functionality
    # but could add custom methods or properties here if needed in the future.
    pass
