from .input_entry import InputEntry
from .policy import BinaryPolicy


class PolicyBinaryAND(BinaryPolicy):
    """
    PolicyBinAND is a Binary Policy that calculates the result of the merge using the AND operator.

    Thus, it returns 1 only if all the actors agree on the value 1.
    """

    def __init__(self):
        super().__init__()

    @classmethod
    def get_name(cls) -> str:
        "Returns the name this class should be referred to in the configuration file."
        return "POLICY_BIN_AND"

    @staticmethod
    def merge_input_entries(entries: list[InputEntry]) -> float:
        val = True
        for input_entry in entries:
            curr = input_entry.input_details.val != 0  # False if 0, True otherwise
            val = val & curr

        return 1 if val else 0
