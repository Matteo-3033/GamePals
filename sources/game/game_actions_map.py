import time
from dataclasses import dataclass

from ...agents import ActionInput, ActionInputWithConfidence
from . import GameAction


@dataclass
class ActionInputRecord:
    """ActionInputRecord stores the value of an input action, the associated confidence level and the timestamp of acquisition"""

    val: float
    confidence: float
    timestamp: float


class GameActionsMap:
    """
    GameActionsMap is a class that stores for each Game Action a corresponding ActionInputRecord
    """

    def __init__(self):
        self.actions_map: dict[GameAction, ActionInputRecord] = {}

    def set(
        self,
        action: ActionInputWithConfidence,
        timestamp: float | None = None,
    ) -> None:
        """
        Updates the entry of the value for an input_type.

        If timestamp is not specified, it uses current time.
        """
        if timestamp is None:
            timestamp = time.time()

        self.actions_map[action.action] = ActionInputRecord(
            val=action.val, confidence=action.confidence, timestamp=timestamp
        )

    def get(self, action: GameAction) -> tuple[ActionInput, ActionInputRecord]:
        """Returns the ControllerInput and the ActionInputRecord associated with the input."""
        record = self.actions_map.get(action)

        if record is None:
            self.set(ActionInputWithConfidence(action, val=0, confidence=0))
            record = self.actions_map[action]

        return ActionInput(action=action, val=record.val), record
