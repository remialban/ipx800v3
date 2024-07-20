from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo, format_mac
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    from .board import IPX800v3
    from .const import DOMAIN

    board: IPX800v3 = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([binary_sensor for binary_sensor in board.get_binary_sensors()])


class BinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator: DataUpdateCoordinator, pin: int, device: DeviceInfo):
        super().__init__(coordinator, pin)
        self._pin = pin
        self._attr_device_info = device
        self._attr_name = "Input " + str(pin)
        self._attr_unique_id = format_mac(device.get("serial_number")) + "-" + str(self._pin) + "-binary_sensor"

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_is_on = self.coordinator.data[self._pin - 1]
        self.async_write_ha_state()

    def set_state(self, state: bool):
        self._attr_is_on = state
