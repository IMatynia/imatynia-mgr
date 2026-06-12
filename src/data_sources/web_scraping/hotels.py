from pydantic import BaseModel


class HotelInfoAtom(BaseModel):
    number_of_hotels: int
    percent_occupied: float

class BookingComHotelInfoScraper:
    def __init__(self) -> None:
        ...

    def scrape_for_location(self, poi_name: str) -> HotelInfoAtom:
        ...