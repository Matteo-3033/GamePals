import json
import time

from agents import MessageData, ActorData
from agents.sw_agent_actor import SWAgentActor
from doom import DoomGameState, MessageType
from sources import ControllerInput, InputType
from sources.game_state_listener import GameStateListener


class InteractCopilot(SWAgentActor):

    def __init__(self, game_state: GameStateListener):
        super().__init__(game_state)
        self.last_input: float = 0.0  # The timestamp of the last press
        self.interactable_tick_count: int = 0  # The duration, in ticks, for the time the player has been looking at something interactable
        self.release_tick_countdown: int = 0  # The number of ticks after which the button will be released

    def get_controlled_inputs(self) -> list[InputType]:
        return [InputType.BTN_A]  # Run button

    def receive_input_update(self, data: ActorData) -> None:
        # Ignore other Actors inputs
        pass

    def receive_message_update(self, data: MessageData) -> None:
        # Ignore other Actors messages
        pass

    def game_state_to_inputs(self, game_state: DoomGameState) -> list[tuple[ControllerInput, float]]:
        """ RunnerCopilots checks whether a monster is close to the player. If not, it decides to run """
        if game_state.type != MessageType.GAMESTATE:
            return []

        game_data = json.loads(game_state.json)
        aimed_at = game_data['AIMED_AT']

        is_interactable = aimed_at['interactable']
        distance = aimed_at['distance']
        curr_timestamp = time.time()
        if is_interactable and distance < 25:
            if curr_timestamp - self.last_input > 2.0:  # At most every 2 seconds
                self.last_input = curr_timestamp
                self.release_tick_countdown = 4
                return [(ControllerInput(InputType.BTN_A, val=1), 1.0)]

        if self.release_tick_countdown >= 0:
            self.release_tick_countdown -= 1

        if self.release_tick_countdown == 0:
            return [(ControllerInput(InputType.BTN_A, val=0), 1.0)]

        return []
