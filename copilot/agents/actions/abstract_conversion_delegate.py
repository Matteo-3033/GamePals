from abc import ABC, abstractmethod

from copilot.sources.controller import ControllerInput
from copilot.utils import ConfigurationHandler

from .action_input import ActionInput
from .game_action import GameAction


class ActionConversionDelegate(ABC):
    """
    Class used to convert Action Inputs to Controller Inputs and vice versa.
    It is useful for actions that manage multiple inputs, such as the throttle a car.


    The conversion from Controller Input to Action is delayed to allow for hold/multiple buttons combinations to happen.
    It works in two steps:
    * Register the occurring of the input
    * Check for any ready-to-be-converted Actions and return them
    """

    def __init__(self, user_idx : int, actions: list[GameAction]) -> None:
        self.user_idx = user_idx
        self.actions = actions

        self.config_handler = ConfigurationHandler()

    def get_user_idx(self) -> int:
        return self.user_idx

    def get_actions(self) -> list[GameAction]:
        """Returns the Game Actions this Delegate is responsible for"""
        return self.actions

    @abstractmethod
    def register_input(self, c_input: ControllerInput) -> None:
        """Registers that an input has occurred"""
        pass

    @abstractmethod
    def get_ready_actions(self) -> list[ActionInput]:
        """Returns the ready-to-be-converted Actions"""
        pass

    @abstractmethod
    def convert_to_inputs(self, action_input: ActionInput) -> list[ControllerInput]:
        """Converts the Action Input to a Controller Input"""
        pass
