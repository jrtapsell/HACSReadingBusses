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
def mock_xml_response() -> str:
    """Return mock XML API response."""
    return """<?xml version="1.0" encoding="UTF-8"?>
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


@pytest.fixture
def mock_aiohttp_response(mock_xml_response):
    """Return mock aiohttp response."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.text = AsyncMock(return_value=mock_xml_response)
    return mock_response
