import time
from abc import ABC, abstractmethod

from . import ActionInputWithConfidence
from ..sources.controller import ControllerInput, InputType, ControllerInputWithConfidence
from ..sources.game import GameState, GameStateListener, GameAction
from .sw_agent_actor import SWAgentActor

ActionToInputMap = dict[GameAction, InputType]

ActionInputWithConfidenceAndDelay = tuple[ActionInputWithConfidence, float]


class SWAgentSequencedActor(SWAgentActor, ABC):
    """
    SWAgentSequencedActor is a particular type of SWAgentActor that calculates actions as sequences of inputs.

    The sequence inputs are sent to its subscribers based on the specified delays.
    """

    def __init__(
            self,
            game_state: GameStateListener,
            action_to_input: ActionToInputMap,
    ) -> None:
        super().__init__(game_state, action_to_input)
        self.current_sequence: list[ActionInputWithConfidenceAndDelay] = []
        self.last_input_timestamp: float = 0

    @abstractmethod
    def game_state_to_action_input_sequence(
            self, game_state: GameState
    ) -> list[ActionInputWithConfidenceAndDelay] | None:
        """Produces input sequences given a Game State. Inputs are specified with a delay from the previous one in the order"""
        pass

    def game_state_to_action_inputs(
            self, game_state: GameState
    ) -> list[ActionInputWithConfidence]:
        """Produces inputs given a Game State. Inputs are specified by GameAction"""

        new_sequence = self.game_state_to_action_input_sequence(game_state)

        if new_sequence is not None:
            self.current_sequence = new_sequence  # Override last sequence if a better sequence is found

        if len(self.current_sequence) == 0:
            return []

        (next_input, next_delay) = self.current_sequence[0]
        current_timestamp = time.time()
        if self.last_input_timestamp + next_delay < current_timestamp:
            # Time to execute a new input
            self.current_sequence.pop(0)
            self.last_input_timestamp = current_timestamp
            return [next_input]
        else:
            return []
