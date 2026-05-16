from abc import ABC, abstractmethod
from pathlib import Path


class DataCollectorBase(ABC):
    @abstractmethod
    async def run_daily_collection(
        self, artifact_folder: Path
    ) -> tuple[list[Path], list[Exception]]:
        """Run collection logic and return a list of generated artifacts and a list of errors that occured"""
        ...
