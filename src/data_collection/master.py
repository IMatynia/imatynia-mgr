import asyncio
import datetime
import logging
from pathlib import Path
from secrets import token_urlsafe
import shutil
from src.configuration.collector import CollectorConfig
from src.data_collection.collector_base import DataCollectorBase
from src.data_collection.weather import WeatherCollector
from src.notifier.telegram_notifier import NotifierBotClient


class MasterCollector(DataCollectorBase):
    def __init__(self, config: CollectorConfig, notifier: NotifierBotClient) -> None:
        self.collectors: list[DataCollectorBase] = [WeatherCollector(config, notifier)]
        self.notifier = notifier

    def get_name(self) -> str:
        return "Master-collector"

    async def run_daily_collection(
        self, artifact_folder: Path
    ) -> tuple[list[Path], list[Exception]]:
        raw_folder = artifact_folder / f"raw_{token_urlsafe(5)}"
        raw_folder.mkdir(parents=True, exist_ok=True)

        tasks = []
        async with asyncio.TaskGroup() as tg:
            for collector in self.collectors:
                logging.info(
                    f"Starting data collection for collector {collector.get_name()}"
                )
                task = tg.create_task(collector.run_daily_collection(raw_folder))
                tasks.append(task)

        all_errors: list[Exception] = []

        for task in tasks:
            if task.cancelled():
                continue

            exception = task.exception()
            if exception is not None:
                await self.notifier.error(f"Magor error: {exception}")
                all_errors.append(exception)
            else:
                _, errors = task.result()
                all_errors.extend(errors)
        logging.info("Collection finished!")
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        zip_name = f"daily_{timestamp}"

        target_zip_path = artifact_folder / zip_name

        await asyncio.to_thread(
            shutil.make_archive,
            base_name=str(target_zip_path),
            format="zip",
            root_dir=str(raw_folder),
        )

        await asyncio.to_thread(shutil.rmtree, str(raw_folder))

        return [artifact_folder / f"{zip_name}.zip"], all_errors
