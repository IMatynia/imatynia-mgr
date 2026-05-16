import asyncio
import pytest
from src.configuration.secrets import Secrets
from src.notifier.telegram_notifier import NotifierBotClient


@pytest.mark.asyncio
async def test_telegram_notif(secrets: Secrets):
    async with NotifierBotClient(secrets) as notifier:
        for i in range(30):
            await notifier.info(f"test message {i}")
            await asyncio.sleep(0.1)
