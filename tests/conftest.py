"""Shared fixtures for Reading Bus tests."""
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant

from custom_components.reading_bus.const import (
    CONF_API_KEY,
    CONF_STOP_ID,
    DOMAIN,
)


@pytest.fixture
def mock_config() -> dict:
    """Return mock configuration."""
    return {
        CONF_API_KEY: "test_api_key_123",
        CONF_STOP_ID: "stop_12345",
    }


@pytest.fixture
def mock_api_response() -> dict:
    """Return mock API response."""
    return {
        "timestamp": "2026-05-31T21:30:00Z",
        "location": "stop_12345",
        "services": [
            {
                "line_name": "1",
                "destination": "Reading Station",
                "actual_departure_time": "14:30",
                "expected_departure_time": "14:32",
                "status": "ON_TIME",
            },
            {
                "line_name": "2",
                "destination": "Royal Berks Hospital",
                "actual_departure_time": "14:45",
                "expected_departure_time": "14:45",
                "status": "ON_TIME",
            },
            {
                "line_name": "3",
                "destination": "Reading Town Centre",
                "actual_departure_time": "15:00",
                "expected_departure_time": "14:58",
                "status": "DELAYED",
            },
        ],
    }


@pytest.fixture
def mock_aiohttp_response(mock_api_response):
    """Return mock aiohttp response."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=mock_api_response)
    return mock_response
