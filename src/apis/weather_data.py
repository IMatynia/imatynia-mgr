import pandas as pd
from pandas import DataFrame
from pydantic import BaseModel
import requests
import shapely as shp
import geopandas as gpd


class WeatherFeatures(BaseModel):
    """Weather features for a given day"""

    temp_min: float
    """Minimum temperature"""
    temp_max: float
    """Maximum temperature"""
    temp_avg: float
    """Average temperature"""

    rain_sum: float
    """Total rain that day"""
    rain_max: float
    """Burst max rain"""

    cloud_coverage_avg: float
    """average cloud coverage"""

    wind_speed_avg: float


class WeatherDataWrapper:
    def __init__(
        self, user_agent: str, weather_api_url: str = "https://api.met.no/"
    ) -> None:
        self.user_agent = user_agent
        self.url = weather_api_url

    def get_weather_info_at_point_raw(self, point: shp.Point) -> gpd.GeoDataFrame:
        url = f"{self.url}/weatherapi/locationforecast/2.0/compact?lat={point.x}&lon={point.y}"
        resp = requests.get(url)
        response = resp.json()
        geo_frame = gpd.GeoDataFrame.from_features([response], crs="EPSG:4326")
        return geo_frame.explode("timeseries", index_parts=False)

    def process_raw_weather(self, forecast: gpd.GeoDataFrame) -> WeatherFeatures:
        return NotImplemented

    def get_weather_at_point(self, point: shp.Point) -> WeatherFeatures:
        data = self.get_weather_info_at_point_raw(point)
        return self.process_raw_weather(data)
