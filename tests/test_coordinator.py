"""Tests for Reading Bus coordinator."""
from unittest.mock import AsyncMock, patch
from datetime import datetime

import aiohttp
import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.reading_bus.const import CONF_API_KEY, CONF_STOP_ID
from custom_components.reading_bus.coordinator import ReadingBusCoordinator


# Sample XML responses for testing
SAMPLE_XML_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<Siri xmlns="http://www.siri.org.uk/siri" xmlns:sm="http://www.ifopt.org.uk/ifopt">
  <ServiceDelivery>
    <ResponseTimestamp>2026-05-31T21:30:00+01:00</ResponseTimestamp>
    <StopMonitoringDelivery>
      <ResponseTimestamp>2026-05-31T21:30:00+01:00</ResponseTimestamp>
      <MonitoredStopVisit>
        <RecordedAtTime>2026-05-31T21:30:00+01:00</RecordedAtTime>
        <MonitoredVehicleJourney>
          <LineRef>1</LineRef>
          <DestinationName>Reading Station</DestinationName>
          <MonitoredCall>
            <ExpectedDepartureTime>2026-05-31T14:32:00+01:00</ExpectedDepartureTime>
            <ActualDepartureTime>2026-05-31T14:30:00+01:00</ActualDepartureTime>
          </MonitoredCall>
        </MonitoredVehicleJourney>
      </MonitoredStopVisit>
      <MonitoredStopVisit>
        <RecordedAtTime>2026-05-31T21:30:00+01:00</RecordedAtTime>
        <MonitoredVehicleJourney>
          <LineRef>2</LineRef>
          <DestinationName>Royal Berks Hospital</DestinationName>
          <MonitoredCall>
            <ExpectedDepartureTime>2026-05-31T14:45:00+01:00</ExpectedDepartureTime>
            <ActualDepartureTime>2026-05-31T14:45:00+01:00</ActualDepartureTime>
          </MonitoredCall>
        </MonitoredVehicleJourney>
      </MonitoredStopVisit>
      <MonitoredStopVisit>
        <RecordedAtTime>2026-05-31T21:30:00+01:00</RecordedAtTime>
        <MonitoredVehicleJourney>
          <LineRef>3</LineRef>
          <DestinationName>Reading Town Centre</DestinationName>
          <MonitoredCall>
            <ExpectedDepartureTime>2026-05-31T14:58:00+01:00</ExpectedDepartureTime>
            <ActualDepartureTime>2026-05-31T15:00:00+01:00</ActualDepartureTime>
          </MonitoredCall>
        </MonitoredVehicleJourney>
      </MonitoredStopVisit>
    </StopMonitoringDelivery>
  </ServiceDelivery>
</Siri>
"""

EMPTY_XML_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<Siri xmlns="http://www.siri.org.uk/siri">
  <ServiceDelivery>
    <StopMonitoringDelivery>
      <ResponseTimestamp>2026-05-31T21:30:00+01:00</ResponseTimestamp>
    </StopMonitoringDelivery>
  </ServiceDelivery>
</Siri>
"""


@pytest.mark.asyncio
async def test_coordinator_initialization(hass, mock_config):
    """Test coordinator initialization."""
    coordinator = ReadingBusCoordinator(hass, mock_config)

    assert coordinator.api_key == mock_config[CONF_API_KEY]
    assert coordinator.stop_id == mock_config[CONF_STOP_ID]
    assert coordinator.data is None


@pytest.mark.asyncio
async def test_coordinator_fetch_data(hass, mock_config):
    """Test coordinator fetches data correctly."""
    coordinator = ReadingBusCoordinator(hass, mock_config)

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=SAMPLE_XML_RESPONSE)
        mock_response.__aenter__.return_value = mock_response
        mock_get.return_value.__aenter__.return_value = mock_response

        data = await coordinator._async_update_data()

        assert "last_updated" in data
        assert len(data["next_times"]) == 3
        assert data["next_times"][0]["line_name"] == "1"
        assert data["next_times"][1]["line_name"] == "2"
        assert data["next_times"][2]["line_name"] == "3"


@pytest.mark.asyncio
async def test_coordinator_parses_xml_correctly(hass, mock_config):
    """Test coordinator correctly parses XML data."""
    coordinator = ReadingBusCoordinator(hass, mock_config)

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=SAMPLE_XML_RESPONSE)
        mock_response.__aenter__.return_value = mock_response
        mock_get.return_value.__aenter__.return_value = mock_response

        data = await coordinator._async_update_data()

        service = data["next_times"][0]
        assert service["line_name"] == "1"
        assert service["destination"] == "Reading Station"
        assert service["expected_departure_time"] == "14:32"
        assert service["actual_departure_time"] == "14:30"


@pytest.mark.asyncio
async def test_coordinator_detects_delays(hass, mock_config):
    """Test coordinator detects delayed services."""
    coordinator = ReadingBusCoordinator(hass, mock_config)

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=SAMPLE_XML_RESPONSE)
        mock_response.__aenter__.return_value = mock_response
        mock_get.return_value.__aenter__.return_value = mock_response

        data = await coordinator._async_update_data()

        # First service: actual < expected (early)
        assert data["next_times"][0]["status"] == "ON_TIME"
        # Third service: actual > expected (delayed)
        assert data["next_times"][2]["status"] == "DELAYED"


@pytest.mark.asyncio
async def test_coordinator_limits_to_three_services(hass, mock_config):
    """Test coordinator limits results to 3 services."""
    coordinator = ReadingBusCoordinator(hass, mock_config)

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=SAMPLE_XML_RESPONSE)
        mock_response.__aenter__.return_value = mock_response
        mock_get.return_value.__aenter__.return_value = mock_response

        data = await coordinator._async_update_data()

        assert len(data["next_times"]) == 3


@pytest.mark.asyncio
async def test_coordinator_handles_empty_response(hass, mock_config):
    """Test coordinator handles empty XML response."""
    coordinator = ReadingBusCoordinator(hass, mock_config)

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=EMPTY_XML_RESPONSE)
        mock_response.__aenter__.return_value = mock_response
        mock_get.return_value.__aenter__.return_value = mock_response

        data = await coordinator._async_update_data()

        assert len(data["next_times"]) == 0


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
async def test_coordinator_handles_malformed_xml(hass, mock_config):
    """Test coordinator handles malformed XML."""
    coordinator = ReadingBusCoordinator(hass, mock_config)

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="<invalid>xml</invalid>")
        mock_response.__aenter__.return_value = mock_response
        mock_get.return_value.__aenter__.return_value = mock_response

        # Should not raise, just return empty list
        data = await coordinator._async_update_data()
        assert len(data["next_times"]) == 0


@pytest.mark.asyncio
async def test_coordinator_api_call_parameters(hass, mock_config):
    """Test coordinator calls API with correct parameters."""
    coordinator = ReadingBusCoordinator(hass, mock_config)

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=SAMPLE_XML_RESPONSE)
        mock_response.__aenter__.return_value = mock_response
        mock_get.return_value.__aenter__.return_value = mock_response

        await coordinator._async_update_data()

        # Verify the API was called with correct parameters
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "params" in call_args.kwargs
        assert call_args.kwargs["params"]["api_token"] == mock_config[CONF_API_KEY]
        assert call_args.kwargs["params"]["location"] == mock_config[CONF_STOP_ID]


def test_format_time():
    """Test time formatting utility."""
    # ISO format with timezone
    formatted = ReadingBusCoordinator._format_time("2026-05-31T14:32:00+01:00")
    assert formatted == "14:32"

    # ISO format with Z timezone
    formatted = ReadingBusCoordinator._format_time("2026-05-31T14:32:00Z")
    assert formatted == "14:32"

    # Already formatted time
    formatted = ReadingBusCoordinator._format_time("14:32")
    assert formatted == "14:32"

    # Empty string
    formatted = ReadingBusCoordinator._format_time("")
    assert formatted == ""

    # None
    formatted = ReadingBusCoordinator._format_time(None)
    assert formatted == ""
