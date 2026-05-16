import httpx
import shapely as shp
import geopandas as gpd


class WeatherApiWrapper:
    def __init__(
        self, client: httpx.AsyncClient, user_agent: str, weather_api_url: str
    ) -> None:
        self.user_agent = user_agent
        self.url = weather_api_url
        self.client = client
        self.client.headers["user-agent"] = self.user_agent

    async def get_weather_info_at_point(self, point: shp.Point) -> gpd.GeoDataFrame:
        url = f"{self.url}/weatherapi/locationforecast/2.0/compact?lat={point.x}&lon={point.y}"
        resp = await self.client.get(url)
        response = resp.json()
        geo_frame = gpd.GeoDataFrame.from_features([response], crs="EPSG:4326")
        return geo_frame.explode("timeseries", index_parts=False)
