import logging

from ...sources import VirtualControllerProvider
from ...sources.controller import ControllerInput, InputType
from .default_action_to_input_delegate import DefaultActionToInputDelegate

from .action_input import ActionInput
from .game_action import GameAction

logger = logging.getLogger(__name__)


class ActionToAxisDelegate(DefaultActionToInputDelegate):
    """
    A conversion delegate for actions that range from -1 to 1 and are controlled using a stick axis.
    For example, a car’s steering (where -1 represents a left turn and +1 a right turn) might be controlled using the X axis of a stick: tilting the stick to the left (negative axis) will be converted to -1, while tilting it to the right (positive axis) will be converted to +1.

    This delegate expects the action to have exactly two inputs defined in both the game configuration file and the assistance file (for each user controlling the action).
    The first input is considered the negative input, and the second one is considered the positive input.
    The game configuration should map the action to the negative and positive axes of the stick accordingly.
    """

    def __init__(self, action: GameAction) -> None:
        super().__init__(action)

        humans_count = self.config_handler.get_humans_count()
        self._is_using_stick: dict[int, bool] = dict()
        for user_idx in range(humans_count):
            inputs = self.config_handler.action_to_user_input(user_idx, action)

            self._is_using_stick[user_idx] = (
                inputs is not None and inputs[0] in VirtualControllerProvider.STICKS
            )

            # TODO: verify that inputs are a good combinations (eg: two binary buttons or negative and positive side of the same stick axis)

    def register_input(self, user_idx: int, c_input: ControllerInput) -> None:
        """Registers that an input has occurred"""

        action = self.get_actions()[0]
        inputs = self.config_handler.action_to_user_input(user_idx, action)

        assert (
            inputs and len(inputs) == 2
        ), f"{action} action expects exactly two inputs."

        negative, positive = inputs

        if c_input.type == negative and not self._is_using_stick[user_idx]:
            c_input.val = -c_input.val

        if c_input.type in inputs or self._is_using_stick[user_idx]:
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
            return [ControllerInput(InputType(positive), action_input.val)]

        return [ControllerInput(InputType(negative), action_input.val)]
