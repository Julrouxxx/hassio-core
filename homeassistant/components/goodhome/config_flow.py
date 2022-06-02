"""Config flow for GoodHome integration.."""
from __future__ import annotations

import logging
from multiprocessing import AuthenticationError
from typing import Any

import requests
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("username"): str,
        vol.Required("password"): str,
    }
)


class GoodHomeHelper:
    """GoodHome API reference (to externalzie)."""

    GOODHOME_LOGIN = "https://shkf02.goodhome.com/v1/auth/login"

    def __init__(self, data: dict[str, Any] = None) -> None:
        """Init the API reference."""
        if data is not None:
            self.token = data["token"]
            self.refresh_token = data["refresh_token"]
            self.id = data["id"]

    def refresh(self) -> str | None:
        """Refresh token."""
        response = requests.get(
            "https://shkf02.goodhome.com/v1/auth/verify",
            headers={"access-token": self.token},
        ).json()
        if "expire" in response and response["expire"] > 100:
            return None
        response = requests.get(
            "https://shkf02.goodhome.com/v1/auth/token",
            headers={"refresh-token": self.refresh_token},
        ).json()
        if "token" not in response:
            raise AuthenticationError
		self.token = response["token"]
        return response["token"]

    def authenticate(self, username: str, password: str) -> dict[str, Any]:
        """Authentificate to get a token."""
        response = requests.post(
            self.GOODHOME_LOGIN, data={"email": username, "password": password}
        ).json()  # type: dict[str, Any]
        if "token" not in response:
            return {}
		self.token = response["token"]
		self.refresh_token = response["refresh_token"]
        return {
            "token": response["token"],
            "refresh_token": response["refresh_token"],
            "id": response["id"],
        }

    def get_heaters_before(self, client_id: str, token: str) -> dict[str, Any]:
        """Depreacated."""
        response = requests.get(
            "https://shkf02.goodhome.com/v1/users/" + client_id + "/devices",
            headers={"access-token": token},
        ).json()  # type: dict[str, Any]
        return response

    def get_heaters(self) -> dict[str, Any]:
        """Get all heaters linked to an account."""
        response = requests.get(
            "https://shkf02.goodhome.com/v1/users/" + self.id + "/devices",
            headers={"access-token": self.token},
        ).json()  # type: dict[str, Any]

        return response["devices"]

    def get_heater(self, heater: str) -> dict[str, Any] | None:
        """Get specific heater."""
        response = requests.get(
            "https://shkf02.goodhome.com/v1/users/" + self.id + "/devices",
            headers={"access-token": self.token},
        ).json()  # type: dict[str, Any]
        for device in response["devices"]:
            if device["_id"] == heater:
                return device
        return None


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """
    Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user
    """

    hub = GoodHomeHelper()

    auth = await hass.async_add_executor_job(
        hub.authenticate, data["username"], data["password"]
    )
    if auth == {}:
        raise InvalidAuth
    return auth


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GoodHome.."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step.."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title="GoodHome heater", data=info)
        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect.."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth.."""
