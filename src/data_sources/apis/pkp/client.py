from re import M

from httpx import AsyncClient
from src.configuration.constants import SCRAPER_AGENT
from src.data_sources.apis.pkp.schemas.network import RailNetworkEdge
from src.data_sources.apis.pkp.schemas.passenger_traffic import PassengerTrafic
from src.data_sources.apis.pkp.schemas.stations import StationHelper, StationsContainer
from src.data_sources.apis.pkp.schemas.train_connection import TrainConnection


class PKPIntercityApi:
    def __init__(
        self,
        client: AsyncClient,
        gtw_url: str = "https://api-gateway.intercity.pl",
        user_agent: str = SCRAPER_AGENT,
    ) -> None:
        self.device = 956
        self.gtw_url = gtw_url
        self.client = client
        self.user_agent = user_agent

    def get_headers(self) -> dict:
        return {"user-agent": self.user_agent,
                
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-GB,en;q=0.6",
    "cache-control": "no-cache",
    "content-type": "application/json",
    "dnt": "1",
    "origin": "https://ebilet.intercity.pl",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://ebilet.intercity.pl/",
    "sec-ch-ua": '"Not;A=Brand";v="99", "Brave";v="139", "Chromium";v="139"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "sec-gpc": "1",
                }

    async def get_stations(self) -> StationsContainer:
        url = f"{self.gtw_url}/server/public/endpoint/Aktualizacja"
        response = await self.client.post(
            url,
            headers=self.get_headers(),
            json={"metoda": "pobierzStacje", "urzadzenieNr": self.device},
        )
        return StationsContainer(response.json())

    async def get_connections(
        self, departure: int, destination: int
    ) -> list[TrainConnection]:
        url = f"{self.gtw_url}/server/public/endpoint/Pociagi"
        response = await self.client.post(
            url,
            headers=self.get_headers(),
            json={
                "metoda": "wyszukajPolaczenia",
                "wersja": "1.5.12_mobile",
                "url": f"https://ebilet.intercity.pl/wyszukiwanie?dwyj=2026-06-13&swyj={departure}&sprzy={destination}&time=21%3A14&przy=0&sprzez=&ticket100=1010&ticket50=&polbez=0",
                "dataWyjazdu": "2026-06-13 00:00:00",
                "dataPrzyjazdu": "2026-06-13 23:59:59",
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
        res = []
        for conn in response.json()["polaczenia"]:
            for train in conn["pociagi"]:
                res.append(TrainConnection(train))

        return res

    async def get_train_full_route(
        self, train: TrainConnection
    ) -> list[RailNetworkEdge]: ...

    async def extract_network_information(
        self, stations: StationsContainer, rome: StationHelper
    ):
        visited = set()
        edges = set()

        conns: list[TrainConnection] = []
        # Parallelize
        for s in stations.iter():
            conns.extend(await self.get_connections(rome.get_id(), s.get_id()))
            conns.extend(await self.get_connections(s.get_id(), rome.get_id()))

        # Parallelize
        for con in conns:
            full_path = await self.get_train_full_route(con)
            for edge in full_path:
                visited.add(edge.start)
                visited.add(edge.end)
                edges.add(edge)
        return visited, edges

    async def get_passenger_traffic_on_connection(
        self, edge: RailNetworkEdge
    ) -> PassengerTrafic: ...
