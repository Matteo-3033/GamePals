from abc import ABC, abstractmethod

from agents import CopilotInputData, MessageData


class CopilotObserver(ABC):
    """
    The CopilotObserver interface represents a class that receives Controller Inputs and messages from the Pilot.
    """

    @abstractmethod
    def input_from_copilot(self, data: CopilotInputData) -> None:
        """ Receives Controller Inputs and the Assistance Level sent by the Copilot """
        pass

    @abstractmethod
    def message_from_copilot(self, data: MessageData) -> None:
        """ Receives a message from the Copilot. Messages are usually Metacommands """
        pass

    def subscribe_to_copilot(self, copilot) -> None:
        """ Subscribes to a Pilot """
        copilot.copilot_inputs_source.subscribe(self.input_from_copilot)
        copilot.copilots_metacommands_source.subscribe(self.message_from_copilot)