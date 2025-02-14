from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
import math
from agents.copilot import Copilot

class MessageType(StrEnum):
    GAMESTATE = "GAMESTATE" # The Game State of the Game, in the form of a JSON
    SPAWN = "SPAWN" # Notifies that the Player has spawned (or respawned)

@dataclass
class GameLogMessage:
    type : MessageType
    json : str
    

class DoomCopilot(Copilot, ABC):
    """
    The DoomCopilot class represents a Software Agent Copilot dedicated to a specific action for the game Ultimate Doom.
    """
    
    @abstractmethod
    def receive_game_state(self, game_state : dict[str, any]) -> None:
        """
        Receives the updated Game State, on which the Copilot will decide and notify the action to take.
        """
        pass
    
    
class Math:
    """
    The Math class provides some mathematical functions
    """
    
    @staticmethod
    def polar_to_cartesian(rho : float, theta : float) -> tuple[float, float]:
        return (rho * math.cos(theta), rho * math.sin(theta))
    
    
    @staticmethod
    def linear_mapping(x : float, range1 : tuple[float, float], range2 : tuple[float, float]) -> float:
        """
        Returns the linear mapping of the value x from range1 to range2
        """
        (x1, x2) = range1
        (y1, y2) = range2
        
        return y1 + (x - x1) * (y2 - y1) / (x2 - x1)
    
    @staticmethod
    def exponential_mapping(x : float, range1 : tuple[float, float], range2 : tuple[float, float], p : int) -> float:
        """
        Returns the exponential mapping of the value x from range1 to range2.
        The parameter p controls the steepness of the curve
        """
        (x1, x2) = range1
        (y1, y2) = range2
        
        return y1 + (y2 - y1) * (((x - x1) / (x2 - x1)) ** p)
    
    