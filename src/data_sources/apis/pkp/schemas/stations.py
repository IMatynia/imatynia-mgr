from collections.abc import Iterator

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
    stations_id: dict[int, StationHelper]
    stations_eva: dict[int, StationHelper]
    stations: dict[str, StationHelper]

    def get_station_by_id(self, id: int) -> StationHelper | None:
        return self.stations_id.get(id)

    def get_station_by_eva(self, id: int) -> StationHelper | None:
        return self.stations_eva.get(id)

    def get_station_by_name(self, name: str) -> StationHelper | None:
        return self.stations.get(name)

    def get_all_station_ids(self) -> set[int]:
        return set(self.stations_id.keys())

    def iter(self) -> Iterator[StationHelper]:
        yield from self.stations_id.values()

    def __init__(self, stations_data: dict) -> None:
        self.stations_id = {}
        self.stations_eva = {}
        self.stations = {}
        for station in stations_data["stacje"]:
            try:
                new_station = StationHelper(station)
                self.stations_id[new_station.get_id()] = new_station
                self.stations_eva[new_station.get_eva()] = new_station
                self.stations[new_station.get_name()] = new_station
            except Exception as e:
                logger.debug(e)

        assert len(self.stations_id) > 10, "Stations failed to download!"
