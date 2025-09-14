from gamepals.sources import VirtualControllerProvider
from gamepals.sources.game import GameState, GameStateListener

from .actions import ActionInput, ActionInputWithConfidence, GameAction
from .actor import Actor
from .observer import ActorData, ActorObserver, MessageData
from .sw_agent_actor import SWAgentActor


class SWAgentPressToToggle(SWAgentActor, ActorObserver):
    """
    SWAgentPressToToggle is a specific type of SWAgentActor that allows the use of a button associated with a certain action as a toggle.

    When the button is pressed, the agent will begin pressing the corresponding action button. When it is pressed again, the agent will release it.

    Classes that inherit from this class can override the compute_actions method to customize the agent's behavior after the button has been pressed once.

    If no pilot is specified, the agent will not perform any actions. However, it will still subscribe to game state events, and its subclasses can still trigger actions based on the game state, just like a regular SWAgentActor.
    """

    def __init__(
        self,
        game_state: GameStateListener,
        pilot: Actor | None = None,
        start_pressed: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(game_state, **kwargs)

        actions = self.get_controllable_actions()

        assert (
            len(actions) == 1
        ), f"SWAgentPressToToggle agent can only control one action. Found {len(actions)}"

        self.last_input_timestamp: float = 0
        self.pressed = start_pressed
        self.pilot = pilot

        if self.pilot is not None:
            self.pilot.subscribe(self)

    @property
    def action(self) -> GameAction:
        return self.get_controllable_actions()[0]

    @property
    def toggle_enabled(self) -> bool:
        """Returns true if the toggle agent is enabled (i.e. has a pilot)"""
        return self.pilot is not None

    def _should_toggle(self, actor_data: ActorData) -> bool:
        """Returns true if the hold to toggle mechanic should be performed when the pilot presses the button"""
        return abs(actor_data.data.val) > VirtualControllerProvider.INPUT_THRESHOLD

    def on_input_update(self, actor_data: ActorData) -> None:
        if (
            self.toggle_enabled
            and actor_data.data.action == self.action
            and self._should_toggle(actor_data)
        ):
            self.pressed = not self.pressed

    def on_message_update(self, message_data: MessageData) -> None:
        pass

    def on_game_state_update(self, game_state: GameState) -> None:
        if self.toggle_enabled and not self.pressed:
            self.notify_input(ActionInput(action=self.action, val=0.0), confidence=1.0)
        else:
            # If the agent is not enabled (no pilot specified) the super method is called as normal
            # Subclasses can override this method to perform actions based on the game state even if the toggle is not enabled
            super().on_game_state_update(game_state)

    def compute_actions(self, game_state: GameState) -> list[ActionInputWithConfidence]:
        if not self.toggle_enabled:
            return list()

        return [ActionInputWithConfidence(self.action, val=1.0, confidence=1.0)]

    def get_controllable_actions(self) -> list[GameAction]:
        return list()
