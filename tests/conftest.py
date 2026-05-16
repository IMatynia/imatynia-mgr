import pytest
import rtoml
from src.configuration.collector import CollectorConfig
from src.schemas.static_data import BoundingBox, StaticAreaDetails
from src.configuration.constants import ROOT
from src.configuration.secrets import Secrets
from src.configuration.general_config import GeneralConfig


def config() -> GeneralConfig:
    return GeneralConfig()


@pytest.fixture(scope="session")
def secrets() -> Secrets:
    with open(ROOT / "secrets.toml", "r") as fd:
        return Secrets.model_validate(rtoml.load(fd))


@pytest.fixture(scope="session")
def collector_config() -> CollectorConfig:
    return CollectorConfig(
        area=StaticAreaDetails(
            name="example",
            description="example",
            bounding_rectangle=BoundingBox(
                bottom_left=(-10.0, -10.0), top_right=(40.0, 20.0)
            ),
            grid_cell_counts=(3, 2),
        )
    )
