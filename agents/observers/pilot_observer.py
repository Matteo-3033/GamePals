from abc import ABC, abstractmethod

from agents import PilotInputData, MessageData


class PilotObserver(ABC):
    """
    The PilotObserver interface represents a class that receives Controller Inputs and messages from the Pilot.
    """

    @abstractmethod
    def input_from_pilot(self, data: PilotInputData) -> None:
        """ Receives Controller Inputs and the Assistance Level sent by the Pilot """
        pass

    @abstractmethod
    def message_from_pilot(self, data: MessageData) -> None:
        """ Receives a message from the Pilot. Messages are usually Metacommands """
        pass

    def subscribe_to_pilot(self, pilot) -> None:
        """ Subscribes to a Pilot """
        pilot.pilot_inputs_source.subscribe(self.input_from_pilot)
        pilot.pilot_metacommands_source.subscribe(self.message_from_pilot)
