from .input_entry import InputEntry
from .policy import ContinuousPolicy


class PolicyContinuousOR(ContinuousPolicy):
    """
    PolicyContinuousOR is a Continuous Policy that allows for all inputs to be executed (similarly to an OR logic).

    Thus, it returns the most recent input of the given entries.
    """

    def __init__(self):
        super().__init__()

    @classmethod
    def get_name(cls) -> str:
        "Returns the name this class should be referred to in the configuration file."
        return "POLICY_CONT_OR"

    @staticmethod
    def merge_input_entries(entries: list[InputEntry]) -> float:
        latest_entry = sorted(entries, key=lambda x: x.input_details.timestamp, reverse=True)[0]
        val = latest_entry.input_details.val
        return val