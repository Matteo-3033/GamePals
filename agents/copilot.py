from abc import ABC
from typing import override
from agents.observers import CopilotInputsObserver, PilotInputsObserver
from game_controllers.utils import ControllerInput, ControllerInputsMap

class Copilot(PilotInputsObserver, ABC):
    """
    The Copilot class represents the Copilot in the Shared Control System.
    It needs to be Implemented by any Class that wants to cover the Role of the Copilot (i.e. Second Player, Software Agent)
    """
    
    def __init__(self):
        self.subscribers : list[CopilotInputsObserver] = []
        self.pilot_inputs_map : ControllerInputsMap = ControllerInputsMap() # The latest Pilot inputs
        
    def subscribe(self, subscriber : CopilotInputsObserver) -> None:
        """
        Adds a subscriber to the list of subscribers
        """
        self.subscribers.append(subscriber)
        
    def notify_all(self, input : ControllerInput, confidence_level : float) -> None:
        """
        Notifies all subscribers of an input
        """
        for subscriber in self.subscribers:
            subscriber.input_from_copilot(input, confidence_level)
            
    @override
    def input_from_pilot(self, input : ControllerInput, assistance_level : float) -> None:
        """
        Receives inputs from the Pilot and saves them in the Pilot Inputs Map
        """
        self.pilot_inputs_map.set(input, assistance_level)
            
    @override
    def message_from_pilot(self, message : str) -> None:
        """
        Receives a message from the Pilot
        """
        print(f"[Copilot] Received message from Pilot: {message}")
            
            
    

        
        