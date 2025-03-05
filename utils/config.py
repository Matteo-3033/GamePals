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
