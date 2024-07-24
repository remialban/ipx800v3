from datetime import timedelta
from httpx import Response
import logging

from .api import Api
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import NUMBER_OF_ANALOG_INPUTS, NUMBER_OF_RELAYS, NUMBER_OF_DIGITAL_INPUTS, \
    NUMBER_OF_COUNTERS


class AnalogInputCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, api: Api, update_interval: int):
        super().__init__(
            hass=hass,
            logger=logging.getLogger(__name__),
            name="Sensor coordinator",
            update_interval=timedelta(seconds=update_interval),
            always_update=True
        )
        self._api = api

    async def _async_update_data(self):
        response: Response = await self._api.call_api("api/xdevices.json?cmd=30")
        data = response.json()

        values: list[int | None] = []
        for i in range(1, NUMBER_OF_ANALOG_INPUTS + 1):
            key = "AN" + str(i)
            if key in data.keys():
                values.append(int(data[key]))
            else:
                values.append(None)

        return values


class CounterCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, api: Api, update_interval: int):
        super().__init__(
            hass=hass,
            logger=logging.getLogger(__name__),
            name="Sensor coordinator",
            update_interval=timedelta(seconds=update_interval),
            always_update=True
        )
        self._api = api


    async def _async_update_data(self):
        response: Response = await self._api.call_api("api/xdevices.json?cmd=40")
        data = response.json()

        values: list[int | None] = []
        for i in range(1, NUMBER_OF_COUNTERS + 1):
            key = "C" + str(i)
            if key in data.keys():
                values.append(int(data[key]))
            else:
                values.append(None)

        return values


class DigitalInputCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, api: Api, update_interval: int):
        super().__init__(
            hass=hass,
            logger=logging.getLogger(__name__),
            name="Binary sensor coordinator",
            update_interval=timedelta(seconds=update_interval),
            always_update=True
        )
        self._api = api

    async def _async_update_data(self):
        response: Response = await self._api.call_api("api/xdevices.json?cmd=10")
        data = response.json()

        values: list[bool | None] = []
        for i in range(1, NUMBER_OF_DIGITAL_INPUTS + 1):
            key = "IN" + str(i)
            if key in data.keys():
                values.append(int(data[key]) == 1)
            else:
                values.append(None)

        return values


class RelayCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, api: Api, update_interval: int):
        super().__init__(
            hass=hass,
            logger=logging.getLogger(__name__),
            name="Switch coordinator",
            update_interval=timedelta(seconds=update_interval),
            always_update=True
        )
        self._api = api

    async def _async_update_data(self):
        response: Response = await self._api.call_api("api/xdevices.json?cmd=20")
        data = response.json()

        values: list[bool | None] = []
        for i in range(1, NUMBER_OF_RELAYS + 1):
            key = "OUT" + str(i)
            if key in data.keys():
                values.append(int(data[key]) == 1)
            else:
                values.append(None)

        return values
