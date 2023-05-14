from asyncio import Queue, QueueEmpty, Task, create_task, current_task, CancelledError, gather, wait
from aiohttp import ClientSession
from .constants import USER_AGENT
from urllib.parse import urlparse


class NonceManager:
    queue: Queue
    tasks: set[Task]
    session: ClientSession
    url: str
    initialized: bool = False
    loop: Task

    def __init__(self, url: str):
        self.url = url
        self.queue = Queue()
        self.tasks = set()

    async def __aenter__(self):
        parsed = urlparse(self.url)
        self.session = ClientSession(base_url=f"{parsed.scheme}://{parsed.netloc}", headers = {"User-Agent": USER_AGENT})
        await self.session.__aenter__()
        self.initialized = True
        self.loop = create_task(self.refill_loop())
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        for task in self.tasks:
            task.cancel()
        await gather(*self.tasks)
        self.initialized = False
        return await self.session.__aexit__(exc_type, exc_val,exc_tb)

    async def _fetch_nonce(self):
        try:
            async with self.session.get(self.url) as resp:
                if resp.status == 200:
                    self.queue.put_nowait(resp.headers.get("Replay-Nonce"))
                else:
                    raise ConnectionError(f"Server returned status code {resp.status} while getting nonce.")
        except CancelledError:
            pass
        finally:
            self.tasks.remove(current_task())

    async def _request_nonce(self):
        self.tasks.add(create_task(self._fetch_nonce()))

    def put_nonce(self, nonce):
        self.queue.put_nowait(nonce)

    async def get_nonce(self):
        assert self.initialized
        try:
            return self.queue.get_nowait()
        except QueueEmpty:
            await self._request_nonce()
            return await self.queue.get()
        finally:
            self.queue.task_done()

    async def refill_loop(self):
        while True:
            if len(self.tasks) == 0 and self.queue.qsize() == 0:
                await gather(*[self._request_nonce() for _ in range(10)])
