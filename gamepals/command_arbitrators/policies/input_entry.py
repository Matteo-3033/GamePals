from dataclasses import dataclass

from gamepals.agents import ActorID
from .policy_role import PolicyRole


@dataclass
class ActionInputRecord:
    """ActionInputRecord stores the value of an input action, the associated confidence level and the timestamp of acquisition"""

    val: float
    confidence: float
    timestamp: float


@dataclass
class InputEntry:
    """
    InputEntry contains all the information needed from an Actor to perform a merge.

    In particular, a Merging Method should be created based on a PolicyType and a list of InputEntry.
    """

    actor_id: ActorID
    actor_role: PolicyRole
    input_details: ActionInputRecord  # Contains Value, Confidence Level and a Timestamp of last acquisition
