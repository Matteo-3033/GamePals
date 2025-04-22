import logging
import time

from .default_action_to_input_delegate import (
    DefaultActionToInputDelegate,
    RegisteredInputDetails,
)
from ...sources.controller import ControllerInput

from .action_input import ActionInput
from .game_action import GameAction

logger = logging.getLogger(__name__)


class ThreeForTwoDelegate(DefaultActionToInputDelegate):
    """
    ThreeForTwoDelegate is a Conversion Delegates that allows to handle 3 actions with just 2 inputs,
    with the following logic:
    * To execute Action 1, press first input
    * To execute Action 2, press second input
    * To execute Action 3, press both inputs at the same time

    In the assistance config file, it expects the 3 actions to be controlled according to what stated above
    """

    HOLD_THRESHOLD = 0.2  # seconds

    def __init__(
        self,
        user_idx: int,
        action_1: GameAction,
        action_2: GameAction,
        action_3: GameAction,
        invert_action_1_val: bool,
    ) -> None:
        """Set invert_action_1_val to True if it's supposed to control the negative part of an axis"""
        super().__init__(user_idx, [action_1, action_2, action_3])

        inputs = self.latest_inputs.keys()

        assert (
            len(inputs) == 2
        ), "3x2 Delegate requires the 3 actions to be mapped on exactly 2 inputs"

        inputs_for_1 = self.config_handler.action_to_user_input(self.user_idx, action_1)
        inputs_for_2 = self.config_handler.action_to_user_input(self.user_idx, action_2)
        if not inputs_for_1 or not inputs_for_2:
            raise ValueError(
                f"Invalid input mapping for actions {action_1} and {action_2}"
            )

        self.action_1 = action_1
        self.action_2 = action_2
        self.action_3 = action_3
        self.input_1 = inputs_for_1[0]
        self.input_2 = inputs_for_2[0]

        self.current_action: GameAction | None = None
        self.invert_action_1_val = invert_action_1_val

    def register_input(self, c_input: ControllerInput) -> None:
        """Registers that an input has occurred"""
        input_idx = 1 if c_input.type == self.input_1 else 2
        latest_input = self.latest_inputs[c_input.type]
        other_latest_input = self.latest_inputs[
            self.input_2 if input_idx == 1 else self.input_1
        ]
        associated_action = self.action_1 if input_idx == 1 else self.action_2
        other_action = self.action_2 if input_idx == 1 else self.action_1

        if c_input.val == 0.0 and latest_input.val != 0.0:  # release
            if self.current_action == self.action_3:
                # Stop action_3
                self.ready_actions_queue.append(
                    ActionInput(action=self.action_3, val=0.0)
                )
                # Go back to executing the other action
                self.ready_actions_queue.append(
                    ActionInput(action=other_action, val=other_latest_input.val)
                )
                self.current_action = (
                    other_action if other_latest_input.val != 0.0 else None
                )
            else:
                self.ready_actions_queue.append(
                    ActionInput(action=associated_action, val=0.0)
                )
                self.current_action = None
        else:  # press
            if associated_action == self.action_1 and self.invert_action_1_val:
                c_input.val = - c_input.val
            action_input = ActionInput(action=associated_action, val=c_input.val)
            self.ready_actions_queue.append(action_input)

        self.latest_inputs[c_input.type] = RegisteredInputDetails(
            val=c_input.val, timestamp=time.time(), sent=False
        )

    def get_ready_actions(self) -> list[ActionInput]:
        """Returns the ready-to-be-converted Actions"""
        latest_input_1 = self.latest_inputs[self.input_1]
        latest_input_2 = self.latest_inputs[self.input_2]

        # If both inputs are pressed, execute action_3 with value 1.0
        if latest_input_1.val != 0.0 and latest_input_2.val != 0.0:
            self.current_action = self.action_3
            return [
                ActionInput(action=self.action_1, val=0.0),
                ActionInput(action=self.action_2, val=0.0),
                ActionInput(action=self.action_3, val=1.0),
            ]

        return super().get_ready_actions()
