import logging

from copilot.sources import VirtualControllerProvider
from copilot.sources.controller import ControllerInput, InputType

from .abstract_conversion_delegate import ActionConversionDelegate
from .action_input import ActionInput
from .game_action import GameAction

logger = logging.getLogger(__name__)


class ActionToAxisDelegate(ActionConversionDelegate):
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
            inputs = self.config_handler.action_to_user_input(user_idx, self.action)

            self._is_using_stick[user_idx] = (
                inputs is not None and inputs[0] in VirtualControllerProvider.STICKS
            )

            # TODO: verify that inputs are a good combinations (eg: two binary buttons or negative and positive side of the same stick axis)

    def convert_to_inputs(self, action_input: ActionInput) -> list[ControllerInput]:
        """Converts the Action Input to a Controller Input"""

        inputs = self.config_handler.action_to_game_input(self.get_action())

        assert (
            inputs and len(inputs) == 2
        ), f"{self.get_action()} action expects exactly two inputs."

        negative, positive = inputs

        if action_input.val >= 0:
            return [ControllerInput(InputType(positive), action_input.val)]

        return [ControllerInput(InputType(negative), action_input.val)]

    def convert_from_input(
        self, user_idx: int, c_input: ControllerInput
    ) -> list[ActionInput]:
        """Converts the Controller Input to an Action Input"""

        inputs = self.config_handler.action_to_user_input(user_idx, self.action)

        assert (
            inputs and len(inputs) == 2
        ), f"{self.get_action()} action expects exactly two inputs."

        negative, positive = inputs

        if self._is_using_stick[user_idx]:
            return [ActionInput(self.action, c_input.val)]

        if c_input.type == negative:
            return [ActionInput(self.action, -c_input.val)]

        if c_input.type == positive:
            return [ActionInput(self.action, c_input.val)]

        return list()
