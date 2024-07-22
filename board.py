import base64
from types import MappingProxyType
from typing import Any

from aiohttp import web

from homeassistant.components.http import HomeAssistantRequest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.http import HomeAssistantView
from .api import Api
from .binary_sensor import BinarySensor
from .const import DOMAIN, NUMBER_OF_COUNTERS, NUMBER_OF_DIGITAL_INPUTS, NUMBER_OF_RELAYS, \
    NUMBER_OF_ANALOG_INPUTS, CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_RELAYS, \
    CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_ANALOG_INPUTS, CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_DIGITAL_INPUTS, \
    CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_COUNTERS
from .coordinator import RelayCoordinator, AnalogInputCoordinator, DigitalInputCoordinator, CounterCoordinator
from .sensor import AnalogInput, Counter
from .switch import Relay


class IPX800v3:
    def __init__(
            self,
            hass: HomeAssistant,
            options: MappingProxyType[str, Any],
            host: str, username: str|None,
            password: str|None, mac: str|None,
            firmware_version: str|None
    ):
        self._hass = hass
        self._host = host
        self._username = username
        self._password = password
        self._mac = mac
        self._firmware_version = firmware_version

        self._device = DeviceInfo(
            name="IPX800v3 (" + self._mac + ")",
            model="IPX800v3",
            manufacturer="GCE Electronics",
            sw_version=self._firmware_version,
            serial_number=self._mac,
            identifiers={
                (DOMAIN, self._mac)
            }
        )

        self._api = Api(
            host=self._host,
            username=self._username,
            password=self._password
        )

        self._relay_coordinator = RelayCoordinator(self._hass, self._api, options[CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_RELAYS])
        self._analog_input_coordinator = AnalogInputCoordinator(self._hass, self._api, options[CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_ANALOG_INPUTS])
        self._digital_input_coordinator = DigitalInputCoordinator(self._hass, self._api, options[CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_DIGITAL_INPUTS])
        self._counter_coordinator = CounterCoordinator(self._hass, self._api, options[CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_COUNTERS])

        self._binary_sensors = [BinarySensor(self._digital_input_coordinator, i, self._device) for i in range(1, NUMBER_OF_DIGITAL_INPUTS + 1)]
        self._counters = [Counter(self._counter_coordinator, i, self._device) for i in range(1, NUMBER_OF_COUNTERS + 1)]
        self._switches = [Relay(self._relay_coordinator, i, self._device, self._api) for i in range(1, NUMBER_OF_RELAYS + 1)]
        self._sensors = [AnalogInput(self._analog_input_coordinator, i, self._device) for i in range(1, NUMBER_OF_ANALOG_INPUTS + 1)]

    async def run_coordinators(self):
        await self._relay_coordinator.async_config_entry_first_refresh()
        await self._analog_input_coordinator.async_config_entry_first_refresh()
        await self._digital_input_coordinator.async_config_entry_first_refresh()
        await self._counter_coordinator.async_config_entry_first_refresh()

    def get_switches(self) -> list[Relay]:
        return self._switches

    def get_binary_sensors(self) -> list[BinarySensor]:
        return self._binary_sensors

    def get_sensors(self) -> list[AnalogInput]:
        return self._sensors

    def get_counters(self) -> list[Counter]:
        return self._counters

    def _get_url(self):
        return "http://" + self._host

    def get_mac(self):
        return self._mac


def check_api_auth(request: HomeAssistantRequest, username: str, password: str) -> bool:
    if request.headers.get("Authorization") is None:
        return False
    if not request.headers.get("Authorization").startswith("Basic"):
        return False

    auth = request.headers.get("Authorization").split(" ")[1]
    auth = base64.b64decode(auth).decode("utf-8").split(":")

    return auth[0] == username and auth[1] == password


def check_url(board: IPX800v3, type: str, id: str, state: str) -> bool:
    if not id.isnumeric():
        return False
    id = int(id)
    try:
        state = float(state)
    except ValueError:
        return False

    if type not in ["relay", "analog_input", "digital_input"]:
        return False

    if id < 1:
        return False

    if state in ["relay", "digital_input"] and state not in [0, 1]:
        return False

    if type == "relay" and id > NUMBER_OF_RELAYS:
        return False
    if type == "digital_input" and id > NUMBER_OF_DIGITAL_INPUTS:
        return False
    if type == "analog_input" and id > NUMBER_OF_ANALOG_INPUTS:
        return False
    return True


class IPX800v3View(HomeAssistantView):
    requires_auth = False

    def __init__(self, board: IPX800v3, username: str, password: str):
        self._username = username
        self._password = password
        self._board = board

        mac_encoded = base64.b64encode(self._board.get_mac().encode("utf-8")).decode("utf-8")
        self.url = "/api/ipx800v3/" + mac_encoded + "/{type}/{id}/{state}"
        self.name = "api:ipx800v3:" + mac_encoded

    async def get(self, request: HomeAssistantRequest, type: str, id: str, state: str):
        if not check_api_auth(request, self._username, self._password):
            return web.Response(status=401, text="Unauthorized")

        if not check_url(self._board, type, id, state):
            return web.Response(status=400, text="Bad request")

        id = int(id)
        state = float(state)

        if type == "relay":
            switch = self._board.get_switches()[id - 1]
            switch.set_state(state == 1)
            await switch.async_update_ha_state(True)
        elif type == "digital_input":
            binary_sensor = self._board.get_binary_sensors()[id - 1]
            binary_sensor.set_state(state == 1)
            await binary_sensor.async_update_ha_state(True)
        elif type == "analog_input":
            sensor = self._board.get_sensors()[id - 1]
            sensor.set_state(state)
            await sensor.async_update_ha_state(True)

        return web.Response(status=200, text="OK")
