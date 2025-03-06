from enum import Enum
from typing import Type

from .input_entry import InputEntry, PolicyRole
from .policy import Policy
from .policy_binary_and import PolicyBinaryAND
from .policy_binary_or import PolicyBinaryOR
from .policy_continuous_or import PolicyContinuousOR
from .policy_continuous_sum import PolicyContinuousSum
from .policy_exclusivity import PolicyExclusivity
from .policy_manager import PolicyManager
from .policy_binary_democracy import PolicyBinaryDemocracy
from .policy_binary_supv_by_pilot import PolicyBinarySupervisionByPilot
from .policy_continuous_slope import PolicyContinuousSlope


def get_all_subclasses(cls: Type) -> set[Type[Policy]]:
    """ Returns a set of all the Policy class concrete implementations. """
    subclasses = set(cls.__subclasses__())  # Find direct subclasses
    all_subclasses = set(subclasses)

    for subclass in subclasses.copy(): # Find nested subclasses
        all_subclasses.update(get_all_subclasses(subclass))

    # Filter out abstract classes, checking the __abstractmethods__ attribute
    all_subclasses = {
        subclass
        for subclass in all_subclasses
        if not hasattr(subclass, "__abstractmethods__") # Doesn't have
        or not subclass.__abstractmethods__ # Has but it's empty
    }

    return all_subclasses


policies = get_all_subclasses(Policy)
PolicyName = Enum("PolicyName", {policy.get_name(): policy for policy in policies})

__all__ = [
    "Policy",
    "PolicyManager",
    "InputEntry",
    "PolicyRole",
    "PolicyName",
]
