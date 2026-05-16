from pathlib import Path
from grid.commons import GridLayer


class WeatherLayer(GridLayer):
    @classmethod
    def load_from(cls, path: Path) -> "WeatherLayer":
        return NotImplemented
