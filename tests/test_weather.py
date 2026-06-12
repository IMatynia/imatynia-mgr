from pathlib import Path
from geopandas import GeoDataFrame
import httpx
import pytest
from src.configuration.collector import CollectorConfig
from src.configuration.secrets import Secrets
from src.data_collection.weather import WeatherCollector
from src.data_sources.apis.weather_data import WeatherApiWrapper
from src.configuration.constants import WARSAW_POINT
from src.notifier.telegram_notifier import NotifierBotClient


@pytest.mark.asyncio
async def test_api_client(collector_config: CollectorConfig):
    client = WeatherApiWrapper(
        httpx.AsyncClient(),
        collector_config.weather_api_user_agent,
        collector_config.weather_api_url,
    )
    response = await client.get_weather_info_at_point(WARSAW_POINT)
    assert response.shape[0] > 50 and response.shape[1] == 3


@pytest.mark.asyncio
async def test_download_and_process_weather(
    secrets: Secrets, collector_config: CollectorConfig, tmp_path: Path
):
    async with NotifierBotClient(secrets) as notifier:
        collector = WeatherCollector(collector_config, notifier)
        paths, errors = await collector.run_collection(tmp_path)
        assert len(errors) == 0
        assert len(paths) == 1
        gdf = GeoDataFrame.from_file(paths[0])
        assert gdf.shape[1] == 3 and gdf.shape[0] > 400
