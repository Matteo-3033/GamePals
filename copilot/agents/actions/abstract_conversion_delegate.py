from abc import ABC, abstractmethod

from ...sources.controller import ControllerInput
from ...utils import ConfigurationHandler
from .action_input import ActionInput
from .game_action import GameAction


class ActionConversionDelegate(ABC):
    """
    Class used to convert Action Inputs to Controller Inputs and vice versa.
    It is useful for actions that manage multiple inputs, such as the throttle a car.
    """

    def __init__(self) -> None:
        self.config_handler = ConfigurationHandler()

    @abstractmethod
    def get_action(self) -> GameAction:
        """Returns the Game Action this Delegate is responsible for"""
        pass

    @abstractmethod
    def convert_to_inputs(self, action_input: ActionInput) -> list[ControllerInput]:
        """Converts the Action Input to a Controller Input"""
        pass

    @abstractmethod
    def convert_from_input(
        self, user_idx: int, c_input: ControllerInput
    ) -> ActionInput | None:
        """Converts the Controller Input to an Action Input"""
        pass
