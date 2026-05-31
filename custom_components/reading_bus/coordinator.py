"""Data coordinator for Reading Bus API."""
import logging
from datetime import timedelta

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
                    data = await resp.json()
                    # Extract next 3 services
                    services = data.get("services", [])[:3]
                    return {
                        "next_times": services,
                        "last_updated": data.get("timestamp"),
                    }
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Reading Bus API error: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error fetching Reading Bus data: {err}") from err
