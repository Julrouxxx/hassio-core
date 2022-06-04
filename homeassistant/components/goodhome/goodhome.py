"""GoodHome API reference."""

from __future__ import annotations

from multiprocessing import AuthenticationError
from typing import Any

from _collections_abc import Mapping
import requests


class GoodHomeHelper:
    """GoodHome API."""

    GOODHOME_LOGIN = "https://shkf02.goodhome.com/v1/auth/login"

    def __init__(self, data: Mapping[str, Any] = None) -> None:
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

    def get_heaters(self) -> dict[str, Any]:
        """Get all heaters linked to an account."""
        response = requests.get(
            "https://shkf02.goodhome.com/v1/users/" + self.id + "/devices",
            headers={"access-token": self.token},
        ).json()  # type: dict[str, Any]

        return response["devices"]
