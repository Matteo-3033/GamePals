from dataclasses import dataclass
from enum import Enum

from agents.actor import Actor, ActorID
from sources.controller_inputs import InputType


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
    policy_type: type['Policy']
    actors: dict[ActorID, PolicyRole]


class PolicyManager:
    """
    PolicyManager manages the Arbitration Policies for a Command Arbitrator.

    A Policy is defined for every Input Type.
    """

    def __init__(self, policies_types: dict[InputType, type['Policy']]) -> None:
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
            actors_number = len(policy_entry.actors)

            if policy_entry.policy_type.get_max_actors() > actors_number:
                self.policies_map[input_type].actors[actor.get_id()] = role
            else:
                raise ValueError("Only one Actor per Input Type is allowed")

    def get_policy(self, input_type: InputType) -> PolicyMapEntry:
        return self.policies_map[input_type]
