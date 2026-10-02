import json
from collections.abc import Callable
from pathlib import Path

from pydantic import BaseModel


def save_to(obj: BaseModel, dst: Path):
    dst.write_text(obj.model_dump_json(), encoding="utf-8")


def load_from[T](validator: Callable[[dict], T], src: Path) -> T:
    with open(src, "r", encoding="utf-8") as fd:
        d = json.load(fd)
        return validator(d)
