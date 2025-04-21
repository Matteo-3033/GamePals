import logging
import time

from ...sources import VirtualControllerProvider
from ...sources.controller import ControllerInput, InputType

from .abstract_conversion_delegate import ActionConversionDelegate
from .action_input import ActionInput
from .default_action_to_input_delegate import RegisteredInputDetails
from .game_action import GameAction

logger = logging.getLogger(__name__)


class DoubleFunctionDelegate(ActionConversionDelegate):
    """
    DoubleFunctionDelegate is a Conversion Delegates that handles multiple actions on the same button
    with the following logic:
    * A quick press and release executes the toggle action
    * A press with a release after some time executes the hold action
    """

    HOLD_THRESHOLD = 0.2  # seconds

    def __init__(self, toggle_action: GameAction, hold_action: GameAction) -> None:
        super().__init__([toggle_action, hold_action])

        self.toggle_action = toggle_action
        self.hold_action = hold_action
        toggle_inputs = self.config_handler.action_to_game_input(toggle_action)
        hold_inputs = self.config_handler.action_to_game_input(hold_action)

        assert (
            toggle_inputs is not None
            and toggle_inputs == hold_inputs
            and len(toggle_inputs) == 1
        ), "Both toggle_action and hold_action should be mapped to the same, single input"

        self.input = toggle_inputs[0]
        self.latest_non_zero_input : tuple[float, float] = (0.0, 0.0)

    def register_input(self, user_idx: int, c_input: ControllerInput) -> None:
        """Registers that an input has occurred"""
        latest_input = self.latest_inputs[c_input.type]

        self.latest_inputs[c_input.type] = RegisteredInputDetails(
            val=c_input.val, timestamp=time.time(), sent=False
        )

        # When the zero input is sent, queue both the non-zero and zero input
        if c_input.val == 0.0 and latest_input.val != 0.0:
            self.ready_inputs.append(ControllerInput(c_input.type, latest_input.val))
            self.ready_inputs.append(c_input)

    def get_ready_actions(self, user_idx: int) -> list[ActionInput]:
        """Returns the ready-to-be-converted Actions"""
        ready_actions: list[ActionInput] = list()
        non_ready_inputs: list[ControllerInput] = list()
        added_actions: set[GameAction] = set()

        current_time = time.time()
        latest_input = self.latest_inputs[self.input]

        action = self.toggle_action

        # If the input is pressed for a certain amount of time without release, it's a HOLD
        if (
            latest_input.val != 0.0
            and current_time - latest_input.timestamp > self.HOLD_THRESHOLD
        ):
            return [ActionInput(action=self.hold_action, val=latest_input.val)]

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
