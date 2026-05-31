"""Sensor platform for Reading Bus integration."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        ReadingBusNextServiceSensor(coordinator, i, entry.entry_id)
        for i in range(3)
    ]

    async_add_entities(sensors)


class ReadingBusNextServiceSensor(CoordinatorEntity, SensorEntity):
    """Sensor for next Reading Bus service."""

    def __init__(self, coordinator, index, entry_id):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.index = index
        self.entry_id = entry_id
        self._attr_unique_id = f"reading_bus_{entry_id}_service_{index}"
        self._attr_has_entity_name = True

    @property
    def name(self):
        """Return name of the sensor."""
        return f"Next Service {self.index + 1}"

    @property
    def state(self):
        """Return next service info."""
        data = self.coordinator.data or {}
        services = data.get("next_times", [])
        if len(services) > self.index:
            service = services[self.index]
            # Format: "Line 1 @ 14:30 (Expected: 14:32)"
            line_name = service.get("line_name", "Unknown")
            actual_time = service.get("actual_departure_time", "N/A")
            expected_time = service.get("expected_departure_time", "N/A")
            return f"{line_name} @ {actual_time} (Exp: {expected_time})"
        return "N/A"

    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        data = self.coordinator.data or {}
        services = data.get("next_times", [])
        if len(services) > self.index:
            service = services[self.index]
            return {
                "line_name": service.get("line_name"),
                "actual_departure_time": service.get("actual_departure_time"),
                "expected_departure_time": service.get("expected_departure_time"),
                "destination": service.get("destination"),
                "status": service.get("status"),
            }
        return {}

    @property
    def icon(self):
        """Return icon for the sensor."""
        return "mdi:bus"
