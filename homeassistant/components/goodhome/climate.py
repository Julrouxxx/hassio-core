"""Entity class for GoodHome heaters ."""
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import ClimateEntityFeature, HVACMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import TEMP_CELSIUS
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    add_entities: AddEntitiesCallback,
) -> None:
    """Add Entity when entry is setup."""
    # The hub is loaded from the associated hass.data entry that was created in the
    # __init__.async_setup_entry function
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]

    try:
        await coordinator.async_config_entry_first_refresh()
    except ConfigEntryNotReady:
        print("GoodHome integration not ready")
    # Add all entities to HA
    for device in coordinator.data:
        add_entities([GoodHomeClimate(coordinator, device["_id"])])


class GoodHomeClimate(CoordinatorEntity, ClimateEntity):
    """GoodHome Entity."""

    def __init__(self, coordinator: CoordinatorEntity, id_device: str) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        for device in self.coordinator.data:
            if device["_id"] == id_device:
                data = device
                break
        if data is None:
            return
        self.manufacturer = data["model"]
        self._name = data["name"]
        self.model = data["state"]["codeName"]
        self.fw_version = data["state"]["fwVer"]
        self._current_temperature = data["state"]["currentTemp"]
        self._preset_mode = "ECO" if data["state"]["targetMode"] == 61 else "COMFORT"
        self._current_humidity = data["state"]["humidity"]
        self._target_temperature = data["state"]["targetTemp"]
        self._unique_id = id_device
        self._temperature_unit = TEMP_CELSIUS
        self._hvac_modes = [HVACMode.HEAT]
        self._hvac_mode = HVACMode.HEAT
        self._preset_modes = ["ECO", "COMFORT"]
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
    def device_info(self) -> DeviceInfo:
        """Get device info."""
        return {
            "identifiers": {(DOMAIN, self._unique_id)},
            "name": self._name,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "sw_version": self.fw_version,
        }

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

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        for device in self.coordinator.data:
            if device["_id"] == self._unique_id:
                data = device
                break
        if data is None:
            return
        self.manufacturer = data["model"]
        self._name = data["name"]
        self.model = data["state"]["codeName"]
        self.fw_version = data["state"]["fwVer"]
        self._current_temperature = data["state"]["currentTemp"]
        self._preset_mode = "ECO" if data["state"]["targetMode"] == 61 else "COMFORT"
        self._current_humidity = data["state"]["humidity"]
        self._target_temperature = data["state"]["targetTemp"]
        self.async_write_ha_state()
