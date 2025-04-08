import argparse
import tomllib
from typing import Any

from .configuration_handler import ConfigurationHandler


class ArgParser:

    def __init__(self) -> None:
        parser = argparse.ArgumentParser(
            prog="Copilot",
            description="Copilot is a tool for emulating a video game controller, allowing gameplay using inputs from either a physical controller or an AI agent.",
        )

        parser.add_argument(
            "-gc",
            "--game_config",
            type=argparse.FileType("rb"),
            help="Game Configuration, containing game information and available actions for the game",
            required=True,
        )

        parser.add_argument(
            "-agc",
            "--agents_config",
            type=argparse.FileType("rb"),
            help="Agents Configuration for the Game, containing details on which agents are available",
            required=True,
        )

        parser.add_argument(
            "-asc",
            "--assistance_config",
            type=argparse.FileType("rb"),
            help="Assistance Configuration, containing details for configuring the Shared Control Architecture settings",
            required=True,
        )

        self._add_arguments(parser)

        self.args = parser.parse_args()

    def _add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Adds Arguments to the parser"""
        pass

    def get_game_config_dict(self) -> dict[str, Any]:
        config: dict[str, Any] = tomllib.load(self.args.game_config)
        return config

    def get_agents_config_dict(self) -> dict[str, Any]:
        config: dict[str, Any] = tomllib.load(self.args.agents_config)
        return config

    def get_assistance_config_dict(self) -> dict[str, Any]:
        config: dict[str, Any] = tomllib.load(self.args.assistance_config)
        return config

    def init_config_handler(self) -> "ConfigurationHandler":
        return ConfigurationHandler(
            game_config=self.get_game_config_dict(),
            agents_config=self.get_agents_config_dict(),
            assistance_config=self.get_assistance_config_dict(),
        )
