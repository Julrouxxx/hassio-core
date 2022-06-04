"""Test the GoodHome significant change platform."""
from homeassistant.components.goodhome.significant_change import (
    async_check_significant_change,
)


async def test_significant_change():
    """Detect GoodHome significant changes."""
    attrs = {}
    assert not async_check_significant_change(None, "on", attrs, "on", attrs)
    assert async_check_significant_change(None, "on", attrs, "off", attrs)
