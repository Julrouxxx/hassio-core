"""Coordinator for GoodHome Module."""
from datetime import timedelta
import logging
from multiprocessing import AuthenticationError
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .goodhome import GoodHomeHelper

_LOGGER = logging.getLogger(__name__)


class GoodHomeCoordinator(DataUpdateCoordinator):
    """GoodHome Coordinator to update all entity in one."""

    def __init__(self, hass: HomeAssistant, api: GoodHomeHelper, entry_id: str) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass, _LOGGER, name="GoodHome", update_interval=timedelta(minutes=5)
        )
        self.api = api
        self.entry_id = entry_id

    async def _async_update_data(self) -> dict[str, Any]:
        credentials = self.hass.config_entries.async_get_entry(self.entry_id)
        if credentials is None:
            raise UpdateFailed("Credentials not found")
        try:
            token = await self.hass.async_add_executor_job(self.api.refresh)
        except AuthenticationError:

            new_creds = await self.hass.async_add_executor_job(
                self.api.authenticate,
                credentials.data["username"],
                credentials.data["password"],
            )
            self.hass.config_entries.async_update_entry(
                credentials,
                data={
                    **credentials.data,
                    "refresh_token": new_creds["refresh_token"],
                },
            )
            token = new_creds["token"]
        if token is not None:
            self.hass.config_entries.async_update_entry(
                credentials,
                data={
                    **credentials.data,
                    "token": token,
                },
            )
        data = await self.hass.async_add_executor_job(self.api.get_heaters)
        return data
