import logging
import time
from dataclasses import dataclass

from copilot.sources import VirtualControllerProvider
from copilot.sources.controller import ControllerInput, InputType

from .abstract_conversion_delegate import ActionConversionDelegate
from .action_input import ActionInput
from .game_action import GameAction

logger = logging.getLogger(__name__)


@dataclass
class RegisteredInputDetails:
    val: float
    timestamp: float
    sent: bool


class DefaultActionToInputDelegate(ActionConversionDelegate):
    """
    Default conversion delegate that just maps any action (only one) to the first input listed in the game
    configuration file.
    """

    def __init__(self, action: GameAction) -> None:
        super().__init__([action])

        inputs = self.config_handler.action_to_game_input(action)
        if inputs:
            self.latest_inputs: dict[InputType, RegisteredInputDetails] = {
                input_type: RegisteredInputDetails(0.0, 0.0, True)
                for input_type in inputs
            }
        else:
            logger.warning(
                f"{action} action: No input found for action {action}. It will be ignored."
            )

        self.ready_inputs: list[ControllerInput] = list()

    def register_input(self, user_idx: int, c_input: ControllerInput) -> None:
        """Registers that an input has occurred"""
        self.ready_inputs.append(c_input)
        self.latest_inputs[c_input.type] = RegisteredInputDetails(
            val=c_input.val, timestamp=time.time(), sent=False
        )

    def get_ready_actions(self, user_idx: int) -> list[ActionInput]:
        """Returns the ready-to-be-converted Actions"""
        ready_actions: list[ActionInput] = list()
        non_ready_inputs: list[ControllerInput] = list()
        added_actions: set[GameAction] = set()

        for c_input in self.ready_inputs:
            action = self.config_handler.user_input_to_action(user_idx, c_input.type)

            if action and action not in added_actions:
                ready_actions.append(ActionInput(action=action, val=c_input.val))
                added_actions.add(action)
            else:
                non_ready_inputs.append(c_input)

        self.ready_inputs = non_ready_inputs
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
