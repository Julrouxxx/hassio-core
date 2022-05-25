"""Entity class for GoodHome heaters ."""
from multiprocessing import AuthenticationError

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import ClimateEntityFeature, HVACMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .config_flow import GoodHomeHelper
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    add_entities: AddEntitiesCallback,
) -> None:
    """Add Entity when entry is setup."""
    # The hub is loaded from the associated hass.data entry that was created in the
    # __init__.async_setup_entry function
    goodhome = GoodHomeHelper(hass.data[DOMAIN][config_entry.entry_id])
    heaters = await hass.async_add_executor_job(goodhome.get_heaters)
    # Add all entities to HA
    for device in heaters:
        add_entities(
            [GoodHomeClimate(device["_id"], config_entry.entry_id)], True  # type: ignore[index]
        )


class GoodHomeClimate(ClimateEntity):
    """GoodHome Entity."""

    def __init__(self, id_device: str, entry_id: str) -> None:
        """Initialize the entity."""
        self._unique_id = id_device
        self.entry_id = entry_id
        self._temperature_unit = TEMP_CELSIUS
        self._hvac_modes = [HVACMode.HEAT]
        self._hvac_mode = HVACMode.HEAT
        self._preset_modes = ["ECO", "COMFORT"]
        self._preset_mode = "ECO"
        self._current_temperature = 0
        self._current_humidity = 0
        self._target_temperature = 0
        self._supported_features = (
            ClimateEntityFeature.PRESET_MODE | ClimateEntityFeature.TARGET_TEMPERATURE
        )

    @property
    def unique_id(self) -> str:
        """Get unique id."""
        return self._unique_id

    @property
    def should_poll(self) -> bool:
        """Poll device."""
        return True

    @property
    def temperature_unit(self) -> str:
        """Get Always C."""
        return self._temperature_unit

    @property
    def hvac_mode(self) -> HVACMode:
        """Get hvac mode heat only."""
        return self._hvac_mode

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """Get HVAC modes."""
        return self._hvac_modes

    @property
    def preset_modes(self) -> list[str]:
        """Get Eco and comfort."""
        return self._preset_modes

    @property
    def preset_mode(self) -> str:
        """Get current preset."""
        return self._preset_mode

    @property
    def current_temperature(self) -> float:
        """Get current temperature."""
        return self._current_temperature

    @property
    def target_temperature(self) -> int:
        """Get target temperature."""
        return self._target_temperature

    @property
    def current_humidity(self) -> int:
        """Get current humidity."""
        return self._current_humidity

    @property
    def supported_features(self) -> int:
        """Get suppoerted features."""
        return self._supported_features

    def update(self):
        """Update trigger."""
        goodhome = GoodHomeHelper(self.hass.data[DOMAIN][self.entry_id])
        try:
            token = goodhome.refresh()
        except AuthenticationError:
            credentials = self.hass.config_entries.async_get_entry(
                self.entry_id
            ).as_dict()
            new_creds = goodhome.authenticate(
                credentials["username"], credentials["password"]
            )
            self.hass.data[DOMAIN][self.entry_id]["refresh_token"] = new_creds[
                "refresh_token"
            ]
            token = new_creds["token"]
        if token is not None:
            self.hass.data[DOMAIN][self.entry_id]["token"] = token
        data = goodhome.get_heater(self.unique_id)

        self._current_temperature = data["state"]["currentTemp"]
        self._preset_mode = "ECO" if data["state"]["targetMode"] == 61 else "COMFORT"
        self._current_humidity = data["state"]["humidity"]
        self._target_temperature = data["state"]["targetTemp"]
