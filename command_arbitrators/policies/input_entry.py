from dataclasses import dataclass
from enum import Enum

from ...agents import ActorID
from ...sources.controller import ControllerInputRecord


class PolicyRole(Enum):
    """
    Enumerator for the Policy Roles. An Actor can register for an input specifying its Role.
    The Role is supposed to be used to allow for more complex Policies to be produced.
    """

    PILOT = 0
    COPILOT = 1


@dataclass
class InputEntry:
    """
    InputEntry contains all the information needed from an Actor to perform a merge.

    In particular, a Merging Method should be created based on a PolicyType and a list of InputEntry.
    """

    actor_id: ActorID
    actor_role: PolicyRole
    input_details: ControllerInputRecord  # Contains Value, Confidence Level and a Timestamp of last acquisition
