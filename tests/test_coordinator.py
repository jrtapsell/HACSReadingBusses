"""Tests for Reading Bus coordinator."""
from unittest.mock import AsyncMock, patch

import aiohttp
import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.reading_bus.const import CONF_API_KEY, CONF_STOP_ID
from custom_components.reading_bus.coordinator import ReadingBusCoordinator


@pytest.mark.asyncio
async def test_coordinator_initialization(hass, mock_config):
    """Test coordinator initialization."""
    coordinator = ReadingBusCoordinator(hass, mock_config)

    assert coordinator.api_key == mock_config[CONF_API_KEY]
    assert coordinator.stop_id == mock_config[CONF_STOP_ID]
    assert coordinator.data is None


@pytest.mark.asyncio
async def test_coordinator_fetch_data(hass, mock_config, mock_api_response):
    """Test coordinator fetches data correctly."""
    coordinator = ReadingBusCoordinator(hass, mock_config)

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_api_response)
        mock_response.__aenter__.return_value = mock_response
        mock_get.return_value.__aenter__.return_value = mock_response

        data = await coordinator._async_update_data()

        assert data["last_updated"] == mock_api_response["timestamp"]
        assert len(data["next_times"]) == 3
        assert data["next_times"][0]["line_name"] == "1"
        assert data["next_times"][1]["line_name"] == "2"
        assert data["next_times"][2]["line_name"] == "3"


@pytest.mark.asyncio
async def test_coordinator_limits_to_three_services(
    hass, mock_config, mock_api_response
):
    """Test coordinator limits results to 3 services."""
    # Add extra services to response
    mock_api_response["services"].extend(
        [
            {
                "line_name": "4",
                "destination": "Test",
                "actual_departure_time": "15:15",
                "expected_departure_time": "15:15",
                "status": "ON_TIME",
            },
            {
                "line_name": "5",
                "destination": "Test",
                "actual_departure_time": "15:30",
                "expected_departure_time": "15:30",
                "status": "ON_TIME",
            },
        ]
    )

    coordinator = ReadingBusCoordinator(hass, mock_config)

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_api_response)
        mock_response.__aenter__.return_value = mock_response
        mock_get.return_value.__aenter__.return_value = mock_response

        data = await coordinator._async_update_data()

        assert len(data["next_times"]) == 3


@pytest.mark.asyncio
async def test_coordinator_handles_api_error(hass, mock_config):
    """Test coordinator handles API errors."""
    coordinator = ReadingBusCoordinator(hass, mock_config)

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.side_effect = aiohttp.ClientError("Connection failed")

        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()


@pytest.mark.asyncio
async def test_coordinator_handles_http_error(hass, mock_config):
    """Test coordinator handles HTTP errors."""
    coordinator = ReadingBusCoordinator(hass, mock_config)

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.__aenter__.return_value = mock_response
        mock_get.return_value.__aenter__.return_value = mock_response

        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()


@pytest.mark.asyncio
async def test_coordinator_api_call_parameters(hass, mock_config, mock_api_response):
    """Test coordinator calls API with correct parameters."""
    coordinator = ReadingBusCoordinator(hass, mock_config)

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_api_response)
        mock_response.__aenter__.return_value = mock_response
        mock_get.return_value.__aenter__.return_value = mock_response

        await coordinator._async_update_data()

        # Verify the API was called with correct parameters
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "params" in call_args.kwargs
        assert call_args.kwargs["params"]["api_token"] == mock_config[CONF_API_KEY]
        assert call_args.kwargs["params"]["location"] == mock_config[CONF_STOP_ID]
