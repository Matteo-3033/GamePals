from typing import Any, Mapping, TypedDict

from ..agents import AssistanceLevels
from ..command_arbitrators import PolicyTypes
from ..command_arbitrators.policies import PolicyName


class Config(TypedDict, total=True):
    AssistanceLevels: list[AssistanceLevels]
    PolicyTypes: PolicyTypes

    @staticmethod
    def from_dict(config: Mapping[str, Any]) -> "Config":
        assistance_levels = config["AssistanceLevels"]
        if not isinstance(assistance_levels, list):
            assistance_levels = [assistance_levels]

        try:
            policy_types = {
                input: PolicyName[policy_name]
                for input, policy_name in config["PolicyTypes"].items()
            }
        except KeyError as e:
            raise ValueError(f"Configuration is not valid: {e}")

        return Config(
            AssistanceLevels=assistance_levels,
            PolicyTypes=policy_types,
        )


def get_config() -> Config:
    import argparse
    import tomllib

    parser = argparse.ArgumentParser(
        prog="Copilot",
        description="Copilot is a tool for emulating a video game controller, allowing gameplay using inputs from either a physical controller or an AI agent.",
    )

    parser.add_argument(
        "-c",
        "--config",
        type=argparse.FileType("rb"),
        help="Controller configuration file. An example configuration file can be found in the main reposity of the project.",
        required=True,
    )

    args = parser.parse_args()
    config: dict[str, Any] = tomllib.load(args.config)

    return Config.from_dict(config)
