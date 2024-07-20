import httpx
from httpx import Response


class Api:
    def __init__(self, host: str, username: str, password: str):
        self._host = host
        self._username = username
        self._password = password

    async def call_api(self, path: str = "") -> Response:
        auth = httpx.BasicAuth(username=self._username, password=self._password)

        async with httpx.AsyncClient() as client:
            return await client.get("http://" + "192.168.0.3" + "/" + path)
