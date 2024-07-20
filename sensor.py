from .const import DOMAIN
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo, format_mac
from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    from .board import IPX800v3

    board: IPX800v3 = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([sensor for sensor in board.get_sensors()])


class Sensor(SensorEntity):
    def __init__(self, pin: int, device: DeviceInfo):
        self._pin = pin
        self._attr_device_info = device
        self._attr_name = "Analog input " + str(pin)
        self._attr_unique_id = format_mac(device.get("serial_number")) + "-" + str(self._pin) + "-sensor"

    def set_state(self, state: float):
        self._attr_native_value = state
