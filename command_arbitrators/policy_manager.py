from dataclasses import dataclass
from enum import Enum, StrEnum

from agents.actor import Actor, ActorID
from input_sources import InputType


class PolicyType(StrEnum):
    # Leave Empty. See https://docs.python.org/3/howto/enum.html#restricted-enum-subclassing
    pass

class BinaryPolicyType(PolicyType):
    POLICY_EXCLUSIVITY = "POLICY_BIN_EXCLUSIVITY"  # Only one Actor allowed for that Command
    POLICY_AND = "POLICY_BIN_AND"
    POLICY_OR = "POLICY_BIN_OR"
    POLICY_PILOT_SUPERVISION = "POLICY_BIN_PILOT_SUPERVISION"
    POLICY_MUTUAL_SUPERVISION = "POLICY_BIN_MUTUAL_SUPERVISION"


class ContinuousPolicyType(PolicyType):
    POLICY_EXCLUSIVITY = "POLICY_CONT_EXCLUSIVITY"  # Only one Actor allowed for that Command
    POLICY_PRODUCT = "POLICY_CONT_PRODUCT"  # Policy confidence * assistance


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

    def __init__(self, policies_types: dict[InputType, PolicyType]) -> None:
        self.policies_map: dict[InputType, PolicyMapEntry] = {}

        # Assert Policies Validity
        for input_type in InputType:

            if input_type not in policies_types:
                raise ValueError(f"Policy type is incomplete: it does not include {input_type}")
            specified_policy = policies_types[input_type]

            if input_type.is_binary() and specified_policy not in BinaryPolicyType:
                raise ValueError(f"Policy for the input {input_type} is invalid")
            elif input_type.is_continuous() and specified_policy not in ContinuousPolicyType:
                raise ValueError(f"Policy for the input {input_type} is invalid")

            self.policies_map[input_type] = PolicyMapEntry(specified_policy, {})



    def register_actor(self, actor: Actor, role: PolicyRole) -> None:
        inputs = actor.get_controlled_inputs()
        for input_type in inputs:
            policy_entry = self.policies_map[input_type]
            match policy_entry.policy_type:
                case BinaryPolicyType.POLICY_EXCLUSIVITY | ContinuousPolicyType.POLICY_EXCLUSIVITY:  # Check if no other Actor has registered for this input
                    if len(policy_entry.actors) == 0:
                        self.policies_map[input_type].actors[actor.get_id()] = role
                    else:
                        raise ValueError("Only one Actor per Input Type is allowed")
                case _:  # Any other Policy doesn't require any check
                    self.policies_map[input_type].actors[actor.get_id()] = role

    def get_policy(self, input_type: InputType) -> PolicyMapEntry:
        return self.policies_map[input_type]
