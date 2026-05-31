"""Config flow for Reading Bus integration."""
import logging
from typing import Any, Dict

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_UNIQUE_ID
from homeassistant.core import callback

from .const import DOMAIN, CONF_API_KEY, CONF_STOP_ID

_LOGGER = logging.getLogger(__name__)


class ReadingBusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Reading Bus."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Handle the initial step."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            # Create entry with the provided data
            return self.async_create_entry(
                title=f"Reading Bus - Stop {user_input[CONF_STOP_ID]}",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): str,
                    vol.Required(CONF_STOP_ID): str,
                }
            ),
            errors=errors,
            description_placeholders={
                "api_key_help": "Get your API key from reading-opendata.r2p.com",
                "stop_id_help": "The stop ID for the bus stop you want to track",
            },
        )
