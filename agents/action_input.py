from dataclasses import dataclass
from typing import Generic

from ..sources.controller import ControllerInput
from ..sources.game import TGameAction


@dataclass
class ActionInput(Generic[TGameAction]):
    """ActionInput is an input yet to be bound to a specific InputType."""

    action: TGameAction
    val: float


@dataclass
class ActionInputWithConfidence(ActionInput):
    """ActionInputWithConfidence extends the ActionInput with the related confidence"""

    confidence: float


from abc import ABC, abstractmethod


class ActionConversionDelegate(Generic[TGameAction], ABC):

    @abstractmethod
    def get_action(self) -> TGameAction:
        """Returns the Game Action this Delegate is responsible for"""
        pass

    @abstractmethod
    def convert_to_input(self, action_input: ActionInput) -> ControllerInput | None:
        """Converts the Action Input to a Controller Input"""
        pass

    @abstractmethod
    def convert_from_input(self, c_input: ControllerInput) -> ActionInput | None:
        """Converts the Controller Input to an Action Input"""
        pass
