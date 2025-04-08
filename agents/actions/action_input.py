from dataclasses import dataclass

from .game_action import GameAction


@dataclass
class ActionInput:
    """ActionInput is an input yet to be bound to a specific InputType."""

    action: GameAction
    val: float


@dataclass
class ActionInputWithConfidence(ActionInput):
    """ActionInputWithConfidence extends the ActionInput with the related confidence"""

    confidence: float
