import logging

from ...sources.controller import ControllerInput, InputType
from .default_action_to_input_delegate import DefaultActionToInputDelegate

from .action_input import ActionInput
from .game_action import GameAction

logger = logging.getLogger(__name__)


class ActionToBinaryInputsDelegate(DefaultActionToInputDelegate):
    """
    A conversion delegate for actions that range from -1 to 1 and are controlled using two binary inputs.
    For example, a car’s throttle (where -1 represents deceleration and +1 represents acceleration) might be controlled using the left and right triggers: the first will be converted to -1 throttle, while the second to +1 throttle

    This delegate expects the action to have exactly two inputs defined in both the game configuration file and the assistance file (for each user controlling the action).
    The first input is considered the negative input, and the second one is considered the positive input.
    """

    def __init__(self, action: GameAction) -> None:
        super().__init__([action])

    def register_input(self, user_idx: int, c_input: ControllerInput) -> None:
        """Registers that an input has occurred"""

        action = self.get_actions()[0]
        inputs = self.config_handler.action_to_user_input(user_idx, action)

        assert (
            inputs and len(inputs) == 2
        ), f"{action} action expects exactly two inputs."

        negative, positive = inputs

        if c_input.type == negative:
            c_input.val = -c_input.val

        if c_input.type in inputs:
            super().register_input(user_idx, c_input)

    def convert_to_inputs(self, action_input: ActionInput) -> list[ControllerInput]:
        """Converts the Action Input to a Controller Input"""

        action = self.get_actions()[0]
        inputs = self.config_handler.action_to_game_input(action)

        assert (
            inputs and len(inputs) == 2
        ), f"{action} action expects exactly two inputs."

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
