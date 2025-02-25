from dataclasses import dataclass
from enum import Enum, StrEnum

from agents.actor import Actor, ActorID
from sources import InputType


class PolicyType(StrEnum):
    """ The Enum Superclass of any Policy Type """
    # Leave Empty. See https://docs.python.org/3/howto/enum.html#restricted-enum-subclassing
    pass


class BinaryPolicyType(PolicyType):
    """ Enumerator for the Binary Policy Types """
    POLICY_EXCLUSIVITY = "POLICY_BIN_EXCLUSIVITY"  # Only one Actor allowed for that Command
    POLICY_AND = "POLICY_BIN_AND"
    POLICY_OR = "POLICY_BIN_OR"
    POLICY_PILOT_SUPERVISION = "POLICY_BIN_PILOT_SUPERVISION"
    POLICY_MUTUAL_SUPERVISION = "POLICY_BIN_MUTUAL_SUPERVISION"


class ContinuousPolicyType(PolicyType):
    """ Enumerator for the Continuous Policy Types """
    POLICY_EXCLUSIVITY = "POLICY_CONT_EXCLUSIVITY"  # Only one Actor allowed for that Command
    POLICY_OR = "POLICY_CONT_OR" # In the Continuous context, "OR" indicates that any Command is forwarded
    POLICY_PRODUCT = "POLICY_CONT_PRODUCT"  # Policy confidence * assistance


class PolicyRole(Enum):
    """
    Enumerator for the Policy Roles. An Actor can register for an input specifying its Role.
    The Role is supposed to be used to allow for more complex Policies to be produced.
    """
    PILOT = 0
    COPILOT = 1


@dataclass
class PolicyMapEntry:
    """ An Entry in the Policies Map for a given Input Type. It contains the PolicyType and the involved Actors. """
    policy_type: PolicyType
    actors: dict[ActorID, PolicyRole]


class PolicyManager:
    """
    PolicyManager manages the Arbitration Policies for a Command Arbitrator.

    A Policy is defined for every Input Type.
    """

    def __init__(self, policies_types: dict[InputType, PolicyType]) -> None:
        self.policies_map: dict[InputType, PolicyMapEntry] = {}

        for input_type in InputType:
            if input_type not in policies_types:
                raise ValueError(f"Policy type is incomplete: it does not include {input_type}")

            specified_policy = policies_types[input_type]
            self.policies_map[input_type] = PolicyMapEntry(specified_policy, {})

    def register_actor(self, actor: Actor, role: PolicyRole) -> None:
        """
        Registers the given Actor with the specified Role, for the Input Types specified by the
        get_controlled_inputs method of the Actor.

        TODO: future improvements could allow for specification of a certain PolicyRole for every InputType
        """
        inputs = actor.get_controlled_inputs()
        for input_type in inputs:
            policy_entry = self.policies_map[input_type]

            if policy_entry.policy_type == BinaryPolicyType.POLICY_EXCLUSIVITY or \
                    policy_entry.policy_type == ContinuousPolicyType.POLICY_EXCLUSIVITY:
                # Check if no other Actor has registered for this input (for Exclusivity Policies)

                if len(policy_entry.actors) == 0:
                    self.policies_map[input_type].actors[actor.get_id()] = role
                else:
                    raise ValueError("Only one Actor per Input Type is allowed")

            else:
                # Any other Policy doesn't need any check
                self.policies_map[input_type].actors[actor.get_id()] = role

    def get_policy(self, input_type: InputType) -> PolicyMapEntry:
        return self.policies_map[input_type]
