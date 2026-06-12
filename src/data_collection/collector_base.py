from abc import ABC, abstractmethod
from datetime import timedelta
from pathlib import Path


class DataCollectorBase(ABC):
    @abstractmethod
    def get_name(self) -> str: ...

    @abstractmethod
    async def run_collection(
        self, artifact_folder: Path
    ) -> tuple[list[Path], list[Exception]]:
        """Run collection logic and return a list of generated artifacts and a list of errors that occured"""
        ...

    @abstractmethod
    def collection_interval(self) -> timedelta:
        """How often does the collection happen?"""
        ...

