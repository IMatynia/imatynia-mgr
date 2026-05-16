from pathlib import Path
from src.data_sources.apis.weather_data import WeatherApiWrapper, WeatherFeature
from grid.commons import iterate_grid, GridLayer
from src.schemas.static_data import BoundingBox
import numpy as np


class WeatherDownloader:
    @classmethod
    def download_daily(
        cls,
        measurement_shape: tuple[int, int],
        geo_boudning_box: BoundingBox,
        client: WeatherApiWrapper,
    ) -> np.ndarray:
        measurement_w, measurement_h = measurement_shape
        datapoints = np.ndarray((measurement_w, measurement_h), dtype=WeatherFeature)
        for i_w, i_h in iterate_grid(measurement_w, measurement_h):
            geo_point = geo_boudning_box.translate_grid_index_into_lat_lon(
                i_w, measurement_w, i_h, measurement_h
            )
            weather = client.get_weather_at_point(geo_point)
            datapoints[i_w][i_h] = weather
        return datapoints

    def save_to(
        self,
        measurement_shape: tuple[int, int],
        grid_shape: tuple[int, int],
        timestamp: int,
        raw: np.ndarray,
        path_prefix: Path,
    ):
        """Precompressed representation that can be cheaply loaded in as a layer."""
        assert raw.dtype == WeatherFeature

        # Save as raw

        # Save as final interpolated grid

        pass

    def interpolate_grid(
        self, original_wh: tuple[int, int], new_wh: tuple[int, int], data: np.ndarray
    ) -> np.ndarray: ...


class WeatherLayer(GridLayer):
    @classmethod
    def load_from(cls, path: Path) -> "WeatherLayer":
        return NotImplemented
