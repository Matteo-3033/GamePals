import json
import time
import logging

from agents.datas import MessageData, ActorData
from agents.actor import Actor
from agents.observers.actor_observer import ActorObserver
from agents.sw_agent_actor import SWAgentActor
from doom.doom_game_state import DoomGameState, MessageType
from sources.controller_inputs import ControllerInput, InputType
from sources.game_state_listener import GameStateListener

logger = logging.getLogger(__name__)

class InteractCopilot(SWAgentActor, ActorObserver):
    TICKS_TO_INTERACT = 10
    MIN_TIME_BETWEEN_PRESSES = 2  # In Seconds
    TICKS_BETWEEN_PRESS_AND_RELEASE = 4

    def __init__(self, game_state: GameStateListener, pilot: Actor):
        super().__init__(game_state)
        pilot.subscribe(self)
        self.last_input: float = 0.0  # The timestamp of the last press
        self.interactable_tick_count: int = 0  # The duration, in ticks, for the time the player has been looking at something interactable
        self.release_tick_countdown: int = 0  # The number of ticks after which the button will be released

    def get_controlled_inputs(self) -> list[InputType]:
        return [InputType.BTN_A]  # Run button

    def receive_input_update(self, data: ActorData) -> None:
        # Other Actors are also able to reset the last_input value
        if data.c_input.type == InputType.BTN_A and data.c_input.val == 1:
            self.last_input = time.time()

    def receive_message_update(self, data: MessageData) -> None:
        # Ignore other Actors messages
        pass

    def get_arbitrated_inputs(self, input_data: ControllerInput) -> None:
        # Ignore Arbitrated Inputs
        pass

    def game_state_to_inputs(self, game_state: DoomGameState) -> list[tuple[ControllerInput, float]]:
        """
        InteractCopilots checks whether the player is looking at an Interactable object.

        It presses the interact button only if:
            - The player has been looking at the Interactable object for TICKS_TO_INTERACT ticks.
            - The last press was more than MIN_TIME_BETWEEN_PRESSES seconds ago.
        """
        if game_state.type != MessageType.GAMESTATE:
            return []

        game_data = json.loads(game_state.json)
        aimed_at = game_data['AIMED_AT']

        is_interactable = aimed_at['interactable']

        distance = aimed_at['distance']
        curr_timestamp = time.time()
        if is_interactable and distance < 25:
            self.interactable_tick_count += 1
            if self.interactable_tick_count >= self.TICKS_TO_INTERACT and \
                    curr_timestamp - self.last_input > self.MIN_TIME_BETWEEN_PRESSES:
                self.last_input = curr_timestamp
                self.release_tick_countdown = self.TICKS_BETWEEN_PRESS_AND_RELEASE
                return [(ControllerInput(InputType.BTN_A, val=1), 1.0)]
        else:
            self.interactable_tick_count = 0

        if self.release_tick_countdown >= 0:
            self.release_tick_countdown -= 1

        if self.release_tick_countdown == 0:
            return [(ControllerInput(InputType.BTN_A, val=0), 1.0)]

        return []
