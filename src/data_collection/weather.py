import asyncio
from datetime import timedelta
from loguru import logger
from pathlib import Path
from geopandas import GeoDataFrame
import httpx
import pandas
from src.configuration.collector import CollectorConfig
from src.data_collection.collector_base import DataCollectorBase
from src.data_sources.apis.weather_data import WeatherApiWrapper
from src.grid.commons import iterate_grid
from src.notifier.telegram_notifier import Notifier


class WeatherCollector(DataCollectorBase):
    def __init__(self, config: CollectorConfig, notifier: Notifier) -> None:
        self.config = config
        self.weather_client = WeatherApiWrapper(
            httpx.AsyncClient(), config.weather_api_user_agent, config.weather_api_url
        )
        self.notifier = notifier
        self.rate_limit = asyncio.Semaphore(config.weather_rate_limit)

    def get_name(self) -> str:
        return "Weather-data-collector"

    def collection_interval(self) -> timedelta:
        return timedelta(days=1)

    async def collect_single(self, seq, x, y) -> GeoDataFrame:
        x_max, y_max = self.config.area.grid_cell_counts
        x_frac = x / x_max
        y_frac = y / y_max

        point = self.config.area.bounding_rectangle.point_from_fractional_coordinates(
            x_frac, y_frac
        )
        async with self.rate_limit:
            try:
                logger.info(f"Downloading weather forecast for {point} as of today")
                return await self.weather_client.get_weather_info_at_point(point)
            except Exception as e:
                await self.notifier.error(f"Error gathering point ({x}, {y}): {e}")
                raise

    async def _collect(self) -> tuple[GeoDataFrame, list[Exception]]:
        x_max, y_max = self.config.area.grid_cell_counts
        tasks = []
        async with asyncio.TaskGroup() as tg:
            for i, (x, y) in enumerate(iterate_grid(x_max, y_max)):
                task = tg.create_task(self.collect_single(i, x, y))
                tasks.append(task)

        results = []
        errors = []

        for task in tasks:
            if task.cancelled():
                continue

            exception = task.exception()
            if exception is not None:
                errors.append(exception)
            else:
                results.append(task.result())

        return pandas.concat(results), errors

    async def run_collection(
        self, artifact_folder: Path
    ) -> tuple[list[Path], list[Exception]]:

        res, errors = await self._collect()
        path = artifact_folder / "weather.fgb"

        if path.exists():
            await self.notifier.info("Weather has already been generated!")
            return [path], []

        try:
            res.to_file(path, driver="FlatGeobuf")
            return ([path], errors)
        except Exception as e:
            return ([], errors + [e])
