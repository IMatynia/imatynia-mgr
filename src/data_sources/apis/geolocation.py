import httpx
from shapely import Point


class GeolocationApi:
    def __init__(
        self, client: httpx.AsyncClient, user_agent: str, api_base_url: str
    ) -> None:
        self.client = client
        self.user_agent = user_agent
        self.url = api_base_url

    def geolocate_by_name(self, name: str) -> Point:
        ...