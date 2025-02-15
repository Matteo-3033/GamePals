from agents.copilot import Copilot
from agents.observers import CopilotInputsObserver
from doom.copilots.runner_copilot import RunnerCopilot
from doom.copilots.aimer_copilot import AimerCopilot
from doom.copilots.shooter_copilot import ShooterCopilot
from doom.observers import GameStateObserver
from doom.utils import DoomCopilot, GameLogMessage, MessageType
from doom.game_state_listener import GameStateListener
import json

class ExpertSystemCopilot(Copilot, CopilotInputsObserver, GameStateObserver):
    """
    The ExpertSystemCopilot class represents the implementation of a Software Agent Copilot for the game Ultimate Doom.
    It represents a Rule-Based System that reads the Game State and notifies its subscribers with some Controller Inputs.
    """ 
    
    def __init__(self, log_file_path : str):
        super().__init__()
        self.copilots : list[DoomCopilot] = []
        self.game_state_listener : GameStateListener = GameStateListener(log_file_path)
        self.game_state_listener.subscribe(self)
        
        # Register Copilots here
        self.register_copilot(RunnerCopilot())
        self.register_copilot(ShooterCopilot())
        self.register_copilot(AimerCopilot())
        
    def register_copilot(self, copilot : DoomCopilot) -> None:
        """
        Registers a Copilot to inform about the Game State
        """
        self.copilots.append(copilot)
        copilot.subscribe(self)
        
    def start(self) -> None:
        """
        Starts listening to the physical controller inputs and notifies its subscribers
        """
        self.game_state_listener.start_listening()
        
    def update_from_copilot(self, input, confidence_level):
        """
        Receives updates from the DoomCopilots and notifies its subscribers with those inputs 
        """
        return super().notify_all(input, confidence_level)
        
    def update_from_game_state(self, state: GameLogMessage) -> None:
        """
        Receives Game State Updates and notifies its subscribers with Controller Inputs and Confidence Levels
        """
        match state.type:
            case MessageType.SPAWN:
                pass # Here should go a reset of all Button Inputs
            case MessageType.GAMESTATE:
                game_state = json.loads(state.json)
                for copilot in self.copilots:
                    copilot.receive_game_state(game_state)
                              
    

        