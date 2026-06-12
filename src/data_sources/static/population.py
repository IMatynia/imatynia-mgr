from typing import Self

from httpx import AsyncClient
from pydantic import BaseModel

from src.configuration.collector import CollectorConfig


class Region(BaseModel):
    region_id: str
    name: str
    location: tuple[float, float]
    population: int


class PopulationData(BaseModel):
    regions: dict[str, Region]

    @classmethod
    def generate(cls, client: AsyncClient, configuration: CollectorConfig) -> Self:
        # Download
        # Load from csv into a good structure
        # Geolocate!
        # Return object
        ...

    def get_regions_sorted_by_population(self):
        return sorted(self.regions.values(), key=lambda x: x.population)
