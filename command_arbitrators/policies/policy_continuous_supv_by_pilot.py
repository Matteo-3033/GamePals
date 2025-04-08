import logging
import math

from .input_entry import InputEntry
from .policy import BinaryPolicy

logger = logging.getLogger(__name__)


class PolicyContinuousSupervisionByPilot(BinaryPolicy):
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
        return "POLICY_CONT_SUPV_BY_PILOT"

    @staticmethod
    def merge_input_entries(entries: list[InputEntry]) -> float:
        from .. import PolicyRole
        from .policy_continuous_sum import PolicyContinuousSum

        for entry in entries:

            if entry.actor_role == PolicyRole.PILOT and not math.isclose(
                entry.input_details.val, 0.0, abs_tol=1e-3
            ):
                return entry.input_details.val

        return PolicyContinuousSum.merge_input_entries(entries)
