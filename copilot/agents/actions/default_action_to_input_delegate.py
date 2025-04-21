import logging
import time

from copilot.sources import VirtualControllerProvider
from copilot.sources.controller import ControllerInput, InputType

from .abstract_conversion_delegate import ActionConversionDelegate
from .action_input import ActionInput
from .game_action import GameAction

logger = logging.getLogger(__name__)


class DefaultActionToInputDelegate(ActionConversionDelegate):
    """
    Default conversion delegate that just maps any action (only one) to the first input listed in the game
    configuration file.
    """

    def __init__(self, action: GameAction) -> None:
        super().__init__([action])

        inputs = self.config_handler.action_to_game_input(action)
        if not inputs:
            logger.warning(
                f"{action} action: No input found for action {action}. It will be ignored."
            )
        else:
            self.latest_inputs: dict[InputType, tuple[float, float]] = {
                input_type: (0.0, 0.0) # Tuple is (value, timestamp)
                for input_type in inputs
            }
            self.ready_inputs: list[tuple[InputType, float]] = list()

    def register_input(self, user_idx: int, c_input: ControllerInput) -> None:
        """Registers that an input has occurred"""
        latest_input_for_type = self.latest_inputs[c_input.type]

        # If it receives a zero input (release), it should send the previous non-zero input (press)
        if c_input.val == 0.0 and latest_input_for_type[0] != 0.0:
            self.ready_inputs.append((c_input.type, latest_input_for_type[0]))

        self.latest_inputs[c_input.type] = (c_input.val, time.time())

    def get_ready_actions(self, user_idx : int) -> list[ActionInput]:
        """Returns the ready-to-be-converted Actions"""
        ready_actions : list[ActionInput] = list()
        for (input_type, value) in self.ready_inputs:
            action = self.config_handler.user_input_to_action(user_idx, input_type)
            if action:
                ready_actions.append(ActionInput(action=action, val=value))

        return ready_actions

    def convert_to_inputs(self, action_input: ActionInput) -> list[ControllerInput]:
        """Converts the Action Input to a Controller Input"""

        inputs = self.config_handler.action_to_game_input(self.get_actions()[0])
        if not inputs:
            return list()

        if (
                len(inputs) > 1
                and inputs[0] in VirtualControllerProvider.STICKS
                and inputs[1] in VirtualControllerProvider.STICKS
        ):  # It's a stick, with split axis. Pick according to value
            idx = 0 if action_input.val >= 0 else 1
        else:
            idx = 0  # Pick the first mapped input if it's not a stick

        return [ControllerInput(type=inputs[idx], val=action_input.val)]

    # def convert_from_input(
    #         self, user_idx: int, c_input: ControllerInput
    # ) -> list[ActionInput]:
    #     """Converts the Controller Input to an Action Input"""
    #
    #     action = self.config_handler.user_input_to_action(user_idx, c_input.type)
    #
    #     if action is None:
    #         return list()
    #
    #     return [ActionInput(action=action, val=c_input.val)]
