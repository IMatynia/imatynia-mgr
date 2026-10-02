import datetime
from collections.abc import Iterator
from typing import Self

from pydantic import BaseModel

from src.data_sources.apis.pkp.schemas.train_connection import Train


class RailNetworkEdge(BaseModel):
    start: int
    end: int
    time_start: datetime.time
    time_end: datetime.time
    train: Train

    def __hash__(self) -> int:
        return hash(
            (
                self.start,
                self.end,
                self.time_start.isoformat(),
                self.time_end.isoformat(),
                self.train,
            )
        )

    def get_real_dates_formatted(self, date: datetime.date) -> tuple[str, str]:
        start = datetime.datetime.combine(date, self.time_start).strftime("%Y%m%d%H%M")
        end = datetime.datetime.combine(date, self.time_end).strftime("%Y%m%d%H%M")
        return (start, end)


class RailNetwork(BaseModel):
    edge_list: set[RailNetworkEdge]
    edges: dict[int, set[RailNetworkEdge]]
    edges_reverse: dict[int, set[RailNetworkEdge]]

    def add_edge(self, edge: RailNetworkEdge):
        self.edge_list.add(edge)
        self.edges[edge.start].add(edge)
        self.edges_reverse[edge.end].add(edge)

    def iter(self) -> Iterator[RailNetworkEdge]:
        return self.edge_list.__iter__()

    @classmethod
    def from_edges(cls, edges: set[RailNetworkEdge]) -> Self:
        new = cls(edge_list=set(), edges={}, edges_reverse={})
        for edge in edges:
            new.add_edge(edge)
        return new
