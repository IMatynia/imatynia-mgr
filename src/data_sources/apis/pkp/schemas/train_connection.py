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
        self.train = Train(
            train_cat=data["kategoriaPociagu"], train_num=data["nrPociagu"]
        )

    def get_departure(self) -> int:
        return self.data["stacjaWyjazdu"]

    def get_destination(self) -> int:
        return self.data["stacjaPrzyjazdu"]

    def get_train(self) -> Train:
        return self.train

    def get_departure_time(self) -> str:
        return self.data["dataWyjazdu"]
