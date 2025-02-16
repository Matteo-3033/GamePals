from abc import ABC, abstractmethod
from game_controllers.utils import ControllerInput

class InputsObserver(ABC):
    """
    The Observer interface represents a class that receives Controller Inputs
    """
    
    @abstractmethod
    def update_from_controller(self, input: ControllerInput) -> None:
        """
        Receives Controller Inputs
        """
        pass


class PilotInputsObserver(ABC):
    """
    The PilotInputsObserver interface represents a class that receives Controller Inputs from the Pilot
    """
    
    def input_from_pilot(self, input: ControllerInput, assistance_level : float) -> None:
        """
        Receives Controller Inputs and the Assistance Level requested by the Pilot
        """
        pass
    
    def message_from_pilot(self, message: str) -> None:
        """
        Receives a message from the Pilot
        """
        pass
  
  
class CopilotInputsObserver(ABC):
    """
    The CopilotInputsObserver interface represents a class that receives Controller Inputs from the Copilot
    """
    
    def input_from_copilot(self, input: ControllerInput, confidence_level : float) -> None:
        """
        Receives Controller Inputs and the Confidence Level provided by the Copilot
        """
        pass
    
    
    def message_from_copilot(self, message: str) -> None:
        """
        Receives a message from the Copilot
        """
        pass
    
