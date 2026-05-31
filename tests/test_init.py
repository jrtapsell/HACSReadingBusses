"""Tests for Reading Bus integration initialization."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from custom_components.reading_bus import async_setup_entry, async_unload_entry
from custom_components.reading_bus.const import DOMAIN, CONF_API_KEY, CONF_STOP_ID


@pytest.mark.asyncio
async def test_async_setup_entry(hass: HomeAssistant, mock_config):
    """Test async setup entry."""
    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "test_entry_id"
    entry.data = mock_config

    with patch(
        "custom_components.reading_bus.ReadingBusCoordinator"
    ) as mock_coordinator_class:
        mock_coordinator = AsyncMock()
        mock_coordinator.async_config_entry_first_refresh = AsyncMock()
        mock_coordinator_class.return_value = mock_coordinator

        hass.data[DOMAIN] = {}
        hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)

        result = await async_setup_entry(hass, entry)

        assert result is True
        assert entry.entry_id in hass.data[DOMAIN]
        assert hass.data[DOMAIN][entry.entry_id] == mock_coordinator
        mock_coordinator.async_config_entry_first_refresh.assert_called_once()


@pytest.mark.asyncio
async def test_async_unload_entry(hass: HomeAssistant):
    """Test async unload entry."""
    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "test_entry_id"

    coordinator = MagicMock()
    hass.data[DOMAIN] = {"test_entry_id": coordinator}
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)

    result = await async_unload_entry(hass, entry)

    assert result is True
    assert entry.entry_id not in hass.data[DOMAIN]
    hass.config_entries.async_unload_platforms.assert_called_once()


@pytest.mark.asyncio
async def test_async_unload_entry_failed(hass: HomeAssistant):
    """Test async unload entry when unload fails."""
    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "test_entry_id"

    coordinator = MagicMock()
    hass.data[DOMAIN] = {"test_entry_id": coordinator}
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=False)

    result = await async_unload_entry(hass, entry)

    assert result is False
    assert "test_entry_id" in hass.data[DOMAIN]
