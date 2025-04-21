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
    value: float
    timestamp: float
    sent: bool


class DefaultActionToInputDelegate(ActionConversionDelegate):
    """
    Default conversion delegate that just maps any action (only one) to the first input listed in the game
    configuration file.
    """

    HOLD_THRESHOLD = 0  # seconds

    def __init__(self, action: GameAction) -> None:
        super().__init__([action])

        inputs = self.config_handler.action_to_game_input(action)
        if not inputs:
            logger.warning(
                f"{action} action: No input found for action {action}. It will be ignored."
            )
        else:
            self.latest_inputs: dict[InputType, RegisteredInputDetails] = {
                input_type: RegisteredInputDetails(0.0, 0.0, True)
                for input_type in inputs
            }

        self.ready_inputs: list[tuple[InputType, float]] = list()
        self.send_zero: bool = False

    def register_input(self, user_idx: int, c_input: ControllerInput) -> None:
        """Registers that an input has occurred"""
        latest_input_for_type = self.latest_inputs[c_input.type]

        # If it receives a zero input (release), it should send the previous non-zero input (press)
        # If the input comes from an axis, it should always be sent
        if (
            c_input.val == 0.0
            and latest_input_for_type.value != 0.0
            or c_input.type in VirtualControllerProvider.AXIS_INPUTS
        ):
            self.ready_inputs.append((c_input.type, latest_input_for_type.value))

        self.latest_inputs[c_input.type] = RegisteredInputDetails(
            value=c_input.val, timestamp=time.time(), sent=False
        )

    def get_ready_actions(self, user_idx: int) -> list[ActionInput]:
        """Returns the ready-to-be-converted Actions"""
        ready_actions: list[ActionInput] = list()
        current_time = time.time()

        # Also send all inputs after a THRESHOLD amount of time
        for input_type, details in self.latest_inputs.items():
            if (
                not details.sent
                and current_time - details.timestamp > self.HOLD_THRESHOLD
            ):
                self.ready_inputs.append((input_type, details.value))
                details.sent = True

        for input_type, value in self.ready_inputs:
            action = self.config_handler.user_input_to_action(user_idx, input_type)
            if action:
                ready_actions.append(ActionInput(action=action, val=value))

        self.ready_inputs = list()
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
