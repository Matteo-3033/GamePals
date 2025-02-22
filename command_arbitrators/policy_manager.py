from dataclasses import dataclass
from enum import Enum

from agents.actor import Actor, ActorID
from input_sources import InputType


class PolicyType(Enum):
    POLICY_AND = 0
    POLICY_OR = 1
    POLICY_PILOT_SUPERVISION = 2
    POLICY_MUTUAL_SUPERVISION = 3


class PolicyRole(Enum):
    PILOT = 0
    COPILOT = 1


@dataclass
class PolicyMapEntry:
    policy_type: PolicyType
    actors: dict[ActorID, PolicyRole]


class PolicyManager:
    """
    PolicyManager manages the Arbitration Policies for a Command Arbitrator.

    A Policy is defined for every Input Type.
    """

    def __init__(self) -> None:
        self.policies_map: dict[InputType, PolicyMapEntry] = {}

        self.policies_map = {
            input_type: PolicyMapEntry(PolicyType.POLICY_AND, {})
            for input_type in InputType
        }

    def register_actor(self, actor: Actor, role: PolicyRole) -> None:
        inputs = actor.get_controlled_inputs()
        for input_type in inputs:
            if len(self.policies_map[input_type].actors) == 0:
                self.policies_map[input_type].actors[actor.get_id()] = role
            else:
                raise ValueError("Only one Actor per Input Type is allowed")

    def get_policy(self, input_type: InputType) -> PolicyMapEntry:
        return self.policies_map[input_type]