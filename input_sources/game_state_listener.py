from abc import abstractmethod

from agents.observers.game_state_observer import GameStateObserver
from input_sources import GameState


class GameStateListener:

    def __init__(self):
        self.subscribers: list[GameStateObserver] = []

    def subscribe(self, subscriber: GameStateObserver) -> None:
        """ Adds a subscriber to the list of subscribers """
        self.subscribers.append(subscriber)

    def notify_all(self, state: GameState) -> None:
        """ Notifies all subscribers of an input """
        for subscriber in self.subscribers:
            subscriber.receive_game_state_update(state)

    @abstractmethod
    def start_listening(self):
        """ Starts listening for Game State Updates """
        pass