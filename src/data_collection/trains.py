import datetime
from collections import deque
from pathlib import Path
from venv import logger

import httpx

from src.configuration.collector import CollectorConfig
from src.data_collection.collector_base import DataCollectorBase
from src.data_collection.util import load_from, save_to
from src.data_sources.apis.pkp.client import PKPIntercityApi
from src.data_sources.apis.pkp.schemas.network import RailNetwork
from src.data_sources.apis.pkp.schemas.passenger_traffic import StatisticsContainer
from src.notifier.telegram_notifier import Notifier


class TrainsCollector(DataCollectorBase):
    def __init__(
        self,
        config: CollectorConfig,
        notifier: Notifier,
        static_artifacts_path: Path,
    ) -> None:
        self.config = config
        self.notifier = notifier
        self.pkpclient = PKPIntercityApi(httpx.AsyncClient())
        self.network_graph_path = static_artifacts_path / "rail_network.json"

    def get_name(self) -> str:
        return "Train-network-data-collector"

    def collection_interval(self) -> datetime.timedelta:
        return datetime.timedelta(minutes=15)

    async def build_connection_graph(self) -> RailNetwork:
        logger.info("Building train network graph")
        stations = await self.pkpclient.get_stations()
        visited_total = set()
        edges_total = set()
        for rome_name in self.config.rome_station_names:
            rome = stations.get_station_by_name(rome_name)
            assert rome

            logger.info(f"Querying connections to {rome_name}")
            visited, edges = await self.pkpclient.extract_network_information(
                stations, rome
            )
            visited_total.update(visited)
            edges_total.update(edges)

        all_station_ids = stations.get_all_station_ids()
        not_visited = all_station_ids.difference(visited_total)

        graph = RailNetwork.from_edges(edges_total)
        logger.info(
            f"visited_stations: {len(visited_total)}, missing:{len(not_visited)}"
        )

        return graph

    async def build_or_load_network_graph(self) -> RailNetwork:
        if self.network_graph_path.exists():
            return load_from(RailNetwork.model_validate, self.network_graph_path)
        else:
            graph = await self.build_connection_graph()
            save_to(graph, self.network_graph_path)
            return graph

    async def run_collection(
        self, artifact_folder: Path
    ) -> tuple[list[Path], list[Exception]]:

        graph = await self.build_or_load_network_graph()

        # Restarts at midnight
        now = datetime.datetime.now()
        dst_path = artifact_folder / f"statistics_{now.date().isoformat()}.json"

        statistics: StatisticsContainer
        if dst_path.exists():
            statistics = load_from(StatisticsContainer.model_validate, dst_path)
        else:
            statistics = StatisticsContainer.empty(now.date())

        dq = deque(graph.iter())
        for edge in dq:
            if edge.time_start < (now + datetime.timedelta(minutes=30)).time():
                if statistics.visited(edge):
                    continue
                flow = await self.pkpclient.get_passenger_traffic_on_connection(edge)
                statistics.add_flow(edge, flow)

        save_to(statistics, dst_path)
        return [dst_path], []
