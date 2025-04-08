import logging

from ...sources.controller import ControllerInput
from .abstract_conversion_delegate import ActionConversionDelegate
from .action_input import ActionInput
from .game_action import GameAction

logger = logging.getLogger(__name__)


class BinaryConversionDelegate(ActionConversionDelegate):
    """
    Conversion delegate for actions that are controlled with two inputs.
    For example, the throttle of a car might by controlled by the left trigger (negative) and the right trigger (positive).

    It expects the action to have exactly two inputs defined in the configuration file.
    The first input is considered the negative input and the second one is considered the positive input.
    """

    def __init__(self, action: GameAction) -> None:
        super().__init__()

        self.action = action
        inputs = self.config_handler.action_to_game_input(self.get_action())

        if not inputs or len(inputs) != 2:
            logger.warning(
                f"Action {self.get_action()} should have exactly 2 inputs. It will be ignored."
            )

            self.negative_input = None
            self.positive_input = None

        else:
            self.negative_input, self.positive_input = inputs

    def get_action(self) -> GameAction:
        """Returns the Game Action this Delegate is responsible for"""
        return self.action

    def convert_to_input(self, action_input: ActionInput) -> ControllerInput | None:
        """Converts the Action Input to a Controller Input"""

        if self.positive_input is None or self.negative_input is None:
            return None

        if action_input.val >= 0:
            return ControllerInput(self.positive_input, action_input.val)

        return ControllerInput(self.negative_input, action_input.val)

    def convert_from_input(self, c_input: ControllerInput) -> ActionInput | None:
        """Converts the Controller Input to an Action Input"""

        if self.positive_input is None or self.negative_input is None:
            return None

        if c_input.type == self.positive_input:
            return ActionInput(self.action, c_input.val)

        if c_input.type == self.negative_input:
            return ActionInput(self.action, -c_input.val)

        return None
