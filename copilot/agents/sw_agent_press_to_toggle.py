from ..sources import VirtualControllerProvider
from ..sources.game import GameState, GameStateListener
from .actions import ActionInput, ActionInputWithConfidence, GameAction
from .actor import Actor
from .observer import ActorData, ActorObserver, MessageData
from .sw_agent_actor import SWAgentActor


class SWAgentPressToToggle(SWAgentActor, ActorObserver):
    """
    SWAgentPressToToggle is a particular type of SWAgentActor that allows to use the button associated to a certain
    action as a toggle button.

    The pilot is the Actor that controls the command.
    """

    def __init__(
        self, game_state: GameStateListener, pilot: Actor | None = None, **kwargs
    ) -> None:
        super().__init__(game_state, **kwargs)

        actions = self.get_controlled_actions()

        assert (
            len(actions) == 1
        ), f"SWAgentPressToToggle agent can only control one action. Found {len(actions)}"

        self.last_input_timestamp: float = 0
        self.pressed = False
        self.pilot = pilot

        if self.pilot is not None:
            self.pilot.subscribe(self)

    @property
    def action(self) -> GameAction:
        return self.get_controlled_actions()[0]

    @property
    def enabled(self) -> bool:
        return self.pilot is not None

    def _should_toggle(self) -> bool:
        """Returns true if the hold to toggle mechanic should be performed"""
        return self.enabled

    def on_input_update(self, actor_data: ActorData) -> None:
        if self._should_toggle() and actor_data.data.action == self.action:
            if abs(actor_data.data.val) > VirtualControllerProvider.INPUT_THRESHOLD:
                self.pressed = not self.pressed

    def on_message_update(self, message_data: MessageData) -> None:
        pass

    def on_game_state_update(self, game_state: GameState) -> None:
        if not self.enabled:
            return

        if not self.pressed:
            self.notify_input(ActionInput(action=self.action, val=0.0), confidence=1.0)
        else:
            super().on_game_state_update(game_state)

    def compute_actions(self, game_state: GameState) -> list[ActionInputWithConfidence]:
        return [ActionInputWithConfidence(self.action, val=1.0, confidence=1.0)]

    def get_controlled_actions(self) -> list[GameAction]:
        return list()
