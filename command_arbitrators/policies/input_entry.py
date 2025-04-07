from dataclasses import dataclass
from enum import StrEnum

from ...agents import ActorID
from ...sources.game.game_actions_map import ActionInputRecord


class PolicyRole(StrEnum):
    """
    Enumerator for the Policy Roles. An Actor can register for an input specifying its Role.
    The Role is supposed to be used to allow for more complex Policies to be produced.
    """

    PILOT = "Pilot"
    COPILOT = "Copilot"


@dataclass
class InputEntry:
    """
    InputEntry contains all the information needed from an Actor to perform a merge.

    In particular, a Merging Method should be created based on a PolicyType and a list of InputEntry.
    """

    actor_id: ActorID
    actor_role: PolicyRole
    input_details: ActionInputRecord  # Contains Value, Confidence Level and a Timestamp of last acquisition
