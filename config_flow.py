import base64
import logging
from typing import Any
import xml.etree.ElementTree as ET

import httpx
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from .const import DOMAIN


class MyConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1
    MINOR_VERSION = 1

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