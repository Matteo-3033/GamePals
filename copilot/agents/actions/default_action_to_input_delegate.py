import logging
import time
from dataclasses import dataclass
from collections import deque

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

    def __init__(self, user_idx : int, actions: list[GameAction]) -> None:
        super().__init__(user_idx, actions)

        all_user_inputs : set[InputType] = set()

        for action in actions:
            game_inputs = self.config_handler.action_to_game_input(action)
            if not game_inputs:
                logger.warning(
                    f"{action} action: No game input found for action {action}. It will be ignored."
                )
            user_inputs = self.config_handler.action_to_user_input(self.user_idx, action)
            if user_inputs:
                all_user_inputs.update(user_inputs)

        self.latest_inputs: dict[InputType, RegisteredInputDetails] = {
            input_type: RegisteredInputDetails(0.0, 0.0, True)
            for input_type in all_user_inputs
        }

        self.ready_actions_queue : deque[ActionInput] = deque()

    def register_input(self, c_input: ControllerInput) -> None:
        """Registers that an input has occurred"""
        if c_input.type not in self.latest_inputs:
            logger.warning(f"Input type {c_input.type} is not recognized by its delegate")

        self.latest_inputs[c_input.type] = RegisteredInputDetails(
            val=c_input.val, timestamp=time.time(), sent=False
        )

        actions = self.config_handler.user_input_to_actions(self.user_idx, c_input.type)
        if len(actions) > 0:
            action = actions[0]
            action_input = ActionInput(action=action, val=c_input.val)
            self.ready_actions_queue.append(action_input)

    def get_ready_actions(self) -> list[ActionInput]:
        """Returns the ready-to-be-converted Actions"""
        ready_actions: list[ActionInput] = list()
        added_actions: set[GameAction] = set()

        still_in_queue : deque[ActionInput] = deque()

        while self.ready_actions_queue:
            action_input = self.ready_actions_queue.popleft()
            action = action_input.action
            if action and action not in added_actions:
                ready_actions.append(action_input)
                added_actions.add(action)
            else:
                still_in_queue.append(action_input)

        self.ready_actions_queue = still_in_queue
        return ready_actions

    def convert_to_inputs(self, action_input: ActionInput) -> list[ControllerInput]:
        """Converts the Action Input to a Controller Input"""

        inputs = self.config_handler.action_to_game_input(action_input.action)
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
