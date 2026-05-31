"""Data coordinator for Reading Bus API."""
import logging
from datetime import timedelta
from xml.etree import ElementTree as ET

import aiohttp
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_API_KEY, CONF_STOP_ID, SCAN_INTERVAL, API_URL, TIMEOUT

_LOGGER = logging.getLogger(__name__)


class ReadingBusCoordinator(DataUpdateCoordinator):
    """Coordinator for fetching Reading Bus data."""

    def __init__(self, hass, config):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )
        self.api_key = config[CONF_API_KEY]
        self.stop_id = config[CONF_STOP_ID]

    async def _async_update_data(self):
        """Fetch data from the Reading Bus API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    API_URL,
                    params={
                        "api_token": self.api_key,
                        "location": self.stop_id,
                    },
                    timeout=aiohttp.ClientTimeout(total=TIMEOUT),
                ) as resp:
                    if resp.status != 200:
                        raise UpdateFailed(f"API returned status {resp.status}")
                    xml_data = await resp.text()
                    services = self._parse_xml_response(xml_data)
                    return {
                        "next_times": services[:3],
                        "last_updated": self._get_timestamp(),
                    }
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Reading Bus API error: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error fetching Reading Bus data: {err}") from err

    @staticmethod
    def _parse_xml_response(xml_data: str) -> list:
        """Parse XML response from Reading Bus API."""
        try:
            root = ET.fromstring(xml_data)
            services = []

            # SIRI namespace
            ns = {"siri": "http://www.siri.org.uk/siri"}

            # Find all MonitoredStopVisit elements
            for visit in root.findall(".//siri:MonitoredStopVisit", ns):
                try:
                    # Get line information
                    line_ref = visit.findtext(
                        "siri:MonitoredVehicleJourney/siri:PublishedLineName",
                        namespaces=ns,
                    )
                    if not line_ref or not line_ref.strip():
                        line_ref = visit.findtext(
                            "siri:MonitoredVehicleJourney/siri:LineRef",
                            namespaces=ns,
                        )
                    line_ref = (line_ref or "Unknown").strip()
                    destination = visit.findtext(
                        "siri:MonitoredVehicleJourney/siri:DestinationName", namespaces=ns
                    ) or "Unknown"

                    # Get timing information
                    expected_time = visit.findtext(
                        "siri:MonitoredVehicleJourney/siri:MonitoredCall/siri:ExpectedDepartureTime",
                        namespaces=ns,
                    )
                    actual_time = visit.findtext(
                        "siri:MonitoredVehicleJourney/siri:MonitoredCall/siri:ActualDepartureTime",
                        namespaces=ns,
                    )
                    aimed_time = visit.findtext(
                        "siri:MonitoredVehicleJourney/siri:MonitoredCall/siri:AimedDepartureTime",
                        namespaces=ns,
                    )

                    # If the service is not yet tracked, fall back to the aimed departure time.
                    if not expected_time:
                        expected_time = aimed_time

                    # Format times - extract just HH:MM from ISO format
                    expected_formatted = ReadingBusCoordinator._format_time(expected_time)
                    actual_formatted = ReadingBusCoordinator._format_time(actual_time) or expected_formatted

                    # Determine if delayed
                    status = "ON_TIME"
                    if expected_time and actual_time:
                        # Simple comparison - if actual > expected, it's delayed
                        if actual_time > expected_time:
                            status = "DELAYED"

                    service = {
                        "line_name": line_ref.strip(),
                        "destination": destination.strip(),
                        "actual_departure_time": actual_formatted,
                        "expected_departure_time": expected_formatted,
                        "status": status,
                    }
                    services.append(service)
                except Exception as e:
                    _LOGGER.warning(f"Error parsing service visit: {e}")
                    continue

            return services
        except ET.ParseError as e:
            _LOGGER.error(f"XML parsing error: {e}")
            raise UpdateFailed(f"Failed to parse XML response: {e}") from e

    @staticmethod
    def _format_time(time_str: str) -> str:
        """Format ISO time string to HH:MM format."""
        if not time_str:
            return ""
        try:
            # Handle ISO format: 2026-05-31T14:30:00+01:00
            if "T" in time_str:
                time_part = time_str.split("T")[1]
                # Remove timezone info
                time_part = time_part.split("+")[0].split("Z")[0]
                # Return just HH:MM
                return ":".join(time_part.split(":")[:2])
            return time_str
        except Exception as e:
            _LOGGER.warning(f"Error formatting time {time_str}: {e}")
            return time_str

    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp."""
        from datetime import datetime

        return datetime.now().isoformat()
