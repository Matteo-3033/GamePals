from abc import ABC, abstractmethod

from .game_state import GameState
from .game_state_observer import GameStateObserver


class GameStateListener(ABC):
    """
    GameStateListener is the Superclass for any Game State listener classes.

    When implementing the architecture for a new game, a GameStateListener class is expected for the SW Agent Actors
    to be able to receive the Game State successfully.
    """

    def __init__(self):
        self.subscribers: list[GameStateObserver] = []

    def subscribe(self, subscriber: GameStateObserver) -> None:
        """Adds a subscriber to the list of subscribers"""
        self.subscribers.append(subscriber)

    def notify_all(self, state: GameState) -> None:
        """Notifies all subscribers of an input"""
        for subscriber in self.subscribers:
            subscriber.on_game_state_update(state)

    @abstractmethod
    def start_listening(self):
        """Starts listening for Game State Updates"""
        pass

    def stop_listening(self):
        """Stops listening for Game State Updates"""
        pass

    @staticmethod
    def game_state_to_log(state: GameState) -> str:
        """Given a Game State, returns the string representation that should be printed on log files"""
        return str(state)