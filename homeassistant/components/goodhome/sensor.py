"""Entity class for GoodHome heaters temperature and humidity sensors ."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, TEMP_CELSIUS
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
        add_entities(
            [
                GoodHomeSensor(coordinator, device["_id"], "temperature"),
                GoodHomeSensor(coordinator, device["_id"], "humidity"),
            ]
        )


class GoodHomeSensor(CoordinatorEntity, SensorEntity):
    """GoodHome Entity."""

    def __init__(
        self, coordinator: CoordinatorEntity, id_device: str, type_of_sensor: str
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        for device in self.coordinator.data:
            if device["_id"] == id_device:
                data = device
                break
        if data is None:
            return
        self.manufacturer = data["model"]
        self.type = type_of_sensor
        self._name = data["name"]
        self.model = data["state"]["codeName"]
        self.fw_version = data["state"]["fwVer"]
        self._unique_id = id_device + "_" + type_of_sensor
        self._native_value = (
            data["state"]["currentTemp"]
            if self.type == "temperature"
            else data["state"]["humidity"]
        )

    @property
    def unique_id(self) -> str:
        """Get unique id."""
        return self._unique_id

    @property
    def device_class(self) -> str:
        """Get device type (temperature or humidity)."""
        return self.type

    @property
    def native_unit_of_measurement(self) -> str:
        """Get Always C."""
        return TEMP_CELSIUS if self.type == "temperature" else PERCENTAGE

    @property
    def device_info(self) -> DeviceInfo:
        """Get device info."""
        return {
            "identifiers": {(DOMAIN, self._unique_id.split("_")[0])},
            "name": self._name,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "sw_version": self.fw_version,
        }

    @property
    def native_value(self) -> float:
        """Get current temperature."""
        return self._native_value

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        for device in self.coordinator.data:
            if device["_id"] == self._unique_id.split("_")[0]:
                data = device
                break
        if data is None:
            return
        self.manufacturer = data["model"]
        self._name = data["name"]
        self.model = data["state"]["codeName"]
        self.fw_version = data["state"]["fwVer"]
        self._native_value = (
            data["state"]["currentTemp"]
            if self.type == "temperature"
            else data["state"]["humidity"]
        )
        self.async_write_ha_state()
