import base64
from typing import Any
import xml.etree.ElementTree as ET

import httpx
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow, ConfigEntry
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from .const import DOMAIN, CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_ANALOG_INPUTS, \
    CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_COUNTERS, CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_DIGITAL_INPUTS, \
    CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_RELAYS


class MyConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1
    MINOR_VERSION = 2

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get("http://" + user_input["username"] + ":" + user_input["password"] + "@" + user_input["host"] + "/globalstatus.xml")
                    xml = ET.fromstring(response.text)

                    mac_address = xml.find("config_mac").text
                    hostname = xml.find("config_hostname").text
                    version = xml.find("version").text

                    return self.async_create_entry(
                        title=user_input["host"] + " (" + mac_address + ")",
                        data={
                            "mac": mac_address,
                            "host": user_input["host"],
                            "version": version,
                            "username": user_input["username"],
                            "password": user_input["password"],
                            "username_api": base64.b64encode(mac_address.encode("utf-8")).decode("utf-8"),
                            "username_password": "ddddf"
                        },
                        options={
                            CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_ANALOG_INPUTS: 10,
                            CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_COUNTERS: 10,
                            CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_DIGITAL_INPUTS: 10,
                            CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_RELAYS: 10
                        }
                    )
                except Exception as exc:
                    return self.async_abort(
                       reason="connection_impossible"
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("host"): str,
                vol.Optional("username", default=""): str,
                vol.Optional("password", default=""): str
            })
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return OptionFlowHandler(config_entry)


class OptionFlowHandler(OptionsFlow):
    def __init__(self, config_entry: ConfigEntry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_ANALOG_INPUTS,
                    default=self.config_entry.options.get(CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_ANALOG_INPUTS)
                ): vol.All(int, vol.Range(min=5)),
                vol.Required(
                    CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_COUNTERS,
                    default=self.config_entry.options.get(CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_COUNTERS)
                ): vol.All(int, vol.Range(min=5)),
                vol.Required(
                    CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_DIGITAL_INPUTS,
                    default=self.config_entry.options.get(CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_DIGITAL_INPUTS)
                ): vol.All(int, vol.Range(min=5)),
                vol.Required(
                    CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_RELAYS,
                    default=self.config_entry.options.get(CONF_OPTIONS_INTERVAL_OF_UPDATE_OF_RELAYS)
                ): vol.All(int, vol.Range(min=5)),
            })
        )
