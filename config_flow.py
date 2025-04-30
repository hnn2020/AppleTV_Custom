"""Config flow for Apple TV Custom integration."""
import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.helpers import config_validation as cv

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)


class AppleTVCustomConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Apple TV Custom."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        # Check if we already have an entry
        if self._async_current_entries():
            return self.async_abort(reason="already_configured")
            
        errors = {}
        
        if user_input is not None:
            return self.async_create_entry(
                title="Apple TV Custom Remotes",
                data={},
            )

        # Simple form with just a submit button
        schema = vol.Schema({})

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_import(self, import_info):
        """Import from YAML config."""
        return await self.async_step_user(import_info)
