import datetime
from pathlib import Path

import pytest
from loguru import logger
from playwright.async_api import async_playwright

from src.configuration.collector import CollectorConfig
from src.data_collection.trains import TrainsCollector
from src.data_sources.apis.pkp.client import PKPIntercityApi
from src.notifier.telegram_notifier import DummyNotifier


@pytest.mark.asyncio
async def test_raw_api_calls():
    async with async_playwright() as p:
        # 1. Launch a real browser (Chromium)
        # Using headless=False can sometimes help avoid detection, but headless=True usually works first.
        browser = await p.chromium.launch(headless=False)

        # Create a browser context (isolated session)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720},
        )
        pkpclient = PKPIntercityApi(context)
        await pkpclient.init_browser_page()
        logger.info("Stations")
        stations = await pkpclient.get_stations()
        logger.info("Connections")
        now = datetime.datetime.now()
        connections = await pkpclient.get_connections(
            stations.get_station_by_name("Gdańsk Gł.").get_id(),  # type: ignore
            stations.get_station_by_name("Kraków Gł.").get_id(),  # type: ignore
            now.date(),
        )
        route = await pkpclient.get_train_full_route(connections[1])
        await pkpclient.get_passenger_traffic_on_connection(route[2], now.date())


@pytest.mark.asyncio
async def test_graph(collector_config: CollectorConfig, tmp_path: Path):
    collector = TrainsCollector(collector_config, DummyNotifier(), tmp_path)

    await collector.build_or_load_network_graph()


@pytest.mark.asyncio
async def test_collector(collector_config: CollectorConfig, tmp_path: Path):
    collector = TrainsCollector(collector_config, DummyNotifier(), tmp_path)

    await collector.run_collection(tmp_path)
