import logging

from ...sources.controller import ControllerInput
from .abstract_conversion_delegate import ActionConversionDelegate
from .action_input import ActionInput
from .game_action import GameAction

logger = logging.getLogger(__name__)


class BinaryConversionDelegate(ActionConversionDelegate):
    """
    Conversion delegate for actions that are controlled with two inputs.
    For example, the throttle of a car might by controlled by the left trigger (negative) and the right trigger (positive).

    It expects the action to have exactly two inputs defined in both the game file and the assistance file (for each user controlling the action).
    The first input is considered the negative input and the second one is considered the positive input.
    """

    def __init__(self, action: GameAction) -> None:
        super().__init__()

        self.action = action

    def get_action(self) -> GameAction:
        """Returns the Game Action this Delegate is responsible for"""
        return self.action

    def convert_to_input(self, action_input: ActionInput) -> ControllerInput | None:
        """Converts the Action Input to a Controller Input"""

        inputs = self.config_handler.action_to_game_input(self.get_action())

        assert (
            inputs and len(inputs) == 2
        ), f"{self.get_action()} action expects exactly two inputs."

        negative, positive = inputs

        if action_input.val >= 0:
            return ControllerInput(positive, action_input.val)

        return ControllerInput(negative, action_input.val)

    def convert_from_input(
        self, user_idx: int, c_input: ControllerInput
    ) -> ActionInput | None:
        """Converts the Controller Input to an Action Input"""

        inputs = self.config_handler.action_to_user_input(user_idx, self.action)

        assert (
            inputs and len(inputs) == 2
        ), f"{self.get_action()} action expects exactly two inputs."

        negative, positive = inputs

        if c_input.type == negative:
            return ActionInput(self.action, c_input.val)

        if c_input.type == positive:
            return ActionInput(self.action, -c_input.val)

        return None
