from abc import ABC, abstractmethod
from agents.input_source import CopilotInputData, InputData, InputSource, MessageData, PilotInputData
from agents.pilot import Pilot
from agents.copilot import Copilot

# Observer Pattern Interfaces, used in combination with the InputSource to notify the Observers of specific SourceData's

class InputObserver(ABC):
    """
    The Input Observer interface represents a class that receives Controller Inputs.
    """
    
    @abstractmethod
    def input_from_source(self, data : InputData) -> None:
        """ Receives Inputs from the Input Source"""
        pass
    
    def subscribe_to_input_source(self, input_source : InputSource) -> None:
        """ Subscribes to an Input Source """
        input_source.subscribe(self.input_from_source)


class PilotObserver(ABC):
    """
    The PilotObserver interface represents a class that receives Controller Inputs and messages from the Pilot.
    """
    
    @abstractmethod
    def input_from_pilot(self, data : PilotInputData) -> None:
        """ Receives Controller Inputs and the Assistance Level sent by the Pilot """
        pass
    
    @abstractmethod
    def message_from_pilot(self, data: MessageData) -> None:
        """ Receives a message from the Pilot. Messages are usually Metacommands """
        pass
        
    def subscribe_to_pilot(self, pilot : Pilot) -> None:
        """ Subscribes to a Pilot """
        pilot.pilot_inputs_source.subscribe(self.input_from_pilot)
        pilot.pilot_metacommands_source.subscribe(self.message_from_pilot)
    
    
class CopilotObserver(ABC):
    """
    The CopilotObserver interface represents a class that receives Controller Inputs and messages from the Pilot.
    """
    
    @abstractmethod
    def input_from_copilot(self, data : CopilotInputData) -> None:
        """ Receives Controller Inputs and the Assistance Level sent by the Copilot """
        pass
    
    @abstractmethod
    def message_from_copilot(self, data: MessageData) -> None:
        """ Receives a message from the Copilot. Messages are usually Metacommands """
        pass
        
    def subscribe_to_copilot(self, copilot : Copilot) -> None:
        """ Subscribes to a Pilot """
        copilot.copilot_inputs_source.subscribe(self.input_from_copilot)
        copilot.copilots_metacommands_source.subscribe(self.message_from_copilot)
    