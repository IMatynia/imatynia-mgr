import asyncio
import datetime
from pathlib import Path

from loguru import logger

from src.configuration.collector import CollectorConfig
from src.data_collection.collector_base import DataCollectorBase
from src.data_collection.weather import WeatherCollector
from src.notifier.telegram_notifier import Notifier


class MasterCollector(DataCollectorBase):
    def __init__(self, config: CollectorConfig, notifier: Notifier) -> None:
        self.collectors: list[DataCollectorBase] = [WeatherCollector(config, notifier)]
        self.next_collector_call: dict[DataCollectorBase, datetime.datetime] = {}
        self.notifier = notifier

    def collection_interval(self) -> datetime.timedelta:
        return datetime.timedelta(minutes=10)

    def get_name(self) -> str:
        return "Master-collector"

    async def run_collection(
        self, artifact_folder: Path
    ) -> tuple[list[Path], list[Exception]]:
        now = datetime.datetime.now()
        raw_folder = artifact_folder / f"raw_{now.isoformat()}"
        raw_folder.mkdir(parents=True, exist_ok=True)

        now = datetime.datetime.now()

        tasks = []
        async with asyncio.TaskGroup() as tg:
            for collector in self.collectors:
                if (
                    collector in self.next_collector_call
                    and self.next_collector_call[collector] >= now
                ):
                    # collector didn add its interval yet or the interval has been reached
                    continue
                self.next_collector_call[collector] = (
                    now + collector.collection_interval()
                )

                logger.info(
                    f"Starting data collection for collector {collector.get_name()}"
                )
                task = tg.create_task(collector.run_collection(raw_folder))
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
        logger.info("Collection finished!")

        return [raw_folder], all_errors
