from abc import ABC, abstractmethod

from agents import ArbitratorData
from agents.actor import Actor
from agents.observers.game_state_observer import GameStateObserver
from input_sources import GameState, ControllerInput
from input_sources.game_state_listener import GameStateListener


class SWAgentActor(Actor, GameStateObserver, ABC):
    """
    SWAgentActor is a particular type of Actor that represents a Software Agent.

    The inputs it produces are generated based on the current Game State, whose updates it receives.
    """

    def __init__(self, game_state: GameStateListener):
        super().__init__()
        self.game_state = game_state

        self.game_state.subscribe(self)

    def start(self) -> None:
        """ Starts listening to the Game State Listener."""
        self.game_state.start_listening()

    def receive_game_state_update(self, game_state: GameState) -> None:
        """ Receives Game State Updates and produces Inputs to notify to its subscribers."""
        inputs = self.game_state_to_inputs(game_state)
        for (c_input, confidence) in inputs:
            self.notify_input(c_input, confidence)

    @abstractmethod
    def game_state_to_inputs(self, game_state: GameState) -> list[tuple[ControllerInput, float]]:
        """ Produces inputs given a Game State """
        pass

    def get_arbitrator_updates(self, data: ArbitratorData) -> None:
        """ Receives updates from the arbitrator it's connected to """
        pass