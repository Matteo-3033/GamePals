import logging

from copilot.sources.controller import ControllerInput, InputType

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
        super().__init__(action)

    def convert_to_inputs(self, action_input: ActionInput) -> list[ControllerInput]:
        """Converts the Action Input to a Controller Input"""

        inputs = self.config_handler.action_to_game_input(self.get_action())

        assert (
            inputs and len(inputs) == 2
        ), f"{self.get_action()} action expects exactly two inputs."

        negative, positive = inputs

        if action_input.val >= 0:
            return [
                ControllerInput(InputType(positive), action_input.val),
                ControllerInput(InputType(negative), 0),
            ]

        return [
            ControllerInput(InputType(negative), -action_input.val),
            ControllerInput(InputType(positive), 0),
        ]

    def convert_from_input(
        self, user_idx: int, c_input: ControllerInput
    ) -> list[ActionInput]:
        """Converts the Controller Input to an Action Input"""

        inputs = self.config_handler.action_to_user_input(user_idx, self.action)

        assert (
            inputs and len(inputs) == 2
        ), f"{self.get_action()} action expects exactly two inputs."

        negative, positive = inputs

        if c_input.type == negative:
            return [ActionInput(self.action, -c_input.val)]

        if c_input.type == positive:
            return [ActionInput(self.action, c_input.val)]

        return list()
