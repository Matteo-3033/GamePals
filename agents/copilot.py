from abc import ABC
from agents.observers import CopilotObserver, PilotObserver
from agents.input_source import CopilotInputData, InputSource, MessageData, PilotInputData
from game_controllers.utils import ControllerInput, ControllerInputsMap

class Copilot(PilotObserver, ABC):
    """
    The Copilot class represents the Copilot in the Shared Control System.
    
    By default, it receives inputs and messages (metacommands) from the Pilot.
    Copilot can use this information to make better informed decisions.
    
    It needs to be extended by any Class that wants to cover the Role of the Copilot (i.e. Second Player, Software Agent).
    """
    
    def __init__(self):
        self.copilot_inputs_source : InputSource[CopilotInputData] = InputSource[CopilotInputData]() # Copilot inputs and confidence levels
        self.copilot_metacommands_source : InputSource[str] = InputSource[str]() # Metacommands are messages that are not inputs
        self.pilot_inputs_map : ControllerInputsMap = ControllerInputsMap() # The latest Pilot inputs
        
    def subscribe(self, observer : CopilotObserver) -> None:
        """ 
        Subscribe an Observer to the Copilot
        """
        observer.subscribe_to_copilot(self)
        
    def notify_inputs(self, input : ControllerInput, confidence_level : float) -> None:
        """ 
        Notify all subscribers with the input and the confidence level
        """
        self.copilot_inputs_source.notify_all(CopilotInputData(input, confidence_level))
        
    def notify_metacommand(self, message : str) -> None:
        """ 
        Notify all subscribers with a message
        """
        self.copilot_metacommands_source.notify_all(message)
            
    def start(self) -> None:
        """ 
        Starts the Copilot 
        """
        pass
    
    def input_from_pilot(self, data : PilotInputData) -> None:
        """ 
        Receives Controller Inputs and the Assistance Level sent by the Pilot.
        The Inputs are stored in the Pilot Inputs Map.
        """
        self.pilot_inputs_map.set(data.input, data.assistance_level)
    
    def message_from_pilot(self, data: MessageData) -> None:
        """ Receives a message from the Pilot. Messages are usually Metacommands """
        print(f"Copilot received a message from Pilot: {data.message}")
    
            
    

        
        