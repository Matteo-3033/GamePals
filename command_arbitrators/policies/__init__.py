from enum import Enum

from ...utils import get_all_concrete_subclasses
from .input_entry import InputEntry, PolicyRole
from .policy import Policy
from .policy_binary_and import PolicyBinaryAND
from .policy_binary_democracy import PolicyBinaryDemocracy
from .policy_binary_or import PolicyBinaryOR
from .policy_binary_supv_by_pilot import PolicyBinarySupervisionByPilot
from .policy_continuous_or import PolicyContinuousOR
from .policy_continuous_slope import PolicyContinuousSlope
from .policy_continuous_sum import PolicyContinuousSum
from .policy_exclusivity import PolicyExclusivity
from .policy_manager import PolicyManager

policies = get_all_concrete_subclasses(Policy)
PolicyName = Enum("PolicyName", {policy.get_name(): policy for policy in policies})

__all__ = [
    "Policy",
    "PolicyManager",
    "InputEntry",
    "PolicyRole",
    "PolicyName",
]
