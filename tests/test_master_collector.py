from pathlib import Path
import pytest
from src.configuration.collector import CollectorConfig
from src.configuration.secrets import Secrets
from src.data_collection.master import MasterCollector
from src.notifier.telegram_notifier import NotifierBotClient


@pytest.mark.asyncio
async def test_master_downloader(
    secrets: Secrets, collector_config: CollectorConfig, tmp_path: Path
):
    async with NotifierBotClient(secrets) as notifier:
        collector = MasterCollector(collector_config, notifier)

        paths, errors = await collector.run_daily_collection(tmp_path)
        assert len(errors) == 0
        assert len(paths) == 1
        assert paths[0].name.endswith("zip")
