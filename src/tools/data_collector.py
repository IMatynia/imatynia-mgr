import asyncio
import logging
from pathlib import Path
import rtoml
import typer
from src.configuration.collector import CollectorConfig
from src.configuration.secrets import Secrets
from src.data_collection.master import MasterCollector
from src.notifier.telegram_notifier import NotifierBotClient

app = typer.Typer()

logging.basicConfig(level=logging.INFO)


def dump_to_log_file(file: Path, errors: list[Exception]):
    with open(file, "a") as fd:
        for error in errors:
            fd.write(f"{error}\n\n")


@app.command()
def main(
    config_path: Path = Path("./configs"),
    dataset_path: Path = Path("./dataset/raw"),
    error_log_file: Path = Path("./errors.log"),
):
    async def inner():
        secrets: Secrets
        with open(config_path / "secrets.toml", "r") as fd:
            secrets = Secrets.model_validate(rtoml.load(fd))

        with open(config_path / "collector.toml", "r") as fd:
            collector_config = CollectorConfig.model_validate(rtoml.load(fd))

        assert dataset_path.exists(), "Dataset path does not exist!"

        async with NotifierBotClient(secrets) as notifier:
            collector = MasterCollector(collector_config, notifier)
            _, errors = await collector.run_daily_collection(dataset_path)
            if len(errors) > 0:
                await notifier.error(
                    f"The most recent run ended with {len(errors)}! Investigate it as soon as possible!"
                )
                dump_to_log_file(error_log_file, errors)

    asyncio.run(inner())


if __name__ == "__main__":
    app()
