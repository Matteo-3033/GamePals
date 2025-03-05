import argparse
from typing import Any


class ArgParser:

    def __init__(self):
        parser = argparse.ArgumentParser(
            prog="Copilot",
            description="Copilot is a tool for emulating a video game controller, allowing gameplay using inputs from either a physical controller or an AI agent.",
        )

        parser.add_argument(
            "-c",
            "--config",
            type=argparse.FileType("rb"),
            help="Controller configuration file. An example configuration file can be found in the main repository of the project.",
            required=True,
        )

        self._add_arguments(parser)

        self.args = parser.parse_args()

    def _add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """ Adds Arguments to the parser """
        pass

    def get_config(self) -> 'Config':
        from copilot.utils import Config
        import tomllib

        config: dict[str, Any] = tomllib.load(self.args.config)

        return Config.from_dict(config)
