"""Tests for Reading Bus sensor."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant

from custom_components.reading_bus.const import DOMAIN
from custom_components.reading_bus.sensor import ReadingBusNextServiceSensor


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.data = {
        "next_times": [
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
        "last_updated": "2026-05-31T21:30:00Z",
    }
    coordinator.async_add_listener = MagicMock(return_value=MagicMock())
    return coordinator


def test_sensor_initialization(mock_coordinator):
    """Test sensor initialization."""
    sensor = ReadingBusNextServiceSensor(mock_coordinator, 0, "test_entry_id")

    assert sensor.index == 0
    assert sensor.entry_id == "test_entry_id"
    assert sensor._attr_unique_id == "reading_bus_test_entry_id_service_0"


def test_sensor_name(mock_coordinator):
    """Test sensor name."""
    sensor = ReadingBusNextServiceSensor(mock_coordinator, 0, "test_entry_id")
    assert sensor.name == "Next Service 1"

    sensor = ReadingBusNextServiceSensor(mock_coordinator, 1, "test_entry_id")
    assert sensor.name == "Next Service 2"

    sensor = ReadingBusNextServiceSensor(mock_coordinator, 2, "test_entry_id")
    assert sensor.name == "Next Service 3"


def test_sensor_state(mock_coordinator):
    """Test sensor state."""
    sensor = ReadingBusNextServiceSensor(mock_coordinator, 0, "test_entry_id")
    state = sensor.state

    assert state == "14:30"


def test_sensor_state_all_services(mock_coordinator):
    """Test sensor state for all three services."""
    expected_states = ["14:30", "14:45", "15:00"]
    for index in range(3):
        sensor = ReadingBusNextServiceSensor(mock_coordinator, index, "test_entry_id")
        state = sensor.state
        assert state == expected_states[index]
        assert "@" not in state


def test_sensor_state_no_data(mock_coordinator):
    """Test sensor state when no data is available."""
    mock_coordinator.data = {"next_times": []}
    sensor = ReadingBusNextServiceSensor(mock_coordinator, 0, "test_entry_id")

    assert sensor.state == "N/A"


def test_sensor_state_none_data(mock_coordinator):
    """Test sensor state when data is None."""
    mock_coordinator.data = None
    sensor = ReadingBusNextServiceSensor(mock_coordinator, 0, "test_entry_id")

    assert sensor.state == "N/A"


def test_sensor_extra_attributes(mock_coordinator):
    """Test sensor extra state attributes."""
    sensor = ReadingBusNextServiceSensor(mock_coordinator, 0, "test_entry_id")
    attrs = sensor.extra_state_attributes

    assert attrs["line_name"] == "1"
    assert attrs["destination"] == "Reading Station"
    assert attrs["actual_departure_time"] == "14:30"
    assert attrs["expected_departure_time"] == "14:32"
    assert attrs["status"] == "ON_TIME"


def test_sensor_extra_attributes_no_data(mock_coordinator):
    """Test sensor extra attributes when no data."""
    mock_coordinator.data = {"next_times": []}
    sensor = ReadingBusNextServiceSensor(mock_coordinator, 0, "test_entry_id")

    assert sensor.extra_state_attributes == {}


def test_sensor_icon(mock_coordinator):
    """Test sensor icon."""
    sensor = ReadingBusNextServiceSensor(mock_coordinator, 0, "test_entry_id")
    assert sensor.icon == "mdi:bus"


def test_sensor_delayed_status(mock_coordinator):
    """Test sensor with delayed status."""
    # The third service is delayed
    sensor = ReadingBusNextServiceSensor(mock_coordinator, 2, "test_entry_id")
    attrs = sensor.extra_state_attributes

    assert attrs["status"] == "DELAYED"
    assert attrs["actual_departure_time"] == "15:00"
    assert attrs["expected_departure_time"] == "14:58"
