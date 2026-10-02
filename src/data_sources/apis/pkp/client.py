import datetime

import more_itertools
from playwright.async_api import BrowserContext

from src.data_sources.apis.pkp.schemas.network import RailNetworkEdge
from src.data_sources.apis.pkp.schemas.passenger_traffic import PassengerTrafic
from src.data_sources.apis.pkp.schemas.stations import StationHelper, StationsContainer
from src.data_sources.apis.pkp.schemas.train_connection import TrainConnection


class PKPIntercityApi:
    def __init__(
        self,
        browser: BrowserContext,
        frontend_url: str = "https://ebilet.intercity.pl",
        gtw_url: str = "https://api-gateway.intercity.pl",
    ) -> None:
        self.device = 956
        self.gtw_url = gtw_url
        self.browser = browser
        self.page = None
        self.front_url = frontend_url
        self._stations_cache = None

    async def init_browser_page(self):
        if self.page is None:
            self.page = await self.browser.new_page()
            await self.page.goto(self.front_url, wait_until="domcontentloaded")
            await self.page.get_by_role("button", name="Allow all").click()
            await self.page.get_by_role("combobox", name="From").click()
            await self.page.get_by_role("option", name="Gdańsk Gł").click()
            await self.page.get_by_role("combobox", name="To").click()
            await self.page.get_by_text("Kraków Gł").click()
            await self.page.get_by_test_id("ConfirmButton").click()
            await self.page.get_by_test_id("MainPageDesktop-confirm-button").click()

    async def get_stations(self) -> StationsContainer:
        if self._stations_cache is None:
            url = f"{self.gtw_url}/server/public/endpoint/Aktualizacja"
            response = await self.browser.request.post(
                url,
                data={"metoda": "pobierzStacje", "urzadzenieNr": self.device},
            )
            self._stations_cache = StationsContainer(await response.json())
        return self._stations_cache

    async def get_connections(
        self, departure: int, destination: int, date: datetime.date
    ) -> list[TrainConnection]:
        await self.init_browser_page()
        url = f"{self.gtw_url}/server/public/endpoint/Pociagi"
        response = await self.browser.request.post(
            url,
            data={
                "metoda": "wyszukajPolaczenia",
                "dataWyjazdu": f"{date.isoformat()} 00:00:00",
                "dataPrzyjazdu": f"{date.isoformat()} 23:59:59",
                "stacjaWyjazdu": departure,
                "stacjaPrzyjazdu": destination,
                "czasNaPrzesiadkeMin": 5,
                "stacjePrzez": [],
                "polaczeniaBezposrednie": 0,
                "polaczeniaNajszybsze": 0,
                "liczbaPolaczen": 0,
                "kategoriePociagow": [],
                "kodyPrzewoznikow": [],
                "rodzajeMiejsc": [],
                "typyMiejsc": [],
                "czasNaPrzesiadkeMax": 1440,
                "braille": 0,
                "liczbaPrzesiadekMax": 2,
                "atrybutyHandlowe": [],
                "urzadzenieNr": self.device,
            },
        )
        data = await response.json()
        res = []
        for conn in data["polaczenia"]:
            for train in conn["pociagi"]:
                res.append(TrainConnection(train))

        return res

    async def get_train_full_route(
        self, train: TrainConnection
    ) -> list[RailNetworkEdge]:
        await self.init_browser_page()
        stations = await self.get_stations()

        url = f"{self.gtw_url}/server/public/endpoint/Pociagi"
        response = await self.browser.request.post(
            url,
            data={
                "dataWyjazdu": train.get_departure_time(),
                "stacjaWyjazdu": stations.get_station_by_id(
                    train.get_departure()
                ).get_eva(),  # type: ignore
                "stacjaPrzyjazdu": stations.get_station_by_id(
                    train.get_destination()
                ).get_eva(),  # type: ignore
                "numerPociagu": train.train.train_num,
                "metoda": "pobierzTrasePrzejazdu",
                "jezyk": "PL",
                "urzadzenieNr": self.device,
            },
        )
        data = await response.json()
        out = []

        for v in more_itertools.windowed(data["trasePrzejezdu"]["trasaPrzejazdu"], 2):
            a: dict
            b: dict
            a, b = v  # type: ignore
            a_station = stations.get_station_by_eva(int(a["kodStacji"]))
            b_station = stations.get_station_by_eva(int(b["kodStacji"]))
            assert a_station and b_station
            _, _, _, a_dep_time_raw, _, _ = a["dataPrzyjazdu"].split(" ")
            a_dep_time = datetime.time.fromisoformat(a_dep_time_raw)
            _, _, _, b_arr_time_raw, _, _ = b["dataPrzyjazdu"].split(" ")
            b_arr_time = datetime.time.fromisoformat(b_arr_time_raw)
            out.append(
                RailNetworkEdge(
                    start=a_station.get_id(),
                    end=b_station.get_id(),
                    time_start=a_dep_time,
                    time_end=b_arr_time,
                    train=train.train,
                )
            )
        return out

    async def extract_network_information(
        self, stations: StationsContainer, rome: StationHelper, date: datetime.date
    ):
        visited = set()
        edges = set()

        conns: list[TrainConnection] = []
        # Parallelize
        for s in stations.iter():
            conns.extend(await self.get_connections(rome.get_id(), s.get_id(), date))
            conns.extend(await self.get_connections(s.get_id(), rome.get_id(), date))

        # Parallelize
        for con in conns:
            full_path = await self.get_train_full_route(con)
            for edge in full_path:
                visited.add(edge.start)
                visited.add(edge.end)
                edges.add(edge)
        return visited, edges

    async def get_passenger_traffic_on_connection(
        self, edge: RailNetworkEdge, date: datetime.date
    ) -> PassengerTrafic:
        stations = await self.get_stations()
        await self.init_browser_page()
        train_category = edge.train.train_cat.upper()
        train_number = edge.train.train_num
        departure, arrival = edge.get_real_dates_formatted(date)
        dep_station = stations.get_station_by_id(edge.start).get_eva()  # type: ignore
        arr_station = stations.get_station_by_id(edge.end).get_eva()  # type: ignore

        wagons_url = f"https://api-gateway.intercity.pl/grm/sklad/wbnet/{train_category}/{train_number}/{arrival}/{dep_station}/{departure}/{arr_station}"
        wagons = await self.browser.request.get(wagons_url)
        for wagon in wagons:
            await self.browser.request.get(
                "https://api-gateway.intercity.pl/grm/wagon/svg/wbnet/TLK/53105/11/1035,WITH_COMPARTMENTS/202606130544/202606131330/5100022/5100051"
            )


def get_occupied_seats_from_svg(svg_text: str) -> int: ...
