"""Helper to test significant GoodHome state changes."""
from __future__ import annotations

from typing import Any

from homeassistant.const import ATTR_DEVICE_CLASS
from homeassistant.core import HomeAssistant, callback


@callback
def async_check_significant_change(
    hass: HomeAssistant,
    old_state: str,
    old_attrs: dict,
    new_state: str,
    new_attrs: dict,
    **kwargs: Any,
) -> bool | None:
    """Test if state significantly changed."""
    device_class = new_attrs.get(ATTR_DEVICE_CLASS)

    if device_class is None:
        if (
            -0.2
            <= old_attrs["current_temperature"] - new_attrs["current_temperature"]
            <= 0.2
        ):
            return False
        if 2 <= old_attrs["current_humidity"] - new_attrs["current_humidity"] <= 2:
            return False
    elif device_class == "temperature":
        if -0.2 <= float(old_state) - float(new_state) <= 0.2:
            return False
    elif device_class == "humidity":
        if -2 <= float(old_state) - float(new_state) <= 2:
            return False
    return True
