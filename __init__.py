from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .board import IPX800v3, IPX800v3View


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    board = IPX800v3(
        hass=hass,
        host=config_entry.data["host"],
        username=config_entry.data["username"],
        password=config_entry.data["password"],
        mac=config_entry.data["mac"],
        firmware_version=config_entry.data["version"]
    )

    hass.data[DOMAIN][config_entry.entry_id] = board

    await hass.config_entries.async_forward_entry_setups(
        entry=config_entry,
        platforms=[Platform.BINARY_SENSOR, Platform.SENSOR, Platform.SWITCH]
    )

    await board.run_coordinators()

    hass.http.register_view(IPX800v3View(board, "remi", "toto"))
    return True
