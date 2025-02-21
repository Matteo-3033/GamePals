from abc import ABC

from agents.actor import Actor
from agents.observers.game_state_observer import GameStateObserver
from doom.gamestate_listener import GameStateListener


class SWAgentActor(Actor, GameStateObserver, ABC):
    """
    SWAgentActor is a particular type of Actor that represents a SW Agent.

    The inputs it produces are generated based on the current Game State, whose updates it receives.
    """

    def __init__(self, game_state: GameStateListener):
        super().__init__()
        self.game_state = game_state

        self.game_state.subscribe(self)

    def start(self) -> None:
        """ Starts listening to the Game State Listener."""
        self.game_state.start_listening()

