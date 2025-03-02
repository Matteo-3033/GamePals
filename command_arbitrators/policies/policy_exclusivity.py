from typing import override

from .input_entry import InputEntry
from .policy import Policy


class PolicyExclusivity(Policy):
    """
    PolicyExclusivity allows only one actor for a certain Input Type.
    It's valid both as Binary and Continuous Policy.

    Thus, the resulting value from the merge is the value given by that actor.
    """

    def __init__(self):
        super().__init__()

    @staticmethod
    @override
    def get_max_actors() -> int:
        """Returns the maximum number of actors allowed in the policy."""
        return 1

    @staticmethod
    def merge_input_entries(entries: list[InputEntry]) -> float:
        val = entries[0].input_details.val
        return val
