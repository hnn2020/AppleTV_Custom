"""Config flow for Apple TV Custom integration."""
import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.data_entry_flow import FlowResult

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

# This is important to make the config flow discoverable
DOMAIN_SCHEMA = vol.Schema({vol.Required(CONF_NAME): str})

@config_entries.HANDLERS.register(DOMAIN)
class AppleTVCustomConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Apple TV Custom."""

    VERSION = 1
    # These attributes are necessary for config flow to work properly
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            # Use the name as the unique ID
            name = user_input[CONF_NAME]
            await self.async_set_unique_id(name)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=name,
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=DOMAIN_SCHEMA,
            errors=errors,
        )

    async def async_step_import(self, import_info):
        """Import from YAML config."""
        return await self.async_step_user(import_info)
