from .nonce import NonceManager
from aiohttp import ClientSession
from asyncio import gather
from urllib.parse import urlparse
from ..objects.directory import ACME_Directory
from .constants import USER_AGENT


class Session:
    directory_url: str
    directory: ACME_Directory
    sessions: dict[str, ClientSession]
    resource_sessions: dict[str, ClientSession]
    nonce_pool: NonceManager

    def __init__(self, directory_url: str):
        self.directory_url = directory_url

    async def __aenter__(self):
        self.directory = await ACME_Directory.get_directory(self.directory_url)
        await self.define_sessions()
        await gather(*[session.__aenter__() for session in self.sessions.values()])
        self.nonce_pool = await NonceManager(self.directory.newNonce, self.resource_sessions["newNonce"]).__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.nonce_pool.__aexit__(exc_type, exc_val, exc_tb)
        await gather(*[session.__aexit__(exc_type, exc_val, exc_tb) for session in self.sessions.values()])

    async def define_sessions(self):
        locations = {k: f"https://{urlparse(v).netloc}" for (k, v) in self.directory}
        self.sessions = {location: ClientSession(base_url=location, headers={"User-Agent": USER_AGENT}) for location in set(locations)}
        self.resource_sessions = {k: self.sessions[url] for (k, url) in locations}

    async def check_session(self, url: str) -> ClientSession:
        location = f"https://{urlparse(url).netloc}"
        if location in self.sessions.keys():
            return self.sessions[location]
        else:
            new_session = ClientSession(base_url=location, headers={"User-Agent": USER_AGENT})
            await new_session.__aenter__()
            self.sessions[location] = new_session
            return new_session

    async def post(self, url: str, payload: dict | bytes) -> tuple[dict, int]:
        session = await self.check_session(url)
        async with session.post(url=url, data=payload) as resp:
            data = await resp.json()
            status = resp.status
            new_nonce = resp.headers["Replay-Nonce"]
            self.nonce_pool.put_nonce(new_nonce)
            return data, status
