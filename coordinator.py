from datetime import timedelta
from httpx import Response
import logging

from .api import Api
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, _DataT


class SensorCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, api: Api):
        super().__init__(
            hass=hass,
            logger=logging.getLogger(__name__),
            name="Sensor coordinator",
            update_interval=timedelta(seconds=10),
            always_update=True
        )
        self._api = api

    async def _async_update_data(self):
        response: Response = await self._api.call_api("api/xdevices.json?cmd=30")
        return response.json()


class SwitchCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, api: Api):
        super().__init__(
            hass=hass,
            logger=logging.getLogger(__name__),
            name="Switch coordinator",
            update_interval=timedelta(seconds=10),
            always_update=True
        )
        self._api = api

    async def _async_update_data(self):
        response: Response = await self._api.call_api("api/xdevices.json?cmd=20")
        data = response.json()

        values: list[int | None] = []
        for i in range(1, 33):
            key = "OUT" + str(i)
            if key in data.keys():
                values.append(int(data["OUT" + str(i)]))
            else:
                values.append(None)

        return values


class BinarySensorCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, api: Api):
        super().__init__(
            hass=hass,
            logger=logging.getLogger(__name__),
            name="Binary sensor coordinator",
            update_interval=timedelta(seconds=10),
            always_update=True
        )
        self._api = api

    async def _async_update_data(self):
        response: Response = await self._api.call_api("api/xdevices.json?cmd=10")
        data = response.json()

        values: list[bool | None] = []
        for i in range(1, 33):
            key = "IN" + str(i)
            if key in data.keys():
                values.append(int(data[key]) == 1)
            else:
                values.append(None)

        return values
