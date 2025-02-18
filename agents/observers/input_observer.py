from abc import ABC, abstractmethod

from agents import InputData


class InputObserver(ABC):
    """
    The Input Observer interface represents a class that receives Controller Inputs.
    """

    @abstractmethod
    def input_from_source(self, data: InputData) -> None:
        """ Receives Inputs from the Input Source"""
        pass

    def subscribe_to_input_source(self, input_source) -> None:
        """ Subscribes to an Input Source """
        input_source.subscribe(self.input_from_source)
