from pathlib import Path

from grid.commons import GridLayer, LayerTypes


class WeatherLayer(GridLayer):
    @classmethod
    def load_from(cls, path: Path) -> "WeatherLayer":
        return NotImplemented

    def save_to(self, path: Path):
        return NotImplemented

    @classmethod
    def generate_layer(cls) -> "WeatherLayer":
        return NotImplemented
