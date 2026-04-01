from enum import Enum

import numpy as np


class GridBase:
    width: int
    height: int


class LayerTypes(str, Enum):
    static = "static"
    dynamic = "dynamic"
    uniform = "uniform"
    output = "output"


class GridLayer(GridBase):
    name: str
    layer_type: LayerTypes
    data: np.ndarray

    def __init__(
        self, w: int, h: int, name: str, layer_type: LayerTypes, data: np.ndarray
    ) -> None:
        self.name = name
        self.layer_type = layer_type
        self.data = data
        self.height = h
        self.width = w


class GridCombine(GridBase):
    timestamp: int
    layers: dict[str, GridLayer]

    def __init__(self, w: int, h: int, timestamp: int, layers: list[GridLayer]) -> None:
        self.width = w
        self.height = h
        self.timestamp = timestamp
        self.layers = {layer.name: layer for layer in layers}

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
