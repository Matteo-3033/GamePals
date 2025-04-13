from abc import ABC, abstractmethod

from copilot.sources.controller import ControllerInput
from copilot.sources.game import GameState, GameStateListener, GameStateObserver

from .actions import ActionInput, ActionInputWithConfidence
from .actor import Actor
from .observer import ActorObserver


class SWAgentActor(Actor, GameStateObserver, ActorObserver, ABC):
    """
    SWAgentActor is a particular type of Actor that represents a Software Agent.

    The inputs it produces are generated based on the current Game State, whose updates it receives.
    In particular, the Agent produces Actions, which will eventually be converted to Game Inputs by the arbitrator.
    """

    def __init__(
        self, game_state: GameStateListener, **kwargs
    ) -> None:
        super().__init__()
        self.game_state = game_state
        self.game_state.subscribe(self)

    @classmethod
    def get_name(cls) -> str:
        """Returns the name of the SW Agent, with which the Agent is identified in the config"""
        return cls.__name__

    def start(self) -> None:
        """Starts listening to the Game State Listener."""
        self.game_state.start_listening()

    def on_game_state_update(self, game_state: GameState) -> None:
        """Receives Game State Updates and produces Inputs to notify to its subscribers."""
        actions = self.compute_actions(game_state)
        for action in actions:
            action_input = ActionInput(action.action, action.val)
            self.notify_input(action_input, action.confidence)

    @abstractmethod
    def compute_actions(self, game_state: GameState) -> list[ActionInputWithConfidence]:
        """Produces a list of action inputs given a Game State. Inputs are executed one after another, with no delay"""
        pass

    def on_arbitrated_inputs(self, input_data: ControllerInput) -> None:
        """Receives the final Inputs produced by the Command Arbitrator and sent to the Game"""
        # Ignore Arbitrated Inputs at the moment (can be overridden by implementations)
        pass
