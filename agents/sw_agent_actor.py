from abc import ABC, abstractmethod

from . import ActionInputWithConfidence
from ..sources.controller import ControllerInputWithConfidence
from ..sources.game import GameState, GameStateListener, GameStateObserver
from .actor import Actor


class SWAgentActor(Actor, GameStateObserver, ABC):
    """
    SWAgentActor is a particular type of Actor that represents a Software Agent.

    The inputs it produces are generated based on the current Game State, whose updates it receives.
    In particular, the Agent produces Actions, which are converted to Game Inputs before sending.
    """

    def __init__(
            self,
            game_state: GameStateListener,
    ) -> None:
        super().__init__()
        self.game_state = game_state

        self.game_state.subscribe(self)

    def start(self) -> None:
        """Starts listening to the Game State Listener."""
        self.game_state.start_listening()

    def receive_game_state_update(self, game_state: GameState) -> None:
        """Receives Game State Updates and produces Inputs to notify to its subscribers."""
        inputs = self.compute_inputs(game_state)
        for c_input, confidence in inputs:
            self.notify_input(c_input, confidence)

    def compute_inputs(
            self,
            game_state: GameState
    ) -> list[ControllerInputWithConfidence]:
        """Produces a list of inputs given a Game State. Inputs are executed one after another, with no delay"""
        action_inputs = self.compute_actions(game_state)
        return [
            ControllerInputWithConfidence(
                val=action_input.val,
                type=self.config_handler.action_to_game_input(action_input.action),
                confidence=action_input.confidence
            )
            for action_input in action_inputs
        ]

    @abstractmethod
    def compute_actions(
            self,
            game_state: GameState
    ) -> list[ActionInputWithConfidence]:
        """Produces a list of action inputs given a Game State. Inputs are executed one after another, with no delay"""
        pass

