from collections import deque
import datetime
from pathlib import Path
import httpx
import pytest
from src.configuration.collector import CollectorConfig
from src.data_collection.trains import TrainsCollector
from src.data_collection.util import load_from, save_to
from src.data_sources.apis.pkp.client import PKPIntercityApi
from src.data_sources.apis.pkp.schemas.network import RailNetwork, RailNetworkEdge
from src.data_sources.apis.pkp.schemas.passenger_traffic import (
    StatisticsContainer,
)
from src.data_sources.apis.pkp.schemas.train_connection import TrainConnection
from src.notifier.telegram_notifier import DummyNotifier


@pytest.mark.asyncio
async def test_raw_api_calls():
    pkpclient = PKPIntercityApi(httpx.AsyncClient(http2=True))
    stations = await pkpclient.get_stations()
    connections = await pkpclient.get_connections(
        stations.get_station_by_name("Warszawa Centr.").get_id(),  # type: ignore
        stations.get_station_by_name("Warszawa Zach.").get_id(),  # type: ignore
    )
    route = await pkpclient.get_train_full_route(connections[0])
    info = await pkpclient.get_passenger_traffic_on_connection(route[0])


@pytest.mark.asyncio
async def test_graph(collector_config: CollectorConfig, tmp_path: Path):
    collector = TrainsCollector(collector_config, DummyNotifier(), tmp_path)

    graph = await collector.build_or_load_network_graph()
    pass


@pytest.mark.asyncio
async def test_collector(collector_config: CollectorConfig, tmp_path: Path):
    collector = TrainsCollector(collector_config, DummyNotifier(), tmp_path)

    await collector.run_collection(tmp_path)
    pass
