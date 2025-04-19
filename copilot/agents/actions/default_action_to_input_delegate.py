import logging

from copilot.sources import VirtualControllerProvider
from copilot.sources.controller import ControllerInput

from .abstract_conversion_delegate import ActionConversionDelegate
from .action_input import ActionInput
from .game_action import GameAction

logger = logging.getLogger(__name__)


class DefaultActionToInputDelegate(ActionConversionDelegate):
    """
    Default conversion delegate that just maps any action to the first input listed in the game configuration file.
    """

    def __init__(self, action: GameAction) -> None:
        super().__init__(action)

        inputs = self.config_handler.action_to_game_input(action)
        if not inputs:
            logger.warning(
                f"{action} action: No input found for action {action}. It will be ignored."
            )

    def convert_to_inputs(self, action_input: ActionInput) -> list[ControllerInput]:
        """Converts the Action Input to a Controller Input"""

        inputs = self.config_handler.action_to_game_input(self.get_action())
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

    def convert_from_input(
            self, user_idx: int, c_input: ControllerInput
    ) -> list[ActionInput]:
        """Converts the Controller Input to an Action Input"""

        action = self.config_handler.user_input_to_action(user_idx, c_input.type)

        if action is None:
            return list()

        return [ActionInput(action=action, val=c_input.val)]
