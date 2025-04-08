from enum import Enum

from ...utils.utils import get_all_concrete_subclasses
from .input_entry import InputEntry, PolicyRole
from .policy import Policy

policies = get_all_concrete_subclasses(Policy)
PolicyName = Enum("PolicyName", {policy.get_name(): policy for policy in policies})

__all__ = [
    "Policy",
    "PolicyManager",
    "InputEntry",
    "PolicyRole",
    "PolicyName",
]
