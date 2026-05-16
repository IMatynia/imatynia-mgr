import asyncio
import datetime
import logging

import httpx

from src.configuration.secrets import Secrets

TELEGRAM_API_URL = "https://api.telegram.org"


class NotifierBotClient:
    """Using telegram to send messages about the state of the web scraping / training"""

    def __init__(self, secrets: Secrets) -> None:
        self.api_key = secrets.telegram_bot_api_key
        self.chat = secrets.telegram_recipient_id
        self.client = httpx.AsyncClient()
        self.message_queue = []
        self.last_message_sent: datetime.datetime = datetime.datetime(
            2020,
            1,
            1,
        )
        self.rate_limit = datetime.timedelta(seconds=2)
        self.mutex = asyncio.Semaphore()
        self._safe = False

    async def __aenter__(self):
        self._safe = True
        return self

    async def __aexit__(self, exc_type, exc, tb):
        async with self.mutex:
            if len(self.message_queue) > 0:
                await self.send_message("Closing notifier", force=True)

    async def error(self, message: str):
        logging.error(f"NOTIFIER: {message}")
        await self.send_message(f"#error\n{message}")

    async def info(self, message: str):
        logging.info(f"NOTIFIER: {message}")
        await self.send_message(f"#info\n{message}")

    async def send_message(self, message: str, force: bool = False):
        assert self._safe, "You must use the notifier within a RAII guard!"
        async with self.mutex:
            self.message_queue.append(message)
            if (
                not force
                and datetime.datetime.now() - self.last_message_sent < self.rate_limit
            ):
                return
            else:
                self.last_message_sent = datetime.datetime.now()
                message = "\n".join(self.message_queue)
                self.message_queue.clear()

                if len(message) > 3000:
                    message = message[:3000]
                await self.client.post(
                    f"{TELEGRAM_API_URL}/bot{self.api_key}/sendMessage",
                    json={"chat_id": self.chat, "text": message},
                )
