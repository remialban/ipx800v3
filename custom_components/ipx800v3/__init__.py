from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_ANALOG_INPUTS, \
    CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_COUNTERS, CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_DIGITAL_INPUTS, \
    CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_RELAYS
from .board import IPX800v3, IPX800v3View

PLATFORMS = [Platform.BINARY_SENSOR, Platform.SENSOR, Platform.SWITCH]


async def async_migrate_entry(hass, config_entry: ConfigEntry):
    if config_entry.version > 1:
        # This means the user has downgraded from a future version
        return False

    if config_entry.version == 1 and config_entry.minor_version == 1:
        new_options = {**config_entry.options, CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_ANALOG_INPUTS: 10,
                       CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_COUNTERS: 10,
                       CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_DIGITAL_INPUTS: 10,
                       CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_RELAYS: 10}

        hass.config_entries.async_update_entry(config_entry, options=new_options, minor_version=2, version=1)

    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    board = IPX800v3(
        hass=hass,
        options=config_entry.options,
        host=config_entry.data["host"],
        username=config_entry.data["username"],
        password=config_entry.data["password"],
        mac=config_entry.data["mac"],
        firmware_version=config_entry.data["version"]
    )

    hass.data[DOMAIN][config_entry.entry_id] = board

    await hass.config_entries.async_forward_entry_setups(
        entry=config_entry,
        platforms=PLATFORMS
    )

    await board.run_coordinators()

    hass.http.register_view(IPX800v3View(board, "remi", "toto"))

    config_entry.async_on_unload(config_entry.add_update_listener(update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_reload(entry.entry_id)
