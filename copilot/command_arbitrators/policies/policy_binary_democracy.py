import logging

from .input_entry import InputEntry
from .policy import BinaryPolicy

logger = logging.getLogger(__name__)


class PolicyBinaryDemocracy(BinaryPolicy):
    """
    PolicyBinarySupervisionByPilot is a Binary Policy that decides democratically the result of the merge.

    The democratic decision is based on the confidence level of the actors.

    Note that, for the purpose of making this policy work for Triggers, it is considered a "value 1" anything != 0
    """

    def __init__(self):
        super().__init__()

    @classmethod
    def get_name(cls) -> str:
        "Returns the name this class should be referred to in the configuration file."
        return "POLICY_BIN_DEMOCRACY"

    @staticmethod
    def merge_input_entries(entries: list[InputEntry]) -> float:
        one_voters: list[InputEntry] = [
            entry
            for entry in entries
            if entry.input_details.val != 0
        ]
        if len(one_voters) == 0: return 0

        zero_voters: list[InputEntry] = [
            entry
            for entry in entries
            if entry.input_details.val == 0
        ]
        if len(zero_voters) == 0: return 1

        one_score = sum(entry.input_details.confidence for entry in one_voters) / len(one_voters)
        zero_score = sum(entry.input_details.confidence for entry in zero_voters) / len(zero_voters)

        #logger.info("Scores are %.2f vs %.2f", one_score, zero_score)

        if zero_score > one_score:
            return 0
        else:
            return 1
