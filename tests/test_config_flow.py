"""Tests for Reading Bus config flow."""
from unittest.mock import patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from custom_components.reading_bus.config_flow import ReadingBusConfigFlow
from custom_components.reading_bus.const import (
    CONF_API_KEY,
    CONF_STOP_ID,
    DOMAIN,
)


@pytest.mark.asyncio
async def test_config_flow_user_step(hass: HomeAssistant, mock_config):
    """Test config flow user step."""
    flow = ReadingBusConfigFlow()
    flow.hass = hass

    result = await flow.async_step_user(user_input=mock_config)

    assert result["type"] == "create_entry"
    assert result["title"] == f"Reading Bus - Stop {mock_config[CONF_STOP_ID]}"
    assert result["data"] == mock_config


@pytest.mark.asyncio
async def test_config_flow_user_step_form(hass: HomeAssistant):
    """Test config flow shows form without input."""
    flow = ReadingBusConfigFlow()
    flow.hass = hass

    result = await flow.async_step_user()

    assert result["type"] == "form"
    assert result["step_id"] == "user"
    assert CONF_API_KEY in result["data_schema"].schema
    assert CONF_STOP_ID in result["data_schema"].schema


@pytest.mark.asyncio
async def test_config_flow_creates_correct_title(hass: HomeAssistant):
    """Test config flow creates entry with correct title."""
    flow = ReadingBusConfigFlow()
    flow.hass = hass

    test_config = {
        CONF_API_KEY: "my_api_key",
        CONF_STOP_ID: "my_stop_id",
    }

    result = await flow.async_step_user(user_input=test_config)

    assert result["type"] == "create_entry"
    assert "my_stop_id" in result["title"]
