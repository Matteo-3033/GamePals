from abc import ABC, abstractmethod

from .input_entry import InputEntry


class Policy(ABC):
    """Policy is the abstract superclass for all policies, binary or continuous."""

    def __init__(self):
        pass

    @staticmethod
    def get_max_actors() -> int:
        """Returns the maximum number of actors allowed in the policy."""
        return 256

    @staticmethod
    @abstractmethod
    def merge_input_entries(entries: list[InputEntry]) -> float:
        pass


class BinaryPolicy(Policy, ABC):
    """BinaryPolicy is the abstract superclass for all binary policies."""

    pass


class ContinuousPolicy(Policy, ABC):
    """ContinuousPolicy is the abstract superclass for all continuous policies."""

    pass
