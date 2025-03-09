import time
from abc import ABC, abstractmethod

from ..sources.controller import ControllerInput
from ..sources.game_state import GameState, GameStateListener, GameStateObserver
from .sw_agent_actor import SWAgentActor


class SWAgentSequencedActor(SWAgentActor, GameStateObserver, ABC):
    """
    SWAgentSequencedActor is a particular type of SWAgentActor that calculates actions as sequences of inputs.

    The sequence inputs are sent to its subscribers based on the specified delays.
    """

    def __init__(self, game_state: GameStateListener):
        super().__init__(game_state)
        self.current_sequence : list[tuple[ControllerInput, float, float]] = []
        self.last_input_timestamp : float = 0


    @abstractmethod
    def game_state_to_input_sequence(
            self, game_state : GameState
    ) -> list[tuple[ControllerInput, float, float]] | None:
        """Produces input sequences given a Game State. Tuples are (input, confidence, delay)"""
        pass


    def game_state_to_inputs(
        self, game_state: GameState
    ) -> list[tuple[ControllerInput, float]]:
        """Produces inputs given a Game State. Tuples are (input, confidence)"""

        new_sequence = self.game_state_to_input_sequence(game_state)

        if new_sequence is not None:
            self.current_sequence = new_sequence # Override last sequence

        if len(self.current_sequence) == 0:
            return []

        (next_input, next_confidence, next_delay) = self.current_sequence[0]
        current_timestamp = time.time()
        if self.last_input_timestamp + next_delay < current_timestamp:
            # Time to execute a new input
            self.current_sequence.pop(0)
            self.last_input_timestamp = current_timestamp
            return [(next_input, next_confidence)]
        else:
            return []

