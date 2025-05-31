import logging

from ...sources import VirtualControllerProvider
from ...sources.controller import ControllerInput, InputType
from .action_input import ActionInput
from .default_action_to_input_delegate import DefaultActionToInputDelegate
from .game_action import GameAction

logger = logging.getLogger(__name__)


class ActionToBinaryInputsDelegate(DefaultActionToInputDelegate):
    """
    A conversion delegate for actions that range from -1 to 1 and are controlled using two binary inputs.
    For example, a car’s throttle (where -1 represents deceleration and +1 represents acceleration) might be controlled using the left and right triggers: the first will be converted to -1 throttle, while the second to +1 throttle

    This delegate expects the action to have exactly two inputs defined in both the game configuration file and the assistance file (for each user controlling the action).
    The first input is considered the negative input, and the second one is considered the positive input.
    """

    def __init__(self, user_idx: int, action: GameAction) -> None:
        super().__init__(user_idx, [action])

        humans_count = self.config_handler.get_humans_count()
        self._is_using_stick: dict[int, bool] = dict()
        for user_idx in range(humans_count):
            inputs = self.config_handler.action_to_user_input(user_idx, action)

            self._is_using_stick[user_idx] = (
                inputs is not None and inputs[0] in VirtualControllerProvider.STICKS
            )

            # TODO: verify that inputs are a good combinations (eg: two binary buttons or negative and positive side of the same stick axis)

    @property
    def action(self) -> GameAction:
        return self.get_actions()[0]

    def register_input(self, c_input: ControllerInput) -> None:
        """Registers that an input has occurred"""

        inputs = self.config_handler.action_to_user_input(self.user_idx, self.action)

        assert (
            inputs and len(inputs) == 2
        ), f"{self.action} action expects exactly two inputs."

        negative, positive = inputs

        if c_input.type not in inputs:
            return

        if c_input.type == negative and not self._is_using_stick[self.user_idx]:
            c_input.val = -c_input.val

        super().register_input(c_input)
        if c_input.val == 0:  # Release
            # If the non-release input is still pressed from earlier, send it again (or it wouldn't happen)
            if c_input.type == negative and self.latest_inputs[positive].val == 1:
                super().register_input(ControllerInput(type=positive, val=1.0))
            elif c_input.type == positive and self.latest_inputs[negative].val == -1:
                super().register_input(ControllerInput(type=negative, val=-1.0))


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
