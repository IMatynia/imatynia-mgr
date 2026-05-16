from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Iterator, Self
import numpy as np


def iterate_grid(w: int, h: int) -> Iterator[tuple[int, int]]:
    inner = GridBase(w, h)
    for cell in inner.cell_iterator():
        yield cell


class GridBase:
    width: int
    height: int

    def __init__(self, w: int, h: int) -> None:
        self.width = w
        self.height = h

    def cell_iterator(self) -> Iterator[tuple[int, int]]:
        for x in range(self.width):
            for y in range(self.height):
                yield (x, y)

    def wh(self) -> tuple[int, int]:
        return self.width, self.height


class LayerTypes(str, Enum):
    static = "static"
    dynamic = "dynamic"
    uniform = "uniform"
    output = "output"


class GridLayer(GridBase, ABC):
    name: str
    layer_type: LayerTypes
    data: np.ndarray

    def __init__(
        self, w: int, h: int, name: str, layer_type: LayerTypes, data: np.ndarray
    ) -> None:
        self.name = name
        self.layer_type = layer_type
        self.data = data
        super().__init__(w, h)

    @classmethod
    @abstractmethod
    def from_file(cls, path: Path) -> Self: ...


class MultilayerGrid(GridBase):
    timestamp: int
    layers: dict[str, GridLayer]

    def __init__(self, timestamp: int, layers: list[GridLayer]) -> None:
        super().__init__(layers[0].width, layers[0].height)
        self.timestamp = timestamp
        self.layers = {layer.name: layer for layer in layers}
        for layer in layers:
            assert layer.wh() == self.wh(), (
                f"Layer {layer.name} has invalid shape {layer.wh()} and should be {self.wh()}"
            )

    def get_sample(
        self, x_data_layers: list[str], y_layers: list[str]
    ) -> tuple[np.ndarray, np.ndarray]:
        X = []
        for name in x_data_layers:
            X.append(self.layers[name].data)

        Y = []
        for name in y_layers:
            Y.append(self.layers[name].data)

        return (np.stack(X), np.stack(Y))


class MultiLayerGridSeries(GridBase):
    time_series: dict[int, MultilayerGrid]

    def __init__(self, series: list[MultilayerGrid]) -> None:
        super().__init__(series[0].width, series[0].height)
        for grid in series:
            assert grid.wh() == self.wh(), (
                f"Timestamp {grid.timestamp} has invalid shape {grid.wh()} but should be {self.wh()}"
            )
        self.time_series = {grid.timestamp: grid for grid in series}
