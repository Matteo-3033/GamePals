from abc import ABC, abstractmethod

from agents import GameState


class GameStateObserver(ABC):
    """
    The Game State Observer interface represents a class that receives a representation of the Game State
    """

    @abstractmethod
    def receive_game_state_update(self, game_state : GameState) -> None:
        """ Receives Game State Updates """
        pass

