from abc import ABC, abstractmethod

from agents.datas import InputData


class ControllerObserver(ABC):
    """
    The Controller Observer interface represents a class that receives Controller Inputs from a Physical Controller.
    """

    @abstractmethod
    def receive_controller_input(self, data: InputData) -> None:
        """ Receives Inputs from the Input Source """
        pass
