from dataclasses import dataclass
from enum import Enum
from unittest import case

from agents.actor import Actor, ActorID
from input_sources import InputType


class PolicyType(Enum):
    POLICY_EXCLUSIVITY = 0  # Only one Actor allowed for that Command
    POLICY_AND = 1
    POLICY_OR = 2
    POLICY_PILOT_SUPERVISION = 3
    POLICY_MUTUAL_SUPERVISION = 4


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

        # Currently the only policy is POLICY_EXCLUSIVITY.
        # TODO: read requested policy from a file/data structure
        self.policies_map = {
            input_type: PolicyMapEntry(PolicyType.POLICY_EXCLUSIVITY, {})
            for input_type in InputType
        }

    def register_actor(self, actor: Actor, role: PolicyRole) -> None:
        inputs = actor.get_controlled_inputs()
        for input_type in inputs:
            policy_entry = self.policies_map[input_type]
            match policy_entry.policy_type:
                case PolicyType.POLICY_EXCLUSIVITY:  # Check if no other Actor has registered for this input
                    if len(policy_entry.actors) == 0:
                        self.policies_map[input_type].actors[actor.get_id()] = role
                    else:
                        raise ValueError("Only one Actor per Input Type is allowed")
                case _:  # Any other Policy doesn't require any check
                    self.policies_map[input_type].actors[actor.get_id()] = role

    def get_policy(self, input_type: InputType) -> PolicyMapEntry:
        return self.policies_map[input_type]
