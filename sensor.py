from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator
from .const import DOMAIN
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo, format_mac
from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    from .board import IPX800v3

    board: IPX800v3 = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([sensor for sensor in board.get_sensors()])
    async_add_entities([counter for counter in board.get_counters()])


class Sensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator: DataUpdateCoordinator, pin: int, device: DeviceInfo):
        super().__init__(coordinator, pin)
        self._pin = pin
        self._attr_device_info = device
        self._attr_name = "Analog input " + str(pin)
        self._attr_unique_id = format_mac(device.get("serial_number")) + "-" + str(self._pin) + "-sensor"

    @callback
    def _handle_coordinator_update(self) -> None:
        try:
            if self.coordinator.data[self._pin - 1] is not None:
                self._attr_native_value = self.coordinator.data[self._pin - 1]
                self.async_write_ha_state()
        except:
            pass

    def set_state(self, state: float):
        self._attr_native_value = state


class Counter(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator: DataUpdateCoordinator, pin: int, device: DeviceInfo):
        super().__init__(coordinator, pin)
        self._pin = pin
        self._attr_device_info = device
        self._attr_name = "Counter " + str(pin)
        self._attr_unique_id = format_mac(device.get("serial_number")) + "-" + str(self._pin) + "-counter-sensor"

    @callback
    def _handle_coordinator_update(self) -> None:
        try:
            if self.coordinator.data[self._pin - 1] is not None:
                self._attr_native_value = self.coordinator.data[self._pin - 1]
                self.async_write_ha_state()
        except:
            pass

    def set_state(self, state: int):
        self._attr_native_value = state
