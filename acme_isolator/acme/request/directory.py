from aiohttp import request
from .constants import USER_AGENT


async def get_directory(directory_url: str):
    async with request("GET", directory_url, headers={"User-Agent": USER_AGENT}) as resp:
        resp.raise_for_status()
        j = await resp.json(encoding="utf-8")
        del j["meta"]
        return j
