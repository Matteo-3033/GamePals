from agents.copilot import Copilot
from doom.observers import GameStateObserver
from doom.utils import GameStateMessage, MessageType
from game_controllers.utils import ControllerInput, InputType
from doom.game_state_listener import GameStateListener

class ExpertSystemCopilot(Copilot, GameStateObserver):
    """
    The ExpertSystemCopilot class represents the implementation of a Software Agent Copilot for the game Ultimate Doom.
    It represents a Rule-Based System that reads the Game State and notifies its subscribers with some Controller Inputs.
    """
    
    def __init__(self, log_file_path : str):
        super().__init__()
        self.game_state_listener = GameStateListener(log_file_path)
        self.game_state_listener.subscribe(self)
        
    def start(self) -> None:
        """
        Starts listening to the physical controller inputs and notifies its subscribers
        """
        self.game_state_listener.start_listening()
        
    def update_from_game_state(self, state: GameStateMessage) -> None:
        """
        Receives Game State Updates and notifies its subscribers with Controller Inputs and Confidence Levels
        """
        inputs = []
        confidence_level = 1.0 # This will be replaced by the actual value
        match state.type:
            case MessageType.AIMED_AT:
                if "Monster" in state.message:
                    inputs.append(ControllerInput(type=InputType.TRIGGER_RIGHT, val = 255))
                else:
                    inputs.append(ControllerInput(type=InputType.TRIGGER_RIGHT, val = 0))
                    
             
        if inputs:      
            for input in inputs:
                self.notify_all(input, confidence_level)