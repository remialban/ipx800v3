from homeassistant.helpers.device_registry import DeviceInfo


class Device:
    def __init__(self, device_info: DeviceInfo):
        self.device_info = device_info
