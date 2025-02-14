from abc import ABC, abstractmethod

from doom.utils import GameLogMessage


class GameStateObserver(ABC):
    """
    The Observer interface represents a class that receives information about the Game State of the game Ultimate Doom
    """
    
    @abstractmethod
    def update_from_game_state(self, input: GameLogMessage) -> None:
        """
        Receives Game State Updates
        """
        pass

