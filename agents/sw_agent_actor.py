from abc import ABC, abstractmethod

from . import ActionInputWithConfidence
from ..sources.controller import ControllerInput, InputType, ControllerInputWithConfidence
from ..sources.game import GameState, GameStateListener, GameStateObserver, GameAction
from .actor import Actor

ActionToInputMap = dict[GameAction, InputType]


class SWAgentActor(Actor, GameStateObserver, ABC):
    """
    SWAgentActor is a particular type of Actor that represents a Software Agent.

    The inputs it produces are generated based on the current Game State, whose updates it receives.
    """

    def __init__(
            self,
            game_state: GameStateListener,
            action_to_game_input: ActionToInputMap,
    ) -> None:
        super().__init__()
        self.game_state = game_state

        #Filter for only actually used actions
        self.action_to_game_input = {
            action: game_input
            for action, game_input in action_to_game_input
            if action in self.get_controlled_actions()
        }

        self.game_state.subscribe(self)

    def start(self) -> None:
        """Starts listening to the Game State Listener."""
        self.game_state.start_listening()

    def receive_game_state_update(self, game_state: GameState) -> None:
        """Receives Game State Updates and produces Inputs to notify to its subscribers."""
        inputs = self.game_state_to_inputs(game_state)
        for c_input, confidence in inputs:
            self.notify_input(c_input, confidence)

    def action_to_controller_input(self, action: GameAction, value: float) -> ControllerInput:
        """Converts (action, value) into (input_type, value)"""
        return ControllerInput(self.action_to_game_input[action], value)

    def game_state_to_inputs(
            self, game_state: GameState
    ) -> list[ControllerInputWithConfidence]:
        """Produces inputs given a Game State. Inputs are specified by InputType"""
        action_inputs = self.game_state_to_action_inputs(game_state)
        return [
            ControllerInputWithConfidence(
                val=action_input.val,
                type=self.action_to_game_input[action_input.action],
                confidence=action_input.confidence
            )
            for action_input in action_inputs
        ]

    @abstractmethod
    def game_state_to_action_inputs(
            self, game_state: GameState
    ) -> list[ActionInputWithConfidence]:
        """Produces inputs given a Game State. Inputs are specified by GameAction"""
        pass

