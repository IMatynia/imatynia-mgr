from pydantic import BaseModel

from src.configuration.constants import SCRAPER_AGENT, USER_AGENT
from src.schemas.static_data import StaticAreaDetails


class CollectorConfig(BaseModel):
    weather_api_url: str = "https://api.met.no"
    weather_api_user_agent: str = USER_AGENT
    weather_downsample: float = 0.5
    weather_rate_limit: int = 4

    scraper_user_agent: str = SCRAPER_AGENT

    area: StaticAreaDetails

    rome_station_names: list[str] = ["Warszawa Centr."]
