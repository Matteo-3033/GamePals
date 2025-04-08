import math

from .input_entry import InputEntry
from .policy import ContinuousPolicy


class PolicyContinuousSum(ContinuousPolicy):
    """
    PolicyContinuousSum is a Continuous Policy that returns the sum of the inputs of the given entries.

    Thus, if two inputs are opposite (e.g. -1 and 1), the result will be 0.
    """

    def __init__(self):
        super().__init__()

    @classmethod
    def get_name(cls) -> str:
        "Returns the name this class should be referred to in the configuration file."
        return "POLICY_CONT_SUM"

    @staticmethod
    def merge_input_entries(entries: list[InputEntry]) -> float:
        values_sum = 0.0
        weights_sum = 0.0

        for entry in entries:
            value = entry.input_details.val
            weight = entry.input_details.confidence

            if not math.isclose(value, 0.0, abs_tol=1e-3):
                values_sum += value * weight
                weights_sum += weight

        return (weights_sum > 0 and values_sum / weights_sum) or 0.0
