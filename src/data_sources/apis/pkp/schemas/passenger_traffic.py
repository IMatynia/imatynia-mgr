import datetime
from typing import Self

from pydantic import BaseModel

from src.data_sources.apis.pkp.schemas.network import RailNetworkEdge


class PassengerTrafic(BaseModel):
    first_class: int
    second_class: int

    def __add__(self, other: Self):
        copy = self.model_copy()
        copy.first_class += other.first_class
        copy.second_class += other.second_class
        return copy

    @classmethod
    def zero(cls) -> Self:
        return cls(first_class=0, second_class=0)


class PassengerTrafficFlow(BaseModel):
    inflow: PassengerTrafic
    outflow: PassengerTrafic

    @classmethod
    def zero(cls) -> Self:
        return cls(inflow=PassengerTrafic.zero(), outflow=PassengerTrafic.zero())

    def add_inflow(self, flow: PassengerTrafic):
        self.inflow += flow

    def add_outflow(self, flow: PassengerTrafic):
        self.outflow += flow


class StatisticsContainer(BaseModel):
    stats: dict[int, PassengerTrafficFlow]
    when: datetime.date
    _visited: set[int]

    @classmethod
    def empty(cls, date: datetime.date) -> Self:
        return cls(when=date, stats={}, _visited=set())

    def visited(self, edge: RailNetworkEdge) -> bool:
        return hash(edge) in self._visited

    def add_flow(self, edge: RailNetworkEdge, flow: PassengerTrafic):
        self._visited.add(hash(edge))

        if edge.start not in self.stats:
            self.stats[edge.start] = PassengerTrafficFlow.zero()
        if edge.end not in self.stats:
            self.stats[edge.end] = PassengerTrafficFlow.zero()

        self.stats[edge.start].add_outflow(flow)
        self.stats[edge.end].add_inflow(flow)
