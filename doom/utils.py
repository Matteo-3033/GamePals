from dataclasses import dataclass
from enum import StrEnum
import math

class MessageType(StrEnum):
    AIMED_AT = "AIMED_AT" # The Object aimed at by the Player
    MONSTERS = "MONSTERS" # The Monsters on the Screen

@dataclass
class GameStateMessage:
    type : MessageType
    message : str
    
    
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
    
    