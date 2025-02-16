from abc import ABC
from typing import override
from game_controllers.physical_controller_listener import PhysicalControllerListener
from agents.observers import CopilotObserver, InputsObserver, PilotObserver
from game_controllers.utils import ControllerInput, InputType
import tomllib

class Pilot(InputsObserver, CopilotObserver, ABC):
    """
    The Pilot class represents the Pilot in the Shared Control System.
    The Pilot listens to the physical controller inputs and notifies its subscribers with Inputs and Assistance Levels.
    It also receives messages (and inputs) from the Copilot.
    It needs to be extended by any Class that wants to cover the Role of the Pilot 
    """
    
    def __init__(self, config_file_path : str):
        self.controller_listener : PhysicalControllerListener = PhysicalControllerListener()
        self.subscribers : list[PilotObserver] = []
        self.assistance_levels : dict[str, float] = {}
        
        self.controller_listener.subscribe(self)
        with open(config_file_path, 'rb') as config_file:
            config = tomllib.load(config_file)
            self.assistance_levels = config["AssistanceLevels"]
            
    def start(self) -> None:
        """
        Starts listening to the physical controller inputs and notifies its subscribers
        """
        
        # Notify all subscribers of the Assistance Levels (using zero-value inputs)
        for key, value in self.assistance_levels.items():
            self.notify_all(ControllerInput(type = InputType(key), val = 0), value)
        
        
        self.controller_listener.start_listening()
        
    def subscribe(self, subscriber : PilotObserver) -> None:
        """
        Adds a subscriber to the list of subscribers
        """
        self.subscribers.append(subscriber)
        
    def notify_all(self, input : ControllerInput, assistance_level : float) -> None:
        """
        Notifies all subscribers of an input
        """
        for subscriber in self.subscribers:
            subscriber.input_from_pilot(input, assistance_level)
    
    def update_from_controller(self, input : ControllerInput) -> None:
        """
        Receives Controller Inputs from the Physical Controller and notifies its subscribers with the Assistance Level
        """
        assistance_level = self.assistance_levels[input.type]
        self.notify_all(input, assistance_level)
        
    @override
    def message_from_copilot(self, message):
        """
        Receives a message from the Copilot
        """
        print(f"[Pilot] Received message from Copilot: {message}")