import json
import math

from agents import MessageData, ActorData
from agents.actor import Actor
from agents.sw_agent_actor import SWAgentActor
from doom import Math, DoomGameState, MessageType
from doom.agents import proximity_factor
from sources import ControllerInput, InputType, GameState
from sources.game_state_listener import GameStateListener


class RunToggler(SWAgentActor):
    """
    RunToggler is a Software Agent Actor that transforms the Run input button in a toggle, instead of an hold type
    of button.
    """

    def __init__(self, game_state: GameStateListener, pilot: Actor):
        """ Pilot is the Actor that controls the Run Command """
        super().__init__(game_state)
        pilot.subscribe(self)
        self.running = False

    def get_controlled_inputs(self) -> list[InputType]:
        return [InputType.BTN_X]  # Run button

    def receive_input_update(self, data: ActorData) -> None:
        if data.c_input.type == InputType.BTN_X:
            if data.c_input.val == 1: # Start Running
                if self.running:
                    print(f"[RunToggler] Stopping the Run")
                    self.notify_input(ControllerInput(InputType.BTN_X, val = 0), 1.0)
                else:
                    print(f"[RunToggler] Starting to Run")
                    self.notify_input(ControllerInput(InputType.BTN_X, val = 1), 1.0)
                self.running = not self.running

    def receive_message_update(self, data: MessageData) -> None:
        # Ignore other Actors messages
        pass

    def game_state_to_inputs(self, game_state: DoomGameState) -> list[tuple[ControllerInput, float]]:
        return []
