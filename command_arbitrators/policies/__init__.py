from enum import Enum
from typing import Type

from ...sources.controller import InputType
from .input_entry import InputEntry, PolicyRole
from .policy import Policy
from .policy_binary_and import PolicyBinaryAND
from .policy_binary_or import PolicyBinaryOR
from .policy_continuous_or import PolicyContinuousOR
from .policy_continuous_sum import PolicyContinuousSum
from .policy_exclusivity import PolicyExclusivity
from .policy_manager import PolicyManager


def get_all_subclasses(cls: Type) -> set[Type]:
    subclasses = set(cls.__subclasses__())  # Trova le sottoclassi dirette
    all_subclasses = set(subclasses)  # Copia iniziale delle sottoclassi dirette

    for subclass in subclasses.copy():
        # Ricorsione per sottoclassi indirette
        all_subclasses.update(get_all_subclasses(subclass))

    # Rimuovi le classi astratte, controllando se hanno il set __abstractmethods__ (e se non è vuoto)
    all_subclasses = {
        subclass
        for subclass in all_subclasses
        if not hasattr(subclass, "__abstractmethods__")
        or not subclass.__abstractmethods__
    }

    return all_subclasses


policies = get_all_subclasses(Policy)
PolicyName = Enum("PolicyName", {policy.get_name(): policy for policy in policies})

__all__ = [
    "Policy",
    "PolicyBinaryAND",
    "PolicyBinaryOR",
    "PolicyContinuousOR",
    "PolicyExclusivity",
    "PolicyContinuousSum",
    "PolicyManager",
    "InputEntry",
    "PolicyRole",
    "PolicyName",
]
