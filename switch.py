from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo, format_mac
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator
from .const import DOMAIN
from .board import Api


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    from .board import IPX800v3

    board: IPX800v3 = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([switch for switch in board.get_switches()])


class Switch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator: DataUpdateCoordinator, pin: int, device: DeviceInfo, api: Api):
        super().__init__(coordinator, str(pin))
        self._pin = pin
        self._attr_device_info = device
        self._api = api
        self._attr_unique_id = format_mac(device.get("serial_number")) + "-" + str(self._pin) + "-switch"
        self._attr_name = "Switch " + str(pin)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = self.coordinator.data[self._pin - 1]
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any):
        await self._api.call_api("preset.htm?led" + str(self._pin) + "=1")
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any):
        await self._api.call_api("preset.htm?led" + str(self._pin) + "=0")
        await self.coordinator.async_refresh()

    def set_state(self, state: bool):
        self._attr_is_on = state
