from abc import ABC, abstractmethod
from dataclasses import dataclass

from .controller_inputs import ControllerInput


@dataclass
class InputData:
    """The wrapper class of the Data sent to a Controller Observer"""

    c_input: ControllerInput


class ControllerObserver(ABC):
    """
    The Controller Observer interface represents a class that receives Controller Inputs from a Physical Controller.
    """

    @abstractmethod
    def on_controller_input(self, data: InputData) -> None:
        """Receives Inputs from the Input Source"""
        pass
