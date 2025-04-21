import logging
import time

from . import DefaultActionToInputDelegate
from ...sources.controller import ControllerInput

from .action_input import ActionInput
from .game_action import GameAction

logger = logging.getLogger(__name__)


class DoubleFunctionDelegate(DefaultActionToInputDelegate):
    """
    DoubleFunctionDelegate is a Conversion Delegates that handles multiple actions on the same button
    with the following logic:
    * A quick press and release executes the toggle action
    * A press with a release after some time executes the hold action

    It receives a toggle_action and hold_action. These should be mapped to the same input in the assistance.toml
    but should have separate inputs in the game.toml
    """

    HOLD_THRESHOLD = 0.2  # seconds

    def __init__(self, toggle_action: GameAction, hold_action: GameAction) -> None:
        super().__init__([toggle_action, hold_action])

        self.toggle_action = toggle_action
        self.hold_action = hold_action

        inputs = self.latest_inputs.keys()

        assert (
            len(inputs) == 1
        ), "Both toggle_action and hold_action should be mapped to the same, single input"

        self.input = list(inputs)[0]
        self._holding : bool = False

    def register_input(self, user_idx: int, c_input: ControllerInput) -> None:
        """Registers that an input has occurred"""
        latest_input = self.latest_inputs[c_input.type]

        # When the zero input is sent, queue both the non-zero and zero input for TOGGLE
        if c_input.val == 0.0 and latest_input.val != 0.0:
            action = self.hold_action if self._holding else self.toggle_action
            self.ready_actions_queue.append(
                ActionInput(action=action, val=latest_input.val)
            )
            self.ready_actions_queue.append(
                ActionInput(action=action, val=0.0)
            )
            self._holding = False

    def get_ready_actions(self, user_idx: int) -> list[ActionInput]:
        """Returns the ready-to-be-converted Actions"""
        current_time = time.time()
        latest_input = self.latest_inputs[self.input]

        # If the input is pressed for a certain amount of time without release, it's a HOLD
        if (
            latest_input.val != 0.0
            and current_time - latest_input.timestamp > self.HOLD_THRESHOLD
        ):
            self._holding = True
            return [ActionInput(action=self.hold_action, val=latest_input.val)]

        return super().get_ready_actions(user_idx)

