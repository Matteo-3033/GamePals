from abc import ABC
from agents.observers import CopilotInputsObserver
from game_controllers.utils import ControllerInput

class Copilot(ABC):
    """
    The Copilot class represents the Copilot in the Shared Control System.
    It needs to be Implemented by any Class that wants to cover the Role of the Copilot (i.e. Second Player, Software Agent)
    """
    
    def __init__(self):
        self.subscribers : list[CopilotInputsObserver] = []
        
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
            subscriber.update_from_copilot(input, confidence_level)

        
        