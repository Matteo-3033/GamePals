from game_controllers.physical_controller_listener import PhysicalControllerListener
from agents.observers import InputsObserver, PilotInputsObserver
from game_controllers.utils import ControllerInput, InputType
import tomllib

class Pilot(InputsObserver):
    """
    The Pilot class represents the Pilot in the Shared Control System.
    The Pilot listens to the physical controller inputs and notifies its subscribers with Inputs and Assistance Levels.
    TODO: Implement the actual Assistance Level Configuration
    """
    
    def __init__(self, config_file_path : str):
        self.controller_listener : PhysicalControllerListener = PhysicalControllerListener()
        self.subscribers : list[PilotInputsObserver] = []
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
        
    def subscribe(self, subscriber : PilotInputsObserver) -> None:
        """
        Adds a subscriber to the list of subscribers
        """
        self.subscribers.append(subscriber)
        
    def notify_all(self, input : ControllerInput, assistance_level : float) -> None:
        """
        Notifies all subscribers of an input
        """
        for subscriber in self.subscribers:
            subscriber.update_from_pilot(input, assistance_level)
    
    def update_from_controller(self, input : ControllerInput) -> None:
        """
        Receives Controller Inputs from the Physical Controller and notifies its subscribers with the Assistance Level
        """
        assistance_level = self.assistance_levels[input.type]
        self.notify_all(input, assistance_level)
        
        