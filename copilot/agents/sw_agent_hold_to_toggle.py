from ..sources import VirtualControllerProvider
from ..sources.game import GameState, GameStateListener
from .actions import ActionInput, ActionInputWithConfidence, GameAction
from .actor import Actor
from .observer import ActorData, ActorObserver, MessageData
from .sw_agent_actor import SWAgentActor


class SWAgentHoldToToggle(SWAgentActor, ActorObserver):
    """
    SWAgentHoldToToggle is a particular type of SWAgentActor that allows to use the button associated to a certain
    action as a toggle button, instead of a hold button.

    The pilot is the Actor that controls the command.
    """

    def __init__(
        self,
        game_state: GameStateListener,
        action: GameAction,
        pilot: Actor | None = None,
    ) -> None:
        super().__init__(game_state)
        self.last_input_timestamp: float = 0
        self.action = action
        self.pressed = False
        self.pilot = pilot

        if self.pilot is not None:
            self.pilot.subscribe(self)

    def _should_toggle(self) -> bool:
        """Returns true if the hold to toggle mechanic should be performed"""
        return self.pilot is not None

    def on_input_update(self, actor_data: ActorData) -> None:
        if self._should_toggle() and actor_data.data.action == self.action:
            if (
                actor_data.data.val > VirtualControllerProvider.INPUT_THRESHOLD
            ):  # Start Running
                if self.pressed:
                    self.notify_input(ActionInput(self.action, val=0.0), 1.0)
                else:
                    self.notify_input(ActionInput(self.action, val=1.0), 1.0)
                self.pressed = not self.pressed

    def on_message_update(self, message_data: MessageData) -> None:
        pass

    def compute_actions(self, game_state: GameState) -> list[ActionInputWithConfidence]:
        return list()

    def get_controlled_actions(self) -> list[GameAction]:
        return list()
