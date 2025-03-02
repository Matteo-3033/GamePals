from .input_entry import InputEntry
from .policy import BinaryPolicy


class PolicyBinaryOR(BinaryPolicy):
    """
    PolicyBinOR is a Binary Policy that calculates the result of the merge using the OR operator.

    Thus, it returns 0 only if all the actors agree on the value 0.
    """

    def __init__(self):
        super().__init__()

    @staticmethod
    def merge_input_entries(entries: list[InputEntry]) -> float:
        val = False
        for input_entry in entries:
            curr = input_entry.input_details.val != 0  # False if 0, True otherwise
            val = val | curr

        return 1 if val else 0