import datetime

from pydantic import BaseModel


class Timestamp(BaseModel):
    day_timestamp: int

    def inner(self) -> int:
        return self.day_timestamp

    @classmethod
    def from_date(cls, date: datetime.date) -> "Timestamp": ...

    def __hash__(self) -> int:
        return hash(self.inner())
