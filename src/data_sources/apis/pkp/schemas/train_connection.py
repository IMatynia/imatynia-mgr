from pydantic import BaseModel


class Train(BaseModel):
    train_cat: str
    train_num: int

    def __hash__(self) -> int:
        return hash((self.train_cat, self.train_num))


class TrainConnection:
    data: dict

    def __init__(self, data: dict) -> None:
        self.data = data

    def get_departure(self) -> int: ...

    def get_destination(self) -> int: ...

    def get_train(self) -> Train: ...
