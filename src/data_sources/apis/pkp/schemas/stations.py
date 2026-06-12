import logging
from typing import Iterator

from loguru import logger


class StationHelper:
    data: dict

    def __init__(self, data: dict) -> None:
        self.data = data
        for k in [
            "nazwa",
            "kod",
            "kodEPA",
            "kodEVA",
            "szerokoscGeograficzna",
            "dlugoscGeograficzna",
        ]:
            assert k in data, f"Missing fields in stacja {data}"
        assert data["kraj"] == "Polska"

    def get_name(self) -> str:
        return self.data["nazwa"]

    def get_id(self) -> int:
        return self.data["kod"]

    def get_epa(self) -> int:
        return self.data["kodEPA"]

    def get_eva(self) -> int:
        return self.data["kodEVA"]

    def get_pos(self) -> tuple[float, float]:
        return float(self.data["szerokoscGeograficzna"]), float(
            self.data["dlugoscGeograficzna"]
        )


class StationsContainer:
    stations: dict[int, StationHelper]

    def get_station_by_id(self, id: int) -> StationHelper | None:
        return self.stations.get(id)

    def get_all_station_ids(self) -> set[int]:
        return set(self.stations.keys())

    def get_station_by_name(self, name: str) -> StationHelper | None:
        for station in self.stations.values():
            if station.get_name() == name:
                return station
        return None

    def iter(self) -> Iterator[StationHelper]:
        for s in self.stations.values():
            yield s

    def __init__(self, stations_data: dict) -> None:
        self.stations = {}
        for station in stations_data["stacje"]:
            try:
                new_station = StationHelper(station)
                self.stations[new_station.get_id()] = new_station
            except Exception as e:
                logger.debug(e)

        assert len(self.stations) > 10, "Stations failed to download!"
