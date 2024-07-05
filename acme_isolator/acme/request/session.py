import sys

from .nonce import NonceManager
from aiohttp import ClientSession, ClientResponseError
from asyncio import gather
from urllib.parse import urlparse
from ..objects.exceptions import UnexpectedResponseException, BadNonceException
from .jws import JwsBase, JwsKid
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
        locations: dict[str, str] = {k: f"https://{urlparse(v).netloc}" for (k, v) in self.directory}
        self.sessions = {location: ClientSession(headers={"User-Agent": USER_AGENT}, conn_timeout=15, read_timeout=15) for location in set(locations.values())}
        self.resource_sessions = {k: self.sessions[url] for (k, url) in locations.items()}

    async def check_session(self, url: str) -> ClientSession:
        location = f"https://{urlparse(url).netloc}"
        if location in self.sessions.keys():
            return self.sessions[location]
        else:
            new_session = ClientSession(base_url=location, headers={"User-Agent": USER_AGENT, "Content-Type": "application/jose+json"})
            await new_session.__aenter__()
            self.sessions[location] = new_session
            return new_session

    async def post(self, request: JwsBase, empty_response: bool = False) -> tuple[dict, int, str]:
        while True:
            try:
                resp, status, location = await self._post(request, empty_response=empty_response)
            except BadNonceException:
                request.reset_build()
            else:
                return resp, status, location

    async def _post(self, request: JwsBase, empty_response: bool) -> tuple[dict, int, str]:
        session = await self.check_session(request.url)
        payload = request.build(await self.nonce_pool.get_nonce())

        async with session.post(url=request.url, data=payload, headers={"Content-Type": "application/jose+json"}) as resp:
            try:
                assert resp.status < 400, "code"
                if empty_response:
                    data = None
                else:
                    assert not resp.headers["Content-Type"] == "application/problem+json", "header"
                    data = await resp.json()
                new_nonce = resp.headers["Replay-Nonce"]
                self.nonce_pool.put_nonce(new_nonce)

                next_url = resp.links.get("next", None)
                while next_url is not None:
                    extracted_properties = {"key": request.key, "url": next_url, "payload": b""}
                    if isinstance(request, JwsKid):
                        extracted_properties["kid"] = request.kid
                    next_request = request.__class__(**extracted_properties)
                    session = await self.check_session(next_url)
                    next_payload = next_request.build(await self.nonce_pool.get_nonce())
                    async with session.post(url=next_url, data=next_payload, headers={"Content-Type": "application/jose+json"}) as next_resp:
                        assert next_resp.status < 400, "code"
                        if empty_response:
                            data = None
                        else:
                            assert not next_resp.headers["Content-Type"] == "application/problem+json", "header"
                            new_data = await next_resp.json()
                        new_nonce = next_resp.headers["Replay-Nonce"]
                        self.nonce_pool.put_nonce(new_nonce)
                        next_url = next_resp.links.get("next", None)
                        for key in new_data.keys():
                            if key in data.keys() and type(new_data[key]) == list and type(data[key] ) == list:
                                data[key] += new_data[key]
                            elif key == "meta":
                                pass
                            elif key not in data.keys():
                                data[key] = new_data[key]
                            else:
                                raise NotImplementedError(f"Case of key '{key} existing in old and new dict, and having types {type(data[key])} and {type(new_data[key])} not covered.")

                return data, resp.status, resp.headers.get("Location", None)
            except KeyError as e:
                print(resp.status, file=sys.stderr)
                s = await resp.text()
                print(s, len(s), file=sys.stderr)
                raise e
            except AssertionError as e:
                if str(e) == "code":
                    raise UnexpectedResponseException(resp.status, response=await resp.json()).convert_exception()
                else:
                    raise ClientResponseError(status=resp.status, headers=resp.headers, history=(resp,), request_info=resp.request_info)
