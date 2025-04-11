import logging

from .input_entry import InputEntry
from .policy import BinaryPolicy
from .policy_binary_democracy import PolicyBinaryDemocracy
from .policy_role import PolicyRole

logger = logging.getLogger(__name__)


class PolicyBinarySupervisionByPilot(BinaryPolicy):
    """
    PolicyBinarySupervisionByPilot is a Binary Policy that:
     * if a Pilot suggests value 1, produces 1
     * otherwise, it decides democratically the result of the merge (equivalent to PolicyBinaryDemocracy.

    The democratic decision is based on the confidence level of the actors.

    Note that, for the purpose of making this policy work for Triggers, it is considered a "value 1" anything != 0
    """

    def __init__(self):
        super().__init__()

    @classmethod
    def get_name(cls) -> str:
        "Returns the name this class should be referred to in the configuration file."
        return "POLICY_BIN_SUPV_BY_PILOT"

    @staticmethod
    def merge_input_entries(entries: list[InputEntry]) -> float:
        if next((
                entry
                for entry in entries
                if entry.actor_role == PolicyRole.PILOT
                   and entry.input_details.val != 0
        ), None) is not None:
            return 1

        return PolicyBinaryDemocracy.merge_input_entries(entries)
